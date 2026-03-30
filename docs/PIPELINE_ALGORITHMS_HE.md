> **LANGUAGE NOTICE:** This document is a legacy Hebrew specification (MyFarmAgents v1.1).
> Platform: **MyFarmAgents** | Agent: **OrganicMarketAgent**
> All new documents are written in English. See `docs/GLOSSARY.md` for canonical terminology.
> This file is pending English rewrite — scheduled per milestone.

---

# אלגוריתמי Pipeline — SmallFarms Market Data System

גרסה: 1.0  
תאריך: 2026-03-29

---

## 1. מבנה ה-Pipeline

```
cron (06:00 יומי)
    │
    ▼
IngestionRunner
    │
    ├── CollectorEngine (לכל מקור פעיל)
    │       ├── FetchRaw
    │       └── SaveRawAsset
    │
    ├── ParserEngine (לכל raw_asset חדש)
    │       └── ExtractItems → raw_extracted_items
    │
    ├── NormalizerEngine (לכל raw_extracted_item)
    │       └── → normalized_observations
    │
    ├── AggregatorEngine
    │       ├── daily_aggregates
    │       └── weekly_snapshots (ביום ראשון)
    │
    ├── QAEngine
    │       └── anomaly detection → observation_flags auto
    │
    └── PublishEngine (אם threshold עבר)
            ├── BuildArtifacts
            ├── UploadArtifacts (FTPS)
            └── UpdateManifest
```

---

## 2. IngestionRunner — אלגוריתם ראשי

```python
# scheduler/runner.py

def run_daily_ingestion(run_type: str = 'daily') -> IngestionRun:
    """
    אלגוריתם:
    1. צור ingestion_run חדש (status='running')
    2. טען כל מקורות פעילים (sources WHERE is_active=true AND status='active')
    3. לכל מקור — הרץ collect+parse+normalize בסדר:
       - daily sources: כולם
       - weekly sources: רק ביום ראשון
    4. עדכן ingestion_run.status לפי תוצאות
    5. הרץ AggregatorEngine
    6. הרץ QAEngine
    7. בדוק publish threshold
    8. אם threshold עבר → הרץ PublishEngine
    9. אם run נכשל לחלוטין → שלח email alert
    """
    
    run = create_ingestion_run(run_type=run_type)
    sources = load_active_sources()
    
    results = []
    for source in sources:
        try:
            result = process_source(source, run)
            results.append(result)
        except Exception as e:
            log_error(run, source, e)
            results.append(SourceResult(source_id=source.id, status='failed'))
    
    update_run_stats(run, results)
    
    if run.status == 'failed':
        send_failure_alert(run)
        return run
    
    aggregator_result = AggregatorEngine(db).run_daily(run)
    
    if is_sunday():
        AggregatorEngine(db).run_weekly()
    
    QAEngine(db).run(run)
    
    if meets_publish_threshold(run):
        PublishEngine(db).run(run)
    else:
        log_warning(run, f'publish skipped: only {run.community_sources_succeeded} community sources succeeded')
    
    return run


def meets_publish_threshold(run: IngestionRun) -> bool:
    """
    Threshold: לפחות 2 מקורות community הצליחו.
    benchmark אינו חובה.
    """
    return run.community_sources_succeeded >= 2
```

---

## 3. CollectorEngine — איסוף Raw

