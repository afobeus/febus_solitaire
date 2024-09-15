import pygame
import random
import os

WIDTH, HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 105, 140
BETWEEN_CARDS = 25
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
        # self.rect.topleft = (0, 0) ???
        self.static_cords = (0, 0)
        self.face_up = False

    def change_face_state(self):
        if self.face_up:
            self.image = self.face_down_image
        else:
            self.image = self.face_up_image
        self.face_up = not self.face_up


class Container(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.cards = []
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.collision_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.fill((255, 255, 255))


class Foundation(Container):
    def __init__(self, suit, x, y):
        super().__init__(x, y)
        self.suit = suit

    def is_valid_card(self, card: Card) -> bool:
        """Returns True if given cards is valid for this foundation else False"""
        if not self.cards:
            return card.suit == self.suit and card.rank == 'A'
        top_card = self.cards[-1]
        return card.suit == self.suit and rank_order.index(card.rank) + 1 == rank_order.index(top_card.rank)

    def append_card(self, card):
        card.static_cords = self.rect.topleft
        self.cards.append(card)

    def remove_card(self):
        pass


class Pile(Container):
    def __init__(self, x, y):
        super().__init__(x, y)

    def is_valid_card(self, card: Card) -> bool:
        """Returns True if given cards is valid for this pile else False"""
        if not self.cards:
            return True
        top_card = self.cards[-1]
        return rank_order.index(top_card.rank) == rank_order.index(card.rank) - 1 and \
            colors_by_suits[top_card.suit] != colors_by_suits[card.suit]

    def append_card(self, card):
        card.static_cords = self.collision_rect.topleft[0], self.collision_rect.topleft[1] + BETWEEN_CARDS
        self.cards.append(card)
        self.collision_rect = card.rect

    def remove_card(self):
        self.cards.pop()
        if self.cards and not self.cards[-1].face_up:
            self.cards[-1].change_face_state()


def create_game():
    deck = [Card(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)

    piles = [Pile(50 + i * (CARD_WIDTH + 10), 50) for i in range(NUM_PILES)]
    for i in range(NUM_PILES):
        for j in range(i + 1):
            card = deck.pop()
            card.rect.topleft = (piles[i].rect.x, piles[i].rect.y + j * BETWEEN_CARDS)
            card.static_cords = card.rect.topleft
            if i == j:
                card.change_face_state()
            piles[i].cards.append(card)
            piles[i].collision_rect.topleft = card.rect.topleft

    foundations = [Foundation(suit, WIDTH - CARD_WIDTH, 50 + i * (CARD_HEIGHT + 10)) for i, suit in enumerate(suits)]
    return deck, piles, foundations


def main():
    deck, piles, foundations = create_game()
    containers = piles + foundations
    all_sprites = pygame.sprite.Group()  # TODO: draw sprites in needed order
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
                mouse_pos = pygame.mouse.get_pos()
                for container in containers:
                    if dragging_card:
                        break
                    for card in container.cards[::-1]:
                        if card.rect.collidepoint(mouse_pos) and card.face_up:
                            dragging_card = card
                            dragging_offset = (card.rect.x - mouse_pos[0], card.rect.y - mouse_pos[1])
                            if isinstance(container, Pile):
                                source_pile = container
                                break

            if event.type == pygame.MOUSEBUTTONUP:
                if not dragging_card:
                    continue
                # x, y = pygame.mouse.get_pos() ???
                target = None
                for container in containers:
                    if container.collision_rect.colliderect(container.collision_rect) and \
                            container.is_valid_card(dragging_card):  # TODO: if card is valid and collides multiple
                        # TODO: containers it is put to the left container, but not to container player ment to put it

                        # TODO: there are some other bugs with multiple valid, discover them
                        target = container
                        break
                if target:
                    target.append_card(dragging_card)
                    all_sprites.remove(dragging_card)
                    all_sprites.add(dragging_card)
                    if source_pile:
                        source_pile.remove_card()
                dragging_card.rect.x, dragging_card.rect.y = dragging_card.static_cords
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
