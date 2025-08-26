"""
This module simulates a game between different player strategies
and visualizes the progression of each player's money over time.

It uses a `Table` class to run the simulation and matplotlib to
generate plots showing how money changes for each player per round.
"""

from poker.Table import Table
from poker.TableState import TableState
from poker.Player import Player


def make_picture_money_over_rounds(
    players: tuple[Player, ...], n_pictures: int = 1, folder: str = "SampleRuns"
) -> None:
    """
    Simulates a game between players and generates plots showing how each player's
    money changes over time, for a specified number of runs.

    Args:
        players (List[Player]): A list of Player instances with assigned strategies and starting money.
        n_pictures (int): Number of simulation plots to generate. Each is a separate game.
        folder (str): Folder path to save the generated images.

    Returns:
        None. Saves plots as JPEG images in the specified folder.
    """

    # Lazy import.
    import matplotlib.pyplot as plt
    import os

    # Ensure the output directory exists
    os.makedirs(folder, exist_ok=True)

    table: Table = Table.construct_withPlayers(players)

    for i in range(n_pictures):
        money_time = {idx: [p.money] for idx, p in enumerate(players)}

        table.reset()
        while not table.done():
            table.step()
            while table.round_underway() and not table.done():
                table.step()

            for idx, p in enumerate(table.state.players):
                money_time[idx].append(p.money)

        winner: Player = table.getWinner()
        print(
            f"Table {i+1} has winning strategy {winner.strategy.__class__.__name__} after {table.round_counter} rounds"
        )
        plt.figure(figsize=(10, 6))  # type: ignore
        for idx, money_history in money_time.items():
            strategy_name = players[idx].strategy.__class__.__name__
            plt.plot(money_history, label=f"Player {idx} ({strategy_name})")  # type: ignore

        plt.title("Player Money over rounds")  # type: ignore
        plt.xlabel("Round")  # type: ignore
        plt.ylabel("Money")  # type: ignore
        plt.legend(title="Players")  # type: ignore
        plt.grid(True)  # type: ignore
        plt.tight_layout()
        plt.savefig(f"{folder}/money_over_rounds_{i+1}.jpeg")  # type: ignore
        plt.close()
