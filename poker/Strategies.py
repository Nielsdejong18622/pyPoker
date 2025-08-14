from poker import Strategy
from poker.Action import Action
from poker.Player import Player
from poker.TableState import TableState
from poker.Money import Money
from poker.Cards import Cards
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

    def make_action(self, tablestate: TableState, me:Player) -> Action:
        return Action(Action.Type.FOLD, 0)


class Cheater(Strategy):

    # :(
    def make_action(self, tablestate: TableState, me:Player) -> Action:
        tablestate.current_player().money = 100
        return Action(Action.Type.FOLD, 0)

class ACaller(Strategy):

    def make_action(self, tablestate: TableState, me:Player) -> Action:
        # Call with the minimal amount required!
        return Action(Action.Type.CALL, tablestate.call_amount())

# Example strategies.
class King(ACaller):

    def make_action(self, tablestate: TableState, me:Player) -> Action:
        required_chip_in:Money = tablestate.call_amount()
        
        if Cards.contain_picture(me.cards):
            return Action(Action.Type.RAISE, required_chip_in + 2)
        return super().make_action(tablestate, me)


class ARaiser(Strategy):

    def make_action(self, tablestate: TableState, me:Player) -> Action:
        return Action(Action.Type.RAISE, 10)


class Human(Strategy):

    def make_action(self, tablestate: TableState, me:Player) -> Action:
        try:
            print(f"Player {tablestate.player_at_hand_index} requires terminal input!")
            userInput = input("Continue (Y/N)?:")
            print(userInput)
            if userInput.lower() == "y":
                bet = int(input("How much to chip-in?:"))
                return Action(Action.Type.CALL, bet)
            return Action(Action.Type.FOLD, 0)
        except:
            print("Exception in user input occurred, folding!")
            return Action(Action.Type.FOLD, 0)