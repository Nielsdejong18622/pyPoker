from poker.Card import Card

from typing import Tuple


class Cards:

    @classmethod
    def contain_picture(cls, cards: Tuple[Card, ...]) -> bool:
        return any(
            card.face
            in (Card.Face.JACK, Card.Face.QUEEN, Card.Face.KING, Card.Face.ACE)
            for card in cards
        )

    @classmethod
    def contains_king(cls, cards: Tuple[Card, ...]) -> bool:
        return any(card.face == Card.Face.KING for card in cards)

    @classmethod
    def MC_prob_one_pair(cls, cards: Tuple[Card, ...]) -> float:
        "Returns the approximate MC possibility that we have a pair."
        assert len(cards) > 0

        if Cards.has_a_pair(cards):
            return 1.0
        return 0.5 # We either have it or we don't

    @classmethod
    def has_a_pair(cls, cards: Tuple[Card, ...]) -> bool:
        return len(cards) > len(set(card.face for card in cards))
