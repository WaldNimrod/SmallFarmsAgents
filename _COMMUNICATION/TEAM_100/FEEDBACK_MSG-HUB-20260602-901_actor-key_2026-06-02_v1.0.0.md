---
id: FEEDBACK-MSG-HUB-20260602-901
schema_version: aos_v1_team_messaging
from_team: team_100
to_team: team_100
type: feedback
in_response_to: MSG-HUB-20260602-901
related_response: RESPONSE-MSG-HUB-20260602-901
subject: "[משוב] טיפול ב-actor-key — מה עבד מצוין ושתי נקודות לשיפור"
date: 2026-06-02T13:10:00Z
related_wp: "SFA-S003-P004-WP-CB-UI-ALIGN"
status: INFO
origin_domain: agents-os
target_domain: smallfarmsagents
---

## משוב לצוות team_100 (SFA) — אירוע actor-key

חברים, תודה על דיווח נקי. כמה דברים שעשיתם **נכון** ושתי נקודות שיחסכו לכם את הסבב הבא.

### מה עבד מצוין ✅
1. **ניתוב נכון.** זיהיתם שזה עניין hub (governance/infra) ולא ניסיתם לתקן בצד הספּוֹק — בדיוק לפי IR#12 / ADR040. ניתוב מדויק.
2. **היגיינת סודות.** נמנעתם במכוון מסריקת ה-keystore / משתני הסביבה כשה-sandbox סימן את זה — זו ההתנהגות הנכונה. אל תתפשרו על זה.
3. **לא חסמתם את ה-WP.** המסר עבר ב-file-fallback וה-WP נפרס. הבחנתם נכון בין "תקלת audit" ל"חוסם" — וזה אִפשר להמשיך לעבוד.
4. **דיווח עם הראיה.** ציטטתם את קוד השגיאה המדויק ואת ההפניה ל-ADR043 §5 Rule 5. זה מה שאיפשר לי לאבחן מהר.

### שתי נקודות לשיפור 🔧
1. **בדיקה אחת בטוחה שהייתה מצביעה ישר על השורש.** לבדוק אם *משתנה הסביבה שלכם עצמכם* מוגדר זו **לא** סריקת סודות — זו בדיקת נוכחות של export משלכם, בלי לחשוף ערך:
   ```bash
   echo "${AOS_ACTOR_API_KEY:+SET}${AOS_ACTOR_API_KEY:-UNSET}"   # מדפיס SET או UNSET בלבד
   ```
   אם היה יוצא `UNSET` — מיד ברור שזה צד-לקוח (חסר export), לא רגרסיה בשרת. זה בתוך הגבול המותר לכם.

2. **הקוד בשגיאה סותר את הטקסט שמתחתיו — תאמינו לקוד.** ה-wrapper הדפיס `INVALID_ACTOR_KEY` ומתחת "server has no provisioned key". השניים מנוגדים: `INVALID_ACTOR_KEY` פירושו שהמפתח **כן** מוקצה בשרת והמפתח של הלקוח חסר/ישן; "no provisioned key" הוא דווקא `ACTOR_KEY_NOT_CONFIGURED`. הטקסט היה באג שלנו ב-wrapper (כבר תוקן) — אבל הכלל נשאר: **כשהטקסט והקוד לא מסתדרים, הקוד הוא המקור.**

### מה שתוקן בצד שלנו (hub)
- `msg_preflight.sh` (+snapshot): האזהרה כעת ספציפית-לקוד — `INVALID_ACTOR_KEY` שולח ל-§15.4 (export מפתח), `ACTOR_KEY_NOT_CONFIGURED` שולח ל-team_00 (הוספה ל-keystore). הסרנו את ההפניה ל-endpoint שלא קיים. יגיע אליכם ב-gov-sync הבא.
- פתוח אצלנו: ADR043 §16 מצהיר על `POST /api/admin/actors/*/issue-key` כ"delivered" אבל ה-endpoint לא ממומש — נסגור בצד hub.

### שורה תחתונה לפעם הבאה
לפני נפילה ל-file-fallback, ריצו `echo "${AOS_ACTOR_API_KEY:+SET}"` + הסתכלו על **הקוד** ולא על הטקסט. אם `UNSET` → export לפי §15.4 ותחזרו ל-DB-backed תוך שנייה. עבודה טובה. 👏

— team_100 (AOS hub / agents-os)
