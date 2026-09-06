"""Independent verification of delta-wing geometry identities.

Expected values here are computed from independently written formulas, not
by calling into delta_vortex_lift.geometry to generate their own answers.
"""

import math

import pytest

from delta_vortex_lift.geometry import DeltaWingGeometry, representative_geometry


def test_triangular_area_identity():
    c_r, b = 5.0, 4.0
    wing = DeltaWingGeometry(root_chord=c_r, span=b)
    expected_area = 0.5 * b * c_r  # independently written: 0.5 * base * height
    assert wing.area == pytest.approx(expected_area)


def test_aspect_ratio_identity():
    c_r, b = 7.3, 6.1
    wing = DeltaWingGeometry(root_chord=c_r, span=b)
    expected_S = 0.5 * b * c_r
    expected_AR = b * b / expected_S
    assert wing.aspect_ratio == pytest.approx(expected_AR)


def test_sweep_identity():
    c_r, b = 10.0, 4.0
    wing = DeltaWingGeometry(root_chord=c_r, span=b)
    # independently: tan(Lambda) = opposite/adjacent = c_r / (b/2)
    expected_sweep_rad = math.atan(c_r / (b / 2.0))
    assert wing.sweep_LE_rad == pytest.approx(expected_sweep_rad)
    assert wing.sweep_LE_deg == pytest.approx(math.degrees(expected_sweep_rad))


def test_sweep_known_45_degrees():
    # If c_r == b/2, tan(Lambda) = 1 => Lambda = 45 deg exactly.
    wing = DeltaWingGeometry(root_chord=3.0, span=6.0)
    assert wing.sweep_LE_deg == pytest.approx(45.0)


def test_inverse_construction_from_span_and_sweep_recovers_root_chord():
    b = 8.0
    sweep_rad = math.radians(60.0)
    wing = DeltaWingGeometry.from_span_and_sweep(span=b, sweep_LE_rad=sweep_rad)
    # independently reconstruct expected root chord
    expected_c_r = (b / 2.0) * math.tan(sweep_rad)
    assert wing.root_chord == pytest.approx(expected_c_r)
    assert wing.span == pytest.approx(b)
    # round-trip: the sweep recovered from the built wing should match input
    assert wing.sweep_LE_rad == pytest.approx(sweep_rad)


def test_inverse_construction_from_root_chord_and_sweep_recovers_span():
    c_r = 9.0
    sweep_rad = math.radians(68.0)
    wing = DeltaWingGeometry.from_root_chord_and_sweep(root_chord=c_r, sweep_LE_rad=sweep_rad)
    expected_b = 2.0 * c_r / math.tan(sweep_rad)
    assert wing.span == pytest.approx(expected_b)
    assert wing.root_chord == pytest.approx(c_r)
    assert wing.sweep_LE_rad == pytest.approx(sweep_rad)


@pytest.mark.parametrize(
    "root_chord,span",
    [(0.0, 5.0), (-1.0, 5.0), (5.0, 0.0), (5.0, -2.0), (float("nan"), 5.0), (5.0, float("inf"))],
)
def test_invalid_geometry_rejected(root_chord, span):
    with pytest.raises(ValueError):
        DeltaWingGeometry(root_chord=root_chord, span=span)


@pytest.mark.parametrize("bad_sweep_rad", [0.0, -0.1, math.pi / 2.0, math.pi, float("nan")])
def test_invalid_sweep_rejected_in_inverse_constructors(bad_sweep_rad):
    with pytest.raises(ValueError):
        DeltaWingGeometry.from_span_and_sweep(span=6.0, sweep_LE_rad=bad_sweep_rad)
    with pytest.raises(ValueError):
        DeltaWingGeometry.from_root_chord_and_sweep(root_chord=6.0, sweep_LE_rad=bad_sweep_rad)


def test_invalid_span_or_chord_rejected_in_inverse_constructors():
    with pytest.raises(ValueError):
        DeltaWingGeometry.from_span_and_sweep(span=-1.0, sweep_LE_rad=math.radians(60.0))
    with pytest.raises(ValueError):
        DeltaWingGeometry.from_root_chord_and_sweep(root_chord=0.0, sweep_LE_rad=math.radians(60.0))


def test_representative_geometry_is_valid_and_in_conceptual_sweep_range():
    wing = representative_geometry()
    assert wing.root_chord > 0.0
    assert wing.span > 0.0
    assert wing.area > 0.0
    # conceptual supersonic-delta sweep range stated in the project brief
    assert 55.0 <= wing.sweep_LE_deg <= 70.0
    # independently recompute area/AR/sweep for the representative wing
    expected_S = 0.5 * wing.span * wing.root_chord
    assert wing.area == pytest.approx(expected_S)
    expected_AR = wing.span**2 / expected_S
    assert wing.aspect_ratio == pytest.approx(expected_AR)
    expected_sweep = math.atan(wing.root_chord / (wing.span / 2.0))
    assert wing.sweep_LE_rad == pytest.approx(expected_sweep)
