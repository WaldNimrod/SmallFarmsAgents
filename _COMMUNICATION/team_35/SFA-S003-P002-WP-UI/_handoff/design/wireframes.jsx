/* wireframes.jsx — LOD200 mobile-portrait wireframes (390×844) */

// ─── A. Home / Module landing ───────────────────────────────────────────────
function WfHome() {
  return (
    <div className="sfa-shell wf">
      <div className="sfa-h">
        <div className="box" style={{ width: 28, height: 28, borderRadius: 99 }}/>
        <div>
          <div className="sfa-h__title">[LOGO + SHELL NAME]</div>
          <div className="sfa-h__sub">sub-tagline</div>
        </div>
        <span className="sfa-h__spacer"/>
        <div className="box" style={{ width: 32, height: 32, borderRadius: 99 }}>⌕</div>
      </div>

      <div style={{ padding: '12px 16px 0' }}>
        <div className="lbl">module switcher · sticky</div>
        <div className="box" style={{ padding: 4, borderRadius: 99, display: 'flex', gap: 4 }}>
          <div className="box box--filled" style={{ flex: 1, textAlign: 'center', borderRadius: 99 }}>● מחירון</div>
          <div className="box" style={{ flex: 1, textAlign: 'center', borderRadius: 99, border: 'none' }}>○ ספר גידולים</div>
        </div>
      </div>

      <div className="sfa-body">
        <div className="stack">
          <div>
            <div className="lbl">section · hero / value</div>
            <div className="box" style={{ height: 96 }}>“למצוא מחיר · להבין גידול” · 1 משפט קצר</div>
            <span className="ann">// יחליף את החזון של nimrod.bio — קצר, כלי-first</span>
          </div>

          <div>
            <div className="lbl">section · live snapshot (mixed)</div>
            <div className="row">
              <div className="box" style={{ flex: 1, height: 72 }}>
                <div className="lbl">מחיר היום</div>
                ▦ עגבנייה ₪.₪₪
              </div>
              <div className="box" style={{ flex: 1, height: 72 }}>
                <div className="lbl">גידול בעונה</div>
                ▣ חסה — אביב
              </div>
            </div>
            <span className="ann">// 2-up snapshot — קישור ראשון בין המודולים על אותו מסך</span>
          </div>

          <div>
            <div className="lbl">section · entry CTAs</div>
            <div className="box" style={{ height: 56 }}>→ הצג מדד מחירים מלא · 30 מוצרים</div>
            <div className="box" style={{ height: 56, marginTop: 6 }}>→ עיין בספר גידולים · 66 גידולים</div>
          </div>

          <div>
            <div className="lbl">section · transparency strip</div>
            <div className="box" style={{ height: 40 }}>🔒 פרטיות · מצרפי בלבד · 7-day rolling</div>
          </div>
        </div>
      </div>

      <div className="sfa-foot">
        <span className="dot"/><span>עודכן לפני 2ש · 14 מקורות · SFA v0.1</span>
      </div>
    </div>
  );
}

