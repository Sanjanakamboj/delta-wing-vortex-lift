"""Independent verification of the conceptual vortex-breakdown sensitivity model.

Expected values are computed from independently written formulas, mirroring
the style of the other test modules in this project.
"""

import math

import numpy as np
import pytest

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.breakdown import (
    ALPHA_B_DEFAULT_RAD,
    F_POST_DEFAULT,
    TRANSITION_WIDTH_DEFAULT_RAD,
    BreakdownParameters,
    effective_vortex_lift_coefficient,
    post_breakdown_aerodynamics,
    post_breakdown_drag_components,
    usable_alpha_limit,
    vortex_effectiveness,
)
from delta_vortex_lift.drag import CD0_DEFAULT, drag_components, total_drag_coefficient
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import KV_REFERENCE, total_lift_coefficient, vortex_lift_coefficient

AR = 1.8652306326199943  # representative wing's aspect ratio, hard-coded independently
E = 0.9
SWEEP_65_RAD = math.radians(65.0)
DEFAULT_PARAMS = BreakdownParameters()


def _expected_fb(alpha_rad, alpha_b=ALPHA_B_DEFAULT_RAD, dalpha=TRANSITION_WIDTH_DEFAULT_RAD, f_post=F_POST_DEFAULT):
    w = dalpha / 2.0
    return f_post + (1.0 - f_post) * 0.5 * (1.0 - math.tanh((alpha_rad - alpha_b) / w))


def _expected_kv(sweep_rad, kv_ref=KV_REFERENCE, sweep_ref_rad=math.radians(65.0)):
    return kv_ref * math.cos(sweep_ref_rad) / math.cos(sweep_rad)


def _expected_cl_vortex_pre(alpha_rad, sweep_rad):
    kv = _expected_kv(sweep_rad)
    return kv * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2


# ---------------------------------------------------------------------
# 1-3. Below-transition identities (M4 reduces exactly to M2/M3)
# ---------------------------------------------------------------------


@pytest.mark.parametrize("alpha_deg", [0.0, 2.0, 5.0, 8.0, 10.0])
def test_below_transition_vortex_lift_matches_m2(alpha_deg):
    alpha = math.radians(alpha_deg)
    m2_value = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    m4_value = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    assert m4_value == pytest.approx(m2_value, abs=1e-4)


@pytest.mark.parametrize("alpha_deg", [0.0, 2.0, 5.0, 8.0, 10.0])
def test_below_transition_total_lift_matches_m2(alpha_deg):
    alpha = math.radians(alpha_deg)
    m2_total = total_lift_coefficient(alpha, AR, E, SWEEP_65_RAD)
    aero = post_breakdown_aerodynamics(alpha, AR, E, SWEEP_65_RAD)
    assert aero.cl_total == pytest.approx(m2_total, abs=1e-4)


@pytest.mark.parametrize("alpha_deg", [0.0, 2.0, 5.0, 8.0, 10.0])
def test_below_transition_total_drag_matches_m3(alpha_deg):
    alpha = math.radians(alpha_deg)
    m3_drag = total_drag_coefficient(alpha, AR, E, SWEEP_65_RAD)
    aero = post_breakdown_aerodynamics(alpha, AR, E, SWEEP_65_RAD)
    assert aero.cd_total == pytest.approx(m3_drag, abs=1e-4)


# ---------------------------------------------------------------------
# 4-6. f_b bounds, monotonicity, smoothness
# ---------------------------------------------------------------------


def test_fb_bounds():
    alphas = np.radians(np.linspace(0.0, 30.0, 301))
    fb = vortex_effectiveness(alphas)
    assert np.all(fb > 0.0)
    assert np.all(fb <= 1.0 + 1e-12)


def test_fb_monotonically_nonincreasing():
    alphas = np.radians(np.linspace(0.0, 30.0, 301))
    fb = vortex_effectiveness(alphas)
    assert np.all(np.diff(fb) <= 1e-12)


def test_fb_smooth_no_jump_at_transition_boundaries():
    # Sample densely around alpha_b +/- transition_width and check that
    # consecutive differences stay small and consistent (no jump/kink).
    center_deg = math.degrees(ALPHA_B_DEFAULT_RAD)
    width_deg = math.degrees(TRANSITION_WIDTH_DEFAULT_RAD)
    alphas_deg = np.linspace(center_deg - 2 * width_deg, center_deg + 2 * width_deg, 401)
    fb = vortex_effectiveness(np.radians(alphas_deg))
    diffs = np.diff(fb)
    # no diff should be more than ~5x the local average step -- catches jumps
    assert np.all(np.abs(diffs) < 0.05)


# ---------------------------------------------------------------------
# 7-8. f_b limiting values
# ---------------------------------------------------------------------


