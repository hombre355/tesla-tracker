"""Unit tests for cost_calculator.py — pure functions, no DB needed."""

import pytest

from app.services.cost_calculator import electricity_cost, gas_equivalent_cost, savings


class TestElectricityCost:
    def test_nominal(self):
        assert electricity_cost(10.0, 0.12) == pytest.approx(1.2)

    def test_zero_kwh(self):
        assert electricity_cost(0.0, 0.12) == 0.0

    def test_zero_rate(self):
        assert electricity_cost(10.0, 0.0) == 0.0

    def test_large_charge(self):
        assert electricity_cost(75.0, 0.15) == pytest.approx(11.25)

    def test_rounding(self):
        # Result is rounded to 4 decimal places
        result = electricity_cost(1.0, 0.1234567)
        assert result == pytest.approx(0.1235, abs=1e-4)


class TestGasEquivalentCost:
    def test_nominal(self):
        # 100 miles / 30 mpg = 3.333 gallons × $4.00 = $13.3333
        assert gas_equivalent_cost(100.0, 30.0, 4.00) == pytest.approx(13.3333, rel=1e-3)

    def test_zero_miles(self):
        assert gas_equivalent_cost(0.0, 30.0, 4.00) == 0.0

    def test_mpg_zero_guard(self):
        # Division by zero is guarded — returns 0.0
        assert gas_equivalent_cost(100.0, 0.0, 4.00) == 0.0

    def test_high_mpg(self):
        # 100 miles / 50 mpg = 2 gallons × $3.50 = $7.00
        assert gas_equivalent_cost(100.0, 50.0, 3.50) == pytest.approx(7.0)

    def test_zero_gas_price(self):
        assert gas_equivalent_cost(100.0, 30.0, 0.0) == 0.0


class TestSavings:
    def test_positive_savings(self):
        # Gas is more expensive → savings are positive
        assert savings(5.0, 20.0) == pytest.approx(15.0)

    def test_negative_savings(self):
        # Electric is more expensive → savings are negative
        assert savings(20.0, 5.0) == pytest.approx(-15.0)

    def test_zero_savings(self):
        assert savings(10.0, 10.0) == 0.0

    def test_both_zero(self):
        assert savings(0.0, 0.0) == 0.0
