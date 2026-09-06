"""Independent verification of the attached-flow lift baseline.

Expected values are computed from independently written formulas (not by
re-invoking the module under test to build its own "expected" answer).
"""

import math

import numpy as np
import pytest

from delta_vortex_lift.attached_flow import (
    A0_THIN_AIRFOIL,
    attached_flow_CL,
    attached_flow_CL_deg,
    dimensional_lift,
    dynamic_pressure,
    finite_wing_lift_curve_slope,
)


def _expected_slope(AR: float, e: float, a0: float = 2 * math.pi) -> float:
    return a0 / (1.0 + a0 / (math.pi * e * AR))


def test_slope_matches_independent_formula():
    AR, e = 1.865, 0.9
    expected = _expected_slope(AR, e)
    assert finite_wing_lift_curve_slope(AR, e) == pytest.approx(expected)


def test_CL_zero_at_zero_alpha():
    assert attached_flow_CL(0.0, aspect_ratio=2.0, e=0.9) == pytest.approx(0.0)


def test_CL_antisymmetric_in_alpha():
    AR, e = 2.3, 0.85
    alpha = math.radians(12.0)
    cl_pos = attached_flow_CL(alpha, AR, e)
    cl_neg = attached_flow_CL(-alpha, AR, e)
    assert cl_neg == pytest.approx(-cl_pos)


def test_CL_equals_slope_times_alpha():
    AR, e = 1.9, 0.8
    alpha = math.radians(7.5)
    a = finite_wing_lift_curve_slope(AR, e)
    expected_CL = a * alpha
    assert attached_flow_CL(alpha, AR, e) == pytest.approx(expected_CL)


def test_slope_decreases_as_AR_decreases():
    e = 0.9
    a_high_AR = finite_wing_lift_curve_slope(aspect_ratio=8.0, e=e)
    a_low_AR = finite_wing_lift_curve_slope(aspect_ratio=2.0, e=e)
    assert a_low_AR < a_high_AR


def test_slope_increases_with_e():
    AR = 2.0
    a_low_e = finite_wing_lift_curve_slope(aspect_ratio=AR, e=0.7)
    a_high_e = finite_wing_lift_curve_slope(aspect_ratio=AR, e=1.0)
    assert a_high_e > a_low_e


def test_slope_approaches_a0_for_very_large_AR():
    a = finite_wing_lift_curve_slope(aspect_ratio=1.0e6, e=0.9)
    assert a == pytest.approx(A0_THIN_AIRFOIL, rel=1e-4)


def test_degrees_vs_radians_consistency():
    AR, e = 1.9, 0.85
    alpha_deg = 10.0
    alpha_rad = math.radians(alpha_deg)
    cl_from_rad = attached_flow_CL(alpha_rad, AR, e)
    cl_from_deg = attached_flow_CL_deg(alpha_deg, AR, e)
    assert cl_from_deg == pytest.approx(cl_from_rad)
    # sanity: using degrees directly as if they were radians must NOT match
    assert attached_flow_CL(alpha_deg, AR, e) != pytest.approx(cl_from_rad)


def test_scalar_input_returns_python_float():
    result = attached_flow_CL(0.1, aspect_ratio=2.0, e=0.9)
    assert isinstance(result, float)


def test_array_input_returns_array_and_matches_elementwise_scalar_calls():
    AR, e = 2.1, 0.9
    alphas = np.radians(np.array([-5.0, 0.0, 5.0, 10.0, 15.0, 20.0]))
    result = attached_flow_CL(alphas, AR, e)
    assert isinstance(result, np.ndarray)
    expected = np.array([attached_flow_CL(float(a), AR, e) for a in alphas])
    np.testing.assert_allclose(result, expected)


def test_dynamic_pressure_formula():
    rho, V = 1.225, 50.0
    assert dynamic_pressure(rho, V) == pytest.approx(0.5 * rho * V**2)


def test_dimensional_lift_equals_q_S_CL():
    rho, V, S, CL = 1.225, 40.0, 12.0, 0.35
    q = dynamic_pressure(rho, V)
    L = dimensional_lift(CL, q, S)
    assert L == pytest.approx(q * S * CL)
    assert L == pytest.approx(0.5 * rho * V**2 * S * CL)


@pytest.mark.parametrize("bad_AR", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_aspect_ratio_rejected(bad_AR):
    with pytest.raises(ValueError):
        finite_wing_lift_curve_slope(aspect_ratio=bad_AR, e=0.9)


@pytest.mark.parametrize("bad_e", [0.0, -0.5, float("nan"), float("inf")])
def test_invalid_e_rejected(bad_e):
    with pytest.raises(ValueError):
        finite_wing_lift_curve_slope(aspect_ratio=2.0, e=bad_e)


def test_invalid_a0_rejected():
    with pytest.raises(ValueError):
        finite_wing_lift_curve_slope(aspect_ratio=2.0, e=0.9, a0=0.0)


def test_invalid_dynamic_pressure_inputs_rejected():
    with pytest.raises(ValueError):
        dynamic_pressure(rho_inf=-1.0, V_inf=10.0)
    with pytest.raises(ValueError):
        dynamic_pressure(rho_inf=1.225, V_inf=-10.0)


def test_invalid_dimensional_lift_inputs_rejected():
    with pytest.raises(ValueError):
        dimensional_lift(C_L=0.3, q_inf=100.0, S=0.0)
    with pytest.raises(ValueError):
        dimensional_lift(C_L=0.3, q_inf=-1.0, S=10.0)
