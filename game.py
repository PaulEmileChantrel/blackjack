from player import Player, Dealer, HumanGambler, RandomComputerGambler,SmartComputerGambler,GeniusComputerPlayer
import random
import time
import matplotlib.pyplot as plt

class CardGame:
    def __init__(self,number_of_deck=1):
        self.deck = self.create_cards()*number_of_deck
        self.shuffle_deck()
        self.card_out = [] #card tossed out of the deck
        self.used_deck = 0
        self.number_of_deck = number_of_deck
        self.card_count = 0
        self.true_count = 0

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
        if len(deck_str)+len(card_out_str)!=52*self.number_of_deck:
            raise ValueError


    def draw_card(self,update = True):
        if self.deck:
            card = self.deck.pop(0)
            #We don't want to update the card count when the dealer draw the hidden card
            if update:
                self.update_card_count(card[0])
            return card
        else:#no more cards in the deck
            self.deck,self.card_out = self.card_out,[]
            self.used_deck += 1
            self.shuffle_deck()
            self.card_count = 0
            return self.draw_card()

    def update_card_count(self,card_value):
        if card_value >=10 or card_value==1:
            self.card_count -= 1
        elif card_value <=6 and card_value!=1:
            self.card_count +=1
        else:
            #count unchange for 7,8,9
            pass
        print(f'*** The card count is {self.card_count}. ***')
        deck_remaining = len(self.deck)/52 +1
        self.true_count = self.card_count/deck_remaining

    def reinitialize_deck(self):
        self.deck = self.deck+self.card_out
        self.card = []
        self.shuffle_deck()


def calcul_average_pot(players):
    avg_random_pot = 0
    avg_smart_pot = 0
    avg_genius_pot = 0

    rc_player = 100
    sc_player = 100
    gc_player = 100
    for player in players:
        if isinstance(player,RandomComputerGambler):
            avg_random_pot += player.pot
        elif isinstance(player,GeniusComputerPlayer):
            avg_genius_pot += player.pot
        elif isinstance(player,SmartComputerGambler):
            avg_smart_pot += player.pot

    avg_random_pot = avg_random_pot/rc_player #if rc_player !=0 else 0
    avg_smart_pot = avg_smart_pot/sc_player #if sc_player !=0 else 0
    avg_genius_pot = avg_genius_pot/gc_player
    return avg_random_pot,avg_smart_pot,avg_genius_pot

def table_play(game,dealer,players,mini_pause,with_plot=False):
    i,i_max = 0,10000
    if with_plot:

        true_count = [0]
        current_turn = [i]
        avg_random_pot,avg_smart_pot,avg_genius_pot = calcul_average_pot(players)

        avg_random_pot = [avg_random_pot]
        avg_smart_pot = [avg_smart_pot]
        avg_genius_pot = [avg_genius_pot]

    while players and i != i_max:
        print('--------------------')
        print(f'Starting a new turn:')
        print('')
        turn_avg_random_pot,turn_avg_smart_pot,turn_avg_genius_pot,turn_true_count = turn(game,dealer,players,mini_pause)
        if with_plot:
            avg_random_pot.append(turn_avg_random_pot)
            avg_smart_pot.append(turn_avg_smart_pot)
            avg_genius_pot.append(turn_avg_genius_pot)
            true_count.append(turn_true_count)
            i +=1
            current_turn.append(i)


    print('-----------')
    print('No player left!')
    if with_plot:
        plt.plot(current_turn, avg_random_pot)
        plt.plot(current_turn,avg_smart_pot)
        plt.plot(current_turn,avg_genius_pot)
        plt.xlabel('Number of turns')
        plt.ylabel('Average Pot ($)')
        plt.legend(['Random Play','Smart Play','Genius Play'])
        plt.title('Evolution of the average pot across time')

        plt.show()
        plt.plot(current_turn,true_count)
        plt.show()


def turn(game,dealer,players,mini_pause):
    # Choose bet size
    for player in players:
        player.choose_bet_size(game.true_count)

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
        cap = list(calcul_average_pot(players))
        cap.append(game.true_count)
        return cap

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
    #game.print_deck()
    # if game.hand_was_splitted:
    #     raise ValueError
    cap = list(calcul_average_pot(players))
    cap.append(game.true_count)
    return cap

def main():

    #ms of pause between moves
    mini_pause = 0

    game = CardGame(4)
    game.print_deck()

    dealer = Dealer(mini_pause)
    player = [SmartComputerGambler(10000,mini_pause),SmartComputerGambler(10000,mini_pause),RandomComputerGambler(10000,mini_pause)]
    table_play(game,dealer,player,mini_pause)

def main_measure():
    # Test Random player Vs Smart player

    #ms of pause between moves
    mini_pause = 0

    game = CardGame(140)
    game.print_deck()

    dealer = Dealer(mini_pause)
    players = []
    for _ in range(1000):
        players.append(RandomComputerGambler(10000,mini_pause,False))
    for _ in range(1000):
        players.append(SmartComputerGambler(10000,mini_pause,False))

    for _ in range(1000):
        players.append(GeniusComputerPlayer(10000,mini_pause,False))


    table_play(game,dealer,players,mini_pause,with_plot=True)

if __name__=='__main__':
    #main()
    main_measure()
