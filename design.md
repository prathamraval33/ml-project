# DESIGN.md
## CineForecast — Visual Design System
### Adapted from the "Dala" style reference for a data-dense analytics dashboard

**Theme:** dark
**Signature line:** *a constellation on black velvet, made legible for data.*

---

## 0. How This File Should Be Used

This is the single source of truth for every visual decision in the CineForecast frontend (`frontend/src/`). Any component built for `Overview.jsx`, `FeatureImportance.jsx`, `MovieExplorer.jsx`, `WhatIfSimulator.jsx`, or `Trends.jsx` must pull its colors, type, spacing, and radii from the tokens in Section 2 — never a hardcoded hex value or pixel size inline.

**Adaptation note (read before building anything):** the source reference (Dala) is a marketing/landing-page brand — spacious, one-or-two-elements-per-viewport, zero borders, zero data tables. CineForecast is a **data dashboard** — it must show scatter plots, SHAP bar charts, a filterable movie table, sliders, and stat cards, often several per viewport. Section 5 defines how the original "float on black, no containers" philosophy is deliberately extended — not abandoned — to support real information density. This is a stated, intentional adaptation, not a deviation from the brief.

---

## 1. Brand Identity Summary

CineForecast keeps Dala's void-and-violet dark-stage aesthetic: pure black canvas, one saturated violet accent for interactive/primary elements, amber for emphasis and positive signals, monolithic weightless typography that uses scale — not weight or boxes — to carry hierarchy. Where Dala's brain-shaped particle constellation was pure brand décor, CineForecast repurposes the same particle-field visual language as **literal data visualization**: the constellation motif becomes the ambient texture behind hero/empty states, while real charts (Recharts) carry the actual analytics in the same violet/amber/teal palette.

---

## 2. Design Tokens

### 2.1 Colors

| Name | Value | Token | Role in CineForecast |
|---|---|---|---|
| Void | `#000000` | `--color-void` | Page canvas, every section/page background — no gray panels, ever |
| Bone White | `#ffffff` | `--color-bone-white` | Headlines, primary body text, primary numeric values in stat cards |
| Ash Gray | `#9a9a9a` | `--color-ash-gray` | Muted nav text, table row secondary text, axis labels, inactive tab labels |
| Silver Mist | `#bdbdbd` | `--color-silver-mist` | Tertiary text — table captions, chart footnotes, helper text under form inputs |
| Electric Iris | `#8052ff` | `--color-electric-iris` | Primary buttons, active nav/tab state, primary data series (predicted revenue line), slider track fill, selected table row indicator |
| Saffron Spark | `#ffb829` | `--color-saffron-spark` | Positive deltas in the What-If Simulator, highlighted SHAP-positive bars, "Hit"/"Blockbuster" success-tier badges, section eyebrow labels |
| Deep Verdant | `#15846e` | `--color-deep-verdant` | Secondary data series (actual revenue line, to contrast against predicted violet), positive-ROI accents |

**Dashboard-only extensions** (needed because a five-page analytics app requires more semantic color than a landing page — kept inside the same chromatic family used by the particle field so nothing feels bolted on):

| Name | Value | Token | Role |
|---|---|---|---|
| Signal Rose | `#ff5c7a` | `--color-signal-rose` | Negative SHAP contribution bars, negative What-If deltas, "Flop" success-tier badge, error states |
| Line Hairline | `#1f1f1f` | `--color-line-hairline` | The **only** border-like value permitted anywhere in the UI — 1px table row dividers and chart baseline gridlines. Never used as a card border. |

### 2.2 Typography

Single typeface across all UI: **PPNeueMontreal** (fallback: Inter). Same governing rule as Dala — hierarchy comes from scale and tracking, not weight swaps or boxes.

| Role | Size | Weight | Line Height | Letter Spacing | Token |
|---|---|---|---|---|---|
| caption | 12px | 400 | 1.5 | — | `--text-caption` |
| nav-label | 14px | 600, uppercase* | 1.2 | 0.025em | `--text-nav-label` |
| body | 18px | 200 | 1.5 | — | `--text-body` |
| body-dense (table cells, form labels) | 15px | 400 | 1.4 | — | `--text-body-dense` |
| stat-value (dashboard KPI numbers) | 48px | 400 | 1.0 | -1.68px | `--text-stat-value` |
| heading-2xs | 24px | 400 | 1.25 | -0.48px | `--text-heading-2xs` |
| heading-xs | 27px | 400 | 1.0 | — | `--text-heading-xs` |
| subheading | 36px | 400 | 1.2 | — | `--text-subheading` |
| heading-sm | 42px | 400 | 1.2 | -1.68px | `--text-heading-sm` |
| heading | 48px | 400 | 1.1 | -1.68px | `--text-heading` |
| heading-lg | 78px | 400 | 1.1 | -3.12px | `--text-heading-lg` |

