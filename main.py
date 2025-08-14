from poker import TableWithWindow, Table, Player, TableState # type: ignore
from poker import make_picture_money_over_time
from poker import ACaller, Cheater, King

import random

if __name__ == "__main__":

    players = (
        Player(strategy=ACaller(), money=2),
        Player(strategy=Cheater(), money=2),
        # Player(strategy=AFolder(), money=20),
        # Player(strategy=AFolder(), money=30),
        Player(strategy=King(), money=2),
    )

    random.seed(127)

    # Init a starting table state as a brand_new game.
    init = TableState.new_game(players)

    # Create a table with window from the init state and some players.
    table = TableWithWindow(init)
    
    # Alternatively create a table without window and run from there. 
    # table = Table(init, loglevel=Table.LogLevel.DEBUG)
    # while not table.done():
    #     table.step()


    # Benchmark the players
    make_picture_money_over_time(players, n_pictures=10)
