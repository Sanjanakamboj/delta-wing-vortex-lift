"""Independent verification of the Polhamus-style reduced-order vortex-lift model.

Expected values are computed from independently written formulas, mirroring
the style of tests/test_attached_flow.py and tests/test_geometry.py.
"""

import math

import numpy as np
import pytest

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import (
    KV_REFERENCE,
    SWEEP_REFERENCE_RAD,
    kv_of_sweep,
    total_lift_coefficient,
    total_lift_coefficient_deg,
    vortex_fraction,
    vortex_lift_coefficient,
    vortex_lift_coefficient_deg,
)

AR = 1.8652306326199943  # representative wing's aspect ratio, hard-coded independently
E = 0.9
SWEEP_65_RAD = math.radians(65.0)


def _expected_kv(sweep_rad, kv_ref=KV_REFERENCE, sweep_ref_rad=SWEEP_REFERENCE_RAD):
    return kv_ref * math.cos(sweep_ref_rad) / math.cos(sweep_rad)


def _expected_cl_vortex(alpha_rad, sweep_rad, kv_ref=KV_REFERENCE, sweep_ref_rad=SWEEP_REFERENCE_RAD):
    kv = _expected_kv(sweep_rad, kv_ref, sweep_ref_rad)
    return kv * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2


def _expected_cl_attached(alpha_rad, aspect_ratio=AR, e=E):
    a0 = 2.0 * math.pi
    a = a0 / (1.0 + a0 / (math.pi * e * aspect_ratio))
    return a * alpha_rad


# ---------------------------------------------------------------------
# 1. Zero-angle identity
# ---------------------------------------------------------------------


def test_vortex_lift_zero_at_zero_alpha():
    assert vortex_lift_coefficient(0.0, SWEEP_65_RAD) == pytest.approx(0.0)


def test_total_lift_zero_at_zero_alpha():
    assert total_lift_coefficient(0.0, AR, E, SWEEP_65_RAD) == pytest.approx(0.0)


# ---------------------------------------------------------------------
# 2. Additive identity
# ---------------------------------------------------------------------


def test_total_equals_attached_plus_vortex():
    alpha = math.radians(12.0)
    cl_attached = attached_flow_CL(alpha, AR, E)
    cl_vortex = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    cl_total = total_lift_coefficient(alpha, AR, E, SWEEP_65_RAD)
    assert cl_total == pytest.approx(cl_attached + cl_vortex)


# ---------------------------------------------------------------------
# 3. Independent hand-formula check
# ---------------------------------------------------------------------


def test_vortex_lift_matches_independent_hand_formula():
    alpha = math.radians(15.0)
    expected = _expected_cl_vortex(alpha, SWEEP_65_RAD)
    assert vortex_lift_coefficient(alpha, SWEEP_65_RAD) == pytest.approx(expected)


def test_total_lift_matches_independent_hand_formula():
    alpha = math.radians(18.0)
    expected = _expected_cl_attached(alpha) + _expected_cl_vortex(alpha, SWEEP_65_RAD)
    assert total_lift_coefficient(alpha, AR, E, SWEEP_65_RAD) == pytest.approx(expected)


# ---------------------------------------------------------------------
# 4. Non-negativity over the intended positive-alpha domain
# ---------------------------------------------------------------------


def test_vortex_lift_nonnegative_over_study_range():
    alphas = np.radians(np.linspace(0.0, 25.0, 51))
    cl_v = vortex_lift_coefficient(alphas, SWEEP_65_RAD)
    assert np.all(cl_v >= -1e-12)


# ---------------------------------------------------------------------
# 5. Nonlinear growth with alpha
# ---------------------------------------------------------------------


def test_vortex_lift_grows_nonlinearly_with_alpha():
    # If it were linear, doubling alpha would double CL,v. It should not.
    alpha1 = math.radians(5.0)
    alpha2 = math.radians(10.0)
    cl1 = vortex_lift_coefficient(alpha1, SWEEP_65_RAD)
    cl2 = vortex_lift_coefficient(alpha2, SWEEP_65_RAD)
    assert cl2 != pytest.approx(2.0 * cl1, rel=1e-2)
    # small-alpha behavior should be ~ alpha^2 (from sin^2(alpha)cos(alpha) ~ alpha^2)
    small = math.radians(1.0)
    smaller = math.radians(0.5)
    ratio = vortex_lift_coefficient(small, SWEEP_65_RAD) / vortex_lift_coefficient(smaller, SWEEP_65_RAD)
    assert ratio == pytest.approx(4.0, rel=1e-2)  # (1.0/0.5)^2 = 4


