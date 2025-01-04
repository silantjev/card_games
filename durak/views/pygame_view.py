from pathlib import Path
import pygame
import sys

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / 'durak'))

from logic import HumanPlayer

BG = (0, 0, 0)
QUIT_KEYS = [pygame.K_ESCAPE, pygame.K_q]
PAUSE_KEYS = [pygame.K_SPACE, pygame.K_RETURN]
UNPAUSE_KEYS = [pygame.K_ESCAPE, pygame.K_q, pygame.K_SPACE, pygame.K_RETURN]
PAUSE_FPS = 15
FPS = 25

# Разрешение
W = 1920
H = 1080

# Оригинальный размер карт: 292 x 440
CARD_ORIG_WIDTH = 292
CARD_ORIG_HEIGHT = 440
CARD_REL_WIDTH = 140 / 1920

CARD_CONTOUR = 1
# CARD_WIDTH = 140 * W // 1920
# CARD_HEIGHT = CARD_WIDTH * (440+CARD_CONTOUR) // (292+CARD_CONTOUR)
HORISONTAL_REL_STEP = 2/3
VERTICAL_REL_STEP = 1/3

def positive_min(a,b):
    if 0 < a < b:
        return a
    return b

class CardRect:
    def __init__(self, card, rect, face_up=True):
        self.card = card
        self.rect = rect
        self.face_up = face_up

class Croupier:
    def __init__(
            self,
            card_style='русский стиль',
            im_dir=ROOT / 'images',
            width=W,
            height=H,
            card_rel_width=CARD_REL_WIDTH,
            countour_size=CARD_CONTOUR,
            black_card_path='black_card.png',
            horizontal_rel_step=HORISONTAL_REL_STEP,
            vertical_rel_step=VERTICAL_REL_STEP,
        ):

        self.width = width
        self.height = height
        self.countour_size = countour_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height)) # Создание окна

        # Загрузим изображения для карт
        dir_path = Path(im_dir) / card_style
        if not dir_path.exists():
            print(f'Error: No folder {card_style}.\nAvailable folders: ')
            print(*[d.name for d in Path(im_dir).glob('*') if d.is_dir() and not d.name.startswith('.')], sep=', ')
            raise ValueError(f"Wrong {card_style=}")

        card_width  = int(card_rel_width * self.width + 0.5)
        card_height = card_width * (CARD_ORIG_HEIGHT+countour_size) // (CARD_ORIG_WIDTH+countour_size)
        self.card_width  = card_width  # размеры вместе с контурами
        self.card_height = card_height
        self.horizontal_step = int(0.5 + card_width*horizontal_rel_step)
        self.vertical_step = int(0.5 + card_height*vertical_rel_step)

        if self.countour_size:
            self.black_card = pygame.image.load(im_dir / black_card_path).convert_alpha()
            self.black_card = pygame.transform.scale(self.black_card, (card_width, card_height))
            self.horizontal_black_card = pygame.transform.rotate(self.black_card, 90)
            card_height -= 2 * self.countour_size  # без контуров
            card_width -= 2 * self.countour_size

        card_file_names = [f"{i:02d}.gif" for i in range(36)]
        card_file_names.append("37.gif") # рубашка
        assert len(card_file_names) == 37
        # Порядок мастей: крести, черви, бубны, пики
        # Порядок карт: 6, 7, ..., король, туз
        self.card_images = []
        for card_file_name in card_file_names:
            card_path = dir_path / card_file_name
            assert card_path.exists(), f'No file {card_path}'
            image = pygame.image.load(card_path).convert_alpha()
            image = pygame.transform.scale(image, (card_width, card_height))
            self.card_images.append(image)

        self.horizontal_back = pygame.transform.rotate(self.card_images[-1], 90)

    @staticmethod
    def get_idx(suit, rank):
        if suit == 4: # рубашка
            # return 36
            return -1

        if suit == 0: # пики
            suit = 3
        elif suit == 1: # крести
            suit = 0
        elif suit == 2: # бубны
            suit = 2
        elif suit == 3: # черви
            suit = 1

        return suit * 9 + rank - 6

    def show_card(self, suit, rank, x, y, where='left_top'):
        if where.endswith('bottom'):
            y -= self.card_height
        else:
            assert  where.endswith('top')
        if where.startswith('right'):
            x -= self.card_width
        else:
            assert where.startswith('left')
        if self.countour_size:
            if suit == -1:
                self.screen.blit(self.horizontal_black_card, (x, y))
            else:
                self.screen.blit(self.black_card, (x, y))
            x += self.countour_size
            y += self.countour_size
        if suit == -1:
            image = self.horizontal_back
        else:
            image = self.card_images[self.get_idx(suit, rank)]
        self.screen.blit(image, (x, y))
        return pygame.Rect(x, y, image.get_width(), image.get_height())


