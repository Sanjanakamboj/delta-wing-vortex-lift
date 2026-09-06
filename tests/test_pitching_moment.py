"""Independent verification of the reduced-order pitching-moment / center-of-pressure model.

Expected values are computed from independently written formulas, mirroring
the style of the other test modules in this project.
"""

import math

import numpy as np
import pytest

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.breakdown import BreakdownParameters, effective_vortex_lift_coefficient, vortex_effectiveness
from delta_vortex_lift.drag import drag_components
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import (
    C_REF_HAT_DEFAULT,
    X_ATTACHED_HAT_DEFAULT,
    X_REF_HAT_DEFAULT,
    X_VORTEX_HAT_DEFAULT,
    PitchingMomentParameters,
    attached_moment_coefficient,
    center_of_pressure_hat,
    moment_from_center_of_pressure,
    pitching_moment_aerodynamics,
    total_moment_coefficient,
    vortex_moment_coefficient,
)
from delta_vortex_lift.vortex_lift import KV_REFERENCE, vortex_lift_coefficient

AR = 1.8652306326199943  # representative wing's aspect ratio, hard-coded independently
E = 0.9
SWEEP_65_RAD = math.radians(65.0)
DEFAULT_PARAMS = PitchingMomentParameters()


def _expected_kv(sweep_rad, kv_ref=KV_REFERENCE, sweep_ref_rad=math.radians(65.0)):
    return kv_ref * math.cos(sweep_ref_rad) / math.cos(sweep_rad)


def _expected_cl_vortex_pre(alpha_rad, sweep_rad):
    kv = _expected_kv(sweep_rad)
    return kv * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2


def _expected_cl_attached(alpha_rad, aspect_ratio=AR, e=E):
    a0 = 2.0 * math.pi
    a = a0 / (1.0 + a0 / (math.pi * e * aspect_ratio))
    return a * alpha_rad


# ---------------------------------------------------------------------
# 5. alpha=0 gives C_m=0 for C_m0=0
# ---------------------------------------------------------------------


def test_moment_zero_at_alpha_zero():
    aero = pitching_moment_aerodynamics(0.0, AR, E, SWEEP_65_RAD)
    assert aero.cm_attached == pytest.approx(0.0)
    assert aero.cm_vortex == pytest.approx(0.0)
    assert aero.cm_total == pytest.approx(0.0)


# ---------------------------------------------------------------------
# 6-7. Attached / vortex contributions match the force-arm equation
# ---------------------------------------------------------------------


def test_attached_moment_matches_force_arm_equation():
    cl_attached = 0.42
    expected = -cl_attached * (X_ATTACHED_HAT_DEFAULT - X_REF_HAT_DEFAULT) / C_REF_HAT_DEFAULT
    assert attached_moment_coefficient(cl_attached) == pytest.approx(expected)


def test_vortex_moment_matches_force_arm_equation():
    cl_vortex = 0.17
    expected = -cl_vortex * (X_VORTEX_HAT_DEFAULT - X_REF_HAT_DEFAULT) / C_REF_HAT_DEFAULT
    assert vortex_moment_coefficient(cl_vortex) == pytest.approx(expected)


def test_moment_arm_sign_convention_force_aft_of_ref_is_nose_down():
    # A force AFT of x_ref (x_force - x_ref > 0) with positive lift must give
    # a NEGATIVE (nose-down) moment, by the derived convention M=-L(x-xref).
    params = PitchingMomentParameters(x_attached_hat=0.8, x_ref_hat=0.5)
    cm = attached_moment_coefficient(1.0, params)
    assert cm < 0.0
    # A force FORWARD of x_ref must give a positive (nose-up) moment.
    params_fwd = PitchingMomentParameters(x_attached_hat=0.2, x_ref_hat=0.5)
    cm_fwd = attached_moment_coefficient(1.0, params_fwd)
    assert cm_fwd > 0.0


# ---------------------------------------------------------------------
# 8. Total moment equals sum of components
# ---------------------------------------------------------------------


def test_total_moment_equals_sum_of_components():
    cl_a, cl_v = 0.5, 0.12
    cm_a = attached_moment_coefficient(cl_a)
    cm_v = vortex_moment_coefficient(cl_v)
    cm_t = total_moment_coefficient(cl_a, cl_v)
    assert cm_t == pytest.approx(cm_a + cm_v)


def test_total_moment_includes_cm0_offset_additively():
    cl_a, cl_v = 0.5, 0.12
    cm0 = 0.03
    params = PitchingMomentParameters(cm0=cm0)
    cm_with_offset = total_moment_coefficient(cl_a, cl_v, params)
    cm_without_offset = total_moment_coefficient(cl_a, cl_v, PitchingMomentParameters(cm0=0.0))
    assert cm_with_offset == pytest.approx(cm_without_offset + cm0)


