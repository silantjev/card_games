from logic import Durak, HumanPlayer
from views.console import ConsoleView
from views.pygame_view import PygameView

class DurakController(Durak):
    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(view, PygameView):
            assert self.n == 3
            for i in range(3):
                assert (i == 1) == isinstance(self.players[i], HumanPlayer)
                # player is human iff i==1
        self.view = view
        self.view.show_deck(self.deck)

    def show_desk(self):
        self.view.clean()
        self.view.show_deck(self.deck)
        self.view.show_center(self.desk_center)
        self.view.show_players(self.players)

    def play_a_game(self, first=1):
        while True:
            self.show_desk()
            card = self.view.choose_card_loop()
            if card is None:
                return
            card_put = self.put(card, 1)
            assert (card_put is not None) and (card_put == card)
            self.deal(first=1)

    def finish(self):
        self.show_desk()
        self.view.final_loop()
        self.view.quit()

def main(view_type="pygame"):
    if view_type.lower().startswith("c"):
        view = ConsoleView()
    else:
        view = PygameView()
    game = DurakController(view, n=3, humans={1: 'Vanja'})
    game.play_a_game(first=0)
    # game.finish()

if __name__ == '__main__':
    main("")

