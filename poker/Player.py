from poker.Card import Card
from poker.Money import Money
from poker.Strategy import Strategy

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Player:
    money: Money
    strategy: Strategy
    cards: Tuple[Card, ...] = field(
        default_factory=tuple
    )  # pyright: ignore[reportUnknownVariableType]
    folded: bool = False
    all_in: bool = False
    bet: "Money" = 0  # Money put forward by the player this round.