def test_fb_equals_one_at_sufficiently_low_alpha():
    fb = vortex_effectiveness(math.radians(-5.0))
    assert fb == pytest.approx(1.0, abs=1e-6)


def test_fb_approaches_f_post_at_sufficiently_high_alpha():
    fb = vortex_effectiveness(math.radians(60.0))
    assert fb == pytest.approx(F_POST_DEFAULT, abs=1e-6)


# ---------------------------------------------------------------------
# 9-10. Effective vortex lift bounds
# ---------------------------------------------------------------------


def test_effective_vortex_lift_never_exceeds_pre_breakdown():
    alphas = np.radians(np.linspace(0.0, 30.0, 301))
    cl_pre = np.asarray(vortex_lift_coefficient(alphas, SWEEP_65_RAD), dtype=float)
    cl_eff = np.asarray(effective_vortex_lift_coefficient(alphas, SWEEP_65_RAD), dtype=float)
    assert np.all(cl_eff <= cl_pre + 1e-12)


def test_effective_vortex_lift_nonnegative():
    alphas = np.radians(np.linspace(0.0, 30.0, 301))
    cl_eff = np.asarray(effective_vortex_lift_coefficient(alphas, SWEEP_65_RAD), dtype=float)
    assert np.all(cl_eff >= -1e-12)


# ---------------------------------------------------------------------
# 11-12. Scalar/array consistency, no NaN/Inf
# ---------------------------------------------------------------------


def test_scalar_array_consistency():
    alphas = np.radians(np.array([0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]))
    fb_array = vortex_effectiveness(alphas)
    fb_scalars = np.array([vortex_effectiveness(float(a)) for a in alphas])
    np.testing.assert_allclose(fb_array, fb_scalars)
    assert isinstance(vortex_effectiveness(0.1), float)
    assert isinstance(fb_array, np.ndarray)


def test_no_nan_or_inf_over_study_domain():
    alphas = np.radians(np.linspace(0.0, 30.0, 301))
    aero = post_breakdown_aerodynamics(alphas, AR, E, SWEEP_65_RAD)
    for field in aero:
        arr = np.asarray(field, dtype=float)
        assert np.all(np.isfinite(arr))


# ---------------------------------------------------------------------
# 13. Invalid-input rejection
# ---------------------------------------------------------------------


@pytest.mark.parametrize("bad_alpha", [float("nan"), float("inf"), float("-inf")])
def test_invalid_alpha_rejected(bad_alpha):
    with pytest.raises(ValueError):
        vortex_effectiveness(bad_alpha)
    with pytest.raises(ValueError):
        effective_vortex_lift_coefficient(bad_alpha, SWEEP_65_RAD)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(alpha_b_rad=0.0),
        dict(alpha_b_rad=-0.1),
        dict(alpha_b_rad=float("nan")),
        dict(transition_width_rad=0.0),
        dict(transition_width_rad=-1.0),
        dict(f_post=0.0),
        dict(f_post=-0.1),
        dict(f_post=1.5),
        dict(f_post=float("nan")),
    ],
)
def test_invalid_breakdown_parameters_rejected(kwargs):
    with pytest.raises(ValueError):
        BreakdownParameters(**kwargs)


def test_invalid_ld_reference_rejected():
    with pytest.raises(ValueError):
        usable_alpha_limit(AR, E, SWEEP_65_RAD, ld_reference=0.0)
    with pytest.raises(ValueError):
        usable_alpha_limit(AR, E, SWEEP_65_RAD, ld_reference=float("nan"))


# ---------------------------------------------------------------------
# 14-15. Sensitivity direction
# ---------------------------------------------------------------------


def test_later_onset_delays_reduction_in_vortex_lift():
    alpha = math.radians(20.0)
    early = BreakdownParameters(alpha_b_rad=math.radians(15.0))
    late = BreakdownParameters(alpha_b_rad=math.radians(25.0))
    cl_early = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD, params=early)
    cl_late = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD, params=late)
    assert cl_late > cl_early


def test_larger_f_post_retains_more_vortex_lift():
    alpha = math.radians(28.0)
    low_retain = BreakdownParameters(f_post=0.3)
    high_retain = BreakdownParameters(f_post=0.6)
    cl_low = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD, params=low_retain)
    cl_high = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD, params=high_retain)
    assert cl_high > cl_low


# ---------------------------------------------------------------------
# 16-17. Drag consistency, L/D identity
# ---------------------------------------------------------------------


def test_effective_vortex_drag_matches_independent_relation():
    alpha_deg = 22.0
    alpha = math.radians(alpha_deg)
    cl_eff = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    expected_cd_vortex = cl_eff * math.tan(alpha)
    cd0, cdi, cd_vortex_eff, cd_total = post_breakdown_drag_components(alpha, AR, E, SWEEP_65_RAD)
    assert cd_vortex_eff == pytest.approx(expected_cd_vortex)
    assert cd_total == pytest.approx(cd0 + cdi + cd_vortex_eff)