// ─── B. Market — list ───────────────────────────────────────────────────────
function WfMarketList() {
  return (
    <div className="sfa-shell wf">
      <div className="sfa-h">
        <div className="box" style={{ width: 28, height: 28, borderRadius: 99 }}/>
        <div><div className="sfa-h__title">SFA</div><div className="sfa-h__sub">מדד מחירים</div></div>
        <span className="sfa-h__spacer"/>
        <div className="box" style={{ width: 32, height: 32, borderRadius: 99 }}>⌕</div>
      </div>
      <div style={{ padding: '10px 16px 0' }}>
        <div className="box" style={{ padding: 4, borderRadius: 99, display: 'flex', gap: 4 }}>
          <div className="box box--filled" style={{ flex: 1, textAlign: 'center', borderRadius: 99 }}>● מחירון</div>
          <div className="box" style={{ flex: 1, textAlign: 'center', borderRadius: 99, border: 'none' }}>○ ספר גידולים</div>
        </div>
      </div>

      <div className="sfa-body">
        <div className="lbl">filter chips · scroll-x · source-type</div>
        <div className="strip" style={{ marginBottom: 10 }}>
          <div className="f"/><div/><div/><div/>
        </div>
        <span className="ann">// [הכל · מגדלים · חנויות · רשתות] — מצב פעיל = הכל</span>

        <div className="h-line"/>
        <div className="lbl">framing line (above list)</div>
        <div className="box" style={{ marginBottom: 12 }}>מדד מחירים מבוסס נתונים מהשטח · 7 ימים אחרונים</div>

        <div className="lbl">product cards (repeat ×N)</div>
        {[0,1,2,3].map(i => (
          <div key={i} className="box" style={{ marginBottom: 8, padding: 10 }}>
            <div className="row" style={{ marginBottom: 6 }}>
              <div className="box" style={{ width: 28, height: 28, borderRadius: 6 }}>▦</div>
              <div style={{ flex: 1 }}>
                <div>שם מוצר · יחידה</div>
                <div className="lbl" style={{ marginTop: 2 }}>3 מקורות · 18 תצפיות</div>
              </div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>₪.₪₪</div>
            </div>
            <div className="strip"><div/><div className="f"/><div className="f"/><div/></div>
            <div className="lbl" style={{ marginTop: 4 }}>טווח · חציון · סטיית תקן</div>
          </div>
        ))}
        <span className="ann">// כל כרטיס: שם · יחידה · ממוצע (גדול) · חציון (משני) · range-bar · ספירות (מקורות + תצפיות)</span>
      </div>
      <div className="sfa-foot"><span className="dot"/><span>עודכן 14:32 · 14 מקורות</span></div>
    </div>
  );
}

// ─── C. Market — detail ─────────────────────────────────────────────────────
function WfMarketDetail() {
  return (
    <div className="sfa-shell wf">
      <div className="sfa-h">
        <div className="box" style={{ width: 28, height: 28 }}>←</div>
        <div><div className="sfa-h__title">חזרה למדד</div><div className="sfa-h__sub">market &gt; detail</div></div>
        <span className="sfa-h__spacer"/>
      </div>
      <div className="sfa-body">
        <div className="lbl">product head</div>
        <div className="box" style={{ height: 80, marginBottom: 12 }}>
          <div className="row"><div className="box" style={{ width: 40, height: 40, borderRadius: 8 }}>▦</div><div><div style={{ fontSize: 14, fontWeight: 700 }}>עגבנייה · קילו</div><div className="lbl">canonical_name_he · normalized_unit</div></div></div>
        </div>

        <div className="lbl">price headline · big number</div>
        <div className="box" style={{ height: 76, marginBottom: 10, padding: 12 }}>
          <div className="row" style={{ alignItems: 'baseline' }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>₪₪.₪₪</div>
            <div className="lbl" style={{ marginInlineStart: 8 }}>ממוצע</div>
            <div style={{ marginInlineStart: 'auto', fontSize: 14 }}>חציון ₪₪.₪₪</div>
          </div>
        </div>

        <div className="lbl">distribution · range bar</div>
        <div className="box" style={{ height: 60, marginBottom: 12 }}>
          <div className="strip" style={{ marginBottom: 6 }}><div/><div className="f"/><div className="f"/><div className="f"/><div/></div>
          <div className="row" style={{ justifyContent: 'space-between', fontSize: 11 }}>
            <span>min ₪₪.₪₪</span><span>max ₪₪.₪₪</span>
          </div>
        </div>

        <div className="lbl">stats grid · 2×2</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 12 }}>
          <div className="box" style={{ padding: 8 }}><div className="lbl">סטיית תקן</div>₪.₪₪</div>
          <div className="box" style={{ padding: 8 }}><div className="lbl">תצפיות</div>18</div>
          <div className="box" style={{ padding: 8 }}><div className="lbl">מקורות</div>●●●● 4</div>
          <div className="box" style={{ padding: 8 }}><div className="lbl">תאריך אחרון</div>23.05</div>
        </div>

        <div className="lbl">cross-link → crop book</div>
        <div className="box box--solid" style={{ padding: 10, marginBottom: 12, borderColor: '#6a8a3a' }}>
          ◐ פתח גידול בספר → תיאור, זנים, ציר זמן, ציוד
          <span className="ann">// אם pricebook_product_id מקושר לגידול → דו-כיווני</span>
        </div>

        <div className="lbl">source attribution</div>
        <div className="box" style={{ padding: 10 }}>
          <div>נתונים מ-4 מגדלים אנונימיים · 7-day rolling</div>
          <div className="lbl" style={{ marginTop: 4 }}>🔒 פרטיות: ללא חשיפת חווה בודדת</div>
        </div>
        <span className="ann">// dq-box המלא חוזר רק במסך index, לא בפרטים</span>
      </div>
      <div className="sfa-foot"><span className="dot"/><span>נכון ל-14:32 היום</span></div>
    </div>
  );
}

