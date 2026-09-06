"""Independent verification of the reduced-order Polhamus-inspired drag/L-D model.

Expected values are computed from independently written formulas, mirroring
the style of the other test modules in this project.
"""

import math

import numpy as np
import pytest

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.drag import (
    CD0_DEFAULT,
    attached_induced_drag_coefficient,
    attached_only_drag_coefficient,
    drag_components,
    lift_to_drag_ratio,
    total_drag_coefficient,
    vortex_drag_coefficient,
)
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import KV_REFERENCE, total_lift_coefficient, vortex_lift_coefficient

AR = 1.8652306326199943  # representative wing's aspect ratio, hard-coded independently
E = 0.9
SWEEP_65_RAD = math.radians(65.0)


def _expected_a(aspect_ratio=AR, e=E):
    a0 = 2.0 * math.pi
    return a0 / (1.0 + a0 / (math.pi * e * aspect_ratio))


def _expected_cdi_attached(alpha_rad, aspect_ratio=AR, e=E):
    a = _expected_a(aspect_ratio, e)
    cl = a * alpha_rad
    return cl**2 / (math.pi * e * aspect_ratio)


def _expected_kv(sweep_rad, kv_ref=KV_REFERENCE, sweep_ref_rad=math.radians(65.0)):
    return kv_ref * math.cos(sweep_ref_rad) / math.cos(sweep_rad)


def _expected_cl_vortex(alpha_rad, sweep_rad):
    kv = _expected_kv(sweep_rad)
    return kv * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2


def _expected_cd_vortex(alpha_rad, sweep_rad):
    return _expected_cl_vortex(alpha_rad, sweep_rad) * math.tan(alpha_rad)


# ---------------------------------------------------------------------
# 1. alpha = 0 identities
# ---------------------------------------------------------------------


def test_alpha_zero_identities():
    assert attached_induced_drag_coefficient(0.0, AR, E) == pytest.approx(0.0)
    assert vortex_drag_coefficient(0.0, SWEEP_65_RAD) == pytest.approx(0.0)
    cd_total = total_drag_coefficient(0.0, AR, E, SWEEP_65_RAD, cd0=CD0_DEFAULT)
    assert cd_total == pytest.approx(CD0_DEFAULT)
    cl_total = total_lift_coefficient(0.0, AR, E, SWEEP_65_RAD)
    assert lift_to_drag_ratio(cl_total, cd_total) == pytest.approx(0.0)


# ---------------------------------------------------------------------
# 2. Attached induced-drag formula: independent hand check
# ---------------------------------------------------------------------


def test_attached_induced_drag_matches_hand_formula():
    alpha = math.radians(12.0)
    expected = _expected_cdi_attached(alpha)
    assert attached_induced_drag_coefficient(alpha, AR, E) == pytest.approx(expected)


# ---------------------------------------------------------------------
# 3. Vortex-drag formula: independent hand calculation
# ---------------------------------------------------------------------


def test_vortex_drag_matches_hand_formula():
    alpha = math.radians(18.0)
    expected = _expected_cd_vortex(alpha, SWEEP_65_RAD)
    assert vortex_drag_coefficient(alpha, SWEEP_65_RAD) == pytest.approx(expected)


# ---------------------------------------------------------------------
# 4. Additive drag identity
# ---------------------------------------------------------------------


def test_total_drag_equals_sum_of_components():
    alpha = math.radians(14.0)
    cd0 = 0.03
    dc = drag_components(alpha, AR, E, SWEEP_65_RAD, cd0=cd0)
    assert dc.cd_total == pytest.approx(dc.cd0 + dc.cdi_attached + dc.cd_vortex)
    assert dc.cd0 == pytest.approx(cd0)


# ---------------------------------------------------------------------
# 5. Positivity over alpha in [0, 25] deg
# ---------------------------------------------------------------------


def test_all_drag_terms_nonnegative_over_study_range():
    alphas = np.radians(np.linspace(0.0, 25.0, 101))
    cdi = attached_induced_drag_coefficient(alphas, AR, E)
    cdv = vortex_drag_coefficient(alphas, SWEEP_65_RAD)
    cdt = total_drag_coefficient(alphas, AR, E, SWEEP_65_RAD)
    assert np.all(cdi >= -1e-12)
    assert np.all(cdv >= -1e-12)
    assert np.all(cdt >= CD0_DEFAULT - 1e-12)


# ---------------------------------------------------------------------
# 6. Finite outputs over study range
# ---------------------------------------------------------------------


def test_no_nan_or_inf_over_study_range():
    alphas = np.radians(np.linspace(0.0, 25.0, 251))
    dc = drag_components(alphas, AR, E, SWEEP_65_RAD)
    assert np.all(np.isfinite(dc.cdi_attached))
    assert np.all(np.isfinite(dc.cd_vortex))
    assert np.all(np.isfinite(dc.cd_total))
    cl_total = total_lift_coefficient(alphas, AR, E, SWEEP_65_RAD)
    ld = lift_to_drag_ratio(cl_total, dc.cd_total)
    assert np.all(np.isfinite(ld))


