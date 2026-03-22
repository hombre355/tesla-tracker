def electricity_cost(kwh: float, rate_per_kwh: float) -> float:
    return round(kwh * rate_per_kwh, 4)


def gas_equivalent_cost(miles: float, mpg: float, gas_price_per_gallon: float) -> float:
    if mpg <= 0:
        return 0.0
    gallons = miles / mpg
    return round(gallons * gas_price_per_gallon, 4)


def savings(electricity_cost_usd: float, gas_cost_usd: float) -> float:
    return round(gas_cost_usd - electricity_cost_usd, 4)
