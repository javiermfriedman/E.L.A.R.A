# E.L.A.R.A — Frontend

> **Enhanced Laughter & Absurdity Response Agent**  
> *Classified Prank Operations Console — Eyes Only*

---

## What Is This?

ELARA is a multi-user AI-powered prank call command system. The frontend is built to feel like a classified military ops terminal — think retro CRT monitor meets hacker command center, but make it funny.

The design language is **retro sci-fi terminal**: neon green on near-black, monospace fonts, scanline overlays, glitch effects, and glow animations throughout. Every interaction should feel like you're launching a covert operation — because you are.

---

## Tech Stack

- **Vite + React** (JavaScript)
- **Plain CSS** with CSS custom properties
- **JWT auth** via FastAPI backend
- **localStorage** for token persistence

---

## What's Been Built

### Foundation
- Global CSS system — theme tokens, animations, grain/scanline effects
- CSS variables for all colors, glows, spacing, and transitions
- Keyframe library — flicker, glitch, glow pulse, fade, scanlines

### Auth Flow
- **Login / Register page** — single page with tab toggle
  - Glitchy animated E.L.A.R.A title
  - Form validation + real API calls
  - `[ ACCESS ]` to login, `[ ENLIST ]` to register
- **ACCESS GRANTED screen** — full-screen glitch animation on successful login
  - Scanning lines, progress bar, credential readout
  - Auto-transitions to dashboard after ~3 seconds
- **Persistent session** — token stored in localStorage, skips login on refresh

### Services & State
- `src/services/api.js` — central API handler with token management
- `src/context/ElaraContext.jsx` — global auth state (token, user, logout)

---

## Proposed Architecture
```
src/
├── assets/                   # Fonts, icons
├── components/
│   ├── ui/
│   │   ├── Button.jsx
│   │   ├── Modal.jsx
│   │   ├── Dropdown.jsx
│   │   ├── StatusBadge.jsx
│   │   └── PanelWrapper.jsx  # Glowing terminal panel container
│   └── layout/
│       ├── TopBar.jsx
│       ├── Dashboard.jsx     # Main grid layout controller
│       ├── Scanlines.jsx     # CRT overlay
│       ├── AccessGranted.jsx # ✅ Done
│       └── AccessGranted.css # ✅ Done
├── pages/
│   └── Login/
│       ├── Login.jsx         # ✅ Done
│       └── Login.css         # ✅ Done
├── panels/                   # Each dashboard panel
│   ├── InitiateCall/
│   ├── Contacts/
│   ├── Agents/
│   ├── CallRecords/
│   ├── SystemStatus/
│   └── SignalMonitor/
├── context/
│   └── ElaraContext.jsx      # ✅ Done
├── hooks/
│   ├── useClock.js
│   └── useCallState.js
├── data/
│   ├── mockContacts.js
│   ├── mockAgents.js
│   └── mockCallRecords.js
├── services/
│   └── api.js                # ✅ Done
└── styles/
    ├── global.css             # ✅ Done
    ├── theme.css              # ✅ Done
    └── animations.css         # ✅ Done
```

---

## What's Next

| Priority | Task |
|----------|------|
| 🔴 High | `TopBar` — version, title, clock, system status |
| 🔴 High | `Dashboard` — main grid layout with panel slots |
| 🔴 High | `PanelWrapper` — reusable glowing panel shell |
| 🟡 Med  | `InitiateCall` panel — hero panel, dropdowns, launch button |
| 🟡 Med  | `Contacts` panel — list, status badges, click to select |
| 🟡 Med  | `Agents` panel — agent cards with persona previews |
| 🟡 Med  | `CallRecords` panel — call history with outcome tags |
| 🟢 Low  | `SystemStatus` panel — fake diagnostics display |
| 🟢 Low  | `SignalMonitor` panel — animated waveform |
| 🟢 Low  | `useClock` hook, `Scanlines` overlay component |
| ⚪ Later | Wire all panels to real API endpoints |
| ⚪ Later | Active call state, recording playback modal |