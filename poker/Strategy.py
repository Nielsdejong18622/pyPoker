# from poker.TableState import TableState
# from poker.Player import Player
from poker.Action import Action
from poker.Money import Money
from abc import ABC, abstractmethod


class Strategy(ABC):

    @abstractmethod
    def make_action(self, tablestate: "TableState", me: "Player") -> Action:  # type: ignore
        """Subclasses must implement this method"""
        pass

    def win(self, tablestate: "TableState", me: "Player", amount: Money) -> None:
        pass