```python
# collectors/engine.py

class CollectorEngine:
    """
    אחראי על:
    - fetch ל-URL של מקור
    - שמירת raw file על filesystem
    - יצירת raw_asset record ב-DB
    """
    
    def collect(
        self,
        source: Source,
        fetch_profile: SourceFetchProfile,
        run: IngestionRun
    ) -> SourceFetchRun:
        
        fetch_run = create_source_fetch_run(source, run)
        
        try:
            raw_content, http_status = self._fetch(fetch_profile)
            
            # שמירה על filesystem
            file_path = self._save_raw_file(source, raw_content, fetch_profile.fetch_mode)
            checksum = sha256(raw_content)
            
            # בדיקת deduplication: אם checksum זהה לriצה הקודמת — לא צריך לעבד שוב
            if self._is_duplicate(source, checksum):
                update_fetch_run(fetch_run, status='skipped', note='duplicate content')
                return fetch_run
            
            raw_asset = create_raw_asset(
                source=source,
                fetch_run=fetch_run,
                storage_path=file_path,
                file_type=fetch_profile.fetch_mode,
                checksum=checksum,
                bytes_size=len(raw_content)
            )
            
            update_fetch_run(fetch_run, status='success', raw_asset_id=raw_asset.id)
            
        except TimeoutError:
            update_fetch_run(fetch_run, status='timeout', error='fetch timeout')
        except Exception as e:
            update_fetch_run(fetch_run, status='failed', error=str(e))
            if fetch_run.retry_count < fetch_profile.retry_policy_json['max_retries']:
                schedule_retry(fetch_run, fetch_profile)
        
        return fetch_run
    
    def _fetch(self, profile: SourceFetchProfile) -> tuple[bytes, int]:
        """
        HTTP GET / POST עם:
        - headers מ-profile.request_headers_json
        - timeout מ-profile.timeout_seconds
        - User-Agent: 'SmallFarmsMarket/1.0'
        """
        import httpx
        response = httpx.get(
            profile.entry_url,
            headers=profile.request_headers_json or {},
            timeout=profile.timeout_seconds,
            follow_redirects=True
        )
        return response.content, response.status_code
    
    def _save_raw_file(self, source: Source, content: bytes, file_type: str) -> str:
        """
        שמירה לנתיב: RAW_FILES_ROOT/{year}/{month}/{day}/{source_code}_{timestamp}.{ext}
        """
        import datetime, os
        now = datetime.datetime.now()
        folder = f"{RAW_FILES_ROOT}/{now.year}/{now.month:02d}/{now.day:02d}"
        os.makedirs(folder, exist_ok=True)
        ext = {'html_page': 'html', 'json_endpoint': 'json', 'pdf_download': 'pdf'}.get(file_type, 'txt')
        filename = f"{source.code}_{now.strftime('%H%M%S')}.{ext}"
        full_path = f"{folder}/{filename}"
        with open(full_path, 'wb') as f:
            f.write(content)
        return full_path
    
    def _is_duplicate(self, source: Source, checksum: str) -> bool:
        """בדיקה אם כבר יש raw_asset עם אותו checksum ממקור זה (24 שעות אחרונות)"""
        yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
        return db.query(RawAsset).filter(
            RawAsset.source_id == source.id,
            RawAsset.checksum_sha256 == checksum,
            RawAsset.captured_at >= yesterday
        ).first() is not None
```

---

## 4. ParserEngine — חילוץ Items מ-Raw

```python
# parsers/engine.py

class ParserEngine:
    """
    Parser per normalizer_type.
    כל parser מחלץ list[RawExtractedItem] מתוך raw content.
    """
    
    PARSERS: dict[str, type] = {
        'easyfarm_catalog':    EasyFarmCatalogParser,
        'simple_product_grid': SimpleProductGridParser,
        'basket_only':         BasketOnlyParser,
        'retail_benchmark':    RetailBenchmarkParser,
        'official_wholesale':  OfficialWholesaleParser,
    }
    
    def parse(self, raw_asset: RawAsset, normalizer_profile: NormalizerProfile) -> list[RawExtractedItem]:
        parser_class = self.PARSERS.get(normalizer_profile.normalizer_type)
        if not parser_class:
            raise ValueError(f"Unknown normalizer_type: {normalizer_profile.normalizer_type}")
        
        raw_content = read_raw_file(raw_asset.storage_path)
        parser = parser_class(normalizer_profile.config_json or {})
        
        try:
            items = parser.extract(raw_content)
        except Exception as e:
            log_error(f"Parser failed for {raw_asset.source_id}: {e}")
            return []
        
        # שמירה ל-DB
        saved_items = []
        for item in items:
            item.source_fetch_run_id = raw_asset.source_fetch_run_id
            item.raw_asset_id = raw_asset.id
            item.normalizer_profile_id = normalizer_profile.id
            db.add(item)
            saved_items.append(item)
        
        db.commit()
        return saved_items


class EasyFarmCatalogParser:
    """
    Parser לאתרי easyFarm (SRC002-SRC006).
    
    מבנה HTML צפוי:
    - טבלת מוצרים עם selector: .price-list-item
    - שדות: .product-name, .product-price, .product-unit
    """
    
    def extract(self, html_content: bytes) -> list[RawExtractedItem]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        items = []
        for row in soup.select('.price-list-item, tr[data-product]'):
            name = self._extract_text(row, '.product-name, td.name')
            price = self._extract_text(row, '.product-price, td.price')
            unit = self._extract_text(row, '.product-unit, td.unit')
            
            if name and price:
                items.append(RawExtractedItem(
                    raw_product_name=name,
                    raw_price_text=price,
                    raw_unit_text=unit,
                    raw_payload_json={'html_row': str(row)[:500]}
                ))
        
        return items


class BasketOnlyParser:
    """
    Parser לאתרי סלים ו-CSA.
    מחלץ מוצרי סל בלבד, בלי פירוק לפריטים.
    """
    
    def extract(self, html_content: bytes) -> list[RawExtractedItem]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        items = []
        for basket in soup.select('.basket-option, .box-size, .subscription-plan'):
            name = self._extract_text(basket, '.basket-name, h3, .plan-name')
            price = self._extract_text(basket, '.basket-price, .price')
            description = self._extract_text(basket, '.basket-description, p')
            
            if name and price:
                items.append(RawExtractedItem(
                    raw_product_name=name,
                    raw_price_text=price,
                    raw_quantity_text=description,
                    raw_payload_json={'description': description}
                ))
        
        return items
```

