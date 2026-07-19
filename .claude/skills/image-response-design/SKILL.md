---
name: image-response-design
description: Design guideline for chart image responses (P/K commands, mplfinance charts in src/quote). Use when creating a new chart type, changing chart colors/themes/layout/labels, or reviewing chart-generation code.
---

# Image Response Design Guideline

Charts are rendered server-side (mplfinance/matplotlib), saved as JPG, uploaded to S3 via
`utils/aws_helper.py::put_image`, and returned as a bare presigned-URL string — `app.py`
detects the URL (`is_s3_presigned_url`) and sends a LINE ImageMessage. Never wrap the URL
in other text, or it degrades to a text reply.

## Color tokens (the only way chart code gets a color)

`src/quote/chart_theme.py` is the single source of truth. Chart code **never hardcodes a
hex or named color** — it calls `get_chart_theme()` and reads tokens. The active theme is
selected by the `CHART_THEME` env var. A new color need = a new
token added to *every* theme and validated, not an inline literal.

| Token | Job |
|---|---|
| `surface` | figure/axes background |
| `grid` | gridlines, legend frame |
| `base_mpf_style` | mpf base style (avoid mpf's built-in `tradingview`: it moves the y-axis to the right edge, which the shared layout clips) |
| `ink` | all text (labels, legend) |
| `label_box` | translucent bbox behind direct labels |
| `up` / `down` / `flat` | polarity (see below) |
| `intraday_mark` | P-chart price line + volume |
| `ma5` / `ma20` / `ma60` | categorical MA slots |

Registered themes (values + per-theme validation notes live in `chart_theme.py`):
`tradingview_dark` (default; TV hues on `#131722`), `tradingview` (TV brand hues on white),
`dark` (the pre-2026-07 production look), `light`.

Theme discipline: a theme is **selected, not flipped** — each theme's values are their own
validated choices against that theme's surface, never an automatic inversion of another
theme. Text wears `ink`, never a series color (one exception: the headline price in the
title, which encodes polarity via `up`/`down`/`flat`).

## Validation (compute it, don't eyeball it)

Any new or changed categorical set, per theme: load the `dataviz` skill and run
`scripts/validate_palette.js "<hex,hex,…>" --mode <dark|light> --surface "<theme surface>"`.

- Hard gates: chroma floor, CVD separation, contrast vs surface.
- The lightness-band check may be waived *upward only* for thin lines on the dark surface.
- `flat` is a neutral midpoint, not a series color — its chroma "failure" is by design.
- Known debt: the **dark** MA triple fails CVD (ma20↔ma60 ΔE 2.3 deutan). Validated
  replacement, pending approval to restyle: `#ffc94d/#4db8ff/#f97fc0`. The light triple
  fully passes (ΔE 34.9). Mitigation until then: the MA legend (identity never color-alone).

## Polarity: Taiwan market convention (non-negotiable)

**`up` = red family (漲), `down` = green/teal family (跌), `flat` = neutral reference.**
Never flip to the Western convention, in any theme — even themes borrowed from Western
products keep TW polarity with the source's hues (e.g. `tradingview` maps TV's red `#ef5350`
to *up* and teal `#26a69a` to *down*). Red/green is CVD-marginal
(dark ΔE ≈ 10, light ΔE ≈ 15.5, TV red/teal ΔE 26), acceptable **only with secondary encoding** — which the
charts have: the `flat` previous-close reference line makes *position above/below* carry
the same information, and the headline shows a signed number with ▲/▼. Keep that
invariant: any new use of `up`/`down` must be redundant with position, a sign, or a label;
never encode a *new* distinction by polarity color alone.

## Categorical lines (MA lines and any future multi-series overlay)

- **Fixed slots, never cycled**: `ma5`/`ma20`/`ma60`. A new overlay gets a new token; it
  never shifts existing assignments (color follows the entity).
- ≥ 2 overlaid series ⇒ legend required (the K chart passes 日線/月線/季線 with current
  values into `ax.legend()`, styled with `surface`/`grid`/`ink`); identity never color-alone.

## Marks & labels

- Thin marks: data lines 1–1.2px; reference lines 0.5px. MA lines render *below* candles
  (line zorder < collection zorder).
- Selective direct labels only — 最高價/最低價 get labels (10pt, `ink` on `label_box`);
  never label every point. Use `get_x_label_align` to keep labels inside the frame.
- Hide redundant ink: no y-axis title, no volume ylabel, no rotated x-ticks.
- One y-axis per panel. Price + volume = two panels (mpf `volume=True`), never a dual axis.

## Layout & scale

- `tight_layout=True`, `scale_padding={"left": 0.6, "top": 4, "right": 1, "bottom": 0.6}`;
  `suptitle` left-aligned at the panel edge, headline price line under it.
- Intraday (P): x spans the full session 09:00–13:30 even if data starts late; y spans
  limit-down→limit-up (ticker's `limitUpPrice/limitDownPrice`, else ±10%; TPEx/index:
  symmetric bound of 1.5× the max excursion from previous close). This keeps visual slope
  honest — a flat day *looks* flat.
- History (K): y = data min/max + 10% padding; dates as `%Y-%m-%d`.
- Output: JPG, `dpi=300`, `facecolor=fig.get_facecolor()`; filename `{symbol}_…_{unix_ts}.jpg`.

## Checklist for a new chart type or restyle

1. Form follows the data's job (see the `dataviz` skill's choosing-a-form reference) — and
   sometimes the answer is text, not an image.
2. Colors come only from `chart_theme.py` tokens; new tokens defined for **all** themes.
3. Validate changed palettes per theme — don't eyeball CVD safety.
4. Render with `save_to_local_file=True` under each `CHART_THEME` and inspect at phone
   width (label collisions, overflow, legibility). The validator checks color, not layout.
5. Confirm the return contract: presigned URL string only; `None`/error-text on failure —
   chart functions must never raise through to `parse_line_command`.
