from typing import List
import requests


class GameOver(Exception):
    """Exception representing game over."""


class Game:
    busted: List[int]

    current_player: int

    deck_id: str

    players: List[List[str]]

    remaining: int

    def __init__(self, num_decks: int = 6) -> None:
        result = requests.get(
            f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={num_decks}"
        )

        if result.status_code != 200:
            print(f"Could not connect to server:\n{result.status_code}: {result.text}")
            return

        result = result.json()
        if result["success"] != True:
            print("Internal API Server Error")
            return

        self.deck_id = result["deck_id"]
        self.remaining = result["remaining"]

    def draw_cards(self, num_cards: int) -> List[str]:
        req = requests.get(
            f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={num_cards}"
        )

        if req.status_code != 200:
            print(f"Could not connect to server:\n{req.status_code}: {req.text}")
            return []

        req = req.json()
        if req["success"] != True:
            print("Internal API Server Error")
            return []

        cards = [card["code"] for card in req["cards"]]
        self.remaining = req["remaining"]
        return cards

    def finished(self) -> bool:
        return self.remaining == 0

    def game_over(self) -> str:
        winner = (-1, 0)
        ret = ""

        for i, player in enumerate(self.players):
            player_total = self.get_hand_total(i)
            player_total = (
                int(player_total)
                if player_total[0] not in ["s", "h"]
                else int(player_total[5:])
            )
            ret += f"Player {i + 1}'s hand: {player} total: {player_total}\n"

            if player_total > winner[1] and i not in self.busted:
                winner = (i, player_total)

        ret += (
            f"Player {winner[0] + 1} is the winner!"
            if winner[0] != -1
            else "The house wins!"
        )

        return ret

    def get_card_value(self, card: str, ace: int = 11) -> int:
        if card[0] in ["J", "Q", "K", "0"]:
            return 10

        if card[0] == "A":
            return ace

        return int(card[0])

    def get_hand_total(self, player: int) -> str:
        total = 0
        aces = 0
        ret = ""

        for card in self.players[player]:
            if card[0] == "A":
                aces += 1

            total += self.get_card_value(card)

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
            ret = "hard "

        ret += str(total)
        if total < 21 and aces > 0:
            ret = "soft " + ret

        return ret

    def get_player_hand(self, player: int) -> List[str]:
        return self.players[player]

    def get_turn_status(self) -> str:
        return f"It is player {self.current_player + 1}'s turn ({self.get_hand_total(self.current_player)})"

    def hit(self) -> str:
        self.players[self.current_player].append(self.draw_cards(1)[0])
        total = self.get_hand_total(self.current_player)

        if total == "21":
            return "Blackjack!"
        elif total[0] == "s" or total[0] == "h":
            if int(total[5:]) == 21:
                return "Blackjack!"
            elif int(total[5:]) > 21:
                self.busted.append(self.current_player)
                return "Bust"

            return total
        elif int(total) < 21:
            return total

        self.busted.append(self.current_player)
        return "Bust"

    def next_player(self) -> None:
        if len(self.busted) == len(self.players):
            raise GameOver

        self.current_player += 1
        if self.current_player in self.busted:
            self.next_player()

        if self.current_player == len(self.players):
            raise GameOver

    def start_game(self, num_players: int = 2) -> None:
        cards = self.draw_cards(num_players * 2)
        self.players = [[] for _ in range(num_players)]
        player = 0

        for card in cards:
            self.players[player].append(card)
            player = (player + 1) % num_players

        self.current_player = 0
        self.busted = []
