from poker.Card import Card

from typing import Tuple

class Cards:

    @classmethod
    def contain_picture(cls, cards: Tuple[Card, ...]) -> bool:
        return any(card.face in (Card.Face.JACK, Card.Face.QUEEN, Card.Face.KING, Card.Face.ACE) for card in cards)

    @classmethod
    def contains_king(cls, cards: Tuple[Card, ...]) -> bool:
        return any(card.face == Card.Face.KING for card in cards)