---

## 5. AggregatorEngine — חישוב אגרגטים

```python
# aggregator/engine.py

class AggregatorEngine:
    
    MIN_SAMPLE_SIZE = 2          # מינימום תצפיות
    MIN_DISTINCT_SOURCES = 2     # מינימום מקורות שונים
    
    def run_daily(self, ingestion_run: IngestionRun) -> AggregatorResult:
        """
        מחשב daily_aggregates לתאריך היום.
        רץ על observations מהריצה הנוכחית + קודמות אם יש חסרים.
        """
        today = date.today()
        products = db.query(Product).filter_by(is_active=True).all()
        
        for product in products:
            for market_scope in ['community', 'benchmark']:
                self._compute_aggregate(today, product, market_scope, None)
                
                # per sales_channel (אם יש מספיק נתונים)
                channels = self._get_active_channels(product, market_scope, today)
                for channel in channels:
                    self._compute_aggregate(today, product, market_scope, channel)
        
        return AggregatorResult(date=today, products_processed=len(products))
    
    def _compute_aggregate(
        self,
        agg_date: date,
        product: Product,
        market_scope: str,
        sales_channel: str | None
    ):
        """
        אלגוריתם אגרגציה:
        
        1. שלוף observations:
           - product_id = product.id
           - market_scope = market_scope
           - flag_status IN ('ok', 'review') -- review נכנס אבל עם confidence נמוך
           - is_benchmark = (market_scope == 'benchmark')
           - is_basket_product = product.is_basket_product
           - normalized_unit NOT NULL (אלא אם basket)
           - observed_at >= agg_date 00:00, <= agg_date 23:59
           - sales_channel = channel (אם לא NULL)
        
        2. בדוק threshold:
           - len(observations) >= MIN_SAMPLE_SIZE
           - len(set(obs.source_id)) >= MIN_DISTINCT_SOURCES
        
        3. חשב סטטיסטיקות:
           prices = [obs.normalized_price_value for obs in observations if obs.flag_status == 'ok']
           weights = [obs.confidence_score for obs in observations if obs.flag_status == 'ok']
           
           unweighted_avg = mean(prices)
           weighted_avg = sum(p*w for p,w in zip(prices,weights)) / sum(weights)
           median = statistics.median(prices)
           stddev = statistics.stdev(prices) if len(prices) > 1 else 0
           
        4. שמור daily_aggregate (upsert)
        """
        
        observations = self._load_observations(agg_date, product, market_scope, sales_channel)
        
        if not observations:
            return
        
        prices = [o.normalized_price_value for o in observations
                  if o.normalized_price_value is not None and o.flag_status == 'ok']
        weights = [o.confidence_score for o in observations
                   if o.normalized_price_value is not None and o.flag_status == 'ok']
        
        if len(prices) < self.MIN_SAMPLE_SIZE:
            meets_threshold = False
        else:
            distinct_sources = len(set(o.source_id for o in observations))
            meets_threshold = (len(prices) >= self.MIN_SAMPLE_SIZE and
                               distinct_sources >= self.MIN_DISTINCT_SOURCES)
        
        import statistics
        
        agg = DailyAggregate(
            aggregate_date=agg_date,
            product_id=product.id,
            market_scope=market_scope,
            sales_channel=sales_channel,
            is_basket_aggregate=product.is_basket_product,
            sample_size=len(prices),
            distinct_sources=len(set(o.source_id for o in observations)),
            min_price=min(prices) if prices else None,
            max_price=max(prices) if prices else None,
            unweighted_avg_price=statistics.mean(prices) if prices else None,
            weighted_avg_price=(
                sum(p*w for p,w in zip(prices,weights)) / sum(weights)
                if prices and sum(weights) > 0 else None
            ),
            median_price=statistics.median(prices) if prices else None,
            stddev_price=(statistics.stdev(prices) if len(prices) > 1 else 0),
            meets_publish_threshold=meets_threshold,
            last_observed_at=max(o.observed_at for o in observations)
        )
        
        # upsert
        db.merge(agg)
        db.commit()
    
    def run_weekly(self):
        """
        רץ כל יום ראשון.
        מחשב weekly_snapshot מתוך daily_aggregates של 7 הימים האחרונים.
        """
        week_end = date.today()
        week_start = week_end - timedelta(days=6)
        
        products = db.query(Product).filter_by(is_active=True).all()
        
        for product in products:
            for market_scope in ['community', 'benchmark']:
                daily_aggs = db.query(DailyAggregate).filter(
                    DailyAggregate.product_id == product.id,
                    DailyAggregate.market_scope == market_scope,
                    DailyAggregate.aggregate_date >= week_start,
                    DailyAggregate.aggregate_date <= week_end,
                    DailyAggregate.meets_publish_threshold == True
                ).all()
                
                if not daily_aggs:
                    continue
                
                all_prices = []
                for agg in daily_aggs:
                    if agg.weighted_avg_price:
                        all_prices.append(agg.weighted_avg_price)
                
                days_with_data = len(daily_aggs)
                completeness = round(days_with_data / 7 * 100, 2)
                
                snapshot = WeeklySnapshot(
                    week_start_date=week_start,
                    week_end_date=week_end,
                    product_id=product.id,
                    market_scope=market_scope,
                    sample_size=sum(a.sample_size for a in daily_aggs),
                    distinct_sources=max(a.distinct_sources for a in daily_aggs),
                    data_completeness_pct=completeness,
                    week_avg_price=statistics.mean(all_prices) if all_prices else None,
                    week_weighted_avg_price=statistics.mean(all_prices) if all_prices else None,
                    week_median_price=statistics.median(all_prices) if all_prices else None,
                    week_stddev_price=statistics.stdev(all_prices) if len(all_prices) > 1 else 0,
                    week_min_price=min(all_prices) if all_prices else None,
                    week_max_price=max(all_prices) if all_prices else None,
                )
                db.merge(snapshot)
        
        db.commit()
```

