# soma — Re-Entry File
*Claude: read this before touching anything.*

---

## What This Is
3D biomarker body heat map — live Apple Watch vitals mapped to glowing body regions

## Re-Entry Phrase
> "Re-entry: soma"

## Current Status
🔨 Just created — ready to build

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
- localhost only (host=127.0.0.1)

---
*Last updated: 2026-06-11*
