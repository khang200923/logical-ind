import math
from src.market.market import Market

def predict_amount_required_for_price(
    target_price: float,
    up_or_down: bool,
    market: Market,
) -> float:
    current_price = market.price
    target_yes_shares = market.liquidity * (
        math.log(target_price / (1 - target_price))
        -
        math.log(current_price / (1 - current_price))
        )
    if up_or_down:
        return max(0, target_yes_shares)
    else:
        return max(0, -target_yes_shares)
