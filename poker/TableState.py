from poker.Card import Card
from poker.Player import Player
from poker.Money import Money

from enum import Enum
from dataclasses import dataclass
from typing import Tuple
import copy


@dataclass
class TableState:

    class Round(Enum):
        PREFLOP = 0
        FLOP = 1
        TURN = 2
        RIVER = 3

    # Describes the state of the table at a moment in time, as observed by a player at the moment of make_action.
    round: Round  # Which round are we currently in
    cards: Tuple[Card, ...]  # Cards on the table
    players: Tuple[Player, ...]  # List of players.
    player_at_hand_index: int  # Player index that needs to make a move
    small_blind_index: int  # Index of the player that is small blind.
    small_blind_amount: Money  # Amount of money put in by the small blind, initially.
    big_blind_index: int  # Index of the player that is small blind.
    big_blind_amount: Money

    # Returns the number of players.
    def num_players(self) -> int:
        return len(self.players)

    # Returns the non-folded players.
    def num_nonfolded_players(self) -> int:
        return sum(
            not player.folded and (player.money > 0 or player.all_in)
            for player in self.players
        )

    # Retrieves the player at hand from the table_state.
    def current_player(self) -> Player:
        return self.players[self.player_at_hand_index]

    # Returns the players that can still play bets.
    def num_bettable_players(self) -> int:
        return sum(not player.folded and player.money > 0 for player in self.players)

    # Returns the highest standing bet of active players.
    def max_bet(self) -> Money:
        bets = (p.bet for p in self.players if p.bet > 0 and not p.folded)
        return max(bets)

    # How much should the current player add to the pot for a call.
    def call_amount(self) -> Money:
        return self.max_bet() - self.current_player().bet

    # Sums the money in the pot
    def pot(self) -> Money:
        return sum(player.bet for player in self.players)

    # Sums the players money.
    def all_player_money(self) -> Money:
        return sum(player.money for player in self.players)

    def get_big_stack_bully(self) -> Player:
        """Get the player with the most chips"""
        bigstack:Player = max(self.players, key= lambda player: player.money)
        return self.players[self.players.index(bigstack)]

    @classmethod
    def obscure_for_player(cls, other: "TableState", player_id: int) -> "TableState":
        obscured_state: "TableState" = copy.deepcopy(other)

        # Set the cards of other players to empty.
        for idx, play in enumerate(obscured_state.players):
            if idx != player_id:
                play.cards = ()
        return obscured_state

    @classmethod
    def new_game(
        cls,
        players: Tuple[Player, ...],
        small_blind_amount: Money = 1,
        small_blind_index: int = 0,
    ) -> "TableState":
        assert len(players) >= 1, "TableState requires atleast one player!"
        return cls(
            round=TableState.Round.PREFLOP,
            cards=(),
            players=players,
            player_at_hand_index=(small_blind_index + 2) % len(players),
            small_blind_index=small_blind_index,
            small_blind_amount=small_blind_amount,
            big_blind_index=(small_blind_index + 1) % len(players),
            big_blind_amount=small_blind_amount * 2,
        )