# ---------------------------------------------------------------------
# 9-10. Center-of-pressure weighted average and reconstruction identity
# ---------------------------------------------------------------------


def test_center_of_pressure_weighted_average_identity():
    cl_a, cl_v = 0.6, 0.25
    params = PitchingMomentParameters(x_attached_hat=0.70, x_vortex_hat=0.55)
    expected_xcp = (cl_a * 0.70 + cl_v * 0.55) / (cl_a + cl_v)
    assert center_of_pressure_hat(cl_a, cl_v, params) == pytest.approx(expected_xcp)


def test_moment_reconstructed_from_cp_matches_direct_sum():
    cl_a, cl_v = 0.6, 0.25
    params = PitchingMomentParameters(x_attached_hat=0.70, x_vortex_hat=0.55, x_ref_hat=0.45)
    x_cp = center_of_pressure_hat(cl_a, cl_v, params)
    cm_direct = total_moment_coefficient(cl_a, cl_v, params)
    cm_from_cp = moment_from_center_of_pressure(cl_a + cl_v, x_cp, params)
    assert cm_from_cp == pytest.approx(cm_direct, abs=1e-12)


def test_moment_reconstruction_identity_holds_with_nonzero_cm0():
    cl_a, cl_v = 0.4, 0.1
    params = PitchingMomentParameters(x_attached_hat=0.68, x_vortex_hat=0.60, cm0=0.02)
    x_cp = center_of_pressure_hat(cl_a, cl_v, params)
    cm_direct = total_moment_coefficient(cl_a, cl_v, params)
    cm_from_cp = moment_from_center_of_pressure(cl_a + cl_v, x_cp, params)
    assert cm_from_cp == pytest.approx(cm_direct, abs=1e-12)


# ---------------------------------------------------------------------
# 11. x_cp lies between x_attached and x_vortex when both contributions positive
# ---------------------------------------------------------------------


def test_xcp_between_attached_and_vortex_locations():
    params = PitchingMomentParameters(x_attached_hat=0.70, x_vortex_hat=0.55)
    x_cp = center_of_pressure_hat(0.5, 0.2, params)
    assert min(0.70, 0.55) <= x_cp <= max(0.70, 0.55)


# ---------------------------------------------------------------------
# 12. x_cp is NaN at zero total lift
# ---------------------------------------------------------------------


def test_xcp_nan_at_zero_total_lift():
    assert math.isnan(center_of_pressure_hat(0.0, 0.0))


def test_xcp_nan_over_array_at_zero_entries():
    cl_a = np.array([0.0, 0.3, 0.0])
    cl_v = np.array([0.0, 0.1, 0.0])
    x_cp = center_of_pressure_hat(cl_a, cl_v)
    assert np.isnan(x_cp[0]) and np.isnan(x_cp[2])
    assert not np.isnan(x_cp[1])


# ---------------------------------------------------------------------
# 13. Scalar/array consistency
# ---------------------------------------------------------------------


def test_scalar_array_consistency():
    alphas = np.radians(np.array([2.0, 5.0, 10.0, 15.0, 20.0]))
    cm_array = total_moment_coefficient(
        attached_flow_CL(alphas, AR, E), vortex_lift_coefficient(alphas, SWEEP_65_RAD)
    )
    cm_scalars = np.array(
        [
            total_moment_coefficient(
                attached_flow_CL(float(a), AR, E), vortex_lift_coefficient(float(a), SWEEP_65_RAD)
            )
            for a in alphas
        ]
    )
    np.testing.assert_allclose(cm_array, cm_scalars)
    assert isinstance(total_moment_coefficient(0.1, 0.05), float)
    assert isinstance(cm_array, np.ndarray)


# ---------------------------------------------------------------------
# 14. Finite outputs over declared positive-alpha domain
# ---------------------------------------------------------------------


def test_finite_outputs_over_study_domain():
    alphas = np.radians(np.linspace(0.5, 30.0, 251))  # avoid exact 0 (NaN x_cp expected there)
    aero = pitching_moment_aerodynamics(alphas, AR, E, SWEEP_65_RAD)
    assert np.all(np.isfinite(aero.cl_total))
    assert np.all(np.isfinite(aero.cm_attached))
    assert np.all(np.isfinite(aero.cm_vortex))
    assert np.all(np.isfinite(aero.cm_total))
    assert np.all(np.isfinite(aero.x_cp_hat))


