from poker import *

import random
import os
import pickle

if __name__ == "__main__":
    random.seed(127)

    reinforcement_player = Player(strategy=Reinforcement(), money=40)

    filename = "Reinforcement_map_6000.pkl"
    if os.path.isfile(filename):
        with open(filename, "rb") as f:  # open a text file
            reinforcement_player.strategy.value_map = pickle.load(f)

    players = (
        # Player(strategy=RandomStrategy(aggression=0.2), money=20),
        # Player(strategy=Random(), money=40),
        # Player(strategy=Human(), money=200),
        Player(strategy=ACaller(), money=40),
        reinforcement_player,
        Player(strategy=ACaller(), money=40),
        # Player(strategy=Random(), money=40),
        # Player(strategy=King(), money=40),
    )

    table2 = Table.construct_withPlayers(players)

    # Train reinforcement player.
    try:
        for iter in range(1_000_000):
            pocket_ace = (Card.Face.ACE, Card.Face.ACE)
            deuce = (Card.Face.TWO, Card.Face.SEVEN)
            # print(reinforcement_player.strategy.value_map)
            table2.reset()
            table2.state.players[1].strategy = reinforcement_player.strategy
            while not table2.done():
                table2.step()
            reinforcement_player.strategy = table2.state.players[1].strategy

            print(
                "Training reinforcement_player iteration:",
                iter,
                "Pocket Ace:",
                reinforcement_player.strategy.value_map[pocket_ace],
                "Deuce :",
                reinforcement_player.strategy.value_map[deuce],
                "Winner:",
                table2.getWinner().strategy.__class__.__name__,
            )
            if iter % 1000 == 0:
                with open(
                    f"Reinforcement_map_{iter}.pkl", "wb"
                ) as f:  # open a text file
                    pickle.dump(reinforcement_player.strategy.value_map, f)
    except:
        pass

    # Create a table with window from the init state and some players.
    # table = TableWithWindow(players=players, loglevel=logging.WARNING)

    # # Alternatively create a table without window and run from there.
    # while not table2.done():
    #     table2.step()

    # Benchmark the players
    BenchMarking.make_picture_money_over_rounds(players, n_pictures=20)
