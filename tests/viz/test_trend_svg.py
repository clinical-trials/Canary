from datetime import date

from cannabis_canary.viz import trend_svg


def test_empty_points_renders_placeholder():
    svg = trend_svg([])
    assert svg.startswith("<svg")
    assert "No dose data" in svg


def test_single_point_renders_circle():
    svg = trend_svg([(date(2026, 1, 1), 100.0)])
    assert "<circle" in svg
    assert "100" in svg


def test_multiple_points_renders_polyline_and_labels():
    points = [
        (date(2026, 1, 1), 50.0),
        (date(2026, 3, 1), 100.0),
        (date(2026, 6, 1), 75.0),
    ]
    svg = trend_svg(points)
    assert "<polyline" in svg
    assert "2026-01-01" in svg and "2026-06-01" in svg
    assert "mg/day" in svg
