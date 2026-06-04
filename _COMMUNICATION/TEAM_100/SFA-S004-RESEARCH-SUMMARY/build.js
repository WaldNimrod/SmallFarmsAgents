const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "Team 100"; p.title = "SFA Research Summary";

// palette
const DARK="13241B", FOREST="1F4D2E", GREEN="2E7D4F", SAGE="8AAE91",
      GOLD="D8A24A", CLAY="C0644A", WHITE="FFFFFF", PANEL="F2F6F1",
      MUTED="5C6B60", INK="1A2620", LINE="D9E2DA";
const HEAD="Georgia", BODY="Calibri";
const W=13.333, H=7.5, M=0.7;
const sh=()=>({type:"outer",color:"000000",blur:7,offset:3,angle:135,opacity:0.12});

function footer(s,n,tag){
  s.addText("SFA · S004 — Strategic Research",{x:M,y:H-0.42,w:5,h:0.3,fontFace:BODY,fontSize:9,color:MUTED,align:"left",margin:0});
  s.addText(String(n),{x:W-1.1,y:H-0.42,w:0.5,h:0.3,fontFace:BODY,fontSize:9,color:MUTED,align:"right",margin:0});
}
function tag(s,t,color){
  s.addText(t.toUpperCase(),{x:M,y:0.5,w:W-2*M,h:0.3,fontFace:BODY,fontSize:12,bold:true,color:color||GOLD,charSpacing:3,align:"left",margin:0});
}
function title(s,t,color){
  s.addText(t,{x:M,y:0.82,w:W-2*M,h:0.9,fontFace:HEAD,fontSize:32,bold:true,color:color||INK,align:"left",margin:0});
}
function card(s,x,y,w,h,fill){
  s.addShape(p.shapes.RECTANGLE,{x,y,w,h,fill:{color:fill||WHITE},line:{color:LINE,width:1},shadow:sh()});
}
function circ(s,x,y,d,fill,txt,txtColor,fs){
  s.addShape(p.shapes.OVAL,{x,y,w:d,h:d,fill:{color:fill}});
  if(txt!=null) s.addText(txt,{x,y,w:d,h:d,fontFace:HEAD,fontSize:fs||18,bold:true,color:txtColor||WHITE,align:"center",valign:"middle",margin:0});
}

/* ---------- S1 TITLE ---------- */
let s=p.addSlide(); s.background={color:DARK};
// decorative circles motif
circ(s,W-2.4,-0.9,3.2,FOREST);
circ(s,W-1.2,1.4,1.1,GREEN);
circ(s,W-3.0,2.2,0.55,GOLD);
s.addText("STRATEGIC RESEARCH SUMMARY  ·  TEAM 100  ·  2026-06",{x:M,y:1.5,w:9,h:0.4,fontFace:BODY,fontSize:13,bold:true,color:SAGE,charSpacing:3,margin:0});
s.addText("The Operating System\nfor the Small Farm",{x:M,y:2.1,w:10,h:2.0,fontFace:HEAD,fontSize:46,bold:true,color:WHITE,lineSpacingMultiple:1.0,margin:0});
s.addText("מערכת ההפעלה של החווה הקטנה",{x:M,y:4.25,w:9,h:0.7,fontFace:BODY,fontSize:26,bold:true,color:GOLD,align:"left",margin:0});
s.addText("Vision Re-Lock  ·  Platform Decision  ·  Competitive Intelligence  ·  Schema Reference",{x:M,y:5.05,w:11,h:0.5,fontFace:BODY,fontSize:15,color:SAGE,margin:0});
s.addShape(p.shapes.LINE,{x:M,y:5.7,w:3.2,h:0,line:{color:GOLD,width:2.5}});
s.addText("SmallFarmsAgents  ·  Hebrew-first  ·  headless over farmOS",{x:M,y:5.85,w:11,h:0.4,fontFace:BODY,fontSize:12,italic:true,color:"9DB4A4",margin:0});

