"""Shared chart-rendering helpers used by both the TW (Fugle) and US/foreign (yfinance)
chart functions: font loading, x-label alignment, the top-right turnover header, and the
save-locally-or-upload-to-S3 output step.

These are market-agnostic; market-specific formatting (TW 億/萬, US K/M/B) lives with each
caller. Design rules for the visuals live in .claude/skills/image-response-design/SKILL.md.
"""

import io
import logging
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, TextArea, VPacker
from matplotlib.transforms import blended_transform_factory

from utils.aws_helper import put_image

logger = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent.parent
FONT_PATH = HERE / "assets" / "fonts" / "NotoSansTC-Regular.ttf"


def get_x_label_align(x, x_max_current):
    if x > x_max_current * 0.9:
        return (x_max_current * 0.99, "right")
    else:
        return (max(x, x_max_current * 0.01), "left")


def load_chart_font_name() -> str:
    """Register the bundled Noto Sans TC font and return its family name."""
    font_name = "Noto Sans TC"
    if FONT_PATH.exists():
        try:
            fm.fontManager.addfont(str(FONT_PATH))
            font_name = fm.FontProperties(fname=FONT_PATH).get_name()
        except Exception as exc:
            logger.warning("Failed to load font %s: %s", FONT_PATH, exc)
    return font_name


def draw_turnover_header(fig, turnover_rows, theme, font_name) -> None:
    """Render the top-right turnover block: label / number / unit columns, right-aligned.

    Each row is (label, number, unit, row_color); row_color overrides the per-column
    default. Lightness hierarchy (muted label, bright value) keeps the header quiet.
    """
    if not turnover_rows:
        return
    top_ax = fig.axes[0]

    def _column(cells, default_color):
        return VPacker(
            children=[TextArea(text, textprops=dict(color=color or default_color, fontsize=12, fontfamily=font_name)) for text, color in cells],
            sep=6,
            pad=0,
            align="right",
        )

    block = HPacker(
        children=[
            _column([(r[0], r[3]) for r in turnover_rows], theme.stat_label),
            _column([(r[1], r[3]) for r in turnover_rows], theme.stat_value),
            # Unit defaults to stat_label (matches its row's label, e.g. 億 = 總量's gray);
            # rows with an explicit accent (成交/張) override this regardless.
            _column([(r[2], r[3]) for r in turnover_rows], theme.stat_label),
        ],
        sep=6,
        pad=0,
        align="top",
    )
    # Anchor x to the price panel's actual right spine (resolved at draw time, so it reflects
    # tight_layout), y=0.97 so the block top aligns with the symbol-name suptitle.
    turnover_transform = blended_transform_factory(top_ax.transAxes, fig.transFigure)
    top_ax.add_artist(
        AnchoredOffsetbox(
            loc="upper right",
            child=block,
            pad=0,
            borderpad=0,
            frameon=False,
            bbox_to_anchor=(1.0, 0.97),
            bbox_transform=turnover_transform,
        )
    )


def save_or_upload_fig(fig, image_name: str, save_to_local_file: bool) -> str:
    """Save the figure locally (dev) or upload to S3 and return a presigned URL (Lambda)."""
    if save_to_local_file:
        output_path = Path(__file__).resolve().parents[2] / image_name
        fig.savefig(str(output_path), format="jpg", facecolor=fig.get_facecolor(), dpi=300)
        return str(output_path)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="jpg", facecolor=fig.get_facecolor(), dpi=300)
    buffer.seek(0)
    return put_image(image_name, buffer.getvalue())