// ─── D. Crop book — grid ────────────────────────────────────────────────────
function WfBookGrid() {
  return (
    <div className="sfa-shell wf">
      <div className="sfa-h">
        <div className="box" style={{ width: 28, height: 28, borderRadius: 99 }}/>
        <div><div className="sfa-h__title">SFA</div><div className="sfa-h__sub">ספר גידולים</div></div>
        <span className="sfa-h__spacer"/>
        <div className="box" style={{ width: 32, height: 32, borderRadius: 99 }}>⌕</div>
      </div>
      <div style={{ padding: '10px 16px 0' }}>
        <div className="box" style={{ padding: 4, borderRadius: 99, display: 'flex', gap: 4 }}>
          <div className="box" style={{ flex: 1, textAlign: 'center', borderRadius: 99, border: 'none' }}>○ מחירון</div>
          <div className="box box--filled" style={{ flex: 1, textAlign: 'center', borderRadius: 99 }}>● ספר גידולים</div>
        </div>
      </div>
      <div className="sfa-body">
        <div className="lbl">search · full width</div>
        <div className="box" style={{ height: 40, marginBottom: 10 }}>⌕ חיפוש גידול…</div>

        <div className="lbl">category chips · scroll-x · 9 חברים</div>
        <div className="strip" style={{ marginBottom: 10 }}>
          <div className="f"/><div/><div/><div/><div/><div/>
        </div>
        <span className="ann">// הכל · ירקות · עשבי תיבול · עלים בייבי · קטניות · פירות · עצי פרי · דגנים · גידולי כיסוי</span>

        <div className="lbl">advanced filters · collapsible</div>
        <div className="box" style={{ height: 44, marginBottom: 12 }}>▾ עונה · ימים לבגרות (slider)</div>

        <div className="lbl">grid · 2-column</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {[0,1,2,3,4,5].map(i => (
            <div key={i} className="box" style={{ minHeight: 96, padding: 8 }}>
              <div className="box" style={{ width: 32, height: 32, borderRadius: 6 }}>◐</div>
              <div style={{ marginTop: 6 }}>שם גידול</div>
              <div className="lbl" style={{ marginTop: 2 }}>name_en</div>
              <div style={{ display: 'flex', gap: 4, marginTop: 6 }}>
                <div className="box" style={{ padding: '1px 6px', fontSize: 9 }}>קטגוריה</div>
                <div className="box" style={{ padding: '1px 6px', fontSize: 9 }}>DTM</div>
              </div>
            </div>
          ))}
        </div>
        <span className="ann">// כרטיס מינימלי: אייקון · עברית · אנגלית · 2 chips (קטגוריה + DTM)</span>
      </div>
      <div className="sfa-foot"><span className="dot"/><span>66 גידולים · DB snapshot</span></div>
    </div>
  );
}