*\*Nav-label uppercase is inherited from Dala's own nav-bar convention and is scoped ONLY to the top nav and small pill badges — per the frontend-design guardrail against generic all-caps labeling, do not apply uppercase to section eyebrows, table headers, or chart legends. Table column headers use `body-dense`, sentence case, `--color-ash-gray`.*

**New role — `stat-value` (48px)** is introduced specifically for KPI numbers on `Overview.jsx` (e.g. "$412M predicted", "0.86 R²") — it borrows the `heading` size/tracking but is reserved exclusively for numeric metrics, never for prose headings, so a user's eye learns to scan for it as "the number that matters."

### 2.3 Spacing & Shape

**Base unit:** 6px (unchanged from Dala)

| Name | Value | Token |
|---|---|---|
| 6 | 6px | `--spacing-6` |
| 12 | 12px | `--spacing-12` |
| 18 | 18px | `--spacing-18` |
| 24 | 24px | `--spacing-24` |
| 30 | 30px | `--spacing-30` |
| 36 | 36px | `--spacing-36` |
| 60 | 60px | `--spacing-60` |
| 96 | 96px | `--spacing-96` |

*(Dala's 120px section-gap is dropped as a default for dashboard pages — 96px is the dashboard's max section gap; a data page cannot afford landing-page-scale whitespace between every panel or key metrics fall below the fold. Marketing-style pages, if any exist — e.g. a public project README/landing page — keep the full 60–120px scale.)*

**Border radius:**

