from poker.Table import Table
from poker.Card import Card
from poker.TableState import TableState
from poker.Player import Player

from dataclasses import dataclass
from typing import Callable
import tkinter as tk
import math
import logging


class TableWithWindow(Table):

    @dataclass
    class WindowSettings:
        CARD_WIDTH = 40
        CARD_HEIGHT = 60
        PLAYER_RADIUS_RATIO = 0.35

    def __init__(
        self,
        players: tuple[Player, ...],
        windowsettings: WindowSettings = WindowSettings(),
        loglevel=logging.DEBUG,
    ):
        super().__init__(TableState.new_game(players), loglevel=loglevel)

        # Add windows.
        self.windowsettings = windowsettings

        self._root = tk.Tk()
        self._root.title("Poker Table")

        # Canvas (main drawing area)
        self._canvas = tk.Canvas(self._root, bg="green", width=1024, height=800)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # Controls frame
        self._controls = tk.Frame(self._root)
        self._controls.pack()

        # Add buttons.
        self._add_button("Reset", self.reset)
        self._add_button("Next", self.__step_and_draw)
        self._add_button("▶ Play", self.__start_play)
        self._add_button("⏸ Pause", command=self.__pause_play)

        # Speed slider.
        self._speedlabel = tk.Label(self._controls, text="Speed:").pack(side=tk.LEFT)
        self._speed_slider = tk.Scale(
            self._controls, from_=0, to=2000, orient=tk.HORIZONTAL
        )
        self._speed_slider.set(1000)  # type: ignore # default to 1 second
        self._speed_slider.pack(side=tk.LEFT, padx=5)

        # Escape closes window
        self._root.bind("<Escape>", lambda e: self._root.destroy())
        self._root.bind("<space>", lambda e: self.__step_and_draw())

        # Resize handling
        self._canvas.bind("<Configure>", self.__on_resize)
        self.canvas_width = self._canvas.winfo_reqwidth()
        self.canvas_height = self._canvas.winfo_reqheight()

        # Drawing state
        self.running = False  # autoplay state
        self._root.mainloop()

    def _add_button(self, text: str, command: Callable[[], None]) -> None:
        self._button = tk.Button(self._controls, text=text, command=command)
        self._button.pack(side=tk.LEFT, padx=5)

    def __on_resize(self, event: tk.Event) -> None:
        if self._root:
            self.canvas_width = event.width
            self.canvas_height = event.height
            self._canvas.delete("all")
        if self.state:
            self.draw(self.state)

    # def _execute(self, event: Event) -> None:
    #     return super()._execute(event, quiet=False)

    def draw(self, state: "TableState") -> None:
        """Draw the current TableState on the canvas."""
        if not self._canvas:
            return
        self.state = state
        self._canvas.delete("all")

        self._root.title(f"PokerTable: {state.round}")
        PLAYER_RADIUS_RATIO = self.windowsettings.PLAYER_RADIUS_RATIO
        CARD_WIDTH = self.windowsettings.CARD_WIDTH
        CARD_HEIGHT = self.windowsettings.CARD_HEIGHT

        cx, cy = self.canvas_width // 2, self.canvas_height // 2
        radius = int(min(self.canvas_width, self.canvas_height) * PLAYER_RADIUS_RATIO)

        n: int = state.num_players()

        # Draw players around the table
        self._canvas.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius, fill="green"
        )
        for i in range(n):
            angle = 2 * math.pi * i / n
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            self._draw_player(i, px, py, state)

        # Draw community cards
        spacing = CARD_WIDTH + 10
        start_x = cx - (len(state.cards) * spacing) // 2
        for i, card in enumerate(state.cards):
            x = start_x + i * spacing
            y = cy - CARD_HEIGHT // 2
            self._draw_card(x, y, card, face_up=True)

    def _draw_card(self, x: float, y: float, card: Card, face_up: bool = True):
        fill = {
            Card.Suit.c: "ORANGE",
            Card.Suit.d: "PINK",
            Card.Suit.h: "GREY",
            Card.Suit.s: "YELLOW",
        }[card.suit]
        CARD_WIDTH = self.windowsettings.CARD_WIDTH
        CARD_HEIGHT = self.windowsettings.CARD_HEIGHT
        self._canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT, fill=fill)
        self._canvas.create_text(
            x + CARD_WIDTH / 2, y + CARD_HEIGHT / 2, text=str(card)
        )

    def _draw_player(self, index: int, x: float, y: float, state: "TableState"):
        player: Player = state.players[index]

        folded = player.folded
        at_hand = index == state.player_at_hand_index
        money = player.money
        bet = player.bet

        color = "purple"
        if at_hand:
            color = "blue"
            self._canvas.create_text(x, y + 50, text=f"${money}", fill="white")
            self._canvas.create_text(x, y + 65, text=f"Bet: {bet}", fill="white")
        elif player.all_in:
            color = "gold"
            self._canvas.create_text(x, y + 50, text=f"${money}", fill="white")
            self._canvas.create_text(x, y + 65, text=f"Bet: {bet}", fill="white")
        elif player.money == 0:
            color = "green"
        else:
            self._canvas.create_text(x, y + 50, text=f"${money}", fill="white")
            self._canvas.create_text(x, y + 65, text=f"Bet: {bet}", fill="white")

        self._canvas.create_oval(x - 30, y - 30, x + 30, y + 30, fill=color)
        self._canvas.create_text(x, y - 40, text=f"Player {index}", fill="white")

        # Draw buttons.
        if index == state.small_blind_index:
            self._canvas.create_text(x, y, text="SMALL")
        elif index == state.big_blind_index:
            self._canvas.create_text(x, y, text="BIG")

        # Draw hole cards for non-folded players with cards.
        if len(player.cards) == 2 and not folded:
            CARD_WIDTH = self.windowsettings.CARD_WIDTH
            self._draw_card(x + CARD_WIDTH, y, player.cards[0], face_up=True)
            self._draw_card(x + CARD_WIDTH * 2, y, player.cards[1], face_up=True)

    def __start_play(self) -> None:
        if not self.running:
            self.running = True
            self.__auto_play()

    def __pause_play(self) -> None:
        self.running = False

    def __step_and_draw(self) -> None:
        self.step()  # Simulate game progression
        self.draw(self.state)

    def __auto_play(self) -> None:
        if self.running:
            self.__step_and_draw()
            delay = self._speed_slider.get()
            self._root.after(int(delay), self.__auto_play)