# ---------------------------------------------------------------------
# 7. Scalar/array consistency
# ---------------------------------------------------------------------


def test_scalar_array_consistency():
    alphas = np.radians(np.array([0.0, 5.0, 10.0, 15.0, 20.0, 25.0]))
    cdi_array = attached_induced_drag_coefficient(alphas, AR, E)
    cdi_scalars = np.array([attached_induced_drag_coefficient(float(a), AR, E) for a in alphas])
    np.testing.assert_allclose(cdi_array, cdi_scalars)

    cdv_array = vortex_drag_coefficient(alphas, SWEEP_65_RAD)
    cdv_scalars = np.array([vortex_drag_coefficient(float(a), SWEEP_65_RAD) for a in alphas])
    np.testing.assert_allclose(cdv_array, cdv_scalars)

    assert isinstance(attached_induced_drag_coefficient(0.1, AR, E), float)
    assert isinstance(cdi_array, np.ndarray)


# ---------------------------------------------------------------------
# 8. Invalid-input rejection
# ---------------------------------------------------------------------


@pytest.mark.parametrize("bad_alpha", [float("nan"), float("inf"), float("-inf")])
def test_invalid_alpha_rejected(bad_alpha):
    with pytest.raises(ValueError):
        attached_induced_drag_coefficient(bad_alpha, AR, E)
    with pytest.raises(ValueError):
        vortex_drag_coefficient(bad_alpha, SWEEP_65_RAD)


def test_alpha_too_close_to_90_deg_rejected():
    with pytest.raises(ValueError):
        vortex_drag_coefficient(math.radians(89.5), SWEEP_65_RAD)


@pytest.mark.parametrize("bad_cd0", [-0.01, float("nan"), float("inf")])
def test_invalid_cd0_rejected(bad_cd0):
    with pytest.raises(ValueError):
        drag_components(math.radians(10.0), AR, E, SWEEP_65_RAD, cd0=bad_cd0)
    with pytest.raises(ValueError):
        attached_only_drag_coefficient(math.radians(10.0), AR, E, cd0=bad_cd0)


@pytest.mark.parametrize("bad_AR", [0.0, -1.0, float("nan")])
def test_invalid_aspect_ratio_rejected(bad_AR):
    with pytest.raises(ValueError):
        attached_induced_drag_coefficient(math.radians(10.0), bad_AR, E)


@pytest.mark.parametrize("bad_e", [0.0, -0.5, float("nan")])
def test_invalid_e_rejected(bad_e):
    with pytest.raises(ValueError):
        attached_induced_drag_coefficient(math.radians(10.0), AR, bad_e)


def test_invalid_lift_to_drag_inputs_rejected():
    with pytest.raises(ValueError):
        lift_to_drag_ratio(float("nan"), 0.03)
    with pytest.raises(ValueError):
        lift_to_drag_ratio(0.3, float("nan"))
    with pytest.raises(ValueError):
        lift_to_drag_ratio(0.3, 0.0)  # CL nonzero, CD zero -> undefined L/D


def test_invalid_alpha_array_rejected():
    bad_alphas = np.array([0.1, 0.2, float("nan")])
    with pytest.raises(ValueError):
        attached_induced_drag_coefficient(bad_alphas, AR, E)


# ---------------------------------------------------------------------
# 9. L/D identity
# ---------------------------------------------------------------------


def test_lift_to_drag_ratio_identity():
    alpha = math.radians(11.0)
    dc = drag_components(alpha, AR, E, SWEEP_65_RAD)
    cl_total = total_lift_coefficient(alpha, AR, E, SWEEP_65_RAD)
    ld = lift_to_drag_ratio(cl_total, dc.cd_total)
    assert ld == pytest.approx(cl_total / dc.cd_total)


# ---------------------------------------------------------------------
# 10. Regression: M1 attached lift and M2 vortex lift unchanged
# ---------------------------------------------------------------------


def test_m1_attached_lift_unchanged():
    wing = representative_geometry()
    a0 = 2.0 * math.pi
    e = 0.9
    a = a0 / (1.0 + a0 / (math.pi * e * wing.aspect_ratio))
    assert a == pytest.approx(2.867211, abs=1e-6)
    for alpha_deg, expected_cl in [(0.0, 0.0), (5.0, 0.250211), (10.0, 0.500423), (15.0, 0.750634)]:
        cl = attached_flow_CL(math.radians(alpha_deg), wing.aspect_ratio, e)
        assert cl == pytest.approx(expected_cl, abs=1e-6)


def test_m2_vortex_lift_unchanged():
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


# ---------------------------------------------------------------------
# 11. Low-angle behavior: induced/vortex drag -> 0 as alpha -> 0
# ---------------------------------------------------------------------


def test_drag_terms_vanish_as_alpha_to_zero():
    tiny = math.radians(0.01)
    assert attached_induced_drag_coefficient(tiny, AR, E) == pytest.approx(0.0, abs=1e-6)
    assert vortex_drag_coefficient(tiny, SWEEP_65_RAD) == pytest.approx(0.0, abs=1e-9)


