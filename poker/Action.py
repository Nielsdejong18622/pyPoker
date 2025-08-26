from poker.Money import Money


from dataclasses import dataclass
from enum import Enum


@dataclass
class Action:

    class Type(Enum):
        FOLD = 0
        RAISE = 2

        CALL = 1
        CHECK = 3
        ALL_IN = 4

    type: Type
    amount: Money = 0

    def __repr__(self) -> str:
        if self.amount > 0:
            return f"{self.type.name} with {self.amount}"
        return f"{self.type.name}"