# ---------------------------------------------------------------------
# 15-17. Invalid-input rejection
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(x_attached_hat=-0.1),
        dict(x_attached_hat=1.1),
        dict(x_attached_hat=float("nan")),
        dict(x_vortex_hat=-0.1),
        dict(x_vortex_hat=1.1),
        dict(x_ref_hat=-0.1),
        dict(x_ref_hat=1.1),
        dict(c_ref_hat=0.0),
        dict(c_ref_hat=-0.5),
        dict(c_ref_hat=float("nan")),
        dict(cm0=float("nan")),
    ],
)
def test_invalid_parameters_rejected(kwargs):
    with pytest.raises(ValueError):
        PitchingMomentParameters(**kwargs)


# ---------------------------------------------------------------------
# 18. C_m0 offset behaves additively (see also test_total_moment_includes_cm0_offset_additively)
# ---------------------------------------------------------------------


def test_cm0_shifts_curve_by_constant_amount_across_alpha():
    alphas = np.radians(np.linspace(1.0, 25.0, 25))
    cl_a = attached_flow_CL(alphas, AR, E)
    cl_v = vortex_lift_coefficient(alphas, SWEEP_65_RAD)
    cm_baseline = np.asarray(total_moment_coefficient(cl_a, cl_v, PitchingMomentParameters(cm0=0.0)))
    cm_offset = np.asarray(total_moment_coefficient(cl_a, cl_v, PitchingMomentParameters(cm0=0.05)))
    np.testing.assert_allclose(cm_offset - cm_baseline, 0.05)


# ---------------------------------------------------------------------
# 19. As vortex fraction rises, x_cp moves toward x_vortex
# ---------------------------------------------------------------------


def test_xcp_moves_toward_x_vortex_as_vortex_fraction_rises():
    params = PitchingMomentParameters(x_attached_hat=0.70, x_vortex_hat=0.55)
    # low vortex fraction
    x_cp_low_fraction = center_of_pressure_hat(0.9, 0.05, params)
    # high vortex fraction
    x_cp_high_fraction = center_of_pressure_hat(0.3, 0.7, params)
    # moving toward x_vortex (0.55) means DECREASING x_cp here since x_vortex < x_attached
    assert x_cp_high_fraction < x_cp_low_fraction
    assert abs(x_cp_high_fraction - 0.55) < abs(x_cp_low_fraction - 0.55)


# ---------------------------------------------------------------------
# 20. Changing x_vortex shifts C_m in the expected direction
# ---------------------------------------------------------------------


def test_moving_x_vortex_aft_makes_vortex_moment_more_negative():
    cl_v = 0.3
    params_fwd = PitchingMomentParameters(x_vortex_hat=0.55)
    params_aft = PitchingMomentParameters(x_vortex_hat=0.75)
    cm_fwd = vortex_moment_coefficient(cl_v, params_fwd)
    cm_aft = vortex_moment_coefficient(cl_v, params_aft)
    assert cm_aft < cm_fwd  # further aft of x_ref=0.5 -> more nose-down


# ---------------------------------------------------------------------
# 21. Changing x_ref shifts C_m per the moment-arm identity
# ---------------------------------------------------------------------


def test_changing_x_ref_shifts_moment_by_expected_amount():
    cl_a = 0.5
    params_1 = PitchingMomentParameters(x_ref_hat=0.5)
    params_2 = PitchingMomentParameters(x_ref_hat=0.6)
    cm_1 = attached_moment_coefficient(cl_a, params_1)
    cm_2 = attached_moment_coefficient(cl_a, params_2)
    # independent expected shift: d(Cm)/d(x_ref) = +CL/c_ref (since Cm=-CL(x-xref)/cref)
    expected_shift = cl_a * (params_2.x_ref_hat - params_1.x_ref_hat) / params_1.c_ref_hat
    assert (cm_2 - cm_1) == pytest.approx(expected_shift)


# ---------------------------------------------------------------------
# 22. Breakdown reducing vortex lift moves x_cp back toward x_attached
# ---------------------------------------------------------------------


def test_breakdown_moves_xcp_toward_x_attached():
    params = PitchingMomentParameters(x_attached_hat=0.70, x_vortex_hat=0.55)
    alpha = math.radians(25.0)  # well past default alpha_b=20deg
    cl_a = attached_flow_CL(alpha, AR, E)
    cl_v_pre = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    cl_v_eff = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD)  # default breakdown params
    x_cp_pre = center_of_pressure_hat(cl_a, cl_v_pre, params)
    x_cp_post = center_of_pressure_hat(cl_a, cl_v_eff, params)
    # breakdown reduces vortex lift's weight -> x_cp moves toward x_attached (0.70),
    # i.e. away from x_vortex (0.55) -> x_cp_post > x_cp_pre here.
    assert x_cp_post > x_cp_pre
    assert abs(x_cp_post - 0.70) < abs(x_cp_pre - 0.70)


