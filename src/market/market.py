from dataclasses import dataclass, field

@dataclass
class Market:
    id: int
    title: str
    description: str
    created_at: str
    liquidity: float
    yes_shares: float
    no_shares: float
    resolution: bool | None
