# Decisions for Nimrod — SFA Visual System Phase 2

team_100 recommendations are pre-filled. "Default" applies if Nimrod does not decide.

| ID | Topic | Options | Recommendation | Impact | Urgency | Default |
|----|-------|---------|----------------|--------|---------|---------|
| D01 | Scope of visual system | A. only current 12 assets · B. 12 + icon set · C. full system (assets, icons, backgrounds, textures, empty states, future module visuals) | **C — full system, produced in phases** | Defines whole program size | Medium | C (phased) |
| D02 | Style anchor priority | A. current SFA draft prompts · B. nimrod.bio illustrations primary · C. new hybrid style | **B — nimrod.bio is primary anchor; SFA prompts are technical/product context only** | Determines the look | High | B |
| D03 | Reference collection size before generation | A. only the 3 existing refs · B. add 5–10 more existing nimrod.bio pieces · C. 15–30 refs + full style board | **B minimum; C if materials exist** (note: only ~4 genuine pieces found — may need new commissions) | Style fidelity | High | B (use the 4 found) |
| D04 | First production step | A. OG first · B. all 12 at once · C. calibration set first | **C — calibration set first** | De-risks the whole batch | High | C |
| D05 | Calibration set size | A. 4 · B. 6 · C. 8 | **6 minimum; 8 if including icon + community scene** | Approval confidence | Medium | 6 |
| D06 | Image generator workflow | A. ChatGPT only · B. Midjourney/external only · C. hybrid (ChatGPT for prompt design+review, best generator for finals) | **C — hybrid** (unless you want all-in-ChatGPT) | Output quality | Medium | C |
| D07 | Final file production | A. manual export only · B. fully scripted · C. hybrid (visual approve PNG → scripted resize/compress) | **C — hybrid** (sips/cwebp recipe in C3) | Throughput + quality | Low | C |
| D08 | Asset naming + folder strategy | A. keep current 12 filenames only · B. structured asset library · C. versioned folders (approved/candidates/rejected) | **C — versioned workflow** | Avoids confusion at scale | Medium | C |
| D09 | Icon style | A. full-color watercolor icons · B. line-art + minimal wash · C. flat vector | **B — line-art + minimal wash** (matches existing line basket + UI usability) | Icon set look | Medium | B |
| D10 | Level of literalness | A. literal per module · B. mix literal objects + abstract textures · C. mostly abstract | **B — mix** | Product-system balance | Medium | B |

## Cross-cutting note
D02 + D03 are the highest-leverage. Because the genuine nimrod.bio reference base
is thin (~4 pieces), the realistic path is: anchor hard on those 4 (D02=B), run a
small calibration set (D04=C, D05=6) to lock the style, optionally commission a few
more reference pieces if calibration reveals gaps (D03).