def test_vortex_drag_grows_faster_than_quadratic_near_zero():
    # C_D,vortex = C_L,vortex * tan(alpha) ~ (Kv*alpha^2)*alpha = Kv*alpha^3 for small alpha:
    # halving alpha should reduce C_D,vortex by a factor of ~8.
    alpha = math.radians(2.0)
    half_alpha = math.radians(1.0)
    ratio = vortex_drag_coefficient(alpha, SWEEP_65_RAD) / vortex_drag_coefficient(half_alpha, SWEEP_65_RAD)
    assert ratio == pytest.approx(8.0, rel=5e-2)


# ---------------------------------------------------------------------
# 12. Sensitivity direction
# ---------------------------------------------------------------------


def test_increasing_cd0_lowers_lift_to_drag_ratio():
    alpha = math.radians(10.0)
    cl_total = total_lift_coefficient(alpha, AR, E, SWEEP_65_RAD)
    cd_low = total_drag_coefficient(alpha, AR, E, SWEEP_65_RAD, cd0=0.02)
    cd_high = total_drag_coefficient(alpha, AR, E, SWEEP_65_RAD, cd0=0.04)
    ld_low = lift_to_drag_ratio(cl_total, cd_low)
    ld_high = lift_to_drag_ratio(cl_total, cd_high)
    assert ld_high < ld_low


def test_increasing_vortex_drag_coefficient_raises_total_drag():
    alpha = math.radians(12.0)
    cd_nominal = total_drag_coefficient(alpha, AR, E, SWEEP_65_RAD, kv_ref=KV_REFERENCE)
    cd_higher_kv = total_drag_coefficient(alpha, AR, E, SWEEP_65_RAD, kv_ref=KV_REFERENCE * 1.2)
    assert cd_higher_kv > cd_nominal


# ---------------------------------------------------------------------
# 13. Degree/radian sanity (drag functions take radians only; cross-check
# against attached_flow_CL_deg / vortex_lift_coefficient_deg helpers)
# ---------------------------------------------------------------------


def test_drag_consistent_with_deg_helpers_for_lift():
    from delta_vortex_lift.attached_flow import attached_flow_CL_deg
    from delta_vortex_lift.vortex_lift import vortex_lift_coefficient_deg

    alpha_deg = 13.0
    alpha_rad = math.radians(alpha_deg)
    cl_attached_rad = attached_flow_CL(alpha_rad, AR, E)
    cl_attached_deg = attached_flow_CL_deg(alpha_deg, AR, E)
    assert cl_attached_deg == pytest.approx(cl_attached_rad)

    cl_v_rad = vortex_lift_coefficient(alpha_rad, SWEEP_65_RAD)
    cl_v_deg = vortex_lift_coefficient_deg(alpha_deg, 65.0)
    assert cl_v_deg == pytest.approx(cl_v_rad)

    cdi = attached_induced_drag_coefficient(alpha_rad, AR, E)
    cdv = vortex_drag_coefficient(alpha_rad, SWEEP_65_RAD)
    assert cdi == pytest.approx(cl_attached_deg**2 / (math.pi * E * AR))
    assert cdv == pytest.approx(cl_v_deg * math.tan(alpha_rad))


# ---------------------------------------------------------------------
# 14. Exact identities implied by the chosen model
# ---------------------------------------------------------------------


def test_cd_vortex_equals_cl_vortex_times_tan_alpha_exactly():
    for alpha_deg in (3.0, 9.0, 17.0, 24.0):
        alpha = math.radians(alpha_deg)
        cl_v = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
        cd_v = vortex_drag_coefficient(alpha, SWEEP_65_RAD)
        assert cd_v == pytest.approx(cl_v * math.tan(alpha))


def test_attached_only_drag_excludes_vortex_and_cd0_matches():
    alpha = math.radians(10.0)
    cd0 = 0.035
    cd_a = attached_only_drag_coefficient(alpha, AR, E, cd0=cd0)
    expected = cd0 + attached_induced_drag_coefficient(alpha, AR, E)
    assert cd_a == pytest.approx(expected)


# ---------------------------------------------------------------------
# 15. No hidden clipping or sign reversal
# ---------------------------------------------------------------------


def test_no_hidden_clipping_monotonic_increase_with_alpha():
    alphas = np.radians(np.linspace(0.0, 25.0, 251))
    cdi = attached_induced_drag_coefficient(alphas, AR, E)
    cdv = vortex_drag_coefficient(alphas, SWEEP_65_RAD)
    cdt = total_drag_coefficient(alphas, AR, E, SWEEP_65_RAD)
    assert np.all(np.diff(cdi) > 0.0)
    assert np.all(np.diff(cdv) > 0.0)
    assert np.all(np.diff(cdt) > 0.0)
    # sign never flips negative anywhere
    assert np.all(cdi >= 0.0) and np.all(cdv >= 0.0) and np.all(cdt > 0.0)