// ─── E. Crop book — detail ──────────────────────────────────────────────────
function WfBookDetail() {
  return (
    <div className="sfa-shell wf">
      <div className="sfa-h">
        <div className="box" style={{ width: 28, height: 28 }}>←</div>
        <div><div className="sfa-h__title">חזרה לספר</div><div className="sfa-h__sub">book &gt; detail</div></div>
        <span className="sfa-h__spacer"/>
      </div>
      <div className="sfa-body">
        <div className="box" style={{ height: 72, marginBottom: 12, padding: 10 }}>
          <div className="row"><div className="box" style={{ width: 44, height: 44, borderRadius: 8 }}>◐</div><div><div style={{ fontSize: 16, fontWeight: 700 }}>שם גידול</div><div className="lbl">scientific · family</div></div></div>
        </div>

        <div className="lbl">tab strip · scroll-x · 8 חברים</div>
        <div style={{ display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 12, paddingBottom: 4, borderBottom: '1px solid #cdc8b3' }}>
          {['זנים','תיאור','כלכלה','טיפולים','ציוד','מקורות','ציר זמן','שדה'].map((t,i) => (
            <div key={i} className="box" style={{ padding: '4px 8px', fontSize: 11, background: i === 0 ? '#ddd8c4' : '#fdfdf8' }}>{t}</div>
          ))}
        </div>
        <span className="ann">// active tab = זנים · tab "ציוד" יכול להסתתר אם אין נתוני seeder</span>

        <div className="lbl">tab body · 1st = varieties</div>
        <div className="box" style={{ padding: 10, marginBottom: 8 }}>
          <div className="row" style={{ alignItems: 'baseline' }}>
            <div style={{ fontWeight: 700 }}>★ זן ברירת מחדל</div>
            <div className="box" style={{ padding: '1px 6px', fontSize: 9, marginInlineStart: 6 }}>מורכב</div>
          </div>
          <div style={{ marginTop: 6, fontSize: 11 }}>· עונה · DTM · תשואה · מחיר מתועד</div>
        </div>
        <div className="box" style={{ padding: 10, marginBottom: 12 }}>
          <div style={{ fontWeight: 600 }}>זן נוסף</div>
          <div style={{ marginTop: 6, fontSize: 11 }}>· …</div>
        </div>

        <div className="lbl">cross-link → market</div>
        <div className="box box--solid" style={{ padding: 10, marginBottom: 10, borderColor: '#c46a3e' }}>
          ◐ מחיר שוק נוכחי · עגבנייה ₪.₪₪/ק"ג
          <span className="ann">// אם pricebook_product_id קיים → קישור · אם לא → "לא מקושר למחירון"</span>
        </div>

        <div className="lbl">deeper data — accordion-style scroll</div>
        <div className="box" style={{ height: 32, marginBottom: 4 }}>▾ ציר זמן · timeline</div>
        <div className="box" style={{ height: 32, marginBottom: 4 }}>▾ ציוד · seeder</div>
        <div className="box" style={{ height: 32, marginBottom: 4 }}>▾ מקורות · source values</div>
        <span className="ann">// במובייל — חלק מהלשוניות מתגלגלות לאקורדיון מתחת ללשוניות הראשיות</span>
      </div>
      <div className="sfa-foot"><span className="dot"/><span>נתונים: Tend CSV + JMF XLSX</span></div>
    </div>
  );
}

// ─── F. Cross-link patterns (split artboard) ────────────────────────────────
function WfCrossLink() {
  return (
    <div className="sfa-shell wf" style={{ height: 844 }}>
      <div className="sfa-h">
        <div><div className="sfa-h__title">CROSS-LINK PATTERNS</div><div className="sfa-h__sub">market ↔ book</div></div>
      </div>
      <div className="sfa-body" style={{ padding: '12px 14px 60px' }}>
        <div className="lbl">pattern 01 · book → market (in crop detail)</div>
        <div className="box box--solid" style={{ padding: 10, marginBottom: 12 }}>
          <div className="row">
            <div className="box" style={{ width: 24, height: 24, borderRadius: 99 }}>↗</div>
            <div style={{ flex: 1 }}>
              <div>מחיר שוק נוכחי</div>
              <div className="lbl" style={{ marginTop: 2 }}>עגבנייה · ₪₪.₪₪/ק"ג · עודכן היום</div>
            </div>
            <div className="lbl">פתח</div>
          </div>
        </div>
        <span className="ann">// מצב: pricebook_product_id IS NOT NULL · payload = canonical_name_he + avg + freshness</span>

        <div className="h-line"/>

        <div className="lbl">pattern 02 · market → book (in product detail)</div>
        <div className="box box--solid" style={{ padding: 10, marginBottom: 12 }}>
          <div className="row">
            <div className="box" style={{ width: 24, height: 24, borderRadius: 99 }}>↗</div>
            <div style={{ flex: 1 }}>
              <div>פרטי הגידול בספר</div>
              <div className="lbl" style={{ marginTop: 2 }}>זנים · עונת שתילה · DTM · ציר זמן</div>
            </div>
            <div className="lbl">פתח</div>
          </div>
        </div>
        <span className="ann">// מצב: מוצר עם crops.id משויך · אם אין crop matching → להעלים את הקישור (no broken links)</span>

        <div className="h-line"/>

        <div className="lbl">pattern 03 · home cross-snapshot</div>
        <div className="row" style={{ gap: 8, marginBottom: 12 }}>
          <div className="box" style={{ flex: 1, padding: 8 }}>
            <div className="lbl">מהמחירון</div>
            <div style={{ fontWeight: 700 }}>עגבנייה ₪.₪₪</div>
            <div className="lbl" style={{ marginTop: 4 }}>↗ פתח בספר</div>
          </div>
          <div className="box" style={{ flex: 1, padding: 8 }}>
            <div className="lbl">מהספר</div>
            <div style={{ fontWeight: 700 }}>חסה · אביב</div>
            <div className="lbl" style={{ marginTop: 4 }}>↗ ראה מחיר</div>
          </div>
        </div>
        <span className="ann">// כל כרטיס בdashboard הראשי כולל קישור צולב — לעודד מעבר בין המודולים</span>

        <div className="h-line"/>

        <div className="lbl">pattern 04 · inline reference</div>
        <div className="box" style={{ padding: 10 }}>
          טקסט גוף עם <span style={{ borderBottom: '1.5px dotted #6a8a3a' }}>הפניה לגידול</span> או <span style={{ borderBottom: '1.5px dotted #c46a3e' }}>הפניה למוצר</span> — entity tags עם tooltip
        </div>
        <span className="ann">// ניצול מנגנון .etag הקיים בקוד (entity_registry) → tooltip + click → אותו מודול אחר</span>
      </div>
    </div>
  );
}