---

## 6. QAEngine — זיהוי חריגות

```python
# qa/engine.py

class QAEngine:
    
    PRICE_OUTLIER_FACTOR = 3.0   # מחיר > 3x median → outlier
    MIN_PRICE_ILS = 0.50         # מחיר מינימלי סביר
    MAX_PRICE_ILS = 500.0        # מחיר מקסימלי סביר לק"ג
    
    def run(self, ingestion_run: IngestionRun):
        """
        בודק:
        1. outlier prices
        2. duplicate observations (אותו מקור + מוצר + מחיר באותו יום)
        3. unrealistic prices
        4. sources שלא דיווחו (missing source alert)
        """
        
        today = date.today()
        
        # 1. outlier detection per product
        for product in db.query(Product).filter_by(is_active=True, is_basket_product=False):
            self._detect_price_outliers(product, today)
        
        # 2. duplicate detection
        self._detect_duplicates(ingestion_run)
        
        # 3. unrealistic prices
        self._detect_unrealistic_prices(ingestion_run)
        
        # 4. missing sources alert
        self._check_missing_sources(ingestion_run)
    
    def _detect_price_outliers(self, product: Product, today: date):
        """
        אלגוריתם:
        1. שלוף median מ-daily_aggregate של ה-7 ימים האחרונים
        2. שלוף כל observations של היום
        3. סמן כ-'review' כל observation שמחירו > 3x median או < 0.33x median
        """
        import statistics
        
        recent_aggs = db.query(DailyAggregate).filter(
            DailyAggregate.product_id == product.id,
            DailyAggregate.market_scope == 'community',
            DailyAggregate.aggregate_date >= today - timedelta(days=7),
            DailyAggregate.meets_publish_threshold == True
        ).all()
        
        if len(recent_aggs) < 3:
            return  # אין מספיק היסטוריה
        
        historical_median = statistics.median(
            [a.median_price for a in recent_aggs if a.median_price]
        )
        
        today_obs = db.query(NormalizedObservation).filter(
            NormalizedObservation.product_id == product.id,
            NormalizedObservation.observed_at >= datetime.combine(today, time.min),
            NormalizedObservation.flag_status == 'ok'
        ).all()
        
        for obs in today_obs:
            if obs.normalized_price_value is None:
                continue
            ratio = obs.normalized_price_value / historical_median
            if ratio > self.PRICE_OUTLIER_FACTOR or ratio < (1 / self.PRICE_OUTLIER_FACTOR):
                obs.flag_status = 'review'
                obs.flag_reason = f'outlier: {obs.normalized_price_value:.2f} vs median {historical_median:.2f}'
        
        db.commit()
    
    def _check_missing_sources(self, run: IngestionRun):
        """
        אם מקור active לא רץ היום → log warning.
        אם מקור priority>=7 לא רץ → flag לadmin.
        """
        active_sources = db.query(Source).filter_by(is_active=True, status='active').all()
        ran_source_ids = {sfr.source_id for sfr in db.query(SourceFetchRun.source_id)
                         .filter_by(ingestion_run_id=run.id)}
        
        for source in active_sources:
            if source.id not in ran_source_ids:
                level = 'WARNING' if source.priority >= 7 else 'INFO'
                log_entry(level, 'qa', f'Source {source.code} did not run today',
                          entity_type='source', entity_id=source.id,
                          ingestion_run_id=run.id)
```

