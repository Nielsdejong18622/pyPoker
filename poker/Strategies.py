from poker import Strategy
from poker.Action import Action
from poker.Player import Player
from poker.TableState import TableState
from poker.Money import Money
from poker.Cards import Cards
from poker.Card import Card
from poker.PokerHand import PokerHand

import random

"""
Example Poker Strategies

This module contains several sample `Strategy` subclasses, used to demonstrate different 
behaviors a player might follow in a poker game. Each strategy determines what action a player 
takes on their turn by implementing:

    def make_action(self, tablestate: TableState, me: Player) -> Action

Each returned `Action` is validated by the dealer and then applied to the current `TableState`.

--------------------------------------------------------
Action Types You Can Use:

The `Action` class supports the following action types:

- Action.Type.FOLD
    The player forfeits the round.
    Use: Action(Action.Type.FOLD, 0)

- Action.Type.RAISE
    The player increases the current bet.
    Use: Action(Action.Type.RAISE, tablestate.call_amount() + raise_amount)
    
- Action.Type.CALL
    The player matches the current highest bet.
    Make sure that the minimum required amount (call_amount) is used. 
    Use: Action(Action.Type.CALL, tablestate.call_amount())

- Action.Type.CHECK
    The player passes the action without betting.
    Equivalent to Action(Action.Type.CALL, 0) 
    Equivalent to Action(Action.Type.RAISE, 0)
    Use: Action(Action.Type.CHECK, 0)

- Action.Type.ALL_IN
    The player bets all their remaining money.
    Equivalent to Action(Action.Type.RAISE, me.money)
    Equivalent to Action(Action.Type.CALL, me.money)
    Use: Action(Action.Type.ALL_IN, me.money)

--------------------------------------------------------
Validation Rules (Enforced Automatically):

The dealer will validate and correct or reject invalid actions:

- Negative amounts are not allowed (converted to FOLD)
- Fractional amounts are not allowed (converted to FOLD)
- Raising/Betting/Calling more than the player's money is not allowed (converted to FOLD)
- Betting more than the player's current money is not allowed (converted to FOLD)
- Folding with a non-zero amount is silently allowed (converted to FOLD)

- Declaring ALL_IN without actually betting all remaining money is invalid (converted to FOLD)
- Betting exactly all remaining money is silently converted to ALL_IN
- Any non-FOLD action with amount == 0 is silently converted to CHECK

Each strategy will play the optimal move when available, in that case make_action(...) will not be called.
Each strategy will also never bet against itself, for example when all other players are all-in.

--------------------------------------------------------
Example Strategies in This Module:

- AFolder  — Always folds.
- Cheater  — Tries (and fails) to illegally modifies the table state before folding.
- ACaller  — Always calls the minimum required to stay in the round.
- King     — Raises if holding a picture card (J, Q, K, A), otherwise calls.

--------------------------------------------------------
Writing Your Own Strategy:

To implement a new strategy:

1. Subclass the `Strategy` class.
2. Override the method:
       def make_action(self, tablestate: TableState, me: Player) -> Action
3. Return a valid `Action` based on the state of the table and your player's cards.
4. Watch for Warnings from the table
Example:

    class AggressiveStrategy(Strategy):
        def make_action(self, tablestate: TableState, me: Player) -> Action:
            required = tablestate.call_amount()
            raise = min(3, me.money)
            return Action(Action.Type.RAISE, required + raise)

You can then assign this strategy to a player:

    player = Player(strategy=AggressiveStrategy(), money=20)

"""


