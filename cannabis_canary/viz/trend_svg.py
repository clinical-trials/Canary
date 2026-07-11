"""Longitudinal THC mg/day trend as a standalone SVG string.

Pure function of (date, mg/day) points; no PHI beyond what the caller passes
(dates + doses only — never names/IDs).
"""
from __future__ import annotations

from datetime import date

_W, _H = 640, 240
_PAD_L, _PAD_R, _PAD_T, _PAD_B = 56, 16, 16, 32


def _header() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_W} {_H}" '
        f'width="{_W}" height="{_H}" role="img" aria-label="THC mg per day over time">'
    )


def trend_svg(points: list[tuple[date, float]]) -> str:
    """Render (date, mg/day) points as a simple line chart SVG."""
    if not points:
        return (
            _header()
            + f'<text x="{_W / 2}" y="{_H / 2}" text-anchor="middle" '
            'font-family="sans-serif" font-size="14" fill="#666">'
            "No dose data recorded yet</text></svg>"
        )

    points = sorted(points)
    xs = [p[0].toordinal() for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_max = max(max(ys), 1.0)
    plot_w = _W - _PAD_L - _PAD_R
    plot_h = _H - _PAD_T - _PAD_B

    def px(x: int) -> float:
        if x_max == x_min:
            return _PAD_L + plot_w / 2
        return _PAD_L + (x - x_min) / (x_max - x_min) * plot_w

    def py(y: float) -> float:
        return _PAD_T + (1 - y / y_max) * plot_h

    parts = [_header()]
    # axes
    parts.append(
        f'<line x1="{_PAD_L}" y1="{_PAD_T}" x2="{_PAD_L}" y2="{_H - _PAD_B}" '
        'stroke="#999" stroke-width="1"/>'
        f'<line x1="{_PAD_L}" y1="{_H - _PAD_B}" x2="{_W - _PAD_R}" y2="{_H - _PAD_B}" '
        'stroke="#999" stroke-width="1"/>'
    )
    # y-axis labels
    parts.append(
        f'<text x="{_PAD_L - 6}" y="{_PAD_T + 4}" text-anchor="end" '
        f'font-family="sans-serif" font-size="11" fill="#444">{y_max:g}</text>'
        f'<text x="{_PAD_L - 6}" y="{_H - _PAD_B}" text-anchor="end" '
        'font-family="sans-serif" font-size="11" fill="#444">0</text>'
        f'<text x="14" y="{_H / 2}" text-anchor="middle" font-family="sans-serif" '
        f'font-size="11" fill="#444" transform="rotate(-90 14 {_H / 2})">mg/day</text>'
    )
    # x-axis date labels (first + last)
    parts.append(
        f'<text x="{_PAD_L}" y="{_H - 10}" font-family="sans-serif" font-size="11" '
        f'fill="#444">{points[0][0].isoformat()}</text>'
    )
    if len(points) > 1:
        parts.append(
            f'<text x="{_W - _PAD_R}" y="{_H - 10}" text-anchor="end" '
            f'font-family="sans-serif" font-size="11" fill="#444">'
            f"{points[-1][0].isoformat()}</text>"
        )
    # data
    if len(points) > 1:
        coords = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(xs, ys))
        parts.append(
            f'<polyline points="{coords}" fill="none" stroke="#c9a11b" stroke-width="2"/>'
        )
    for x, y in zip(xs, ys):
        parts.append(
            f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="3.5" fill="#c9a11b"/>'
        )
    parts.append("</svg>")
    return "".join(parts)