// ─── G. Empty / loading / error / freshness states ──────────────────────────
function WfStates() {
  return (
    <div className="sfa-shell wf" style={{ height: 844 }}>
      <div className="sfa-h">
        <div><div className="sfa-h__title">STATES</div><div className="sfa-h__sub">empty · loading · stale · error</div></div>
      </div>
      <div className="sfa-body" style={{ padding: '12px 14px 60px' }}>
        <div className="lbl">freshness · 4 levels in footer</div>
        <div className="stack">
          <div className="box" style={{ padding: '6px 10px' }}>● עודכן לפני 14 דקות · 14 מקורות → <em>fresh</em></div>
          <div className="box" style={{ padding: '6px 10px' }}>● עודכן לפני 2 שעות · 14 מקורות → <em>fresh</em></div>
          <div className="box" style={{ padding: '6px 10px' }}>◐ עודכן לפני יום · 11 מקורות → <em>aging</em> (כתום עדין)</div>
          <div className="box" style={{ padding: '6px 10px' }}>◑ עודכן לפני 4 ימים · 7 מקורות → <em>stale</em> (כתום מלא + banner)</div>
        </div>
        <span className="ann">// סף stale: 3 ימים — תואם ל-stale_banner הקיים</span>

        <div className="h-line"/>

        <div className="lbl">stale banner · above list/grid</div>
        <div className="box" style={{ padding: 10, background: '#fde9d4', borderColor: '#c47b2e' }}>
          ⚠️ הנתונים עשויים שלא להיות עדכניים — מעל 3 ימים מאז התצפית האחרונה
        </div>

        <div className="h-line"/>

        <div className="lbl">empty · no results in filter</div>
        <div className="box" style={{ padding: 18, textAlign: 'center' }}>
          <div style={{ fontSize: 24 }}>◌</div>
          <div style={{ marginTop: 6 }}>לא נמצאו גידולים</div>
          <div className="lbl" style={{ marginTop: 4 }}>נסה לאפס פילטר עונה / קטגוריה</div>
          <div className="box" style={{ marginTop: 10, padding: '6px 10px', display: 'inline-block' }}>↺ אפס פילטרים</div>
        </div>

        <div className="h-line"/>

        <div className="lbl">loading · skeleton</div>
        <div className="stack">
          <div className="box" style={{ height: 56, background: 'linear-gradient(90deg, #ddd8c4 0%, #ebe7d5 50%, #ddd8c4 100%)', border: 'none' }}/>
          <div className="box" style={{ height: 56, background: 'linear-gradient(90deg, #ddd8c4 0%, #ebe7d5 50%, #ddd8c4 100%)', border: 'none' }}/>
        </div>

        <div className="h-line"/>

        <div className="lbl">error · fetch failed</div>
        <div className="box" style={{ padding: 14, textAlign: 'center', borderColor: '#d23a2e', color: '#d23a2e' }}>
          ✕ שגיאה בטעינת הנתונים
          <div className="lbl" style={{ color: 'inherit', marginTop: 4 }}>נסה שוב · refresh</div>
        </div>
        <span className="ann">// מקביל ל-sfa-crop-book-error ולמצב MoU 404 ב-shortcode PHP</span>
      </div>
    </div>
  );
}