def test_lift_to_drag_identity():
    alpha = math.radians(18.0)
    aero = post_breakdown_aerodynamics(alpha, AR, E, SWEEP_65_RAD)
    assert aero.lift_to_drag == pytest.approx(aero.cl_total / aero.cd_total)


def test_lift_to_drag_zero_at_alpha_zero():
    aero = post_breakdown_aerodynamics(0.0, AR, E, SWEEP_65_RAD)
    assert aero.lift_to_drag == pytest.approx(0.0)


# ---------------------------------------------------------------------
# 18-20. M1/M2/M3 regression
# ---------------------------------------------------------------------


def test_m1_regression():
    wing = representative_geometry()
    a0 = 2.0 * math.pi
    a = a0 / (1.0 + a0 / (math.pi * E * wing.aspect_ratio))
    assert a == pytest.approx(2.867211, abs=1e-6)
    for alpha_deg, expected_cl in [(0.0, 0.0), (5.0, 0.250211), (10.0, 0.500423), (15.0, 0.750634)]:
        cl = attached_flow_CL(math.radians(alpha_deg), wing.aspect_ratio, E)
        assert cl == pytest.approx(expected_cl, abs=1e-6)


def test_m2_regression():
    wing = representative_geometry()
    for alpha_deg, expected_cl_v in [
        (0.0, 0.0),
        (5.0, 0.024972),
        (10.0, 0.097995),
        (15.0, 0.213526),
        (20.0, 0.362746),
    ]:
        cl_v = vortex_lift_coefficient(math.radians(alpha_deg), wing.sweep_LE_rad)
        assert cl_v == pytest.approx(expected_cl_v, abs=1e-6)


def test_m3_regression():
    wing = representative_geometry()
    for alpha_deg, expected_cd_total in [(5.0, 0.04206), (10.0, 0.09276), (15.0, 0.19205)]:
        dc = drag_components(math.radians(alpha_deg), wing.aspect_ratio, E, wing.sweep_LE_rad, cd0=CD0_DEFAULT)
        assert dc.cd_total == pytest.approx(expected_cd_total, abs=1e-4)


# ---------------------------------------------------------------------
# 21. No silent change below the declared transition
# ---------------------------------------------------------------------


def test_no_silent_change_below_transition_across_full_grid():
    alphas = np.radians(np.linspace(0.0, 10.0, 101))  # well below alpha_b=20deg
    m2_vals = np.asarray(vortex_lift_coefficient(alphas, SWEEP_65_RAD), dtype=float)
    m4_vals = np.asarray(effective_vortex_lift_coefficient(alphas, SWEEP_65_RAD), dtype=float)
    np.testing.assert_allclose(m4_vals, m2_vals, atol=1e-4)


# ---------------------------------------------------------------------
# 22. Degree/radian sanity (module takes radians only; cross-check against
# an independently-converted degree value)
# ---------------------------------------------------------------------


def test_degree_radian_conversion_sanity():
    alpha_deg = 21.0
    alpha_rad = math.radians(alpha_deg)
    fb_rad = vortex_effectiveness(alpha_rad)
    fb_hand = _expected_fb(alpha_rad)
    assert fb_rad == pytest.approx(fb_hand)


# ---------------------------------------------------------------------
# Independent hand-formula check for f_b and effective vortex lift
# ---------------------------------------------------------------------


def test_fb_matches_independent_hand_formula():
    for alpha_deg in (12.0, 18.0, 20.0, 24.0, 29.0):
        alpha = math.radians(alpha_deg)
        expected = _expected_fb(alpha)
        assert vortex_effectiveness(alpha) == pytest.approx(expected)


def test_effective_vortex_lift_matches_independent_hand_formula():
    alpha = math.radians(23.0)
    expected = _expected_cl_vortex_pre(alpha, SWEEP_65_RAD) * _expected_fb(alpha)
    assert effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD) == pytest.approx(expected)


# ---------------------------------------------------------------------
# usable_alpha_limit sanity
# ---------------------------------------------------------------------


def test_usable_alpha_limit_within_declared_domain():
    limit_rad = usable_alpha_limit(AR, E, SWEEP_65_RAD, ld_reference=6.9697)
    assert 0.0 <= limit_rad <= math.radians(25.0)


def test_usable_alpha_limit_zero_reference_case_is_never_negative():
    # sanity: a very small but valid reference should not break the search
    limit_rad = usable_alpha_limit(AR, E, SWEEP_65_RAD, ld_reference=0.5)
    assert limit_rad >= 0.0