/* ---------- S2 WHAT WE DID ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"What this session produced",GREEN); title(s,"From open question to a locked, evidence-backed direction");
const phases=[
 ["1","Vision Re-Lock","North star, 5 pillars, audience, Freemium model — approved in-session."],
 ["2","Platform Decision","farmOS chosen (vs LiteFarm), headless, 3-tier delivery."],
 ["3","Competitive Intelligence","12 competitors + 2 OSS, mapped across internal + 4 AI engines."],
 ["4","Tend Reference","Field-exact schema from real farm exports → build-ready blueprint."],
];
let cx=M, cw=(W-2*M-3*0.35)/4, cy=2.0, ch=3.0;
phases.forEach((ph,i)=>{ let x=cx+i*(cw+0.35);
  card(s,x,cy,cw,ch); s.addShape(p.shapes.RECTANGLE,{x,y:cy,w:cw,h:0.12,fill:{color:GREEN}});
  circ(s,x+0.3,cy+0.4,0.7,FOREST,ph[0],WHITE,22);
  s.addText(ph[1],{x:x+0.25,y:cy+1.25,w:cw-0.5,h:0.7,fontFace:HEAD,fontSize:15,bold:true,color:INK,margin:0});
  s.addText(ph[2],{x:x+0.25,y:cy+1.95,w:cw-0.5,h:0.95,fontFace:BODY,fontSize:12,color:MUTED,margin:0});
});
// stat strip
let sy=5.4; const stats=[["12+2","competitors + OSS benchmarks"],["4","external AI research engines"],["16+","research sub-agents run"],["100%","findings converge"]];
let sw=(W-2*M-3*0.35)/4;
stats.forEach((st,i)=>{ let x=M+i*(sw+0.35);
  s.addText(st[0],{x,y:sy,w:sw,h:0.7,fontFace:HEAD,fontSize:34,bold:true,color:GOLD,align:"left",margin:0});
  s.addText(st[1],{x,y:sy+0.7,w:sw,h:0.5,fontFace:BODY,fontSize:11,color:MUTED,align:"left",margin:0});
});
footer(s,2);

/* ---------- S3 NORTH STAR ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"North Star",GREEN); title(s,"The page every grower opens in the morning");
s.addText("מערכת ההפעלה של החווה הקטנה",{x:M,y:1.7,w:W-2*M,h:0.6,fontFace:BODY,fontSize:22,bold:true,color:FOREST,align:"left",margin:0});
s.addText("End-to-end across five pillars — unified in one role-aware daily cockpit (Manager + Worker).",{x:M,y:2.3,w:W-2*M,h:0.4,fontFace:BODY,fontSize:14,italic:true,color:MUTED,margin:0});
const pil=[["Plan","what & when to grow"],["Execute","today's field tasks"],["Sell","orders & market"],["Relate","customers / CSA"],["Improve","data → better next year"]];
let pw=(W-2*M-4*0.3)/5, py=3.0, pch=2.7;
pil.forEach((pl,i)=>{ let x=M+i*(pw+0.3);
  card(s,x,py,pw,pch); s.addShape(p.shapes.RECTANGLE,{x,y:py,w:pw,h:1.0,fill:{color:i==0||i==4?GOLD:GREEN}});
  s.addText(pl[0],{x,y:py+0.18,w:pw,h:0.6,fontFace:HEAD,fontSize:18,bold:true,color:WHITE,align:"center",margin:0});
  s.addText(pl[1],{x:x+0.12,y:py+1.25,w:pw-0.24,h:1.2,fontFace:BODY,fontSize:12.5,color:INK,align:"center",valign:"top",margin:0});
});
s.addText("Brain (Plan / Improve) = our agronomic-economic engine  ·  Operations (Execute / Sell / Relate) = farmOS + integrations",{x:M,y:5.95,w:W-2*M,h:0.4,fontFace:BODY,fontSize:12,italic:true,color:MUTED,align:"center",margin:0});
footer(s,3);

/* ---------- S4 AUDIENCE & MODEL ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Audience & Business Model",GREEN); title(s,"Two audiences, one funnel");
let half=(W-2*M-0.4)/2;
card(s,M,1.9,half,3.0); s.addShape(p.shapes.RECTANGLE,{x:M,y:1.9,w:0.14,h:3.0,fill:{color:GOLD}});
s.addText("Commercial market gardener",{x:M+0.35,y:2.1,w:half-0.5,h:0.5,fontFace:HEAD,fontSize:18,bold:true,color:INK,margin:0});
s.addText([
 {text:"Paying core (JM Fortier / bio-intensive style)",options:{bullet:true,breakLine:true}},
 {text:"It's a business → real willingness to pay for tools that make/save money",options:{bullet:true,breakLine:true}},
 {text:"What the notebookLM spec & the data engine target",options:{bullet:true}},
],{x:M+0.35,y:2.7,w:half-0.6,h:2.0,fontFace:BODY,fontSize:13,color:INK,paraSpaceAfter:6,margin:0});
card(s,M+half+0.4,1.9,half,3.0); s.addShape(p.shapes.RECTANGLE,{x:M+half+0.4,y:1.9,w:0.14,h:3.0,fill:{color:GREEN}});
s.addText("Home / private grower",{x:M+half+0.75,y:2.1,w:half-0.5,h:0.5,fontFace:HEAD,fontSize:18,bold:true,color:INK,margin:0});
s.addText([
 {text:"Brand engine, not just free users — Nimrod's course customers",options:{bullet:true,breakLine:true}},
 {text:"Free community → trust → courses, consulting, custom dev",options:{bullet:true,breakLine:true}},
 {text:"Establishes the brand for SFA and for Nimrod as consultant",options:{bullet:true}},
],{x:M+half+0.75,y:2.7,w:half-0.6,h:2.0,fontFace:BODY,fontSize:13,color:INK,paraSpaceAfter:6,margin:0});
s.addShape(p.shapes.RECTANGLE,{x:M,y:5.25,w:W-2*M,h:1.25,fill:{color:FOREST}});
s.addText([{text:"Monetization:  ",options:{bold:true,color:GOLD}},{text:"Freemium + strong indirect.  ",options:{color:WHITE,bold:true}},{text:"Free Hebrew Crop-Book + calculators = the brand front (build first, build excellently). Paid = durable farm management + economics. Indirect revenue (brand → courses → consulting) may exceed direct.",options:{color:"D7E6DC"}}],{x:M+0.3,y:5.4,w:W-2*M-0.6,h:0.95,fontFace:BODY,fontSize:13.5,valign:"middle",margin:0});
footer(s,4);

/* ---------- S5 PLATFORM ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Platform Decision",GREEN); title(s,"farmOS — adopted headless");
const reasons=[
 ["API built for integration","Documented JSON:API + OAuth2 + official Python client. (LiteFarm's API is internal-only → brittle.)"],
 ["Flexible data model","Asset / Log / Quantity / Term + custom fields hold our 13-topic taxonomy & provenance. (LiteFarm schema rigid.)"],
 ["Blessed, documented self-host","Docker — fits our stack. (LiteFarm self-host unsupported.)"],
];
let ry=2.0;
reasons.forEach((r,i)=>{ let y=ry+i*1.15;
  circ(s,M,y,0.55,GREEN,String(i+1),WHITE,16);
  s.addText(r[0],{x:M+0.8,y:y-0.05,w:5.0,h:0.6,fontFace:HEAD,fontSize:16,bold:true,color:INK,margin:0});
  s.addText(r[1],{x:M+0.8,y:y+0.45,w:6.0,h:0.65,fontFace:BODY,fontSize:12,color:MUTED,margin:0});
});
// right callout
card(s,8.3,1.95,W-M-8.3,3.6,PANEL);
s.addText("Why headless?",{x:8.6,y:2.15,w:3.8,h:0.5,fontFace:HEAD,fontSize:17,bold:true,color:FOREST,margin:0});
s.addText([
 {text:"We build our own Hebrew/RTL UI — solves UX + Hebrew + GPL boundary at once.",options:{bullet:true,breakLine:true}},
 {text:"License GPL-2.0 (not AGPL): SaaS + headless → our engine stays proprietary.",options:{bullet:true,breakLine:true}},
 {text:"Bus-factor managed: we hold the code, data & frontend; Farmier = commercial backstop.",options:{bullet:true}},
],{x:8.6,y:2.75,w:W-M-8.3-0.6,h:2.6,fontFace:BODY,fontSize:12.5,color:INK,paraSpaceAfter:8,margin:0});
s.addText("LiteFarm's deciding negatives: zero RTL/Hebrew + internal-only API → headless neutralizes its UI advantage.",{x:M,y:5.95,w:W-2*M,h:0.5,fontFace:BODY,fontSize:12,italic:true,color:CLAY,margin:0});
footer(s,5);

/* ---------- S6 3-TIER DELIVERY ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Delivery Architecture",GREEN); title(s,"Three tiers — cost scales with commitment");
const tiers=[
 ["No account","Stateless",["Crop Book + 14 calculators","Plan + export, anonymous","∞ concurrency · ~0 cost","FREE"],SAGE],
 ["Rented sandbox","Ephemeral instance",["Full farmOS, spun up on demand","Bundle loaded → saved → reset","Fits farming's seasonality","PAY-PER-USE"],GREEN],
 ["Permanent instance","Always-on",["For serious operators","Live volume, always mounted","Full operational record-keeping","SUBSCRIPTION"],FOREST],
];
let tw=(W-2*M-2*0.4)/3, ty=2.0, tch=3.7;
tiers.forEach((t,i)=>{ let x=M+i*(tw+0.4);
  card(s,x,ty,tw,tch); s.addShape(p.shapes.RECTANGLE,{x,y:ty,w:tw,h:1.0,fill:{color:t[3]},line:{type:"none"}});
  s.addText(t[0],{x:x+0.2,y:ty+0.14,w:tw-0.4,h:0.45,fontFace:HEAD,fontSize:17,bold:true,color:WHITE,margin:0});
  s.addText(t[1],{x:x+0.2,y:ty+0.58,w:tw-0.4,h:0.35,fontFace:BODY,fontSize:12,italic:true,color:"EAF2EC",margin:0});
  s.addText(t[2].slice(0,3).map((b,j)=>({text:b,options:{bullet:true,breakLine:true}})),{x:x+0.25,y:ty+1.2,w:tw-0.5,h:1.7,fontFace:BODY,fontSize:12.5,color:INK,paraSpaceAfter:7,margin:0});
  s.addText(t[2][3],{x:x+0.2,y:ty+3.05,w:tw-0.4,h:0.5,fontFace:HEAD,fontSize:15,bold:true,color:t[3],align:"center",margin:0});
});
s.addText('Unified by the "bundle" = a DB/volume snapshot. Promotion ladder: draft → save bundle → keep always-on. Ephemerality kills the upgrade-debt of always-on instances.',{x:M,y:6.0,w:W-2*M,h:0.5,fontFace:BODY,fontSize:12,italic:true,color:MUTED,align:"center",margin:0});
footer(s,6);

/* ---------- S7 CI SCOPE ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"How we mapped the landscape",GREEN); title(s,"Quadruple-source competitive intelligence");
s.addText("Every finding cross-checked across internal research agents and four independent AI engines.",{x:M,y:1.7,w:W-2*M,h:0.4,fontFace:BODY,fontSize:14,italic:true,color:MUTED,margin:0});
const eng=["Internal agents","Perplexity","Claude (web)","OpenAI","Gemini"];
let ew=(W-2*M-4*0.3)/5;
eng.forEach((e,i)=>{ let x=M+i*(ew+0.3);
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y:2.25,w:ew,h:0.7,rectRadius:0.08,fill:{color:i==0?FOREST:PANEL},line:{color:LINE,width:1}});
  s.addText(e,{x,y:2.25,w:ew,h:0.7,fontFace:BODY,fontSize:12.5,bold:true,color:i==0?WHITE:INK,align:"center",valign:"middle",margin:0});
});
s.addText("The market splits into four shallow, un-moated clusters — none spans the whole farm:",{x:M,y:3.3,w:W-2*M,h:0.4,fontFace:BODY,fontSize:14,bold:true,color:INK,margin:0});
const clusters=[
 ["Crop / production planners","Tend · Heirloom · Seedtime · MarketGardenPlanner · VeggieCropper · GrowVeg · Planter"],
 ["Farm records & compliance","Farmbrite · Croptracker · AgriWebb (livestock)"],
 ["Sales / CSA commerce","Local Line · Barn2Door · Harvie (defunct)"],
 ["Open-source benchmarks","farmOS (our backend) · LiteFarm"],
];
let clw=(W-2*M-0.4)/2;
clusters.forEach((c,i)=>{ let x=M+(i%2)*(clw+0.4), y=3.85+Math.floor(i/2)*1.25;
  card(s,x,y,clw,1.1);
  s.addText(c[0],{x:x+0.25,y:y+0.12,w:clw-0.5,h:0.4,fontFace:HEAD,fontSize:14,bold:true,color:FOREST,margin:0});
  s.addText(c[1],{x:x+0.25,y:y+0.52,w:clw-0.5,h:0.5,fontFace:BODY,fontSize:11.5,color:MUTED,margin:0});
});
footer(s,7);

/* ---------- S8 THE 3 FINDINGS (HERO/DARK) ---------- */
s=p.addSlide(); s.background={color:DARK};
s.addText("THE VERDICT — UNANIMOUS ACROSS ALL 12 COMPETITORS",{x:M,y:0.6,w:W-2*M,h:0.4,fontFace:BODY,fontSize:13,bold:true,color:GOLD,charSpacing:2,margin:0});
s.addText("Three open lanes nobody serves",{x:M,y:1.05,w:W-2*M,h:0.8,fontFace:HEAD,fontSize:34,bold:true,color:WHITE,margin:0});
const finds=[
 ["1","No one closes the market-price → plan → profit loop","All economics is retrospective or self-entered. Heirloom lists it on its public roadmap — unshipped. → Our #1 wedge."],
 ["2","Zero Hebrew / zero RTL — anywhere","Even $64M AgriWebb & JM Fortier's Heirloom built no RTL. The only Israeli product is a printed paper calendar. → Our moat."],
 ["3","The production ↔ sales loop is industry-wide open","Sales tools never feed planning; planners never pull demand. → Our unified 5-pillar OS is unbuilt anywhere."],
];
let fy=2.3;
finds.forEach((f,i)=>{ let y=fy+i*1.5;
  circ(s,M,y,0.95,i==1?GREEN:GOLD,f[0],DARK,30);
  s.addText(f[1],{x:M+1.25,y:y-0.05,w:W-2*M-1.25,h:0.55,fontFace:HEAD,fontSize:19,bold:true,color:WHITE,margin:0});
  s.addText(f[2],{x:M+1.25,y:y+0.55,w:W-2*M-1.25,h:0.8,fontFace:BODY,fontSize:13,color:"AFC4B5",margin:0});
});
footer(s,8);

