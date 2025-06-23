from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    username: str
    balance: float = field(default=0.0)

    def __post_init__(self):
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")

    def update_balance(self, amount: float):
        if self.balance + amount < 0:
            raise ValueError("Insufficient balance")
        self.balance += amount
