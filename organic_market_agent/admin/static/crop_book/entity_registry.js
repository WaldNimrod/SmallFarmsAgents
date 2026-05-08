/**
 * ENTITY_REGISTRY — repo-owned static asset
 * Loaded via url_for('static', filename='crop_book/entity_registry.js')
 * Maps entity type + id to display name (he) + entity type label.
 * Version: 1.0.0 (initial — populated from WP002 seed entities)
 */
const ENTITY_REGISTRY = {
  version: "1.0.0",

  // Entity type Hebrew labels
  typeLabels: {
    pest:      "מזיק",
    disease:   "מחלה",
    equip:     "ציוד",
    input:     "תשומה",
    technique: "טכניקה",
    crop:      "גידול",
  },

  // Entity definitions: type → id → { nameHe, nameEn }
  entities: {
    pest: {
      "diamondback-moth":    { nameHe: "עש יהלום",         nameEn: "Diamondback moth" },
      "aphid":               { nameHe: "כנימת עלים",       nameEn: "Aphid" },
      "whitefly":            { nameHe: "זבוב לבן",          nameEn: "Whitefly" },
      "spider-mite":         { nameHe: "קרדית עכביש",      nameEn: "Spider mite" },
      "flea-beetle":         { nameHe: "חיפושית פרעוש",    nameEn: "Flea beetle" },
      "thrips":              { nameHe: "טריפס",             nameEn: "Thrips" },
      "caterpillar":         { nameHe: "זחל",               nameEn: "Caterpillar" },
    },
    disease: {
      "downy-mildew":        { nameHe: "אבקת שפם",          nameEn: "Downy mildew" },
      "powdery-mildew":      { nameHe: "אבקת אמיתית",      nameEn: "Powdery mildew" },
      "botrytis":            { nameHe: "בוטריטיס",          nameEn: "Botrytis" },
      "fusarium":            { nameHe: "פוזריום",            nameEn: "Fusarium" },
      "alternaria":          { nameHe: "אלטרנריה",          nameEn: "Alternaria" },
    },
    equip: {
      "jang-jp1":            { nameHe: "מזרע Jang JP-1",   nameEn: "Jang JP-1 seeder" },
      "paper-pot":           { nameHe: "פפר פוט",           nameEn: "Paper pot transplanter" },
      "broadfork":           { nameHe: "ברודפורק",          nameEn: "Broadfork" },
    },
    input: {
      "compost":             { nameHe: "קומפוסט",           nameEn: "Compost" },
      "fish-emulsion":       { nameHe: "תמצית דגים",        nameEn: "Fish emulsion" },
      "insect-netting":      { nameHe: "רשת חרקים",         nameEn: "Insect netting" },
      "row-cover":           { nameHe: "כיסוי שורה",        nameEn: "Row cover" },
      "drip-irrigation":     { nameHe: "השקיה בטפטוף",     nameEn: "Drip irrigation" },
    },
    technique: {
      "succession-planting": { nameHe: "זריעת רצף",         nameEn: "Succession planting" },
      "transplanting":       { nameHe: "שתילה",              nameEn: "Transplanting" },
      "direct-seeding":      { nameHe: "זריעה ישירה",       nameEn: "Direct seeding" },
      "grafting":            { nameHe: "הרכבה",              nameEn: "Grafting" },
      "pinching":            { nameHe: "קיטום",              nameEn: "Pinching" },
      "soil-blocking":       { nameHe: "בלוק אדמה",         nameEn: "Soil blocking" },
    },
    crop: {
      "arugula":             { nameHe: "ארוגולה",            nameEn: "Arugula" },
      "tomato":              { nameHe: "עגבנייה",            nameEn: "Tomato" },
      "basil":               { nameHe: "בזיל",               nameEn: "Basil" },
      "lettuce":             { nameHe: "חסה",                nameEn: "Lettuce" },
    },
  },

  /**
   * Look up entity display name + type label.
   * @param {string} etype - entity type (pest, disease, etc.)
   * @param {string} eid   - entity id (slug)
   * @returns {{ nameHe: string, typeLabel: string } | null}
   */
  lookup(etype, eid) {
    const typeEntities = this.entities[etype];
    if (!typeEntities) return null;
    const entity = typeEntities[eid];
    if (!entity) return null;
    return {
      nameHe: entity.nameHe,
      typeLabel: this.typeLabels[etype] || etype,
    };
  },
};