/* ---------- S9 THE WEDGE ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"The Wedge",GOLD); title(s,'"What is most profitable to grow — right now?"');
// flow boxes
const flow=[["Israeli market-price index","Ministry of Agriculture wholesale feed"],["14 planning calculators","yield × price × cost, per bed"],["Ranked: most profitable to grow","forward, before you plant"]];
let fw=3.6, fgap=((W-2*M)-3*fw)/2, fy2=2.6, fhh=1.5;
flow.forEach((b,i)=>{ let x=M+i*(fw+fgap);
  card(s,x,fy2,fw,fhh,i==2?GOLD:PANEL);
  s.addText(b[0],{x:x+0.2,y:fy2+0.25,w:fw-0.4,h:0.6,fontFace:HEAD,fontSize:15,bold:true,color:i==2?DARK:FOREST,align:"center",margin:0});
  s.addText(b[1],{x:x+0.2,y:fy2+0.85,w:fw-0.4,h:0.5,fontFace:BODY,fontSize:11.5,color:i==2?"4A3a12":MUTED,align:"center",margin:0});
  if(i<2) s.addShape(p.shapes.CHEVRON,{x:x+fw+0.12,y:fy2+0.5,w:fgap-0.24,h:0.5,fill:{color:SAGE}});
});
card(s,M,4.65,W-2*M,1.7,FOREST);
s.addText([{text:"Nobody else does this.  ",options:{bold:true,color:GOLD}},{text:"Every competitor that touches money tracks it ",options:{color:WHITE}},{text:"backward",options:{italic:true,color:WHITE,bold:true}},{text:" (your own books) or uses self-entered prices. SFA turns the record-book into a ",options:{color:WHITE}},{text:"forward economic engine",options:{bold:true,color:GOLD}},{text:" — agronomy × live Israeli market prices.",options:{color:WHITE}}],{x:M+0.3,y:4.85,w:W-2*M-0.6,h:1.3,fontFace:BODY,fontSize:15,valign:"middle",margin:0});
footer(s,9);

/* ---------- S10 THE MOAT ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"The Moat",GOLD); title(s,"Hebrew-first, RTL-native, Israeli climate & market");
s.addText([
 {text:"Structural, not cosmetic.  ",options:{bold:true,color:FOREST}},
 {text:"RTL must be built in from day one — every field, calendar, bed-map and notification.",options:{color:INK}},
],{x:M,y:1.85,w:W-2*M,h:0.6,fontFace:BODY,fontSize:15,margin:0});
const moat=[
 ["0","competitors with any Hebrew or RTL — out of 12 + 2 OSS"],
 ["1","Israeli home-garden product exists — a printed paper calendar"],
 ["$64M","AgriWebb funding — still built no RTL (nor full Spanish)"],
];
let my=2.7;
moat.forEach((mm,i)=>{ let y=my+i*1.15;
  s.addText(mm[0],{x:M,y:y,w:2.2,h:0.8,fontFace:HEAD,fontSize:38,bold:true,color:GOLD,align:"left",margin:0});
  s.addText(mm[1],{x:M+2.4,y:y+0.05,w:W-2*M-2.4,h:0.8,fontFace:BODY,fontSize:14.5,color:INK,valign:"middle",margin:0});
  if(i<2) s.addShape(p.shapes.LINE,{x:M,y:y+1.0,w:W-2*M,h:0,line:{color:LINE,width:1}});
});
s.addText("Plus Israeli specifics no global tool will build: Negev vs Galilee seasonality, local pests, holidays, Shabbat-friendly views, water-salinity.",{x:M,y:6.05,w:W-2*M,h:0.5,fontFace:BODY,fontSize:12,italic:true,color:MUTED,margin:0});
footer(s,10);

/* ---------- S11 WHITE SPACE ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"White-Space",GREEN); title(s,"Where (almost) nobody plays");
const ws=[
 ["Market-price → profit planning","The forward economic engine. Universal gap."],
 ["Hebrew / RTL / Israel","Uncontested. A defensible moat, not a feature."],
 ["The unified morning cockpit","Plan+Execute+Sell+Relate in one role-aware screen."],
 ["Beautiful mobile canvas + cockpit","Planter owns mobile; Seedtime owns the cockpit; nobody owns both."],
];
let wsw=(W-2*M-0.4)/2, wsh=1.7;
ws.forEach((w,i)=>{ let x=M+(i%2)*(wsw+0.4), y=2.0+Math.floor(i/2)*(wsh+0.35);
  card(s,x,y,wsw,wsh); s.addShape(p.shapes.RECTANGLE,{x,y,w:0.14,h:wsh,fill:{color:GOLD}});
  circ(s,x+0.35,y+0.35,0.55,FOREST,String(i+1),WHITE,16);
  s.addText(w[0],{x:x+1.1,y:y+0.3,w:wsw-1.3,h:0.55,fontFace:HEAD,fontSize:15.5,bold:true,color:INK,margin:0});
  s.addText(w[1],{x:x+1.1,y:y+0.9,w:wsw-1.3,h:0.65,fontFace:BODY,fontSize:12.5,color:MUTED,margin:0});
});
footer(s,11);

/* ---------- S12 SCHEMA ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Data Model",GREEN); title(s,"What we adopt — three layers");
const layers=[
 ["Tend — the spine","Crop → Growing-Template → Planting → Task → Harvest → Lot → Inventory. Multiple templates per crop, cascade/clone. Maps 1:1 to farmOS Asset/Log/Quantity/Term.",GOLD],
 ["LiteFarm — crop depth","Deepest OSS crop schema (crop type → varietal → management plan, estimated yield + value/yield). Second reference.",GREEN],
 ["farmOS — the substrate","Asset/Log/Quantity/Term + custom fields. The operational ledger; we own the opinionated UI on top.",FOREST],
];
let ly=2.0;
layers.forEach((l,i)=>{ let y=ly+i*1.25;
  card(s,M,y,W-2*M,1.1); s.addShape(p.shapes.RECTANGLE,{x:M,y,w:0.16,h:1.1,fill:{color:l[2]}});
  s.addText(l[0],{x:M+0.4,y:y+0.13,w:3.2,h:0.85,fontFace:HEAD,fontSize:15.5,bold:true,color:INK,valign:"middle",margin:0});
  s.addText(l[1],{x:M+3.7,y:y+0.12,w:W-2*M-3.9,h:0.9,fontFace:BODY,fontSize:12.5,color:MUTED,valign:"middle",margin:0});
});
s.addShape(p.shapes.RECTANGLE,{x:M,y:5.95,w:W-2*M,h:0.7,fill:{color:PANEL},line:{color:LINE,width:1}});
s.addText([{text:"Field-exact, validated:  ",options:{bold:true,color:FOREST}},{text:"4 years of real Tend exports from Nimrod's own farm are already in-repo (64-column CROP_PLAN, metric, ₪) + an existing importer. Inference → fact.",options:{color:INK}}],{x:M+0.3,y:5.95,w:W-2*M-0.6,h:0.7,fontFace:BODY,fontSize:12.5,valign:"middle",margin:0});
footer(s,12);

/* ---------- S13 MATCH vs BEAT ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Strategy",GREEN); title(s,"Match the table stakes — beat on what matters");
let bw=(W-2*M-0.4)/2;
// MATCH
s.addShape(p.shapes.RECTANGLE,{x:M,y:1.95,w:bw,h:0.6,fill:{color:SAGE}});
s.addText("MATCH  (table stakes)",{x:M,y:1.95,w:bw,h:0.6,fontFace:HEAD,fontSize:16,bold:true,color:DARK,align:"center",valign:"middle",margin:0});
card(s,M,2.55,bw,3.6);
s.addText([
 {text:"Backward-from-harvest scheduling + bed-turnover",options:{bullet:true,breakLine:true}},
 {text:"Connected loop + public order forms + availability sheets",options:{bullet:true,breakLine:true}},
 {text:"Crew / manager accounts with task autonomy",options:{bullet:true,breakLine:true}},
 {text:"Succession + rotation as the planning hook",options:{bullet:true,breakLine:true}},
 {text:"CSA box-first backward planning",options:{bullet:true,breakLine:true}},
 {text:"The 14 calculators (seed/yield/spacing/succession)",options:{bullet:true}},
],{x:M+0.35,y:2.8,w:bw-0.7,h:3.1,fontFace:BODY,fontSize:13.5,color:INK,paraSpaceAfter:9,margin:0});
// BEAT
let bx=M+bw+0.4;
s.addShape(p.shapes.RECTANGLE,{x:bx,y:1.95,w:bw,h:0.6,fill:{color:GOLD}});
s.addText("BEAT  (where we win)",{x:bx,y:1.95,w:bw,h:0.6,fontFace:HEAD,fontSize:16,bold:true,color:DARK,align:"center",valign:"middle",margin:0});
card(s,bx,2.55,bw,3.6);
s.addText([
 {text:"Market-price → forward profit loop (the hero)",options:{bullet:true,breakLine:true,bold:true}},
 {text:"Hebrew-first / RTL + Israeli climate & market",options:{bullet:true,breakLine:true,bold:true}},
 {text:"Curated agronomic KB + 14 calculators (rivals: free fields, no science)",options:{bullet:true,breakLine:true}},
 {text:"Openness & durability (farmOS + export) vs closed, bus-factor-1 rivals",options:{bullet:true,breakLine:true}},
 {text:'Commercial tier = capability (Sell+Relate+finance), not "more beds"',options:{bullet:true}},
],{x:bx+0.35,y:2.8,w:bw-0.7,h:3.1,fontFace:BODY,fontSize:13.5,color:INK,paraSpaceAfter:9,margin:0});
footer(s,13);

/* ---------- S14 PRICING ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Pricing Benchmark",GREEN); title(s,"Where a serious tool sits — and our target");
s.addChart(p.charts.BAR,[{name:"$/mo (equiv.)",labels:["Seedtime","MyGardenPlanner","Farmbrite","Tend Pro","VeggieCropper","AgriWebb","Local Line","Solara"],values:[14,19,29,30,37,55,99,99]}],{
  x:M,y:2.0,w:7.7,h:4.3,barDir:"col",chartColors:[GREEN],
  chartArea:{fill:{color:WHITE}},catAxisLabelColor:MUTED,catAxisLabelFontSize:9,valAxisLabelColor:MUTED,
  valGridLine:{color:"E2E8F0",size:0.5},catGridLine:{style:"none"},
  showValue:true,dataLabelPosition:"outEnd",dataLabelColor:INK,dataLabelFontSize:9,showLegend:false,valAxisHidden:true,
});
card(s,8.9,2.2,W-M-8.9,2.0,FOREST);
s.addText("SFA target",{x:9.15,y:2.4,w:3.4,h:0.4,fontFace:BODY,fontSize:13,bold:true,color:GOLD,margin:0});
s.addText("~$25–40 / mo",{x:9.15,y:2.75,w:3.4,h:0.7,fontFace:HEAD,fontSize:30,bold:true,color:WHITE,margin:0});
s.addText("equiv. ₪ — below Tend Pro, justified by the economics engine",{x:9.15,y:3.45,w:W-M-9.15-0.25,h:0.7,fontFace:BODY,fontSize:11.5,color:"D7E6DC",margin:0});
s.addText([
 {text:"Free tier = table stakes (rare → our advantage).",options:{bullet:true,breakLine:true}},
 {text:"Croptracker ~$275/mo (enterprise, off-scale).",options:{bullet:true,breakLine:true}},
 {text:"Flat, transparent, no setup fees, no % of sales.",options:{bullet:true}},
],{x:8.9,y:4.45,w:W-M-8.9,h:1.8,fontFace:BODY,fontSize:11.5,color:INK,paraSpaceAfter:6,margin:0});
footer(s,14);

/* ---------- S15 DESIGN PRINCIPLES ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Design Principles",GREEN); title(s,"From Nimrod's years inside Tend");
const dp=[
 ["①  The harvest loop is priority #1","Harvest-list → field-report → accumulated learning is the most valuable AND the most painful loop. The crew never understood what to update. Make it fast, structured, worker-obvious — the gold lives here."],
 ["②  Speed is a hard requirement","Many Tend operations were simply slow. Slowness kills field adoption. Treat responsiveness as a non-negotiable NFR."],
 ["③  Keep what worked","Time+space colour bed-map, auto-generated tasks, auto harvest-lists, clone-crop-shows-on-map."],
 ["④  Redo what didn't","Everything must run much faster; all field reporting must be far simpler & more structured for the worker."],
];
let dy=1.95, dhh=1.18;
dp.forEach((d,i)=>{ let y=dy+i*(dhh+0.05);
  s.addText(d[0],{x:M,y:y,w:4.3,h:dhh,fontFace:HEAD,fontSize:15,bold:true,color:i<2?GOLD:FOREST,valign:"top",margin:0});
  s.addText(d[1],{x:M+4.5,y:y,w:W-2*M-4.5,h:dhh,fontFace:BODY,fontSize:12.5,color:INK,valign:"top",margin:0});
  if(i<3) s.addShape(p.shapes.LINE,{x:M,y:y+dhh,w:W-2*M,h:0,line:{color:LINE,width:1}});
});
footer(s,15);

/* ---------- S16 RECOMMENDATION ---------- */
s=p.addSlide(); s.background={color:WHITE};
tag(s,"Recommendation",GREEN); title(s,"Research is complete → proceed to Phase 0");
s.addText("12 competitors + 2 OSS · 4 AI engines · internal agents — all converge. No further CI rounds needed.",{x:M,y:1.75,w:W-2*M,h:0.4,fontFace:BODY,fontSize:14,italic:true,color:MUTED,margin:0});
const ph0=[
 ["Data model","farmOS Asset/Log/Quantity/Term × Tend spine × 13-topic taxonomy × 14 calculators"],
 ["3-tier delivery","No-account · rented sandbox · permanent — the bundle lifecycle"],
 ["The morning cockpit","Role-aware (Manager/Worker), RTL-native, harvest-loop-first, fast"],
 ["The wedge, wired","Ministry-of-Ag price index → calculators → 'most profitable to grow'"],
];
let phw=(W-2*M-0.4)/2;
ph0.forEach((q,i)=>{ let x=M+(i%2)*(phw+0.4), y=2.35+Math.floor(i/2)*1.55;
  card(s,x,y,phw,1.35);
  circ(s,x+0.3,y+0.35,0.6,FOREST,String(i+1),WHITE,17);
  s.addText(q[0],{x:x+1.05,y:y+0.18,w:phw-1.25,h:0.45,fontFace:HEAD,fontSize:15,bold:true,color:INK,margin:0});
  s.addText(q[1],{x:x+1.05,y:y+0.62,w:phw-1.25,h:0.65,fontFace:BODY,fontSize:11.5,color:MUTED,margin:0});
});
s.addText("Open decisions carried forward: D1 pricing specifics · D2 multi-tenancy at scale · D3 Sell/Relate = build (no clean integration target).",{x:M,y:5.95,w:W-2*M,h:0.5,fontFace:BODY,fontSize:11.5,italic:true,color:MUTED,align:"center",margin:0});
footer(s,16);

