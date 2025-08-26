from enum import Enum
from dataclasses import dataclass


@dataclass
class Card:

    class Suit(Enum):
        c = 1
        s = 2
        h = 3
        d = 4

    class Face(Enum):
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        JACK = 11
        QUEEN = 12
        KING = 13
        ACE = 14

    suit: Suit
    face: Face

    @classmethod
    def color(cls, card: "Card") -> str:
        return "grey"

    def __repr__(self) -> str:
        if self.face.value > 10:
            val = {11: "J", 12: "Q", 13: "K", 14: "A"}[self.face.value]
        else:
            val = self.face.value

        return f"{val}{self.suit.name}"

    def __hash__(self):
        return self.face.value