def test_vortex_lift_monotonically_increasing_over_study_range():
    alphas = np.radians(np.linspace(0.0, 25.0, 101))
    cl_v = vortex_lift_coefficient(alphas, SWEEP_65_RAD)
    assert np.all(np.diff(cl_v) > 0.0)


# ---------------------------------------------------------------------
# 6-7. Vortex fraction behavior with alpha
# ---------------------------------------------------------------------


def test_vortex_fraction_tends_to_zero_as_alpha_to_zero():
    tiny_alpha = math.radians(0.01)
    f = vortex_fraction(tiny_alpha, AR, E, SWEEP_65_RAD)
    assert f == pytest.approx(0.0, abs=1e-3)
    assert vortex_fraction(0.0, AR, E, SWEEP_65_RAD) == pytest.approx(0.0)


def test_vortex_fraction_increases_with_alpha_at_moderate_angles():
    f_5 = vortex_fraction(math.radians(5.0), AR, E, SWEEP_65_RAD)
    f_10 = vortex_fraction(math.radians(10.0), AR, E, SWEEP_65_RAD)
    f_15 = vortex_fraction(math.radians(15.0), AR, E, SWEEP_65_RAD)
    f_20 = vortex_fraction(math.radians(20.0), AR, E, SWEEP_65_RAD)
    assert f_5 < f_10 < f_15 < f_20


def test_attached_lift_dominates_at_low_alpha():
    alpha = math.radians(2.0)
    cl_attached = attached_flow_CL(alpha, AR, E)
    cl_vortex = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    assert cl_attached > cl_vortex


# ---------------------------------------------------------------------
# 8. Sweep / coefficient sensitivity direction
# ---------------------------------------------------------------------


def test_kv_increases_with_sweep():
    # K_v = kv_ref * cos(sweep_ref)/cos(sweep): as sweep -> 90 deg, cos(sweep) -> 0, K_v increases.
    kv_55 = kv_of_sweep(math.radians(55.0))
    kv_65 = kv_of_sweep(math.radians(65.0))
    kv_75 = kv_of_sweep(math.radians(75.0))
    assert kv_55 < kv_65 < kv_75


def test_vortex_lift_increases_with_sweep_at_fixed_alpha():
    alpha = math.radians(15.0)
    cl_55 = vortex_lift_coefficient(alpha, math.radians(55.0))
    cl_65 = vortex_lift_coefficient(alpha, math.radians(65.0))
    cl_75 = vortex_lift_coefficient(alpha, math.radians(75.0))
    assert cl_55 < cl_65 < cl_75


def test_vortex_lift_scales_linearly_with_kv_ref():
    alpha = math.radians(12.0)
    cl_nominal = vortex_lift_coefficient(alpha, SWEEP_65_RAD, kv_ref=KV_REFERENCE)
    cl_plus_20pct = vortex_lift_coefficient(alpha, SWEEP_65_RAD, kv_ref=KV_REFERENCE * 1.2)
    cl_minus_20pct = vortex_lift_coefficient(alpha, SWEEP_65_RAD, kv_ref=KV_REFERENCE * 0.8)
    assert cl_plus_20pct == pytest.approx(1.2 * cl_nominal)
    assert cl_minus_20pct == pytest.approx(0.8 * cl_nominal)
    assert cl_minus_20pct < cl_nominal < cl_plus_20pct


# ---------------------------------------------------------------------
# 9. No NaN/Inf over the declared study range
# ---------------------------------------------------------------------


def test_no_nan_or_inf_over_study_range():
    alphas = np.radians(np.linspace(0.0, 25.0, 251))
    for sweep_deg in (55.0, 65.0, 75.0):
        cl_v = vortex_lift_coefficient(alphas, math.radians(sweep_deg))
        cl_t = total_lift_coefficient(alphas, AR, E, math.radians(sweep_deg))
        f_v = vortex_fraction(alphas, AR, E, math.radians(sweep_deg))
        assert np.all(np.isfinite(cl_v))
        assert np.all(np.isfinite(cl_t))
        assert np.all(np.isfinite(f_v))


# ---------------------------------------------------------------------
# 10. Scalar/array consistency
# ---------------------------------------------------------------------


def test_scalar_array_consistency_vortex_and_total():
    alphas = np.radians(np.array([0.0, 5.0, 10.0, 15.0, 20.0, 25.0]))
    cl_v_array = vortex_lift_coefficient(alphas, SWEEP_65_RAD)
    cl_v_scalars = np.array([vortex_lift_coefficient(float(a), SWEEP_65_RAD) for a in alphas])
    np.testing.assert_allclose(cl_v_array, cl_v_scalars)

    cl_t_array = total_lift_coefficient(alphas, AR, E, SWEEP_65_RAD)
    cl_t_scalars = np.array([total_lift_coefficient(float(a), AR, E, SWEEP_65_RAD) for a in alphas])
    np.testing.assert_allclose(cl_t_array, cl_t_scalars)

    assert isinstance(vortex_lift_coefficient(0.1, SWEEP_65_RAD), float)
    assert isinstance(cl_v_array, np.ndarray)


