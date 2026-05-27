/* app.jsx — root wiring all artboards into the design canvas */

const { DesignCanvas, DCSection, DCArtboard } = window;

function App() {
  const [ready, setReady] = React.useState(false);
  React.useEffect(() => {
    const t = setTimeout(() => setReady(true), 50);
    return () => clearTimeout(t);
  }, []);

  if (!ready) {
    return (
      <div style={{
        position: 'fixed', inset: 0, display: 'grid', placeItems: 'center',
        background: '#f6f1e3', fontFamily: '"Frank Ruhl Libre", serif',
        color: '#2a2418', direction: 'rtl'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 26, fontWeight: 700, marginBottom: 6 }}>SFA — חקלאות קטנה</div>
          <div style={{ fontSize: 13, color: '#776a4d', fontFamily: 'system-ui' }}>טוען אזור עבודה…</div>
        </div>
      </div>
    );
  }

  return (
    <React.Fragment>
      <window.WatercolorDefs />

      <DesignCanvas>

        {/* ============================================================ */}
        {/* 0 · Architecture                                              */}
        {/* ============================================================ */}
        <DCSection id="mental" title="00 · ארכיטקטורה"
          subtitle="מערכת אחת · ‎8 מודולים · ‎3 רמות · ‎נטול-מסגרת nimrod.bio">
          <DCArtboard id="overview" label="System overview" width={920} height={780}>
            <window.MentalModel />
          </DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 1 · MOBILE · Module Hub                                       */}
        {/* ============================================================ */}
        <DCSection id="hub-mobile" title="01 · מובייל · Module Hub"
          subtitle="דף בית של המערכת — גלריית מודולים מקובצים ל-3 רמות. ‎390×844.">

          <DCArtboard id="hub-home"  label="H1 · דף בית"                  width={390} height={2200} data-screen-label="H1 · Hub home"><window.HubHome /></DCArtboard>
          <DCArtboard id="hub-tiers" label="H2 · איך זה עובד · 3 רמות"   width={390} height={1100} data-screen-label="H2 · Tiers"><window.HubTiers /></DCArtboard>
          <DCArtboard id="hub-calc"  label="H3 · מחשבון לחקלאי (בטא)"     width={390} height={1280} data-screen-label="H3 · Calculator"><window.HubCalculator /></DCArtboard>
          <DCArtboard id="hub-comm"  label="H4 · רכיבי קהילה ומשוב"       width={390} height={1700} data-screen-label="H4 · Community"><window.CommunityShowcase /></DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 2 · MOBILE · Crop Book — knowledge base                       */}
        {/* ============================================================ */}
        <DCSection id="cropbook-mobile" title="02 · מובייל · ספר גידולים"
          subtitle="בסיס ידע מקצועי. ריבוי דרכי-כניסה: שאלות מנחות · משפחה · טבלה מקצועית · חיפוש מתקדם. ‎גידול → זנים.">

          <DCArtboard id="cb-entry"    label="CB0 · עמוד פתיחה"          width={390} height={1100} data-screen-label="CB0 · Entry"><window.CB_Entry /></DCArtboard>
          <DCArtboard id="cb-question" label="CB1 · שאלות מנחות"          width={390} height={1100} data-screen-label="CB1 · Questions"><window.CB_QuestionView /></DCArtboard>
          <DCArtboard id="cb-family"   label="CB2 · משפחות צמחיות"       width={390} height={1200} data-screen-label="CB2 · Families"><window.CB_FamilyTree /></DCArtboard>
          <DCArtboard id="cb-table"    label="CB3 · תצוגה מקצועית"        width={390} height={900} data-screen-label="CB3 · Pro table"><window.CB_ProTable /></DCArtboard>
          <DCArtboard id="cb-search"   label="CB4 · חיפוש מתקדם"          width={390} height={1100} data-screen-label="CB4 · Search"><window.CB_Search /></DCArtboard>
          <DCArtboard id="cb-full"     label="CB5 · גידול + זנים (היררכיה)" width={390} height={1700} data-screen-label="CB5 · Crop+vars"><window.CB_CropFull /></DCArtboard>
          <DCArtboard id="cb-original" label="CB6 · גריד פשוט (קיים)"      width={390} height={1200} data-screen-label="CB6 · Simple grid"><window.GJ_BookGrid /></DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 3 · MOBILE · Market                                            */}
        {/* ============================================================ */}
        <DCSection id="market-mobile" title="03 · מובייל · מחירון"
          subtitle="כלי שיווקי קהילתי + דיסקליימר מפורש.">

          <DCArtboard id="mk-list"   label="MK1 · רשימה (עם דיסקליימר)"   width={390} height={1600} data-screen-label="MK1 · List"><window.GJ_MarketList /></DCArtboard>
          <DCArtboard id="mk-detail" label="MK2 · פירוט מוצר"              width={390} height={1100} data-screen-label="MK2 · Detail"><window.GJ_MarketDetail /></DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 4 · DESKTOP variants                                           */}
        {/* ============================================================ */}
        <DCSection id="desktop" title="04 · דסקטופ · גרסאות רחבות"
          subtitle="1200×800 · sidebar עם תפריט אקורדיון + קהילה בצד. ‎אותו מערכת, layout שונה.">

          <DCArtboard id="dt-hub"        label="D1 · Hub"                  width={1200} height={1500} data-screen-label="D1 · Hub"><window.Desktop_Hub /></DCArtboard>
          <DCArtboard id="dt-tiers"      label="D2 · איך זה עובד"          width={1200} height={1100} data-screen-label="D2 · Tiers"><window.Desktop_Tiers /></DCArtboard>
          <DCArtboard id="dt-book-table" label="D3 · ספר · טבלה מקצועית"   width={1200} height={1100} data-screen-label="D3 · Book table"><window.Desktop_CropBookProTable /></DCArtboard>
          <DCArtboard id="dt-crop"       label="D4 · ספר · פירוט גידול"    width={1200} height={1500} data-screen-label="D4 · Crop detail"><window.Desktop_CropDetail /></DCArtboard>
          <DCArtboard id="dt-mkt"        label="D5 · מחירון · רשימה"       width={1200} height={1300} data-screen-label="D5 · Market"><window.Desktop_Market /></DCArtboard>
          <DCArtboard id="dt-mkt-detail" label="D6 · מחירון · פירוט מוצר"  width={1200} height={1300} data-screen-label="D6 · Market detail"><window.Desktop_MarketDetail /></DCArtboard>
          <DCArtboard id="dt-calc"       label="D7 · מחשבון"               width={1200} height={1100} data-screen-label="D7 · Calculator"><window.Desktop_Calculator /></DCArtboard>
          <DCArtboard id="dt-search"     label="D8 · חיפוש גלובלי"          width={1200} height={1200} data-screen-label="D8 · Search"><window.Desktop_Search /></DCArtboard>
          <DCArtboard id="dt-comm"       label="D9 · קהילה (עמוד מלא)"      width={1200} height={1700} data-screen-label="D9 · Community"><window.Desktop_Community /></DCArtboard>
          <DCArtboard id="dt-states"     label="D10 · מצבי קצה"            width={1200} height={700} data-screen-label="D10 · States"><window.Desktop_States /></DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 5 · Asset library                                              */}
        {/* ============================================================ */}
        <DCSection id="library" title="00 · ספריית נכסים"
          subtitle="אייקוני SVG + פרומפטים ל-AI לרקעים.">
          <DCArtboard id="lib" label="ספריה" width={920} height={2400} data-screen-label="Library"><window.GJ_Library /></DCArtboard>
        </DCSection>

        {/* ============================================================ */}
        {/* 6 · LOD200 wireframes (reference)                              */}
        {/* ============================================================ */}
        <DCSection id="lod200" title="LOD200 · Wireframes"
          subtitle="Structural greyboxes. נשמרים כ-reference.">

          <DCArtboard id="wf-home"    label="A · Home"           width={390} height={844} data-screen-label="A · Home"><window.WfHome /></DCArtboard>
          <DCArtboard id="wf-cross"   label="F · Cross-link"     width={390} height={844} data-screen-label="F · Cross-link"><window.WfCrossLink /></DCArtboard>
          <DCArtboard id="wf-states"  label="G · States"         width={390} height={844} data-screen-label="G · States"><window.WfStates /></DCArtboard>
          <DCArtboard id="wf-sources" label="H · Sources"        width={390} height={844} data-screen-label="H · Sources"><window.WfSources /></DCArtboard>
        </DCSection>

      </DesignCanvas>
    </React.Fragment>
  );
}

const root = ReactDOM.createRoot(document.body.appendChild(document.createElement('div')));
root.render(<App />);
