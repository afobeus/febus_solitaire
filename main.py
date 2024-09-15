import pygame
import random
import os

# Константы
WIDTH, HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 72, 96
FPS = 30
NUM_FOUNDATIONS = 4
NUM_PILES = 7

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Solitaire Klondike')
clock = pygame.time.Clock()


# Загрузка карт
def load_cards():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    # return [f'{rank}_of_{suit}.png' for suit in suits for rank in ranks]
    return [f'card.png' for suit in suits for rank in ranks]


# Класс для карт
class Card(pygame.sprite.Sprite):
    def __init__(self, suit, rank):
        super().__init__()
        self.suit = suit
        self.rank = rank
        # self.image = pygame.image.load(os.path.join('cards', f'{rank}_of_{suit}.png'))
        self.image = pygame.image.load(os.path.join('cards', f'card.png'))
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.face_up = True

    def is_valid_move(self, target):
        if not target:
            return False
        if isinstance(target, Foundation):
            return self.rank == 'A' if not target.cards else \
                self.suit == target.cards[-1].suit and \
                self.rank == ranks[ranks.index(target.cards[-1].rank) + 1]
        elif isinstance(target, Pile):
            return self.rank in valid_moves_pile(self, target)
        return False


class Foundation(pygame.sprite.Sprite):
    def __init__(self, suit, x, y):
        super().__init__()
        self.suit = suit
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((255, 255, 255))  # Белый фон для области основания


class Pile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((255, 255, 255))  # Белый фон для области колоды


# Проверка допустимых перемещений в колонках
def valid_moves_pile(card, pile):
    rank_order = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']
    if not pile.cards:
        return []
    top_card = pile.cards[-1]
    top_rank_index = rank_order.index(top_card.rank)
    valid_ranks = rank_order[:top_rank_index]
    return valid_ranks


# Функция для создания начальной раскладки карт
def create_game():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [Card(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)

    piles = [Pile(50 + i * (CARD_WIDTH + 10), 50) for i in range(NUM_PILES)]
    for i in range(NUM_PILES):
        for j in range(i + 1):
            card = deck.pop()
            card.rect.topleft = (piles[i].rect.x, piles[i].rect.y + j * 20)
            card.face_up = (j == i)  # Только верхняя карта перевернута лицом вверх
            piles[i].cards.append(card)

    foundations = [Foundation(suit, 700, 50 + i * (CARD_HEIGHT + 10)) for i, suit in enumerate(suits)]
    return deck, piles, foundations


# Основной цикл игры
def main():
    global ranks
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    deck, piles, foundations = create_game()
    all_sprites = pygame.sprite.Group()
    for pile in piles:
        all_sprites.add(*pile.cards)
    for foundation in foundations:
        all_sprites.add(foundation)

    dragging_card = None
    dragging_offset = (0, 0)
    source_pile = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for card in all_sprites:
                    if isinstance(card, Card) and card.rect.collidepoint(pos) and card.face_up:
                        dragging_card = card
                        dragging_offset = (card.rect.x - pos[0], card.rect.y - pos[1])
                        for pile in piles:
                            if card in pile.cards:
                                source_pile = pile
                                break
                        break

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging_card:
                    x, y = pygame.mouse.get_pos()
                    target = None
                    for t in foundations + piles:
                        if t.rect.collidepoint(x, y):
                            target = t
                            break
                    if target and dragging_card.is_valid_move(target):
                        if isinstance(target, Foundation):
                            if not target.cards or dragging_card.rank == 'A' or \
                                    (target.cards[-1].suit == dragging_card.suit and
                                     ranks.index(dragging_card.rank) == ranks.index(target.cards[-1].rank) + 1):
                                target.cards.append(dragging_card)
                        elif isinstance(target, Pile):
                            if not target.cards or \
                                    (target.cards[-1].rank in valid_moves_pile(dragging_card, target) and
                                     target.cards[-1].suit != dragging_card.suit):
                                target.cards.append(dragging_card)
                        if source_pile:
                            source_pile.cards.remove(dragging_card)
                        dragging_card.rect.topleft = target.rect.topleft
                    dragging_card = None
                    source_pile = None

            if event.type == pygame.MOUSEMOTION:
                if dragging_card:
                    dragging_card.rect.x = event.pos[0] + dragging_offset[0]
                    dragging_card.rect.y = event.pos[1] + dragging_offset[1]

        screen.fill((0, 128, 0))  # Цвет фона
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