---

## 7. PublishEngine — בניית artifacts והעלאה

```python
# publisher/engine.py

class PublishEngine:
    
    def run(self, ingestion_run: IngestionRun) -> PublishRun:
        publish_run = create_publish_run(ingestion_run)
        
        try:
            # 1. בנה artifacts
            artifacts = self._build_artifacts(publish_run)
            
            # 2. אמת checksums
            for artifact in artifacts:
                verify_file_checksum(artifact.local_path, artifact.checksum_sha256)
            
            # 3. העלה לshרת (FTPS) — artifacts לפני manifest
            for artifact in [a for a in artifacts if a.artifact_type != 'manifest_json']:
                self._upload_artifact(artifact)
            
            # 4. עדכן manifest אחרון — רק אם כל שאר הuploads הצליחו
            manifest_artifact = next(a for a in artifacts if a.artifact_type == 'manifest_json')
            self._upload_artifact(manifest_artifact)
            
            # 5. שמור manifest_last_good
            last_good_artifact = next(a for a in artifacts
                                       if a.artifact_type == 'manifest_last_good_json')
            self._upload_artifact(last_good_artifact)
            
            # 6. סמן publish_run כהצלחה
            update_publish_run(publish_run, status='published', published_at=datetime.now())
            
            # 7. עדכן is_last_good
            self._update_last_good_flag(publish_run)
            
        except Exception as e:
            update_publish_run(publish_run, status='upload_failed', error=str(e))
            send_publish_failure_alert(publish_run, e)
        
        return publish_run
    
    def _build_artifacts(self, publish_run: PublishRun) -> list[PublishArtifact]:
        """
        1. שלוף daily_aggregates עם meets_publish_threshold=True לתאריך היום
        2. שלוף weekly_snapshots אחרון
        3. בנה public_report_data dict
        4. כתוב JSON
        5. render HTML עם embedded JS
        6. בנה manifest
        7. בנה manifest_last_good (עותק של manifest הקודם הטוב)
        """
        
        today = date.today()
        version = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        # שלב נתונים
        community_data = self._build_community_section(today)
        benchmark_data = self._build_benchmark_section(today)
        history_data = self._build_history_section()
        
        report = {
            'schema_version': '1.0',
            'artifact_version': version,
            'generated_at': datetime.now(tz=timezone('Asia/Jerusalem')).isoformat(),
            'community': community_data,
            'benchmark': benchmark_data,
            'history': history_data,
        }
        
        # JSON
        json_path = f"{ARTIFACTS_ROOT}/market/public_report-{version}.json"
        write_json(json_path, report)
        
        # HTML
        html_path = f"{ARTIFACTS_ROOT}/market/public_report-{version}.html"
        render_html(html_path, report)
        
        # manifest
        manifest = self._build_manifest(version, json_path, html_path, today)
        manifest_path = f"{ARTIFACTS_ROOT}/market/manifest.json"
        write_json(manifest_path, manifest)
        
        # manifest_last_good: עותק של manifest הנוכחי לשם שמירה
        last_good_path = f"{ARTIFACTS_ROOT}/market/manifest_last_good.json"
        
        return [
            PublishArtifact(artifact_type='public_json', local_path=json_path,
                            remote_path=f"wp-content/uploads/market/public_report-{version}.json"),
            PublishArtifact(artifact_type='public_html', local_path=html_path,
                            remote_path=f"wp-content/uploads/market/public_report-{version}.html"),
            PublishArtifact(artifact_type='manifest_json', local_path=manifest_path,
                            remote_path="wp-content/uploads/market/manifest.json"),
            PublishArtifact(artifact_type='manifest_last_good_json', local_path=last_good_path,
                            remote_path="wp-content/uploads/market/manifest_last_good.json"),
        ]
    
    def _build_manifest(self, version: str, json_path: str, html_path: str, today: date) -> dict:
        """
        בונה manifest.json עם staleness_level מחושב.
        """
        last_good_run = db.query(PublishRun).filter_by(is_last_good=True).first()
        days_since_last_good = (
            (datetime.now() - last_good_run.published_at).days
            if last_good_run and last_good_run.published_at else 999
        )
        
        if days_since_last_good < 3:
            staleness_level = 'ok'
        elif days_since_last_good < 8:
            staleness_level = 'warning'
        else:
            staleness_level = 'stale'
        
        return {
            'schema_version': '1.0',
            'artifact_version': version,
            'published_at': datetime.now(tz=timezone('Asia/Jerusalem')).isoformat(),
            'json_path': f"market/public_report-{version}.json",
            'html_path': f"market/public_report-{version}.html",
            'staleness_level': staleness_level,
            'staleness_days': days_since_last_good,
            'community_products': len([]),  # מחושב בפועל
            'benchmark_products': len([]),
            'status': 'published'
        }
    
    def _upload_artifact(self, artifact: PublishArtifact):
        """
        FTPS upload.
        על כשל: raise exception → PublishEngine.run() תופס ומדווח.
        """
        import ftplib
        
        with ftplib.FTP_TLS(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASSWORD)
            ftp.prot_p()  # data channel encryption
            
            with open(artifact.local_path, 'rb') as f:
                ftp.storbinary(f'STOR {artifact.remote_path}', f)
            
            artifact.upload_status = 'uploaded'
            artifact.uploaded_at = datetime.now()


def _build_community_section(self, today: date) -> dict:
    """
    בונה את ה-community section ל-JSON הציבורי.
    כולל רק מוצרים שעוברים publish threshold.
    """
    aggs = db.query(DailyAggregate).filter(
        DailyAggregate.aggregate_date == today,
        DailyAggregate.market_scope == 'community',
        DailyAggregate.meets_publish_threshold == True
    ).join(Product).order_by(Product.display_order).all()
    
    products_out = []
    for agg in aggs:
        product = agg.product
        unit = db.query(MeasurementUnit).get(agg.normalized_unit_id)
        
        products_out.append({
            'code': product.code,
            'name': product.canonical_name_he,
            'category': product.category,
            'is_basket': product.is_basket_product,
            'price_unit': unit.code if unit else None,
            'avg_price': float(agg.weighted_avg_price) if agg.weighted_avg_price else None,
            'median_price': float(agg.median_price) if agg.median_price else None,
            'stddev_price': float(agg.stddev_price) if agg.stddev_price else None,
            'min_price': float(agg.min_price) if agg.min_price else None,
            'max_price': float(agg.max_price) if agg.max_price else None,
            'sample_size': agg.sample_size,
            'distinct_sources': agg.distinct_sources,
        })
    
    return {'date': today.isoformat(), 'products': products_out}
```

