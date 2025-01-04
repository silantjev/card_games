
class ConsoleView:
    def __init__(self):
        pass

    def show_humans_cards(self, player):
        print(f"{player.name}'s cards:", *player.cards)

    def show_last_card(self, last_card):
        print("Last card in the deck:", last_card)