# Example strategies.
class AFolder(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        return Action(Action.Type.FOLD, 0)


class Cheater(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        tablestate.current_player().money = 100
        return Action(Action.Type.FOLD, 0)


class ACaller(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        # Call with the minimal amount required!
        return Action(Action.Type.CALL, min(tablestate.call_amount(), me.money))


# Example strategies.
class King(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        required_chip_in: Money = tablestate.call_amount()

        # If we can freely check -> CHECK!
        if required_chip_in == 0:
            return Action(Action.Type.CHECK, 0)

        # If we do not hold a picture card (A, K, Q, J) -> Fold.
        if not Cards.contain_picture(me.cards):
            return Action(Action.Type.FOLD, 0)

        # If we do hold a picture card and we have funds!
        if me.money > required_chip_in + 2:
            return Action(Action.Type.RAISE, required_chip_in + 2)

        # If we hold a picture card we still want to play if the required chip_in is not too much.
        if me.money >= required_chip_in:
            return Action(Action.Type.CALL, required_chip_in)

        # Fold.
        return Action(Action.Type.FOLD, 0)


class ARaiser(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        return Action(Action.Type.RAISE, 10)


class Random(Strategy):

    def __init__(self, aggression: float = 0.2):
        super().__init__()
        self.agression = aggression

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        # print(f"RandomStrategy! min_call: {tablestate.call_amount()} money: {me.money}, already bet:{me.bet}, pot on the line: {tablestate.pot()}")
        # Draw a U(0, 1)
        unif = random.random()

        min_call_chip_in: Money = tablestate.call_amount()

        # If we have sufficient money to continue.
        if me.money > min_call_chip_in:

            if unif < 1 - self.agression:
                # We call.
                return Action(Action.Type.CALL, min_call_chip_in)

            # Else we raise.
            additional: Money = random.randint(min_call_chip_in, me.money)
            return Action(Action.Type.RAISE, additional)

        # We fold.
        return Action(Action.Type.FOLD, 0)


class CopyCat(AFolder):

    def __init__(self):
        self.play_as: Strategy = AFolder()
        self.play_for_steps: int = 10
        self.steps = 0

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        self.steps += 1

        # # If it is time to switch.
        if self.steps == self.play_for_steps:
            self.steps = 0
            good_player = tablestate.get_big_stack_bully()

            # Avoid playing as ourselves.
            if not isinstance(good_player.strategy, CopyCat):
                self.play_as = good_player.strategy

        return self.play_as.make_action(tablestate, me)


class Human(Strategy):

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        print(
            f"Player {tablestate.player_at_hand_index} with Human strategy requires input!"
        )
        userInput = input("Continue (Y/N)?:")
        if userInput.lower() == "y":
            bet = int(input("How much to chip-in?:"))
            return Action(Action.Type.CALL, bet)
        return Action(Action.Type.FOLD, 0)


class Reinforcement(Strategy):

    def __init__(self):
        super().__init__()

        self.value_map = {
            (face1, face2): [
                50
                + 5 * (face1.value > 10 or face2.value > 10)
                + 5 * (face1.value == face2.value),
                0,
            ]
            for face1 in Card.Face
            for face2 in Card.Face
        }

        # print(self.value_map)

    def win(self, tablestate, me, amount):
        # Learning step.
        state = (me.cards[0].face, me.cards[1].face)
        rstate = (me.cards[1].face, me.cards[0].face)
        lr: float = 0.05
        self.value_map[state][1] += 1
        n: int = self.value_map[state][1]
        self.value_map[state][0] += (amount - self.value_map[state][0]) / n
        self.value_map[rstate] = self.value_map[state]
        return super().win(tablestate, me, amount)

    def make_action(self, tablestate: TableState, me: Player) -> Action:
        req_to_play: Money = tablestate.call_amount()

        # If we can freely check -> CHECK!
        if req_to_play == 0:
            return Action(Action.Type.CHECK, 0)

        # If it is not worth it.
        value_to_play: float = self.value_map[(me.cards[0].face, me.cards[1].face)][0]
        value_to_play += random.normalvariate()
        if me.bet >= value_to_play:
            return Action(Action.Type.FOLD, 0)

        # If it is worth it and we have sufficient funds!
        additional_raise = int(random.random() * (me.money // 4) + req_to_play)
        if me.money > req_to_play + additional_raise:
            return Action(Action.Type.RAISE, req_to_play + additional_raise)

        # If we hold a picture card we still want to play if the required chip_in is not too much.
        if me.money >= req_to_play and (me.money // 4) >= req_to_play:
            return Action(Action.Type.CALL, req_to_play)

        # Fold.
        return Action(Action.Type.FOLD, 0)
