from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.cards import Card, Deck, BasePlayer

class HumanPlayer(BasePlayer):
    def __init__(self, name):
        super().__init__()
        self.name = name


class Durak:
    def __init__(self, n, humans=[]):
        self.n = n
        self.deck = Deck()
        self.deck.shuffle()
        self.desk_center = {} # Карты посредине стола
        self.last_card = self.deck.cards[0]
        self.trump = self.last_card.suit
        self.players = []
        self.winners = []
        for i in range(n):
            if i in humans:
                player = HumanPlayer(name=humans[i])
            else:
                player = BasePlayer()
            player.say_trump(self.trump)
            self.players.append(player)

        self.first = 0
        self.deal(first=self.first)

    def deal(self, first=0):
        for i in range(self.n):
            j = (first + i) % self.n
            number = max(0, 6 - len(self.players[j].cards))
            if number:
                cards = self.deck.give(number)
                self.players[j].get(cards)

    def put(self, card, site):
        for i in range(self.n):
            player = self.players[i]
            card_given = player.give(card.suit, card.rank)
            if card_given is not None:
                assert card == card_given
                self.desk_center[site] = card
                return card
        
    def finish(self):
        if len(self.winners) == self.n - 1:
            losers = set(range(self.n)) - set(self.winners)
            self.winners.extend(list(losers))
        assert len(self.winners) == self.n
        self.show_winners()



