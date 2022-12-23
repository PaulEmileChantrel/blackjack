from player import Player, Dealer, HumanGambler, RandomComputerGambler,SmartComputerGambler
import random
import time
class CardGame:
    def __init__(self):
        self.deck = self.create_cards()
        self.shuffle_deck()
        self.card_out = [] #card tossed out of the deck
        self.used_deck = 0

        self.hand_was_splitted = False #for debugging
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
        card_out_str = [str(card[0])+card[1] for card in self.card_out]
        print(f'The deck has {len(deck_str)} cards left')
        print(f'Total cards : {len(deck_str)+len(card_out_str)}.')
        print(f'{self.used_deck} deck used')
        print(deck_str)
        print(card_out_str)
        if len(deck_str)+len(card_out_str)!=52:
            raise ValueError


    def draw_card(self):
        if self.deck:
            card = self.deck.pop(0)
            #self.card_out.append(card)
            return card
        else:#no more cards in the deck
            self.deck,self.card_out = self.card_out,[]
            self.used_deck += 1
            self.shuffle_deck()
            return self.draw_card()

    def reinitialize_deck(self):
        self.deck = self.deck+self.card_out
        self.card = []
        self.shuffle_deck()



def table_play(game,dealer,players,mini_pause):

    while player:

        print('--------------------')
        print(f'Starting a new turn:')
        print('')
        turn(game,dealer,players,mini_pause)
    print('-----------')
    print('No player left!')


def turn(game,dealer,players,mini_pause):
    # Choose bet size
    for player in players:
        player.choose_bet_size()

    #The dealer draw his cards
    dealer.draw_first_cards(game)

    time.sleep(mini_pause)
    #The players draw their cards
    for player in players:
        player.draw_first_cards(game)


    if dealer.players_need_insurance:
        for player in players:
            player.take_insurance()

    # Check for dealer Blackjack
    dealer_blackjack = dealer.hands[0].blackjack()

    if dealer.players_need_insurance:
        if dealer_blackjack:
            print('Paying insurance')
            for player in players:
                #if the player is not insured-> insurance_bet = 0
                player.pot += 3*player.insurance_bet #2:1 payout

        else :
            print('The Dealer doen\'t have a Blackjack, the insurance is lost')
            for player in players:
                player.insurance_bet = 0




    # Check for Blackjack
    for player in players:
        if player.hands[0].blackjack():
            if dealer_blackjack:
                player.equal_hand()
            else:
                player.won_blackjack()

            player.hands[0].toss_hand(game)
            player.hands.remove(player.hands[0])

    #No insurance concept for now
    if dealer_blackjack:
        for player in players:
            if player.hands:
                player.lost_hand()
                player.hands[0].toss_hand(game)
                player.hands.remove(player.hands[0])
        #The turn is over
        players = Player.remove_loser(players)
        dealer.hands[0].toss_hand(game)
        dealer.hands = []
        return

    dealer_card = dealer.hands[0].hand[0]
    # Here, the dealer does not have a blackjack
    # And the remaining player neither
    for player in players:
        print('')
        if player.hands:
            print(f'Player {player.player_id} turn:')
            time.sleep(mini_pause)
            player.get_moves(game,dealer_card)

    # The dealer turn
    print('')
    print('The Dealer is playing:')
    time.sleep(mini_pause)
    dealer_cards = dealer.hands[0].get_printable_card()
    print(f'The Dealer cards are [{dealer_cards[0]}] and [{dealer_cards[1]}]')
    print(f'The Dealer score is {dealer.hands[0].hand_score()}')
    dealer.make_move(game)
    print('')

    if dealer.status =='blown_up':
        #every remaining hands won
        for player in players:
            for hand in player.hands:
                player.won_hand()
                hand.toss_hand(game)
            player.hands = []
            player.bet = 0


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
                hand.toss_hand(game)
            player.hands = []
            player.bet = 0

    #Print player pot
    print('--------------------')
    pot_str = "The player pots are : "
    for player in players:
        pot_str +=f"{player.pot} for Player {player.player_id}, "
    pot_str = pot_str[:-2]
    print(pot_str)

    #Remove player with 0$ pot
    players = Player.remove_loser(players)

    # End of turn
    game.print_deck()
    # if game.hand_was_splitted:
    #     raise ValueError
    return


if __name__=='__main__':

    mini_pause = 0
    game = CardGame()
    game.print_deck()

    dealer = Dealer(mini_pause)
    player = [SmartComputerGambler(10000,mini_pause),SmartComputerGambler(10000,mini_pause),RandomComputerGambler(10000,mini_pause)]
    table_play(game,dealer,player,mini_pause)
