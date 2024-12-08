import pygame
import random
import os

# Interface
WIDTH, HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 105, 140
BETWEEN_CARDS = 20
BORDER = 30
# Game consts
FPS = 60
NUM_FOUNDATIONS = 4
NUM_PILES = 7
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['hearts', 'diamonds', 'clubs', 'spades']
colors_by_suits = {'hearts': 0, 'diamonds': 0, 'clubs': 1, 'spades': 1}
rank_order = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Febus Solitaire')
clock = pygame.time.Clock()


# pops
class Card(pygame.sprite.Sprite):
    def __init__(self, suit, rank):
        super().__init__()
        self.suit, self.rank = suit, rank
        self.face_up_image = pygame.image.load(os.path.join('cards', f'{rank}_of_{suit}.jpg'))
        self.face_up_image = pygame.transform.scale(self.face_up_image, (CARD_WIDTH, CARD_HEIGHT))
        self.face_down_image = pygame.image.load(os.path.join('cards', f'closed_card.png'))
        self.face_down_image = pygame.transform.scale(self.face_down_image, (CARD_WIDTH, CARD_HEIGHT))
        self.image = self.face_down_image
        self.rect = self.image.get_rect()
        self.static_cords = (0, 0)
        self.face_up = False

    def change_face_state(self):
        if self.face_up:
            self.image = self.face_down_image
        else:
            self.image = self.face_up_image
        self.face_up = not self.face_up


class Pile:
    def __init__(self, x, y):
        super().__init__()
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.collision_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((255, 255, 255))

    def is_valid_card(self, card: Card) -> bool:
        """Returns True if given cards is valid for this pile else False"""
        if not self.cards:
            return card.rank == 'K'
        top_card = self.cards[-1]
        return rank_order.index(top_card.rank) == rank_order.index(card.rank) - 1 and \
            colors_by_suits[top_card.suit] != colors_by_suits[card.suit]

    def get_new_card_pos(self):
        return self.rect.topleft[0], self.rect.topleft[1] + BETWEEN_CARDS * len(self.cards)

    def append_group(self, group):
        for card in group.cards:
            card.static_cords = self.get_new_card_pos()
            self.cards.append(card)
            self.collision_rect.topleft = card.static_cords

    def remove_cards(self, count):
        for i in range(min(count, len(self.cards))):
            self.cards.pop()
            if self.cards and not self.cards[-1].face_up:
                self.cards[-1].change_face_state()
            self.collision_rect.topleft = self.get_new_card_pos()


