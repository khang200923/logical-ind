from dataclasses import dataclass, field

@dataclass
class Transaction:
    id: int
    user_id: int
    market_id: int
    up_or_down: bool
    amount: float
    created_at: str

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero")
