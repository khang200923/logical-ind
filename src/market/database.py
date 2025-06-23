from dataclasses import dataclass, field
import logging
import psycopg2
from src.market import lmsr
from src.market.market import Market
from src.market.transaction import Transaction
from src.market.user import User

logger = logging.getLogger("database")

@dataclass
class Database:
    url: str
    connection: psycopg2.extensions.connection = field(init=False)

    def __post_init__(self):
        self.connect()

    def connect(self):
        self.connection = psycopg2.connect(self.url)
        self.connection.autocommit = False
        logger.info("Connected to the database")

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            return
        logger.warning("No database connection to close")

    def reset(self):
        with self.connection:
            with self.connection.cursor() as cursor:
                logger.info("Resetting database...")
                cursor.execute("""DROP TABLE IF EXISTS transactions;""")
                cursor.execute("""DROP TABLE IF EXISTS users;""")
                cursor.execute("""DROP TABLE IF EXISTS markets;""")

                cursor.execute("""CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    balance DECIMAL(16, 8) NOT NULL DEFAULT 0.00
                );""")
                cursor.execute("""CREATE TABLE markets (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    liquidity DECIMAL(16, 8) NOT NULL,
                    yes_shares DECIMAL(16, 8) NOT NULL DEFAULT 0.00,
                    no_shares DECIMAL(16, 8) NOT NULL DEFAULT 0.00,
                    resolution BOOLEAN DEFAULT NULL
                );""")
                cursor.execute("""CREATE TABLE transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
                    up_or_down BOOLEAN NOT NULL,
                    amount DECIMAL(16, 8) NOT NULL CHECK (amount > 0),
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );""")
                cursor.execute("""CREATE INDEX idx_market_id ON transactions (market_id);""")
                cursor.execute("""CREATE INDEX idx_user_id ON transactions (user_id);""")

    def create_user(self, username: str):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id, username, balance;", (username,))
                res = cursor.fetchone()
                assert res is not None, "Failed to create user"
        return User(id=res[0], username=res[1], balance=res[2])

    def get_user(self, user_id: int, cur: psycopg2.extensions.cursor | None = None) -> User:
        if cur is not None:
            cur.execute("SELECT id, username, balance FROM users WHERE id = %s;", (user_id,))
            res = cur.fetchone()
            if res is None:
                raise ValueError(f"User with ID {user_id} not found")
        else:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, username, balance FROM users WHERE id = %s;", (user_id,))
                    res = cursor.fetchone()
                    if res is None:
                        raise ValueError(f"User with ID {user_id} not found")
        return User(id=res[0], username=res[1], balance=res[2])

    def update_user(self, user: User, cur: psycopg2.extensions.cursor | None = None):
        if cur is not None:
            cur.execute("UPDATE users SET username = %s, balance = %s WHERE id = %s;", (user.username, user.balance, user.id))
            if cur.rowcount == 0:
                raise ValueError(f"User with ID {user.id} not found")
            return
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE users SET username = %s, balance = %s WHERE id = %s;", (user.username, user.balance, user.id))
                if cursor.rowcount == 0:
                    raise ValueError(f"User with ID {user.id} not found")

    def delete_user(self, user_id: int):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
                if cursor.rowcount == 0:
                    raise ValueError(f"User with ID {user_id} not found")

    def create_market(self, title: str, description: str, liquidity: float) -> Market:
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO markets (title, description, liquidity) VALUES (%s, %s, %s) RETURNING id, title, description, created_at, liquidity, yes_shares, no_shares, resolution;", (title, description, liquidity))
                res = cursor.fetchone()
                assert res is not None, "Failed to create market"
        return Market(id=res[0], title=res[1], description=res[2], created_at=res[3], liquidity=res[4], yes_shares=res[5], no_shares=res[6], resolution=res[7])

    def get_market(self, market_id: int, cur: psycopg2.extensions.cursor | None = None) -> Market:
        if cur is not None:
            cur.execute("SELECT id, title, description, created_at, liquidity, yes_shares, no_shares, resolution FROM markets WHERE id = %s;", (market_id,))
            res = cur.fetchone()
            if res is None:
                raise ValueError(f"Market with ID {market_id} not found")
        else:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, title, description, created_at, liquidity, yes_shares, no_shares, resolution FROM markets WHERE id = %s;", (market_id,))
                    res = cursor.fetchone()
                    if res is None:
                        raise ValueError(f"Market with ID {market_id} not found")
        return Market(id=res[0], title=res[1], description=res[2], created_at=res[3], liquidity=res[4], yes_shares=res[5], no_shares=res[6], resolution=res[7])

    def update_market(self, market: Market, cur: psycopg2.extensions.cursor | None = None):
        if cur is not None:
            cur.execute("UPDATE markets SET title = %s, description = %s, liquidity = %s, yes_shares = %s, no_shares = %s, resolution = %s WHERE id = %s;",
                        (market.title, market.description, market.liquidity, market.yes_shares, market.no_shares, market.resolution, market.id))
            if cur.rowcount == 0:
                raise ValueError(f"Market with ID {market.id} not found")
            return
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE markets SET title = %s, description = %s, liquidity = %s, yes_shares = %s, no_shares = %s, resolution = %s WHERE id = %s;",
                               (market.title, market.description, market.liquidity, market.yes_shares, market.no_shares, market.resolution, market.id))
                if cursor.rowcount == 0:
                    raise ValueError(f"Market with ID {market.id} not found")

    def delete_market(self, market_id: int):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM markets WHERE id = %s;", (market_id,))
                if cursor.rowcount == 0:
                    raise ValueError(f"Market with ID {market_id} not found")

    def buy_shares(self, user_id: int, market_id: int, up_or_down: bool, amount: float):
        with self.connection:
            with self.connection.cursor() as cursor:
                if amount <= 0:
                    raise ValueError("Amount must be greater than zero")
                user = self.get_user(user_id, cursor)
                market = self.get_market(market_id, cursor)
                cost = lmsr.get_cost(amount, up_or_down, market)
                if user.balance < cost:
                    raise ValueError(f"User with ID {user.id} has insufficient balance to buy shares")
                if market.resolution is not None:
                    raise ValueError(f"Market with ID {market.id} has already been resolved")

                cursor.execute("INSERT INTO transactions (user_id, market_id, up_or_down, amount) VALUES (%s, %s, %s, %s);", (user.id, market.id, up_or_down, amount))
                if cursor.rowcount == 0:
                    raise ValueError("Failed to buy shares")

                user.balance -= cost
                self.update_user(user, cursor)

                if up_or_down:
                    market.yes_shares += amount
                else:
                    market.no_shares += amount
                self.update_market(market, cursor)

    def get_all_transactions_of_market(self, market_id: int, cur: psycopg2.extensions.cursor | None = None) -> list[Transaction]:
        if cur is not None:
            cur.execute("SELECT id, user_id, market_id, up_or_down, amount, created_at FROM transactions WHERE market_id = %s;", (market_id,))
            res = cur.fetchall()
            if not res:
                raise ValueError(f"No transactions found for market with ID {market_id}")
        else:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, user_id, market_id, up_or_down, amount, created_at FROM transactions WHERE market_id = %s;", (market_id,))
                    res = cursor.fetchall()
                    if not res:
                        raise ValueError(f"No transactions found for market with ID {market_id}")
        return [Transaction(id=row[0], user_id=row[1], market_id=row[2], up_or_down=row[3], amount=row[4], created_at=row[5]) for row in res]

    def resolve_market(self, market_id: int, resolution: bool):
        with self.connection:
            with self.connection.cursor() as cursor:
                market = self.get_market(market_id, cursor)
                if market.resolution is not None:
                    raise ValueError(f"Market with ID {market.id} has already been resolved")

                cursor.execute("UPDATE markets SET resolution = %s WHERE id = %s;", (resolution, market.id))
                if cursor.rowcount == 0:
                    raise ValueError(f"Market with ID {market.id} not found")

                transactions = self.get_all_transactions_of_market(market.id, cursor)
                for transaction in transactions:
                    user = self.get_user(transaction.user_id, cursor)
                    if transaction.up_or_down == resolution:
                        payout = transaction.amount
                        user.balance += payout
                        self.update_user(user, cursor)

                market.resolution = resolution
                self.update_market(market, cursor)
