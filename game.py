from player import Dealer, HumanGambler, RandomComputerGambler
import random
import time
class CardGame:
    def __init__(self):
        self.deck = self.create_cards()
        self.shuffle_deck()
        self.card_out = [] #card tossed out of the deck

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

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def print_deck(self):
        deck_str = [str(card[0])+card[1] for card in self.deck]
        print(f'The deck has {len(deck_str)} cards left')
        print(deck_str)

    def draw_card(self):
        if len(self.deck)>1:
            card = self.deck.pop(0)
            #self.card_out.append(card)
            return card
        else:#no more cards in the deck
            self.deck,self.card_out = self.card_out,[]
            self.shuffle_deck()
            return self.draw_card()

    def reinitialize_deck(self):
        self.deck = self.deck+self.card_out
        self.card = []
        self.shuffle_deck()



def table_play(game,dealer,players):
    i = 0
    while player:

        print('--------------------')
        print(f'Starting a new turn:')
        print('')
        turn(game,dealer,players)
    print('-----------')
    print('No player left!')


def turn(game,dealer,players):
    # Choose bet size
    for player in players:
        player.choose_bet_size()

    #The dealer draw his cards
    dealer.draw_first_cards(game)
    time.sleep(0.8)
    #The players draw their cards
    for player in players:
        player.draw_first_cards(game)

    # Check for dealer Blackjack
    dealer_blackjack = dealer.hands[0].blackjack()

    # Check for Blackjack
    for player in players:
        if player.hands[0].blackjack():
            if dealer_blackjack:
                player.equal_hand()
            else:
                player.won_blackjack()
            player.hands[0].toss_hand(game)

    #No insurance concept for now
    if dealer_blackjack:
        for player in players:
            if player.hands[0].status != 'done':
                player.lost_hand()
                player.hands[0].toss_hand(game)
        #The turn is over
        return


    # Here, the dealer does not have a blackjack
    # And the remaining player neither
    for player in players:
        print('')
        print(f'Player {player.player_id} turn:')
        
        time.sleep(0.8)
        player.get_moves(game)

    # The dealer turn
    print('')
    print('The Dealer is playing:')
    time.sleep(0.8)
    dealer_cards = dealer.hands[0].get_printable_card()
    print(f'The dealer cards are [{dealer_cards[0]}] and [{dealer_cards[1]}]')
    print(f'The Dealer score is {dealer.hands[0].hand_score()}')
    dealer.make_move(game)
    print('')

    if dealer.status =='blown_up':
        #every remaining hands won
        for player in players:
            for hand in player.hands:
                player.won_hand()
                player.hands.remove(hand)
                hand.toss_hand(game)


    else:
        # hands with higher score won, lower score lose, same score equalized
        dealer_score = dealer.score

        for player in players:
            for hand in player.hands:
                hand_score = hand.score

                if 21>=hand_score > dealer_score:
                    player.won_hand()
                elif hand_score < dealer_score or hand_score>21:
                    player.lost_hand()
                else:
                    player.equal_hand()
                player.hands.remove(hand)
                hand.toss_hand(game)
            player.bet = 0

    #Print player pot
    print('--------------------')
    pot_str = "The player pots are : "
    for player in players:
        pot_str +=f"{player.pot} for {player.player_id}, "
    pot_str = pot_str[:-3]
    print(pot_str)
    #Remove player with 0$ pot
    for player in players:
        if player.pot<=0:
            print(f'Player {player.player_id} is eliminated')
            players.remove(player)
    # End of turn
    game.print_deck()
    return


if __name__=='__main__':


    game = CardGame()
    game.print_deck()

    dealer = Dealer()
    player = [HumanGambler(10000),RandomComputerGambler(10000)]
    table_play(game,dealer,player)
