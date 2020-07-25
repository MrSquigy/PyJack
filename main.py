from sys import exit

from src.pyjack import Game, GameOver


def next_player(game: Game) -> None:
    try:
        game.next_player()
    except GameOver:
        print("\nGame over!")
        print(game.game_over())
        exit()


num_players = 3
game = Game()
game.start_game(num_players)

while not game.finished():
    turn = input(game.get_turn_status() + " Type 'hit' to hit or leave empty to stay: ")

    if turn.casefold() == "hit":
        res = game.hit()
        print(f"You got: {res}")
        if res == "Bust":
            next_player(game)
    else:
        next_player(game)