/* ---------- S17 CLOSING ---------- */
s=p.addSlide(); s.background={color:DARK};
circ(s,-1.0,H-2.6,3.4,FOREST);
circ(s,0.5,H-1.2,1.0,GOLD);
s.addText("מערכת ההפעלה של החווה הקטנה",{x:M,y:2.0,w:W-2*M,h:0.8,fontFace:BODY,fontSize:30,bold:true,color:GOLD,align:"center",margin:0});
s.addText("The operating system for the small farm.",{x:M,y:2.95,w:W-2*M,h:0.7,fontFace:HEAD,fontSize:26,bold:true,color:WHITE,align:"center",margin:0});
s.addText("Wedge + moat confirmed against 12 competitors + 2 open-source benchmarks.",{x:M,y:3.95,w:W-2*M,h:0.5,fontFace:BODY,fontSize:15,color:SAGE,align:"center",margin:0});
s.addShape(p.shapes.LINE,{x:W/2-1.6,y:4.7,w:3.2,h:0,line:{color:GOLD,width:2.5}});
s.addText("Next: Phase 0 — technical design",{x:M,y:4.9,w:W-2*M,h:0.5,fontFace:BODY,fontSize:14,italic:true,color:"9DB4A4",align:"center",margin:0});

p.writeFile({fileName:"/tmp/sfa_deck/SFA_Research_Summary.pptx"}).then(f=>console.log("WROTE",f));
