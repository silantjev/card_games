from random import shuffle
from termcolor import colored

class Card:
    def __init__(self, suit, rank, colored=True):
        self.suit = suit
        self.rank = rank
        self.colored = colored

    def __eq__(self, other):
        return (self.suit == other.suit) and (self.rank == other.rank)

    def __lt__(self, other):
        if self.suit < other.suit:
            return True
        if self.suit > other.suit:
            return False
        return self.rank > other.rank

    def __repr__(self):
        if self.suit == 0:
            r = '♠'
        elif self.suit == 1:
            r = '♣'
        elif self.suit == 2:
            r = '♦'
        elif self.suit == 3:
            r = '♥'
        if self.rank < 11:
            # return r + f'{self.rank+7}'
            return r + chr(int("245F", 16) + self.rank)
        if self.rank == 11:
            return r + 'В'
        if self.rank == 12:
            return r + 'Д'
        if self.rank == 13:
            return r + 'К'
        if self.rank == 14:
            return r + 'Т'

    def __str__(self):
        if self.colored:
            if self.suit < 2:
                return colored(self.__repr__(), 'blue')
            else:
                return colored(self.__repr__(), 'red')
        else:
            return self.__repr__()

        

class Deck:
    def __init__(self, min_rank=6, colored=True):
        self.cards = [] # list of Card
        for suit in range(4):
            for rank in range(6, 15):
                self.cards.append(Card(suit, rank, colored))

    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        shuffle(self.cards)

    def give(self, number):
        result = []
        while self.cards and len(result) < number:
            result.append(self.cards.pop())
        return result

class BasePlayer:
    def __init__(self):
        self.cards = []

    def get(self, cards):
        self.cards.extend(cards)
        self.cards.sort()

    def has_suit(self, suit):
        for card in self.cards:
            if card.suit == suit:
                return True
        return False

    def find_card(self, suit, rank):
        for i, card in enumerate(self.cards):
            if (card.suit == suit) and (card.rank == rank):
                return i

    def ranks_and_idx_for_suit(self, suit):
        ranks_with_idx = []
        for i, card in enumerate(self.cards):
            if card.suit == suit:
                ranks_with_idx.append((card.suit, i))
        return ranks_with_idx

    def give(self, suit, rank):
        i = self.find_card(suit, rank)
        if i is None:
            return
        return self.cards.pop(i)

    def say_trump(self, suit):
        self.trump = suit


if __name__ == '__main__':
    player1 = BasePlayer()
    player2 = BasePlayer()
    player3 = BasePlayer()
    players = [player1, player2, player3]
    deck = Deck()
    print(f"deck has {len(deck)} cards")
    deck.shuffle()
    for i in range(3):
        cards = deck.give(12)
        players[i].get(cards)

    for i in range(3):
        print(f"Player{i}:", *players[i].cards)