class Foundation(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.collision_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((255, 255, 255))

    def is_valid_card(self, card: Card) -> bool:
        """Returns True if given cards is valid for this foundation else False"""
        if not self.cards:
            return card.rank == 'A'
        top_card = self.cards[-1]
        return card.suit == top_card.suit and rank_order.index(card.rank) + 1 == rank_order.index(top_card.rank)

    def get_new_card_pos(self):
        return self.rect.topleft

    def append_card(self, card):
        card.static_cords = self.get_new_card_pos()
        self.cards.append(card)

    def remove_card(self):
        self.cards.pop()


class Deck(pygame.sprite.Sprite):
    def __init__(self, x, y, cards):
        super().__init__()
        self.cards = cards
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.image.load(os.path.join('cards', f'closed_card.png'))
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

    def is_empty(self):
        return not self.cards

    def take_card(self):
        return self.cards.pop()

    def add_cards(self, cards):
        self.cards.extend(cards)


class Layout(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.cards = []
        self.rect = pygame.Rect(x - CARD_WIDTH - BETWEEN_CARDS, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((210, 210, 210))

    def add_card(self, card):
        self.cards.append(card)
        card.rect.topleft = self.rect.topleft
        card.static_cords = self.rect.topleft
        self.image = self.cards[-1].image.copy()

    def is_empty(self):
        return not self.cards

    def remove_card(self):
        self.cards.pop()
        if not self.cards:
            self.image.fill((210, 210, 210))


class CardsGroup:
    def __init__(self, cards):
        self.cards = cards
        self.static_cords = self.cards[0].rect.topleft
        self.base_rect = self.cards[0].rect

    def update_view(self, event_pos, dragging_offset):
        for index, card in enumerate(self.cards):
            card.rect.x = event_pos[0] + dragging_offset[0]
            card.rect.y = event_pos[1] + dragging_offset[1] + BETWEEN_CARDS * index

    def reset_pos(self):
        for card in self.cards:
            card.rect.topleft = card.static_cords

    def top_card(self):
        return self.cards[0]


def create_game():
    all_cards = [Card(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(all_cards)

    piles = [Pile(BORDER + i * (CARD_WIDTH + 10), BORDER) for i in range(NUM_PILES)]
    for i in range(NUM_PILES):
        for j in range(i + 1):
            if not all_cards:
                break
            card = all_cards.pop()
            card.rect.topleft = (piles[i].rect.x, piles[i].rect.y + j * BETWEEN_CARDS)
            card.static_cords = card.rect.topleft
            if i == j:
                card.change_face_state()
            piles[i].cards.append(card)
            piles[i].collision_rect.topleft = card.rect.topleft

    foundations = [Foundation(WIDTH - CARD_WIDTH - BORDER, BORDER + CARD_HEIGHT + BETWEEN_CARDS +
                              i * (CARD_HEIGHT + 10))
                   for i, suit in enumerate(suits)]

    for card in all_cards:
        card.change_face_state()
    deck = Deck(WIDTH - CARD_WIDTH - BORDER, BORDER, all_cards)
    layout = Layout(WIDTH - CARD_WIDTH - BORDER, BORDER)

    return all_cards, piles, foundations, deck, layout


def main():
    deck, piles, foundations, deck, layout = create_game()
    containers = piles + foundations
    all_sprites = pygame.sprite.Group()
    for pile in piles:
        all_sprites.add(*pile.cards)
    for foundation in foundations:
        all_sprites.add(foundation)
    layout_image = pygame.sprite.Sprite()
    layout_image.rect = pygame.Rect(WIDTH - CARD_WIDTH - BORDER - CARD_WIDTH - BETWEEN_CARDS, BORDER,
                                    CARD_WIDTH, CARD_HEIGHT)
    layout_image.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    layout_image.image.fill((210, 210, 210))
    all_sprites.add(layout_image)
    all_sprites.add(deck)
    all_sprites.add(layout)

    dragging_group = None
    dragging_offset = (0, 0)
    source_container = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if deck.rect.collidepoint(mouse_pos) and not deck.is_empty():
                    next_card = deck.take_card()
                    all_sprites.remove(next_card)
                    all_sprites.add(next_card)
                    layout.add_card(next_card)
                    continue
                if layout.rect.collidepoint(mouse_pos) and not layout.is_empty():
                    cur_card = layout.cards[-1]
                    dragging_offset = (cur_card.rect.x - mouse_pos[0], cur_card.rect.y - mouse_pos[1])
                    all_sprites.remove(cur_card)
                    all_sprites.add(cur_card)
                    dragging_group = CardsGroup([cur_card])
                    source_container = layout
                    continue
                for container in containers:
                    if dragging_group:
                        break
                    for index, card in enumerate(container.cards[::-1]):
                        if card.rect.collidepoint(mouse_pos) and card.face_up:
                            dragging_offset = (card.rect.x - mouse_pos[0], card.rect.y - mouse_pos[1])
                            for c in container.cards[len(container.cards) - index - 1:]:
                                all_sprites.remove(c)
                                all_sprites.add(c)
                            dragging_group = CardsGroup(container.cards[len(container.cards) - index - 1:])
                            source_container = container
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if not dragging_group:
                    continue
                target = None
                for container in containers:
                    if container.collision_rect.colliderect(dragging_group.base_rect) and \
                            container.is_valid_card(dragging_group.top_card()):  # TODO: if card is valid and collides multiple
                        # TODO: containers it is put to the left container, but not to container player ment to put it

                        # TODO: there are some other bugs with multiple valid, discover them
                        target = container
                        break
                if target:
                    if isinstance(target, Foundation) and len(dragging_group.cards) == 1:
                        target.append_card(dragging_group.cards[0])
                    if isinstance(target, Pile):
                        target.append_group(dragging_group)

                    if isinstance(source_container, Pile):
                        source_container.remove_cards(len(dragging_group.cards))
                    if isinstance(source_container, Foundation):
                        source_container.remove_card()
                    if isinstance(source_container, Layout):
                        source_container.remove_card()
                dragging_group.reset_pos()
                dragging_group = None
                source_container = None

            if event.type == pygame.MOUSEMOTION:
                if dragging_group:
                    dragging_group.update_view(event.pos, dragging_offset)

        screen.fill((0, 128, 0))  # background color
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
