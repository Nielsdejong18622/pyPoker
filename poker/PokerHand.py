from poker.Card import Card
from poker.Score import Score
from poker.Deck import Deck

from typing import Tuple, Counter
from enum import Enum

from functools import total_ordering
from itertools import combinations


@total_ordering
class PokerHand:

    class Tier(Enum):
        HIGH_CARD = 0
        ONE_PAIR = 1
        TWO_PAIR = 2
        THREE_OF_A_KIND = 3
        STRAIGHT = 4
        FLUSH = 5
        FULL_HOUSE = 6
        FOUR_OF_A_KIND = 7
        STRAIGHT_FLUSH = 8
        ROYAL_FLUSH = 9

    def __init__(self, cards: Tuple[Card, ...]) -> None:
        """Evaluate the pokerHand"""
        assert len(cards) == 5, "PokerHand consists of 5 cards!"
        self.cards = cards
        self.tier, self.score = self._evaluate_score()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PokerHand):
            return NotImplemented
        return self.score == other.score

    def __le__(self, other: object) -> bool:
        if not isinstance(other, PokerHand):
            return NotImplemented
        return self.score <= other.score

    def __repr__(self) -> str:
        return f"PokerHand {self.tier.name} ({self.score}) {self.cards}"

    @classmethod
    def random(cls):
        """Constructs a random pokerhand."""
        deck: Deck = Deck(shuffle=True)
        cards = (
            deck.sample(),
            deck.sample(),
            deck.sample(),
            deck.sample(),
            deck.sample(),
        )
        return PokerHand(cards)

    @classmethod
    def best(cls, cards: Tuple[Card, ...]):
        """Constructs the best Pokerhand out of the available cards."""
        assert len(cards) >= 5, "PokerHand consists of 5 cards!"
        best = max((PokerHand(combo) for combo in combinations(cards, 5)))
        return best

    def _evaluate_score(self) -> Tuple[Tier, Score]:
        """Scores the current Pokerhand."""
        assert len(self.cards) == 5, "Pokerhands consists of exactly 5 cards!"

        cards = list(self.cards)
        cards.sort(key=lambda x: x.face.value, reverse=True)
        faces = [card.face.value for card in cards]
        suits = [card.suit for card in cards]
        face_counter = Counter(faces)
        face_counts = sorted(face_counter.items(), key=lambda x: (-x[1], -x[0]))
        unique_faces = sorted(set(faces), reverse=True)

        # print(face_counts)

        def is_flush():
            return len(set(suits)) == 1

        def is_straight():
            sorted_faces = sorted(unique_faces)
            if len(sorted_faces) != 5:
                return False
            if sorted_faces == [2, 3, 4, 5, 14]:  # Wheel
                return True
            return sorted_faces[4] - sorted_faces[0] == 4

        flush = is_flush()
        straight = is_straight()

        # TIER 10: ROYAL FLUSH
        if flush and faces == [14, 13, 12, 11, 10]:
            return (
                PokerHand.Tier.ROYAL_FLUSH,
                PokerHand.Tier.ROYAL_FLUSH.value * 1_000_000,
            )

        # TIER 9: STRAIGHT FLUSH
        if flush and straight:
            high_card = 5 if set(faces) == {14, 2, 3, 4, 5} else max(unique_faces)
            return (
                PokerHand.Tier.STRAIGHT_FLUSH,
                PokerHand.Tier.STRAIGHT_FLUSH.value * 1_000_000 + high_card,
            )

        # TIER 8: FOUR OF A KIND
        if face_counts[0][1] == 4:
            quad = face_counts[0][0]
            kicker = face_counts[1][0]
            return (
                PokerHand.Tier.FOUR_OF_A_KIND,
                PokerHand.Tier.FOUR_OF_A_KIND.value * 1_000_000 + quad * 100 + kicker,
            )

        # TIER 7: FULL HOUSE
        if face_counts[0][1] == 3 and face_counts[1][1] == 2:
            trips = face_counts[0][0]
            pair = face_counts[1][0]
            return (
                PokerHand.Tier.FULL_HOUSE,
                PokerHand.Tier.FULL_HOUSE.value * 1_000_000 + trips * 100 + pair,
            )

        # TIER 6: FLUSH
        if flush:
            return (
                PokerHand.Tier.FLUSH,
                PokerHand.Tier.FLUSH.value * 1_000_000 + max(faces),
            )

        # TIER 5: STRAIGHT
        if straight:
            high_card = 5 if set(faces) == {14, 2, 3, 4, 5} else max(unique_faces)
            return (
                PokerHand.Tier.STRAIGHT,
                PokerHand.Tier.STRAIGHT.value * 1_000_000 + high_card,
            )

        # TIER 4: THREE OF A KIND
        if face_counts[0][1] == 3:
            trips = face_counts[0][0]
            kickers = [f for f in faces if f != trips]
            kickers.sort(reverse=True)
            return (
                PokerHand.Tier.THREE_OF_A_KIND,
                PokerHand.Tier.THREE_OF_A_KIND.value * 1_000_000
                + trips * 10_000
                + kickers[0] * 1000
                + kickers[1] * 100,
            )

        # TIER 3: TWO PAIR
        if face_counts[0][1] == 2 and face_counts[1][1] == 2:
            high_pair = max(face_counts[0][0], face_counts[1][0])
            low_pair = min(face_counts[0][0], face_counts[1][0])
            kicker = [f for f in faces if f != high_pair and f != low_pair][0]
            return (
                PokerHand.Tier.TWO_PAIR,
                PokerHand.Tier.TWO_PAIR.value * 1_000_000
                + high_pair * 10_000
                + low_pair * 100
                + kicker,
            )

        # TIER 2: ONE PAIR
        if face_counts[0][1] == 2:
            pair = face_counts[0][0]
            kickers = [f for f in faces if f != pair]
            kickers.sort(reverse=True)
            return (
                PokerHand.Tier.ONE_PAIR,
                PokerHand.Tier.ONE_PAIR.value * 1_000_000
                + pair * 10_000
                + kickers[0] * 1000
                + kickers[1] * 100
                + kickers[2] * 10,
            )

        # TIER 1: HIGH CARD
        return (
            PokerHand.Tier.HIGH_CARD,
            faces[0] * 10000
            + faces[1] * 1000
            + faces[2] * 100
            + faces[3] * 10
            + faces[4],
        )
