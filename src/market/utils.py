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
        - math.log(current_price / (1 - current_price))
        )
    if up_or_down:
        return max(0, target_yes_shares)
    else:
        return max(0, -target_yes_shares)

def cost_to_amount(
    cost: float,
    up_or_down: bool,
    market: Market,
) -> float:
    yes_shares = market.yes_shares
    no_shares = market.no_shares
    liquidity = market.liquidity
    if up_or_down:
        return liquidity * math.log(
            math.exp(cost / liquidity)
            * (math.exp(yes_shares / liquidity) + math.exp(no_shares / liquidity))
            - math.exp(no_shares / liquidity)
        ) - yes_shares
    else:
        return liquidity * math.log(
            math.exp(cost / liquidity)
            * (math.exp(yes_shares / liquidity) + math.exp(no_shares / liquidity))
            - math.exp(yes_shares / liquidity)
        ) - no_shares

def limit_order_to_price(
    bid: float,
    target_price: float,
    market: Market,
):
    current_price = market.price
    up_or_down = target_price > current_price
    willing_amount = cost_to_amount(bid, up_or_down, market)
    required_amount = predict_amount_required_for_price(target_price, up_or_down, market)
    assert required_amount >= 0, "Required amount must be non-negative"
    return min(willing_amount, required_amount)
