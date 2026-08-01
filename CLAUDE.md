# soma — Re-Entry File
*Claude: read this before touching anything.*

---

## What This Is
3D biomarker body heat map — live Apple Watch vitals mapped to glowing body regions

## Re-Entry Phrase
> "Re-entry: soma"

## Current Status
🔨 Active — Phases 1–4 done. 3D body live, glowing by region, driven by a
simulated 12-signal Apple Watch feed, click-to-inspect panel working.

## The Build (phase plan)
- [x] Phase 0 — scaffold (port 5573)
- [x] Phase 1 — rotatable stylized androgynous body (Three.js, capsules/spheres, bloom, orbit)
- [x] Phase 2 — region heat-map glow (green→amber→red severity, problem zones pulse)
- [x] Phase 3 — live simulated biomarker engine (12 Watch signals, /api/biomarkers, random-walk drift)
- [x] Phase 4 — interaction: raycast click → detail panel (markers, values, trend arrows, legend, selection glow)
- [ ] Phase 5 — luxury UI polish (overall score ring, transitions, ambient motion, brand)
- [x] Lab layer (Path B) — 8 simulated blood-panel markers (cortisol, testosterone, CRP, glucose, vit D, TSH, estradiol, LDL) fill gut/pelvis/arms/brain; Watch/Lab/Both toggle, LAB badges, "not Watch data" disclaimer
- [ ] Phase 6 — real HealthKit data path (swap STATE source for exported Watch data; needs iOS companion or Health export — its own project)

## Data model
- 12 markers in `app.py` MARKERS tuple: (key,label,unit,regions,base,optLo,optHi,scale,sd,lo,hi)
- Severity = clamp(max(optLo-v, v-optHi, 0)/scale, 0, 1); region severity = max of its markers
- Real data later: replace the STATE drift in `_step()` with HealthKit values

## Stack
- Python + Flask, port 5573, host 127.0.0.1
- Dark theme, Inter font, CSS variables
- Logo at /static/logo.png

## File Structure
```
soma/
├── app.py
├── templates/index.html
├── static/
├── data/
├── requirements.txt
├── Makefile
├── launch.command
├── .env
└── .env.example
```

## How to Run
```bash
cd ~/soma && make run
```

## GitHub
- Repo: papjamzzz/soma
- Push: `make m="your message" push`

## What's Done
- [x] Project scaffold created

## What's Next
- [ ] Define core functionality
- [ ] Add logo to static/
- [ ] Wire up first route/feature

## Key Technical Decisions
- Binds to 0.0.0.0 (Railway-ready); no real HealthKit data flows yet, all biomarker values are simulated random-walk, so there's nothing sensitive to expose

---
*Last updated: 2026-06-11*