| Element | Value |
|---|---|
| buttons | 24px (pill, unchanged) |
| tags / success-tier badges | 9999px (unchanged) |
| stat cards, chart panels | 16px *(reduced from Dala's 24px — see Section 5 rationale)* |
| table container | 16px |
| slider thumb | 9999px (circular) |
| input fields | 12px |

**Layout:**
- Dashboard shell max-width: 1440px (wider than Dala's 1280px marketing max-width, to fit chart+table layouts)
- Sidebar width: 240px, fixed, `--color-void` background, no border — separated from content only by a `--color-line-hairline` 1px vertical rule
- Content padding: 36px desktop, 18px mobile
- Panel-to-panel gap: 24px (dense grids), 36px (between major sections)

---

## 3. Iconography & Motion

- **Icons:** Lucide React, 18–20px, `--color-ash-gray` default / `--color-bone-white` on hover-active / `--color-electric-iris` when representing the active/selected state
- **Motion:** reserved for the moments defined in the frontend-design principle of "answers a person's action" — chart tooltips fading in on hover, the What-If Simulator's predicted-revenue number ticking to its new value when a slider moves, a table row's SHAP waterfall panel expanding on click. No scroll-triggered fade-ins, no hover-lift on every card — those are the generic tells this system explicitly avoids.
- **Particle field:** used only in two places — the empty/loading state of `MovieExplorer.jsx` (a sparse ambient version signals "searching the dataset") and as a static, low-density background texture behind the `Overview.jsx` hero stat row. Never behind dense chart/table regions, where it would hurt legibility.

---

## 4. Components

### 4.1 Inherited from Dala (used as-is)

**Primary Action Button** — filled `--color-electric-iris` pill, white text, 14px/600/uppercase, 22.5px radius, 14.4px × 16px padding. Used for: "Run Prediction," "Apply Filters," "Export." Only one per view, per Dala's own rule.

**Ghost Text Button** — no background/border, `--color-bone-white` or `--color-ash-gray` text. Used for: "Reset," "Clear filters," pagination "Next/Prev."

**Navigation Bar** — transparent on `--color-void`, logo left, page links center (`Overview`, `Explorer`, `What-If`, `Trends`), no border, no backdrop blur.

**Carousel Navigation Dot** — reused verbatim for the What-If Simulator's scenario-history stepper (if multiple what-if runs are compared side by side).

### 4.2 New — Dashboard-Specific Components (not present in the source reference; required for CineForecast's actual screens)

**Stat Card** (`Overview.jsx` KPI row)
No border, no shadow, no fill — the Dala "float on black" rule is preserved even here. Structure: small uppercase label (14px, `--color-ash-gray`) above a `stat-value` (48px, `--color-bone-white`), with an optional delta chip below in `--color-saffron-spark` (positive) or `--color-signal-rose` (negative). Cards sit in a 3–4 column grid separated by whitespace only, exactly like Dala's Team Member Card pattern — no card chrome introduced.

**Chart Panel** (wraps every Recharts component)
16px-radius container, `--color-void` background (i.e., visually invisible against the page — the radius only matters for the subtle `--color-line-hairline` outline used at 40% opacity, the ONE permitted exception to "no borders," because chart plot areas need a legible boundary against an all-black canvas to be scannable). Panel title in `heading-xs` (27px), no eyebrow label above it — the title IS the label.

**Data Table** (`MovieExplorer.jsx`)
No cell borders, no zebra striping (would violate the flat-black rule). Rows are separated by a single 1px `--color-line-hairline` bottom border only. Column headers: `body-dense`, sentence case, `--color-ash-gray`, sticky on scroll. Row hover state: text brightens from `--color-ash-gray`/`--color-bone-white` mix to full `--color-bone-white`, no background fill (preserves "no surfaces" rule even on hover). Selected row: a 3px `--color-electric-iris` left-edge accent bar, nothing else changes.

**Success-Tier Badge** (Flop / Break-even / Hit / Blockbuster)
9999px pill radius (reuses Dala's "tags" token), 12px uppercase text, transparent fill, 1px `--color-line-hairline`-weight colored outline matching the tier: `--color-signal-rose` (Flop), `--color-ash-gray` (Break-even), `--color-saffron-spark` (Hit), `--color-electric-iris` (Blockbuster). This is the one place a colored border is intentionally introduced, because a badge's entire job is to be a bounded, at-a-glance token — an unbounded pill would just be colored text.

**SHAP Waterfall Bar**
Horizontal bars growing left (negative, `--color-signal-rose`) or right (positive, `--color-saffron-spark`) from a center zero-line rendered in `--color-line-hairline`. Bar labels in `body-dense`, `--color-silver-mist`. No axis box, no gridlines beyond the single center line — consistent with Dala's "structural devices encode information, don't decorate" principle: the center line IS the zero-revenue-impact reference, so it earns its place.

**What-If Slider**
Track: 4px height, `--color-line-hairline` base with `--color-electric-iris` fill up to the thumb position. Thumb: 16px circle, `--color-bone-white` fill, `--color-electric-iris` 2px ring on focus/drag (keyboard-focus-visible, per accessibility floor). Current value displayed as a `body` (18px) number directly above the thumb, not in a separate label — reduces chrome.

**Filter Chip / Genre Tag**
9999px pill, `--color-ash-gray` text on transparent background by default; selected state flips to `--color-electric-iris` text with a 1px `--color-electric-iris` outline. Used in `MovieExplorer.jsx` genre/studio-tier filters and `Trends.jsx` breakdowns.

**Input Field** (What-If Simulator numeric/dropdown inputs)
12px radius, transparent background, single `--color-line-hairline` bottom border only (not a full box) — echoes the table row pattern so forms and tables feel like the same visual family. Label above in `body-dense`, `--color-ash-gray`; focus state turns the bottom border `--color-electric-iris`.

**Tab Switcher** (e.g. "Pre-release model" vs "Early-signal model" toggle on `FeatureImportance.jsx`, surfacing the leakage-ablation comparison from the ML spec)
Ghost-text style, active tab in `--color-bone-white` with a 2px `--color-electric-iris` underline; inactive tabs in `--color-ash-gray`, no underline. No pill/box wrapping the tab group — consistent with Dala's underline-over-container link convention.

---

## 5. Why the Adaptation Was Made This Way (design rationale, for future contributors)

1. **Radius reduced 24px → 16px on data containers only** (buttons/badges keep 24px/pill): at dashboard information density, a 24px radius on a chart panel or table reads as "marketing card," fighting the content instead of housing it. 16px keeps the same soft, non-clinical character without that association. This is a deliberate, scoped exception — not a wholesale departure from the token.
2. **One new border value introduced** (`--color-line-hairline`, 1px, low-opacity): Dala's zero-border rule works because a landing page has 1–2 elements per screen and whitespace alone can separate them. A table with 50 rows or a chart with axes cannot rely on whitespace alone without becoming illegible. The hairline is deliberately near-invisible (dark gray, not white or violet) so it reads as *structure*, not as the boxed-card aesthetic Dala explicitly rejects.
3. **Section gap ceiling lowered from 120px to 96px** for the same density reason — a dashboard user needs more information per scroll than a manifesto page.
4. **The particle constellation was re-scoped from "hero art everywhere" to two specific, sparse uses** (empty states, hero backdrop) so that it never competes with the real Recharts data visualizations, which now carry the job the constellation did on the marketing site: being the thing the user actually looks at.

Everything else — the void canvas, the single violet action color, the weight-400-headlines/weight-200-body split, the pill buttons, the no-shadow/no-elevation rule, PPNeueMontreal at massive tracking-negative display sizes — is carried over unchanged, because none of it conflicts with a dashboard's functional needs.

---

## 6. Do's and Don'ts (CineForecast-specific, in addition to all inherited Dala rules)

### Do
- Use `--color-line-hairline` for table row separators and chart baselines — this is the only approved border-like value in the entire system
- Reserve `stat-value` (48px) exclusively for KPI numbers on `Overview.jsx` — never reuse this size for a section heading
- Use `--color-saffron-spark` and `--color-signal-rose` consistently as the positive/negative semantic pair across SHAP bars, What-If deltas, and success-tier badges — a user should learn this color language once and reuse it everywhere
- Keep chart panels background-transparent (`--color-void`) — only the 16px-radius hairline outline distinguishes a panel from the page

### Don't
- Do not add drop shadows or gradient fills to stat cards or chart panels to "lift" them off the black background — legibility comes from the hairline and whitespace, never elevation
- Do not zebra-stripe table rows — this is the single most common "SaaS-card-kit" tell the frontend-design guardrails call out, and it directly conflicts with Dala's flat-black surface rule
- Do not introduce a second accent color beyond violet/amber/rose for semantic meaning — three is the ceiling (primary action, positive, negative)
- Do not let the particle constellation visual appear behind or near an active data table or chart grid — reserved for empty/hero states only, per Section 5.4

---

## 7. Quick Start — CSS Custom Properties

```css
:root {
  /* Colors — inherited */
  --color-void: #000000;
  --color-bone-white: #ffffff;
  --color-ash-gray: #9a9a9a;
  --color-silver-mist: #bdbdbd;
  --color-electric-iris: #8052ff;
  --color-saffron-spark: #ffb829;
  --color-deep-verdant: #15846e;

  /* Colors — dashboard extensions */
  --color-signal-rose: #ff5c7a;
  --color-line-hairline: #1f1f1f;

  /* Typography */
  --font-ppneuemontreal: 'PPNeueMontreal', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  --text-caption: 12px;
  --text-nav-label: 14px;
  --tracking-nav-label: 0.35px;
  --text-body: 18px;          /* weight 200 */
  --text-body-dense: 15px;    /* weight 400 — tables, form labels */
  --text-stat-value: 48px;    /* weight 400, tracking -1.68px — KPI numbers only */
  --text-heading-2xs: 24px;
  --text-heading-xs: 27px;
  --text-subheading: 36px;
  --text-heading-sm: 42px;
  --text-heading: 48px;
  --text-heading-lg: 78px;

  --font-weight-extralight: 200;
  --font-weight-regular: 400;
  --font-weight-semibold: 600;

  /* Spacing */
  --spacing-6: 6px;
  --spacing-12: 12px;
  --spacing-18: 18px;
  --spacing-24: 24px;
  --spacing-30: 30px;
  --spacing-36: 36px;
  --spacing-60: 60px;
  --spacing-96: 96px;

  /* Radius */
  --radius-buttons: 24px;
  --radius-pill: 9999px;
  --radius-panel: 16px;        /* dashboard-specific, reduced from Dala's 24px */
  --radius-input: 12px;

  /* Layout */
  --dashboard-max-width: 1440px;
  --sidebar-width: 240px;
}
```

### Tailwind v4

```css
@theme {
  --color-void: #000000;
  --color-bone-white: #ffffff;
  --color-ash-gray: #9a9a9a;
  --color-silver-mist: #bdbdbd;
  --color-electric-iris: #8052ff;
  --color-saffron-spark: #ffb829;
  --color-deep-verdant: #15846e;
  --color-signal-rose: #ff5c7a;
  --color-line-hairline: #1f1f1f;

  --font-ppneuemontreal: 'PPNeueMontreal', ui-sans-serif, system-ui, sans-serif;

  --radius-buttons: 24px;
  --radius-pill: 9999px;
  --radius-panel: 16px;
  --radius-input: 12px;
}
```

---

## 8. Page-by-Page Application Notes

| Page | Key components used | Notes |
|---|---|---|
| `Overview.jsx` | Stat Card row, Chart Panel (predicted-vs-actual scatter), particle hero backdrop | Only page permitted the ambient particle-field texture at any real presence |
| `FeatureImportance.jsx` | Chart Panel (SHAP summary bar), Tab Switcher (pre-release vs early-signal model) | Tab switcher surfaces the leakage-ablation comparison — a functional, not decorative, use of tabs |
| `MovieExplorer.jsx` | Data Table, Filter Chips, Success-Tier Badge, SHAP Waterfall Bar (in row-expand panel) | Densest page — hairline discipline matters most here |
| `WhatIfSimulator.jsx` | What-If Slider, Input Field, Primary Action Button, Chart Panel (live-updating result) | The only page with a form — keep the single-primary-button rule strict |
| `Trends.jsx` | Chart Panel ×multiple, Filter Chips | Grid of chart panels at 24px gap, per Section 2.3 dense-grid spacing |

**END OF DESIGN.md**