---

## 8. Alerting

```python
# utils/alerts.py

def send_failure_alert(run: IngestionRun):
    """
    שולח email אם run נכשל לחלוטין.
    מינימלי: Python smtplib ל-localhost או SMTP מוגדר.
    """
    subject = f"[SmallFarms] Ingestion Run #{run.id} FAILED"
    body = f"""
Run ID: {run.id}
Type: {run.run_type}
Started: {run.started_at}
Sources total: {run.sources_total}
Succeeded: {run.sources_succeeded}
Failed: {run.sources_failed}
Community succeeded: {run.community_sources_succeeded}

Action required: check admin UI → Runs → #{run.id}
"""
    send_email(ALERT_EMAIL, subject, body)


def send_publish_failure_alert(publish_run: PublishRun, error: Exception):
    subject = f"[SmallFarms] Publish Run #{publish_run.id} FAILED"
    body = f"Error: {error}\nPublish run: {publish_run.id}"
    send_email(ALERT_EMAIL, subject, body)


def send_staleness_warning(days: int):
    """
    נשלח אם לא היה publish מוצלח ב-2 ימים (אזהרה מוקדמת לפני שהציבור רואה warning).
    """
    if days >= 2:
        send_email(ALERT_EMAIL,
                   f"[SmallFarms] No publish for {days} days",
                   f"Last successful publish was {days} days ago. Check system.")
```

