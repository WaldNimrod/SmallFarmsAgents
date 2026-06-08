<?php
/**
 * assumptions.php — Route /assumptions — WP-CB-UI-REDESIGN (WI-6)
 *
 * The standalone "הנחות היסוד שלי" editor from the team_35 mockup: the base
 * data (bed width, germination %, …) that feeds every calculator and the
 * computed numbers in the book — in searchable, collapsible groups that scale
 * to many parameters. Each row shows the community default + where it is used.
 * Local overrides persist client-side (localStorage 'sfa.assumptions'); the
 * page never mutates the locked calc engine.
 *
 * Controller contract (AssumptionsController::page): $groups[name] => {icon,
 * rows[]: {key,label,explainer,unit,used[],value,post_url}}.
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$page_title = 'הנחות היסוד שלי';
$page_sub   = 'נתוני הבסיס שלי';
$active     = 'calc';

$groups = is_array($groups ?? null) ? $groups : [];
$total  = 0;
foreach ($groups as $g) { $total += count($g['rows'] ?? []); }

ob_start();
?>
<div class="assum-page" id="assum-page">

  <div class="lead">
    <h1>הנחות היסוד שלי</h1>
    <p>ברירות המחדל שמזינות את כל המחשבונים ואת המספרים המחושבים בספר.</p>
  </div>

  <div class="why">
    <span class="ic" aria-hidden="true"><svg class="gi"><use href="#i-bulb"/></svg></span>
    <div>שנו ערך <b>פעם אחת</b> — וכל החישובים בכל הגידולים מתעדכנים. למשל: שינוי <b>רוחב הערוגה</b> מ-80 ל-100 ס״מ משפיע על צפיפות השתילה, כמות הזרעים והיבול לערוגה בכל הספר. כל ערך מציג היכן הוא בשימוש ומה ברירת המחדל הקהילתית.</div>
  </div>

  <div class="atoolbar">
    <div class="fsearch">
      <span aria-hidden="true">⌕</span>
      <input type="search" id="assum-search" placeholder="חפשו הנחה… (רוחב ערוגה, נביטה, מחיר…)" aria-label="חיפוש הנחה">
    </div>
    <span class="cnt"><b class="num"><?= (int)$total ?></b> הנחות פעילות · <span id="assum-changed-n" class="num">0</span> שונו מברירת המחדל</span>
    <button type="button" class="btn btn--ghost" id="assum-reset-all" style="padding:8px 16px">↺ אפס הכל</button>
  </div>

  <?php $first = true; foreach ($groups as $gname => $g): ?>
  <details class="agroup"<?= $first ? ' open' : '' ?>>
    <summary>
      <span class="gic"><svg class="gi" aria-hidden="true"><use href="#<?= $h((string)($g['icon'] ?? 'i-gear')) ?>"/></svg></span>
      <?= $h((string)$gname) ?>
      <span class="gc"><span class="num"><?= count($g['rows'] ?? []) ?></span> הנחות</span>
      <span class="chev">▾</span>
    </summary>
    <div class="agroup__body">
      <?php foreach (($g['rows'] ?? []) as $r): ?>
      <div class="arow" data-assum-row data-label="<?= $h((string)$r['label']) ?> <?= $h(implode(' ', (array)$r['used'])) ?>">
        <div class="arow__main">
          <b><?= $h((string)$r['label']) ?></b>
          <?php if (!empty($r['explainer'])): ?><p><?= $h((string)$r['explainer']) ?></p><?php endif; ?>
          <div class="usedin">
            <?php foreach ((array)$r['used'] as $u): ?><span class="u"><?= $h((string)$u) ?></span><?php endforeach; ?>
          </div>
        </div>
        <div class="val">
          <input type="text" inputmode="decimal" class="num"
                 data-assum-input="<?= $h((string)$r['key']) ?>"
                 data-default="<?= $h((string)$r['value']) ?>"
                 value="<?= $h((string)$r['value']) ?>"
                 aria-label="<?= $h((string)$r['label']) ?>">
          <?php if (!empty($r['unit'])): ?><span class="un"><?= $h((string)$r['unit']) ?></span><?php endif; ?>
        </div>
        <div class="def">
          <span class="def__state">ברירת מחדל: <span class="num"><?= $h((string)$r['value']) ?></span></span>
          <a href="#" data-assum-reset="<?= $h((string)$r['key']) ?>">↺ אפס</a>
          <?php if (!empty($r['post_url'])): ?><a href="<?= $h((string)$r['post_url']) ?>" target="_blank" rel="noopener">הסבר ←</a><?php endif; ?>
        </div>
      </div>
      <?php endforeach; ?>
    </div>
  </details>
  <?php $first = false; endforeach; ?>

  <div class="savebar">
    <span class="muted" style="font-size:13px">נשמר במכשיר זה · התחברו לחשבון לסנכרון בין מכשירים</span>
    <div style="display:flex;gap:10px">
      <a class="btn btn--ghost" href="/calc/">חזרה למחשבון</a>
      <button type="button" class="btn btn--leaf" id="assum-save">שמירה</button>
    </div>
  </div>

</div>
<script>
(function(){
  var KEY='sfa.assumptions';
  var page=document.getElementById('assum-page'); if(!page) return;
  var inputs=Array.prototype.slice.call(page.querySelectorAll('[data-assum-input]'));
  function load(){ try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){return {};} }
  function save(o){ try{localStorage.setItem(KEY,JSON.stringify(o));}catch(e){} }
  var store=load();
  // apply saved overrides
  inputs.forEach(function(inp){ var k=inp.getAttribute('data-assum-input'); if(store[k]!=null) inp.value=store[k]; mark(inp); });
  function mark(inp){
    var row=inp.closest('.arow'); if(!row) return;
    var changed=String(inp.value).trim()!==String(inp.getAttribute('data-default')).trim();
    row.classList.toggle('is-changed',changed);
    var st=row.querySelector('.def__state');
    if(st){ st.innerHTML = changed ? '<span class="changed">שונה</span> · מחדל: <span class="num">'+inp.getAttribute('data-default')+'</span>' : 'ברירת מחדל: <span class="num">'+inp.getAttribute('data-default')+'</span>'; }
    count();
  }
  function count(){ var n=page.querySelectorAll('.arow.is-changed').length; var el=document.getElementById('assum-changed-n'); if(el) el.textContent=n; }
  inputs.forEach(function(inp){ inp.addEventListener('input',function(){ mark(inp); }); });
  // per-field reset
  page.querySelectorAll('[data-assum-reset]').forEach(function(a){
    a.addEventListener('click',function(e){ e.preventDefault(); var k=a.getAttribute('data-assum-reset');
      var inp=page.querySelector('[data-assum-input="'+k+'"]'); if(inp){ inp.value=inp.getAttribute('data-default'); mark(inp);} });
  });
  // reset all
  var ra=document.getElementById('assum-reset-all');
  if(ra) ra.addEventListener('click',function(){ inputs.forEach(function(inp){ inp.value=inp.getAttribute('data-default'); mark(inp); }); });
  // search filter
  var search=document.getElementById('assum-search');
  if(search) search.addEventListener('input',function(){
    var q=search.value.trim();
    page.querySelectorAll('[data-assum-row]').forEach(function(row){
      var hit=q===''||(row.getAttribute('data-label')||'').indexOf(q)>=0;
      row.style.display=hit?'':'none';
    });
  });
  // save
  var sv=document.getElementById('assum-save');
  if(sv) sv.addEventListener('click',function(){
    var o={}; inputs.forEach(function(inp){ var k=inp.getAttribute('data-assum-input');
      if(String(inp.value).trim()!==String(inp.getAttribute('data-default')).trim()) o[k]=inp.value; });
    save(o); sv.textContent='✓ נשמר'; setTimeout(function(){sv.textContent='שמירה';},1600);
  });
})();
</script>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
