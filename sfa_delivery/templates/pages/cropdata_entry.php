<?php
/**
 * cropdata_entry.php — Route /cropdata-entry — WP-CB-UI-REDESIGN (WI-8)
 *
 * Internal owner-only guided classification tool from the team_35 mockup:
 * classify planting_method + frost_class (+ conditional nursery days) one crop
 * at a time, keyboard 1–5 to pick, Enter to save & advance. Progress + queue.
 *
 * STAGING ONLY: selections persist client-side (localStorage 'sfa.cropdata')
 * and are meant to feed the backend pipeline through the contribution funnel.
 * The read-only delivery tier never writes canonical data. Not linked in the
 * public nav (owner reaches it by URL).
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$page_title = 'סיווג נתוני גידולים';
$page_sub   = 'כלי פנימי';
$active     = '';

$crops = is_array($crops ?? null) ? $crops : [];

ob_start();
?>
<div class="cde" id="cde" data-crops='<?= $h(json_encode($crops, JSON_UNESCAPED_UNICODE | JSON_HEX_APOS | JSON_HEX_QUOT)) ?>'>
  <div class="thead">
    <span class="badge">פנימי · בעלים בלבד</span>
    <h1>סיווג נתוני גידולים</h1>
    <span class="muted">מקלדת: 1–5 לבחירה · Enter לשמירה</span>
  </div>

  <div class="prog"><i id="cde-prog"></i></div>
  <div class="proglbl"><span><b id="cde-done" style="color:var(--gj-ink)">0</b> / <span id="cde-total"><?= count($crops) ?></span> גידולים סווגו</span><span id="cde-remain"></span></div>

  <div class="card" id="cde-card">
    <div class="crop">
      <div class="crop__art" id="cde-art"></div>
      <div><div class="crop__n" id="cde-name">—</div><div class="crop__l" id="cde-lat"></div></div>
      <div class="crop__c" id="cde-counter"></div>
    </div>

    <div class="q" data-q="planting_method">
      <div class="q__h">שיטת ריבוי</div>
      <div class="picks">
        <button class="pick" data-v="direct_seed"><kbd>1</kbd>זריעה ישירה</button>
        <button class="pick" data-v="transplant"><kbd>2</kbd>שתיל</button>
        <button class="pick" data-v="both"><kbd>3</kbd>גם וגם</button>
        <button class="pick" data-v="tuber"><kbd>4</kbd>פקעת / שלוחה</button>
        <button class="pick" data-v="cutting"><kbd>5</kbd>ייחור</button>
      </div>
      <div class="cond" id="cde-nursery"><div style="font-size:13px;font-weight:600;margin-bottom:8px">ימים במשתלה (לשתיל / גם-וגם)</div><div class="fld"><input id="cde-nursery-val" inputmode="numeric" placeholder="—"><span class="muted">ימים</span></div></div>
    </div>

    <div class="q" data-q="frost_tolerance_class">
      <div class="q__h">עמידות לקרה</div>
      <div class="picks">
        <button class="pick" data-v="very_hardy"><kbd>1</kbd>קשיח מאוד</button>
        <button class="pick" data-v="hardy"><kbd>2</kbd>קשיח</button>
        <button class="pick" data-v="half_hardy"><kbd>3</kbd>בינוני</button>
        <button class="pick" data-v="tender"><kbd>4</kbd>רגיש</button>
        <button class="pick" data-v="very_tender"><kbd>5</kbd>רגיש מאוד</button>
      </div>
    </div>

    <div class="actions">
      <span class="hint">⏎ שמור והמשך · ⌫ דלג · → הקודם</span>
      <span class="sp"></span>
      <button class="btn btn--ghost" id="cde-skip">דלג</button>
      <button class="btn btn--leaf" id="cde-save">שמור והבא ←</button>
    </div>
  </div>

  <div class="queue">
    <h5>תור הסיווג</h5>
    <div class="row" id="cde-queue"></div>
  </div>
</div>
<script>
(function(){
  var KEY='sfa.cropdata';
  var root=document.getElementById('cde'); if(!root) return;
  var crops; try{ crops=JSON.parse(root.getAttribute('data-crops')||'[]'); }catch(e){ crops=[]; }
  var store; try{ store=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(e){ store={}; }
  var idx=0;
  var nameEl=document.getElementById('cde-name'), latEl=document.getElementById('cde-lat'),
      artEl=document.getElementById('cde-art'), cntEl=document.getElementById('cde-counter'),
      nursery=document.getElementById('cde-nursery'), nurseryVal=document.getElementById('cde-nursery-val'),
      qs=Array.prototype.slice.call(root.querySelectorAll('.q'));
  function doneCount(){ return Object.keys(store).filter(function(k){return store[k] && store[k].planting_method;}).length; }
  function save(){ try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){} }
  function render(){
    var c=crops[idx]; if(!c) return;
    nameEl.textContent=c.name_he||c.slug;
    latEl.textContent=(c.name_lat?c.name_lat:'')+(c.fam_he?(' · '+c.fam_he):'');
    artEl.innerHTML=c.wc_art?('<img src="/public_assets/img/crops/'+c.wc_art+'" alt="">'):('<svg class="gi" style="width:40px;height:40px;color:var(--gj-leaf-soft)"><use href="#icon-leaf"/></svg>');
    cntEl.textContent='גידול '+(idx+1)+' מתוך '+crops.length;
    var rec=store[c.slug]||{};
    qs.forEach(function(q){ var k=q.getAttribute('data-q');
      q.querySelectorAll('.pick').forEach(function(p){ p.classList.toggle('on', rec[k]===p.getAttribute('data-v')); });
    });
    nurseryVal.value=rec.days_in_nursery||'';
    updNursery();
    // progress
    var done=doneCount(), total=crops.length;
    document.getElementById('cde-done').textContent=done;
    document.getElementById('cde-prog').style.width=(total?Math.round(done/total*100):0)+'%';
    document.getElementById('cde-remain').textContent='נותרו '+(total-done);
    // queue (window around current)
    var q=document.getElementById('cde-queue'), html='';
    var start=Math.max(0,idx-2), end=Math.min(crops.length,start+7);
    for(var i=start;i<end;i++){ var cc=crops[i], cls='chip', st='';
      if(store[cc.slug]&&store[cc.slug].planting_method){ cls+=' done'; }
      if(i===idx){ st=' style="background:var(--gj-leaf-deep);color:#fff"'; }
      html+='<span class="'+cls+'"'+st+'>'+(store[cc.slug]&&store[cc.slug].planting_method?'✓ ':'')+(cc.name_he||cc.slug)+'</span>';
    }
    if(end<crops.length){ html+='<span class="chip">+ '+(crops.length-end)+'</span>'; }
    q.innerHTML=html;
  }
  function curPM(){ var q=root.querySelector('.q[data-q="planting_method"] .pick.on'); return q?q.getAttribute('data-v'):''; }
  function updNursery(){ var v=curPM(); nursery.classList.toggle('show', v==='transplant'||v==='both'); }
  root.querySelectorAll('.q').forEach(function(q){ var k=q.getAttribute('data-q');
    q.querySelectorAll('.pick').forEach(function(p){ p.addEventListener('click',function(){
      q.querySelectorAll('.pick').forEach(function(x){x.classList.remove('on');});
      p.classList.add('on'); if(k==='planting_method') updNursery();
    }); });
  });
  function commit(){
    var c=crops[idx]; if(!c) return; var rec=store[c.slug]||{};
    qs.forEach(function(q){ var k=q.getAttribute('data-q'); var on=q.querySelector('.pick.on'); if(on) rec[k]=on.getAttribute('data-v'); });
    if(nurseryVal.value) rec.days_in_nursery=nurseryVal.value;
    store[c.slug]=rec; save();
    // best-effort funnel to the backend pipeline
    try{ fetch('/api/v1/contribute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:'request-info',field_name:'classify',crop_slug:c.slug})}).catch(function(){}); }catch(e){}
  }
  function next(commitFirst){ if(commitFirst) commit(); idx=Math.min(crops.length-1, idx+1); render(); }
  function prev(){ idx=Math.max(0, idx-1); render(); }
  document.getElementById('cde-save').addEventListener('click',function(){ next(true); });
  document.getElementById('cde-skip').addEventListener('click',function(){ next(false); });
  document.addEventListener('keydown',function(e){
    if(e.target===nurseryVal) return;
    if(e.key>='1'&&e.key<='5'){ var n=parseInt(e.key,10);
      // apply to the first unanswered question, else planting_method
      var q=qs.find(function(qq){ return !qq.querySelector('.pick.on'); })||qs[0];
      var picks=q.querySelectorAll('.pick'); if(picks[n-1]) picks[n-1].click();
    } else if(e.key==='Enter'){ next(true); }
    else if(e.key==='Backspace'){ e.preventDefault(); next(false); }
    else if(e.key==='ArrowRight'){ prev(); }
  });
  render();
})();
</script>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