---

## 9. cron Setup

```bash
# /etc/cron.d/smallfarms או crontab -e

# הרצה יומית ב-06:00
0 6 * * * /path/to/venv/bin/python /path/to/smallfarms/scheduler/run_daily.py >> /data/smallfarms/logs/cron.log 2>&1

# בדיקת staleness פעמיים ביום
0 8,20 * * * /path/to/venv/bin/python /path/to/smallfarms/scheduler/check_staleness.py >> /data/smallfarms/logs/cron.log 2>&1
```

```python
# scheduler/run_daily.py
import sys
sys.path.insert(0, '/path/to/smallfarms')

from db.session import get_session
from scheduler.runner import run_daily_ingestion

if __name__ == '__main__':
    with get_session() as db:
        run = run_daily_ingestion()
        sys.exit(0 if run.status in ('completed', 'partial') else 1)
```

---

## 10. סיכום זרימת נתונים מלאה

```
06:00 cron trigger
  │
  ▼
IngestionRun #N created (status='running')
  │
  ├── SRC002 → fetch HTML → raw_asset → parse → 45 items → normalize → 42 observations
  ├── SRC003 → fetch HTML → raw_asset → parse → 3 basket items → normalize → 3 basket obs
  ├── SRC004 → fetch HTML → raw_asset → parse → 38 items → normalize → 35 observations
  ├── SRC005 → timeout → status='timeout', retry scheduled
  ├── SRC008 → fetch HTML → raw_asset → parse → 52 items → normalize → 48 observations
  ├── SRC009 → fetch HTML → raw_asset → parse → 61 items → normalize → 58 observations
  ├── SRC010 → fetch HTML → raw_asset → parse → 33 items → normalize → 30 observations
  ├── SRC011 → fetch HTML → raw_asset → parse → 28 items → normalize → 25 observations
  ├── SRC015 → fetch JSON → raw_asset → parse → 120 items → normalize → 118 obs (benchmark)
  └── SRC017 → fetch HTML → raw_asset → SKIPPED (legal_review_required=true)
  │
  ▼
community_sources_succeeded = 7 (>=2 ✓)
  │
  ▼
AggregatorEngine
  ├── daily_aggregates for 29 community products
  ├── daily_aggregates for 12 benchmark products
  └── (not Sunday, no weekly snapshot)
  │
  ▼
QAEngine
  ├── 2 price outliers detected → flag_status='review'
  └── SRC005 missing → log WARNING
  │
  ▼
publish threshold met ✓
  │
  ▼
PublishEngine
  ├── build public_report-20260329-060000.json (18 community + 8 benchmark products)
  ├── build public_report-20260329-060000.html
  ├── build manifest.json (staleness_level='ok')
  ├── upload JSON ✓
  ├── upload HTML ✓
  ├── upload manifest.json ✓
  └── upload manifest_last_good.json ✓
  │
  ▼
PublishRun #M (status='published', is_last_good=true)
IngestionRun #N (status='partial', 7/8 community succeeded)
```