class PygameView(Croupier):
    def __init__(self, card_style='русский стиль', fps=FPS):
        super().__init__(card_style)
        self.card_rects = []  # карты, которые можно нажимать
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.clean()

    def clean(self, color=(0,0,0)):
        self.screen.fill(color)

    def show_players(self, players):
        self.card_rects = []
        for site, player in enumerate(players):
            face_up = isinstance(player, HumanPlayer)
            self.show_cards(player, site=site, face_up=face_up)

    def show_cards(self, player, site, face_up):
        # name = player.name
        cards = player.cards
        n_cards = len(cards)
        if n_cards == 0:
            return
        if site == 1:
            where = 'left_bottom'
            space_width = self.width - 3 * self.card_width
            step_x = min(self.horizontal_step, space_width // n_cards)
            step_y = 0
            x = (self.width - (n_cards-1) * step_x - self.card_width) // 2
            y = self.height
        else:
            where = 'left_top' if site == 0 else 'right_top'
            space_height = self.height - 2 * self.card_height
            step_x = 0
            step_y = min(self.vertical_step, space_height // n_cards)
            x = self.width * site // 2
            y = (self.height - (n_cards-1) * step_y - self.card_height) // 2
        for i in range(n_cards):
            card = cards[i]
            if face_up:
                rect = self.show_card(card.suit, card.rank, x=x, y=y, where=where)
                if i != n_cards - 1:
                    w = positive_min(step_x, rect.width)
                    h = positive_min(step_y, rect.height)
                    rect = pygame.Rect(rect.left, rect.top, w, h)
                self.card_rects.append(CardRect(card, rect, face_up=True))
            else:
                self.show_card(4, 0, x=x, y=y, where=where)
            x += step_x
            y += step_y

    def has_card_been_pressed(self, x, y):
        for i, card_rect in enumerate(self.card_rects):
            if card_rect.rect.collidepoint(x, y):
                return i
        return -1


    def show_last_card(self, last_card):
        self.show_card(last_card.suit, last_card.rank, x=self.width//2 - self.card_width//2, y=0)

    def show_deck(self, deck):
        n = len(deck.cards)
        if n == 0:
            return
        last_card = deck.cards[0]
        x = self.width//2 - self.card_width//2
        y = 0
        self.show_card(last_card.suit, last_card.rank, x=x, y=y)
        delta = self.card_height - self.card_width
        y += delta
        x -= delta // 2
        shift = max(2, 2*self.countour_size)
        for _ in range(n-1):
            self.show_card(-1, -1, x=x, y=y)
            x += shift
            y += shift


    def choose_card_loop(self):
        if not self.card_rects:
            return
        while True:
            pygame.display.update()  # Обновление экрана

            event = self.find_event()
            if event == "quit":
                return
            if isinstance(event, int):
                return self.card_rects[event].card

            self.clock.tick(self.fps)  # Задержка на 1000 / self.fps миллисекунд

    def final_loop(self):
        while True:
            pygame.display.update()  # Обновление экрана

            event = self.find_event()
            if event == "quit":
                break

            self.clock.tick(self.fps)  # Задержка на 1000 / self.fps миллисекунд

    def find_event(self, quit_keys=QUIT_KEYS):
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                self.quit()
                sys.exit()
            if (event.type == pygame.KEYDOWN) and (event.key in quit_keys):
                return "quit"
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                card_rect_idx = self.has_card_been_pressed(*event.pos)
                if card_rect_idx >= 0:
                    return card_rect_idx

    def quit(self):
        pygame.quit()

    def show_center(self, center):
        for site, card in center.items():
            assert isinstance(site, int) and 0 <= site < 3
            # center:
            x = (self.width - self.card_width) // 2 
            y = (self.height - self.card_height) // 2 
            x += (site - 1 ) * self.card_width
            if site == 1:
                y += self.card_height // 2

            self.show_card(card.suit, card.rank, x, y)


if __name__ == '__main__':
    from main import main
    main("pygame")