// ─── H. Source attribution UI ───────────────────────────────────────────────
function WfSources() {
  return (
    <div className="sfa-shell wf" style={{ height: 844 }}>
      <div className="sfa-h">
        <div><div className="sfa-h__title">SOURCE ATTRIBUTION</div><div className="sfa-h__sub">privacy + transparency</div></div>
      </div>
      <div className="sfa-body" style={{ padding: '12px 14px 60px' }}>
        <div className="lbl">badge level · inline (per card)</div>
        <div className="row" style={{ gap: 12, marginBottom: 12 }}>
          <div className="box" style={{ padding: '4px 8px' }}>●●● 3 מקורות</div>
          <div className="box" style={{ padding: '4px 8px' }}>18 תצפיות</div>
        </div>
        <span className="ann">// פעמוני נקודות = N distinct_sources · לא חושף שמות חוות</span>

        <div className="h-line"/>

        <div className="lbl">privacy block · in dq-box</div>
        <div className="box" style={{ padding: 10 }}>
          🔒 פרטיות:
          <ul style={{ margin: '6px 0 0 16px', padding: 0, fontSize: 11 }}>
            <li>נתונים מצרפיים בלבד</li>
            <li>ללא חשיפת מחירים ברמת חווה</li>
            <li>לא ניתן לזהות מגדל ספציפי</li>
          </ul>
        </div>

        <div className="h-line"/>

        <div className="lbl">data quality block · collapsed by default in mobile</div>
        <div className="box" style={{ padding: 10 }}>
          <div style={{ fontWeight: 700 }}>▾ שקיפות — מצב צינור הנירמול</div>
          <div className="lbl" style={{ marginTop: 6 }}>מנורמל: 412 · לא ניתן לזיהוי: 23 · ממתין: 4 · אחוז פתרון: 94%</div>
        </div>
        <span className="ann">// המספרים תואמים את data_quality.raw_extracted_items ב-public_report_body</span>

        <div className="h-line"/>

        <div className="lbl">crop book attribution · per-row in sources tab</div>
        <div className="box" style={{ padding: 10 }}>
          <div className="row" style={{ fontSize: 11, gap: 4 }}>
            <div className="box" style={{ flex: 1.5, padding: 4 }}>שדה</div>
            <div className="box" style={{ flex: 1, padding: 4 }}>מקור</div>
            <div className="box" style={{ flex: 1, padding: 4 }}>ערך</div>
            <div className="box" style={{ flex: 0.6, padding: 4 }}>יח׳</div>
          </div>
          <div className="row" style={{ fontSize: 11, gap: 4, marginTop: 4 }}>
            <div className="box" style={{ flex: 1.5, padding: 4 }}>DTM</div>
            <div className="box" style={{ flex: 1, padding: 4 }}>Tend CSV</div>
            <div className="box" style={{ flex: 1, padding: 4 }}>65</div>
            <div className="box" style={{ flex: 0.6, padding: 4 }}>ימים</div>
          </div>
        </div>
        <span className="ann">// crop_variety_source_values · מקור הוא חופשי (Tend / JMF / nimrod_override)</span>

        <div className="h-line"/>

        <div className="lbl">footer attribution · always-on</div>
        <div className="box" style={{ padding: 8 }}>
          ● עודכן 14:32 · 14 מקורות · SFA v0.1 · build {`{hash}`}
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { WfHome, WfMarketList, WfMarketDetail, WfBookGrid, WfBookDetail, WfCrossLink, WfStates, WfSources });
