from poker.TableState import TableState
from poker.Deck import Deck
from poker.Player import Player
from poker.Money import Money
from poker.PokerHand import PokerHand
from poker.Action import Action
from poker.Card import Card

from enum import Enum
from copy import deepcopy
from typing import Tuple

import logging


class Table:

    class Event(Enum):
        RESET = 1
        NEW_ROUND = 2
        SMALL_BLIND = 3
        BIG_BLIND = 4
        DEAL_PLAYER_CARD = 5
        QUERY_PLAYER = 6
        START_BETTING_ROUND = 7
        SHOWDOWN = 8
        INCREASE_ROUND = 9
        INCREMENT_BUTTONS = 10
        DETERMINE_WINNER = 11
        DONE = 12

    @classmethod
    def construct_withPlayers(cls, players: Tuple[Player, ...]) -> "Table":
        """
        Construct a simulator that simulates a poker table with the given players.
        """
        return cls(init_state=TableState.new_game(players))

    def __init__(self, init_state: TableState, loglevel=logging.WARNING):
        """
        Construct a simulator that simulates a poker table from an initial state onwards.
        """
        assert len(init_state.players) >= 1, "Requires atleast one players!"
        assert len(init_state.players) <= 22, "Limited up to 22 players!"
        self._create_logger(terminal_level=loglevel)
        self._init_state: TableState = deepcopy(init_state)
        self.state = deepcopy(self._init_state)
        self._queried: dict[int, bool] = {}
        self._deck = Deck(shuffle=True)
        self.round_counter = 0
        self.reset()

    def _create_logger(self, terminal_level) -> None:
        # create logger for "Sample App"
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler("Table.log", mode="w", encoding="utf-8")
        # fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        import sys

        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(terminal_level)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            "[%(asctime)s]%(levelname)8s:%(message)s ",
            # + "(%(filename)s:%(lineno)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self._logger.addHandler(ch)
        self._logger.addHandler(fh)

    def getWinner(self) -> Player:
        assert self.done(), "Table game not over yet!"
        winner: Player = max(self.state.players, key=lambda player: player.money)
        return self.state.players[self.state.players.index(winner)]

    def reset(self) -> None:
        self._execute(Table.Event.RESET)

    def _schedule(self, event: Event) -> None:
        self._q = event

    def step(self) -> None:
        if not self.done():
            self._execute(self._q)

    def round_underway(self) -> bool:
        return self._q != Table.Event.NEW_ROUND

    def done(self) -> bool:
        return self._q == Table.Event.DONE

    def _execute(self, event: Event) -> None:
        state: TableState = self.state
        play_idx: int = state.player_at_hand_index
        play: Player = state.players[play_idx]

        self._logger.debug(f"Executing {event.name}")

        assert not play.folded
        assert not play.all_in
        assert play.money > 0

        if event == Table.Event.RESET:

            self._logger.info("Resetting Table to init_state.")
            self.state = deepcopy(self._init_state)
            self._queried: dict[int, bool] = {}
            self._deck = Deck(shuffle=True)
            self.round_counter = 0
            self._schedule(Table.Event.NEW_ROUND)
        elif event == Table.Event.NEW_ROUND:
            # If we setup a table with only one player having money, we have a winner.
            remain: Tuple[Player, ...] = tuple(
                play for play in state.players if play.money > 0
            )
            if len(remain) == 1:
                self._logger.info(f"We have a table winner! Player: {play_idx}")
                self._q = Table.Event.DONE
                return

            self.round_counter += 1

            # Otherwise shuffle the deck etc.
            self._deck: Deck = Deck(shuffle=True)
            self.state.round = TableState.Round.PREFLOP
            self.state.cards = ()

            self._schedule(Table.Event.DEAL_PLAYER_CARD)
        elif event == Table.Event.DEAL_PLAYER_CARD:
            # If current player has no cards.
            if len(play.cards) == 0:
                # If current player is the small_blind.
                if play_idx == state.small_blind_index:
                    small_bet: Money = min(state.small_blind_amount, play.money)
                    self._logger.info(
                        f"Small blind Player {play_idx} chips in {small_bet}"
                    )
                    play.all_in = small_bet == play.money
                    play.money -= small_bet
                    play.bet += small_bet

                # If current player is the small_blind.
                if play_idx == state.big_blind_index:
                    big_bet: Money = min(state.big_blind_amount, play.money)
                    self._logger.info(f"Big blind Player {play_idx} chips in {big_bet}")
                    play.all_in = big_bet == play.money
                    play.money -= big_bet
                    play.bet += big_bet

                card1 = self._deck.sample()
                card2 = self._deck.sample()
                self.state.players[play_idx].cards = (card1, card2)
                self.state.player_at_hand_index = self.__search_next_player(play_idx)
                self._schedule(Table.Event.DEAL_PLAYER_CARD)
            else:
                self._schedule(Table.Event.START_BETTING_ROUND)
        elif event == Table.Event.START_BETTING_ROUND:
            UTG = self.__search_next_player(state.big_blind_index)
            self.state.player_at_hand_index = UTG
            self._logger.info(
                f"Starting Betting Round {state.round.name} with Player {UTG}"
            )

            self._queried = {
                idx: p.folded or p.money == 0 for idx, p in enumerate(state.players)
            }
            self._schedule(Table.Event.QUERY_PLAYER)
        elif event == Table.Event.QUERY_PLAYER:

            assert len(play.cards) == 2

            # We arrive at a player that needs to make a move.
            sitting_players = self.state.num_nonfolded_players()
            betting_players = self.state.num_bettable_players()

            # If we are the only non-folded player remaining.
            if sitting_players == 1:
                self._schedule(Table.Event.DETERMINE_WINNER)
                return

            # If we can only play against ourselves...
            if betting_players == 1:
                self._schedule(Table.Event.SHOWDOWN)
                return

            # Get and implement the current player action.
            self._get_and_implement_player_action()
            self._queried[play_idx] = True
            # Go to the next player.
            self.state.player_at_hand_index = self.__search_next_player(play_idx)

            # Betting is done if betting_equal and everybody responded.
            betting_equal = all(
                other.folded
                or other == play
                or (other.all_in and play.bet >= other.bet)
                or (not other.all_in and (other.money == 0 or other.bet == play.bet))
                for other in self.state.players
            )

            # If current player folded remaining.
            if self.state.num_nonfolded_players() == 1:
                self._execute(Table.Event.DETERMINE_WINNER)
                return

            # If this betting round is completed.
            if betting_equal and all(self._queried.values()):
                self._execute(Table.Event.INCREASE_ROUND)
            else:
                # Else we QUERY the other players
                self._schedule(Table.Event.QUERY_PLAYER)
        elif event == Table.Event.DETERMINE_WINNER:
            # Loop over all non-folded players that remain in the game with positive bet
            remaining_players = [
                (
                    idx,
                    play,
                    (
                        PokerHand.best(self.state.cards + play.cards)
                        if len(self.state.cards + play.cards) == 7
                        else 0
                    ),
                )
                for idx, play in enumerate(self.state.players)
                if play.bet > 0 and not play.folded
            ]

            # If there is only one player remaining.
            if len(remaining_players) == 1:
                # Give the entire pot to the player.
                win_idx: int = remaining_players[0][0]

                self._logger.info(f"Player {win_idx} wins {self.state.pot()}!")
                self.state.players[win_idx].money += self.state.pot()
                self._execute(Table.Event.INCREMENT_BUTTONS)
                return
            # Sort on score.
            remaining_players.sort(key=lambda x: x[2])
            max_score = max(x[2] for x in remaining_players)

            # Step 2: Filter out tuples where second value >= min_second
            winner_idx = [x[0] for x in remaining_players if x[2] == max_score]

            # Take Profit.
            self._logger.info(f"Community cards: {self.state.cards}")
            pot: Money = self.state.pot()
            for idx, player, hand in remaining_players:
                if idx in winner_idx:
                    self._logger.info(
                        f"Player {idx} cards: {player.cards}, Best {hand}"
                    )
                    self._logger.info(f"Player {idx} wins €{pot // len(winner_idx)}")
                    player.money += pot // len(winner_idx)
                    player.strategy.win(state, player, pot // len(winner_idx))
                else:
                    player.strategy.win(state, player, 0)

            self._execute(Table.Event.INCREMENT_BUTTONS)
        elif event == Table.Event.INCREMENT_BUTTONS:
            # Reset everything.
            for play in self.state.players:
                play.bet = 0
                play.folded = False
                play.all_in = False
                play.cards = ()
            # Increment the buttons.
            self.state.small_blind_index = self.__search_next_player(
                self.state.small_blind_index
            )
            self.state.big_blind_index = self.__search_next_player(
                self.state.small_blind_index
            )
            self.state.player_at_hand_index = self.__search_next_player(
                self.state.big_blind_index
            )

            self._schedule(Table.Event.NEW_ROUND)
        elif event == Table.Event.INCREASE_ROUND:
            if self.state.round == TableState.Round.PREFLOP:
                self._deal_card_to_table(3, 1)
                self.state.round = TableState.Round.FLOP
            elif self.state.round == TableState.Round.FLOP:
                self._deal_card_to_table(1, 1)
                self.state.round = TableState.Round.RIVER
            elif self.state.round == TableState.Round.RIVER:
                self._deal_card_to_table(1, 1)
                self.state.round = TableState.Round.TURN
            elif self.state.round == TableState.Round.TURN:
                self._schedule(Table.Event.SHOWDOWN)
                return
            self._schedule(Table.Event.START_BETTING_ROUND)
        elif event == Table.Event.SHOWDOWN:
            # If not all cards are on the table. Put them.
            while self.state.round != TableState.Round.TURN:
                self._execute(Table.Event.INCREASE_ROUND)

            # Determine the winner.
            self._execute(Table.Event.DETERMINE_WINNER)
        else:
            assert False, f"Unknown event: {event}"

    def _deal_card_to_table(self, num_cards: int, num_burn_cards: int = 1) -> None:
        for __ in range(num_burn_cards):
            self._deck.sample()
        for __ in range(num_cards):
            card: Card = self._deck.sample()
            self.state.cards = self.state.cards + (card,)

    def _get_player_action(self) -> Action:
        # Obtain the raw action from the strategy run by the player.
        return self.state.current_player().strategy.make_action(  # type: ignore
            TableState.obscure_for_player(self.state, self.state.player_at_hand_index),
            self.state.current_player(),
        )

    def _get_and_implement_player_action(self, quiet: bool = False) -> None:
        self._implement_player_action(self._get_player_action(), quiet)

    def _implement_player_action(self, action: Action, quiet: bool = False):
        # Current player index.
        play_idx: int = self.state.player_at_hand_index

        # Validate the action.
        action = self._validateAction(action)

        # Implement the action.
        self.state.players[play_idx].bet += action.amount
        self.state.players[play_idx].money -= action.amount
        if action.type == Action.Type.FOLD:
            self.state.players[play_idx].folded = True
        elif action.type == Action.Type.ALL_IN:
            self.state.players[play_idx].all_in = True

        self._logger.info(f"Player {play_idx} {action}")

    def _validateAction(self, action: Action) -> Action:
        play_idx: int = self.state.player_at_hand_index
        play_money: Money = self.state.players[play_idx].money
        amount: Money = action.amount
        foldAction = Action(Action.Type.FOLD, 0)

        # Negative betting not allowed.
        if action.amount < 0:
            self._logger.warning(
                f"Player {play_idx} has negative action.amount: {amount}"
            )
            return foldAction

        # Fractional betting not allowed.
        if int(action.amount) != action.amount:
            self._logger.warning(
                f"Player {play_idx} has fractional action.amount: {amount}"
            )
            return foldAction

        # Betting more than the player money not allowed.
        if action.amount > play_money:
            self._logger.warning(
                f"Player {play_idx} chips in {amount} but owns {play_money}"
            )
            return foldAction

        # Warning if the player folds with action.amount > 0
        # The user probably intended Action(Action.Type.FOLD, 0)
        if action.type == Action.Type.FOLD and amount > 0:
            self._logger.warning(f"Player {play_idx} FOLDED with {amount} > 0.")
            return foldAction

        # If we go all in but have money remaining
        if action.type == Action.Type.ALL_IN and amount < play_money:
            self._logger.warning(
                f"Player {play_idx} ALL INed but has €{play_money - amount}"
            )
            return foldAction

        # If we bet the remaining money
        # Silently convert to ALL_IN
        if action.amount == play_money:
            return Action(Action.Type.ALL_IN, play_money)

        if action.amount < self.state.call_amount() and action.type != Action.Type.FOLD:
            self._logger.warning(
                f"Player {play_idx} {action.type.name} {action.amount} which is lower than the required amount {self.state.call_amount()}"
            )
            return foldAction

        # If we RAISE with 0.
        # Silently convert to CHECK.
        if action.amount == 0 and action.type != Action.Type.FOLD:
            return Action(Action.Type.CHECK, 0)

        return action

    # Search for the next active player.
    def __search_next_player(self, p_idx: int) -> int:
        state: TableState = self.state
        n: int = state.num_players()
        p_idx += 1
        p_idx %= n

        while state.players[p_idx].folded or state.players[p_idx].money == 0:
            p_idx += 1
            p_idx %= n
        return p_idx