# ---------------------------------------------------------------------
# 11. Invalid-input rejection
# ---------------------------------------------------------------------


@pytest.mark.parametrize("bad_alpha", [float("nan"), float("inf"), float("-inf")])
def test_invalid_alpha_rejected(bad_alpha):
    with pytest.raises(ValueError):
        vortex_lift_coefficient(bad_alpha, SWEEP_65_RAD)
    with pytest.raises(ValueError):
        vortex_fraction(bad_alpha, AR, E, SWEEP_65_RAD)


@pytest.mark.parametrize("bad_sweep_rad", [0.0, -0.1, math.pi / 2.0, math.pi, float("nan")])
def test_invalid_sweep_rejected(bad_sweep_rad):
    with pytest.raises(ValueError):
        vortex_lift_coefficient(math.radians(10.0), bad_sweep_rad)
    with pytest.raises(ValueError):
        kv_of_sweep(bad_sweep_rad)


@pytest.mark.parametrize("bad_kv", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_kv_ref_rejected(bad_kv):
    with pytest.raises(ValueError):
        vortex_lift_coefficient(math.radians(10.0), SWEEP_65_RAD, kv_ref=bad_kv)
    with pytest.raises(ValueError):
        kv_of_sweep(SWEEP_65_RAD, kv_ref=bad_kv)


def test_invalid_alpha_array_rejected():
    bad_alphas = np.array([0.1, 0.2, float("nan")])
    with pytest.raises(ValueError):
        vortex_lift_coefficient(bad_alphas, SWEEP_65_RAD)


# ---------------------------------------------------------------------
# 12. Regression: M1 attached-flow output unchanged
# ---------------------------------------------------------------------


def test_m1_attached_flow_output_unchanged():
    # These values are exactly what scripts/manual_check.py reported at the
    # end of Milestone 1, hard-coded independently of any M2 code.
    wing = representative_geometry()
    assert wing.aspect_ratio == pytest.approx(1.8652306326199943)
    a0 = 2.0 * math.pi
    e = 0.9
    a = a0 / (1.0 + a0 / (math.pi * e * wing.aspect_ratio))
    assert a == pytest.approx(2.867211, abs=1e-6)
    for alpha_deg, expected_cl in [(0.0, 0.0), (5.0, 0.250211), (10.0, 0.500423), (15.0, 0.750634)]:
        cl = attached_flow_CL(math.radians(alpha_deg), wing.aspect_ratio, e)
        assert cl == pytest.approx(expected_cl, abs=1e-6)


# ---------------------------------------------------------------------
# 13. Degree/radian conversion sanity checks
# ---------------------------------------------------------------------


def test_vortex_lift_deg_matches_rad():
    alpha_deg = 14.0
    sweep_deg = 65.0
    cl_rad = vortex_lift_coefficient(math.radians(alpha_deg), math.radians(sweep_deg))
    cl_deg = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
    assert cl_deg == pytest.approx(cl_rad)


def test_total_lift_deg_matches_rad():
    alpha_deg = 14.0
    sweep_deg = 65.0
    cl_rad = total_lift_coefficient(math.radians(alpha_deg), AR, E, math.radians(sweep_deg))
    cl_deg = total_lift_coefficient_deg(alpha_deg, AR, E, sweep_deg)
    assert cl_deg == pytest.approx(cl_rad)


# ---------------------------------------------------------------------
# 14. Analytical identities implied by the chosen formula
# ---------------------------------------------------------------------


def test_vortex_lift_analytical_maximum_location():
    # d/d(alpha)[cos(alpha) sin^2(alpha)] = 0 at tan^2(alpha) = 2,
    # i.e. alpha = arctan(sqrt(2)) ~ 54.7356 deg -- an exact analytical
    # property of the chosen functional form, independent of K_v.
    alpha_star = math.atan(math.sqrt(2.0))
    eps = 1e-4
    cl_at_star = vortex_lift_coefficient(alpha_star, SWEEP_65_RAD)
    cl_before = vortex_lift_coefficient(alpha_star - eps, SWEEP_65_RAD)
    cl_after = vortex_lift_coefficient(alpha_star + eps, SWEEP_65_RAD)
    assert cl_at_star > cl_before
    assert cl_at_star > cl_after


def test_kv_reduces_to_reference_value_at_reference_sweep():
    assert kv_of_sweep(SWEEP_REFERENCE_RAD) == pytest.approx(KV_REFERENCE)
