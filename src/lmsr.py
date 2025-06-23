import math
from src.market import Market

def cost_function(market: Market):
    yes_shares = market.yes_shares
    no_shares = market.no_shares
    liquidity = market.liquidity

    return liquidity * math.log(math.exp(yes_shares / liquidity) + math.exp(no_shares / liquidity))

def price_function(market: Market):
    yes_shares = market.yes_shares
    no_shares = market.no_shares
    liquidity = market.liquidity

    return math.exp(yes_shares / liquidity) / (math.exp(yes_shares / liquidity) + math.exp(no_shares / liquidity))

def get_cost(amount: float, up_or_down: bool, market: Market) -> float:
    if up_or_down:
        yes_shares = market.yes_shares + amount
        no_shares = market.no_shares
    else:
        yes_shares = market.yes_shares
        no_shares = market.no_shares + amount

    new_market = Market(
        id=market.id,
        title=market.title,
        description=market.description,
        created_at=market.created_at,
        price=market.price,
        liquidity=market.liquidity,
        yes_shares=yes_shares,
        no_shares=no_shares,
        resolution=market.resolution
    )

    return cost_function(new_market) - cost_function(market)

def get_price(amount: float, up_or_down: bool, market: Market) -> float:
    if up_or_down:
        yes_shares = market.yes_shares + amount
        no_shares = market.no_shares
    else:
        yes_shares = market.yes_shares
        no_shares = market.no_shares + amount

    new_market = Market(
        id=market.id,
        title=market.title,
        description=market.description,
        created_at=market.created_at,
        price=market.price,
        liquidity=market.liquidity,
        yes_shares=yes_shares,
        no_shares=no_shares,
        resolution=market.resolution
    )

    return price_function(new_market)
