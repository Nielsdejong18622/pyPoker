from poker.Card import Card

from typing import List, Optional

import random


class Deck:

    def __init__(self, shuffle: bool = True):
        self._original_deck: List[Card] = [
            Card(suit, face) for suit in Card.Suit for face in Card.Face
        ]
        self._cards: List[Card] = self._original_deck.copy()
        if shuffle:
            self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw(self) -> Optional[Card]:
        """Draw a card from the top of the deck. Returns None if deck is empty."""
        if self._cards:
            return self._cards.pop()
        return None

    def sample(self) -> Card:
        """Randomly sample a card. If replace=False, the card is removed from the deck."""
        assert self._cards, "Deck is empty! No sample possible!"
        card: Card = self._cards.pop()
        return card

    def reset(self, shuffle: bool = True) -> None:
        """Reset the deck to full 52 cards."""
        self._cards = self._original_deck.copy()
        if shuffle:
            self.shuffle()

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self):
        return f"<Deck with {len(self)} cards>"