# ---------------------------------------------------------------------
# 23. M4 effectiveness factor used exactly, not duplicated
# ---------------------------------------------------------------------


def test_m4_effectiveness_used_exactly():
    alpha = math.radians(22.0)
    aero = pitching_moment_aerodynamics(alpha, AR, E, SWEEP_65_RAD)
    expected_fb = vortex_effectiveness(alpha)
    expected_cl_v_eff = effective_vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    assert aero.f_b == pytest.approx(expected_fb)
    assert aero.cl_vortex_effective == pytest.approx(expected_cl_v_eff)


# ---------------------------------------------------------------------
# 24. Below-breakdown M4/M5 consistency
# ---------------------------------------------------------------------


@pytest.mark.parametrize("alpha_deg", [0.0, 2.0, 5.0, 8.0, 10.0])
def test_below_transition_moment_matches_pre_breakdown_model(alpha_deg):
    alpha = math.radians(alpha_deg)
    cl_a = attached_flow_CL(alpha, AR, E)
    cl_v_pre = vortex_lift_coefficient(alpha, SWEEP_65_RAD)
    cm_pre = total_moment_coefficient(cl_a, cl_v_pre)

    aero = pitching_moment_aerodynamics(alpha, AR, E, SWEEP_65_RAD)
    assert aero.cm_total == pytest.approx(cm_pre, abs=1e-4)


# ---------------------------------------------------------------------
# 25-28. M1/M2/M3/M4 regression
# ---------------------------------------------------------------------


def test_m1_regression():
    wing = representative_geometry()
    for alpha_deg, expected_cl in [(0.0, 0.0), (5.0, 0.250211), (10.0, 0.500423), (15.0, 0.750634)]:
        cl = attached_flow_CL(math.radians(alpha_deg), wing.aspect_ratio, E)
        assert cl == pytest.approx(expected_cl, abs=1e-6)


def test_m2_regression():
    wing = representative_geometry()
    for alpha_deg, expected_cl_v in [(5.0, 0.024972), (10.0, 0.097995), (15.0, 0.213526), (20.0, 0.362746)]:
        cl_v = vortex_lift_coefficient(math.radians(alpha_deg), wing.sweep_LE_rad)
        assert cl_v == pytest.approx(expected_cl_v, abs=1e-6)


def test_m3_regression():
    wing = representative_geometry()
    for alpha_deg, expected_cd_total in [(5.0, 0.04206), (10.0, 0.09276), (15.0, 0.19205)]:
        dc = drag_components(math.radians(alpha_deg), wing.aspect_ratio, E, wing.sweep_LE_rad)
        assert dc.cd_total == pytest.approx(expected_cd_total, abs=1e-4)


def test_m4_regression():
    for alpha_deg, expected_fb in [(15.0, 0.9963), (20.0, 0.7250), (25.0, 0.4537)]:
        fb = vortex_effectiveness(math.radians(alpha_deg))
        assert fb == pytest.approx(expected_fb, abs=1e-3)


# ---------------------------------------------------------------------
# Independent hand-formula check tying it all together
# ---------------------------------------------------------------------


def test_full_pipeline_matches_independent_hand_formula():
    alpha_deg = 18.0
    alpha = math.radians(alpha_deg)
    wing = representative_geometry()

    cl_a_hand = _expected_cl_attached(alpha)
    cl_v_pre_hand = _expected_cl_vortex_pre(alpha, wing.sweep_LE_rad)
    bp = BreakdownParameters()
    w_hand = bp.transition_width_rad / 2.0
    fb_hand = bp.f_post + (1 - bp.f_post) * 0.5 * (1 - math.tanh((alpha - bp.alpha_b_rad) / w_hand))
    cl_v_eff_hand = cl_v_pre_hand * fb_hand
    cl_total_hand = cl_a_hand + cl_v_eff_hand

    x_a, x_v, x_ref, c_ref = X_ATTACHED_HAT_DEFAULT, X_VORTEX_HAT_DEFAULT, X_REF_HAT_DEFAULT, C_REF_HAT_DEFAULT
    cm_a_hand = -cl_a_hand * (x_a - x_ref) / c_ref
    cm_v_hand = -cl_v_eff_hand * (x_v - x_ref) / c_ref
    cm_total_hand = cm_a_hand + cm_v_hand
    x_cp_hand = (cl_a_hand * x_a + cl_v_eff_hand * x_v) / cl_total_hand

    aero = pitching_moment_aerodynamics(alpha, wing.aspect_ratio, E, wing.sweep_LE_rad)
    assert aero.cl_total == pytest.approx(cl_total_hand)
    assert aero.cm_total == pytest.approx(cm_total_hand)
    assert aero.x_cp_hat == pytest.approx(x_cp_hand)
