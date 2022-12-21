from player import Dealer, HumanGambler, RandomComputerGambler

class CardGame:
    def __init__(self):
        self.deck = self.create_cards()
        random.suffle(self.deck)
        self.card_out = []

    def create_cards(self):
        # [1-13,'H'-'S'-'D'-'C'] ex. [2,'D']
        cards = []
        suits = ['♠','♥','♦','♣']#['S','H','D','C']
        #♠ ♥ ♦ ♣
        for i in range(1,14):
            for j in suits:
                cards.append([i,j])
        return cards

    def toss_card(self,cards):
        #we always have more than one card
        self.card_out += cards

    def suffle_deck(self):
        random.suffle(self.deck)

    def draw_card(self):
        if len(self.deck)<1:
            card = self.deck.pop(0)
            #self.card_out.append(card)
            return card
        else:#no more cards in the deck
            self.deck, = self.card,[]
            self.suffle_deck(self.deck)
            return self.draw_card()

    def reinitialize_deck(self):
        self.deck = self.deck+self.card_out
        self.card = []
        self.suffle_deck(self.deck)

class BlackJack(CardGame):
    def __init__(self):
        super().__init__()


def play(game,dealer,players):
    dealer.draw_first_cards(game)
    for player in players:
        player.draw_first_cards(game)

    for player in players:
        print(f'Player {player.id} turn :')
        player.get_moves(game)
