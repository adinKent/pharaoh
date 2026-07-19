"""Color tokens for chart image responses.

Single source of truth for every color used in chart generation. Chart code must
reference tokens from the active theme instead of hardcoding hex values, so a
theme switch restyles all charts consistently.

Design rules and per-theme validation live in
.claude/skills/image-response-design/SKILL.md. Any new/changed categorical set
must be validated (dataviz skill's validate_palette.js) against the theme's
surface before shipping.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ChartTheme:
    name: str

    # Canvas
    surface: str  # figure/axes background
    grid: str
    base_mpf_style: str  # mplfinance base style the theme builds on
    ink: str  # default text color; text never wears a series color
    label_box: str  # translucent bbox behind direct labels (最高價/最低價)

    # Header stat hierarchy by lightness (not hue): muted label + bright value, so the
    # top-right turnover stays quiet and the price/change keeps visual priority.
    stat_label: str  # secondary/muted (成交, 總量)
    stat_value: str  # primary/bright (the numbers)
    stat_accent: str  # the 成交 row (label+number+unit) — a distinct accent, not the hierarchy pair

    # Polarity — Taiwan market convention: red = up (漲), green = down (跌).
    # This pair is CVD-marginal; only legal with secondary encoding (reference
    # line / sign / label). Never encode a *new* distinction with up/down alone.
    up: str
    down: str
    flat: str  # neutral midpoint: flat segments, reference lines; not a series color

    # Intraday (P command) single-color price line / volume bars
    intraday_mark: str

    # Categorical overlays — fixed slots, never cycled. A new overlay gets a new
    # token; it never shifts existing assignments.
    ma5: str
    ma20: str
    ma60: str


DARK_THEME = ChartTheme(
    name="dark",
    surface="#0b1b3b",
    grid="#1f2f57",
    base_mpf_style="nightclouds",
    ink="white",
    label_box="#01050A54",
    stat_label="#8B95A9",
    stat_value="#E6EAF2",
    stat_accent="#6FA8E8",  # contrast 6.84:1 on #0b1b3b
    up="red",
    down="green",
    flat="#8e8989",
    intraday_mark="#8fb3ff",
    # Known CVD gap: ma20↔ma60 ΔE 2.3 (deutan). Validated replacement if/when a
    # restyle is approved: ma5 #ffc94d, ma20 #4db8ff, ma60 #f97fc0 (ΔE ≈ 20).
    ma5="#fbe08a",
    ma20="#9dddf8",
    ma60="#dcc3f3",
)

LIGHT_THEME = ChartTheme(
    name="light",
    surface="#ffffff",
    grid="#e4e8f0",
    base_mpf_style="default",
    ink="#1c2333",
    label_box="#FFFFFFC0",
    # Light surface inverts the hierarchy: muted gray label, near-black value.
    stat_label="#6B7280",
    stat_value="#1C2333",
    stat_accent="#3a6fd8",  # same hue family as #6FA8E8, darkened for contrast 4.72:1 on white
    # Validated on #ffffff: CVD ΔE 15.5, contrast >= 3:1
    up="#d32f2f",
    down="#1a7f37",
    flat="#767676",
    intraday_mark="#3a6fd8",
    # Validated on #ffffff: all checks pass (worst CVD ΔE 34.9)
    ma5="#b26a00",
    ma20="#1e6fd4",
    ma60="#c2317f",
)

TRADINGVIEW_THEME = ChartTheme(
    name="tradingview",
    surface="#ffffff",
    grid="#e0e3eb",
    # Not mpf's built-in "tradingview" style: that base moves the y-axis to the
    # right edge, which the shared chart layout clips. The TV look comes from
    # the tokens below instead.
    base_mpf_style="default",
    ink="#131722",
    label_box="#FFFFFFC0",
    stat_label="#6B7280",
    stat_value="#131722",
    stat_accent="#2962ff",  # same hue family as #6FA8E8, darkened for contrast 4.9:1 on white
    # TradingView brand hues mapped to TW polarity (red = up, teal = down).
    # Validated on #ffffff: red↔teal CVD ΔE 26.0; teal contrast 3.0:1 (WARN) —
    # relieved by the always-present direct labels and signed headline.
    up="#ef5350",
    down="#26a69a",
    flat="#787b86",
    intraday_mark="#2962ff",
    # Validated on #ffffff: all checks pass (worst CVD ΔE 71.1)
    ma5="#e65100",
    ma20="#2962ff",
    ma60="#c2185b",
)

TRADINGVIEW_DARK_THEME = ChartTheme(
    name="tradingview_dark",
    surface="#131722",
    grid="#2a2e39",
    base_mpf_style="nightclouds",
    ink="#d1d4dc",
    label_box="#00000059",
    stat_label="#8B95A9",
    stat_value="#E6EAF2",
    stat_accent="#6FA8E8",  # contrast 7.19:1 on #131722
    # Validated on #131722: red↔teal CVD ΔE 26.0, contrast >= 3:1
    up="#ef5350",
    down="#26a69a",
    flat="#787b86",
    intraday_mark="#2962ff",
    # Validated on #131722: chroma/CVD (ΔE 37.8)/contrast pass; lightness band
    # exceeded upward only (waived for thin lines on a dark surface).
    ma5="#ffa726",
    ma20="#42a5f5",
    ma60="#f06292",
)

_THEMES = {theme.name: theme for theme in (DARK_THEME, LIGHT_THEME, TRADINGVIEW_THEME, TRADINGVIEW_DARK_THEME)}


def get_chart_theme() -> ChartTheme:
    """Return the active theme. Selected via CHART_THEME env var; defaults to tradingview_dark."""
    return _THEMES.get(os.environ.get("CHART_THEME", "tradingview_dark"), TRADINGVIEW_DARK_THEME)
