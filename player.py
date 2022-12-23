import math
import random
import time
class Hand:
    def __init__(self,game,card=None):
        if card :
            self.hand = [card,game.draw_card()]
        else:
            self.hand = [game.draw_card(),game.draw_card()]
        self.status = 'playing'
        self.score = self.hand_score()

    def toss_hand(self,game):
        game.toss_card(self.hand)
        del self

    def __del__(self):
        pass
        #print("Object deleted")

    def blackjack(self):
        # return True if the hand is a blackjack
        if len(self.hand) == 2 and ((self.hand[0][0]>=10 and self.hand[1][0]==1) or (self.hand[1][0]>=10 and self.hand[0][0]==1)):
            print('BLACKJACK!')
            return True

    def get_printable_card(self):
        card_str = [self.card_value(card[0])+card[1] for card in self.hand]
        return card_str

    def print_hand(self):
        card_str = self.get_printable_card()
        card_str = ', '.join(card_str)
        print(f'The hand is composed of {card_str}')

    def hand_score(self):
        self.score = 0
        as_num = 0
        #print(self.hand)
        for card in self.hand:

            if card[0] == 1:
                as_num +=1
            else:
                self.score += card[0] if card[0]<=10 else 10
        if as_num:
            self.score += as_num-1 #if only 1 as -> +0
            self.score += 11 if self.score <=10 else 1

        return self.score

    @staticmethod
    def card_value(card_number):
        card_val = ['As','2','3','4','5','6','7','8','9','10','J','Q','K']
        return card_val[card_number-1]

    def add_card(self,game):
        # draw a card and update hand score and status
        card = game.draw_card()
        self.print_hand()
        self.hand.append(card)
        print(f'The card [{self.card_value(card[0])+card[1]}] is drawn.')
        self.print_hand()
        self.score = self.hand_score()
        print(f'The new hand score is {self.score}.')

        if self.score >21:
            self.status = 'blown_up'
        elif self.score == 21:
            self.status = 'done'
        else:
            self.status = 'playing'
    def get_card_number(self):
        return len(self.hand)

    def can_split(self):
        # return True if the player can split his card
        return len(self.hand)==2 and self.hand[0][0] == self.hand[1][0]

    def split(self,game):
        return Hand(game,card = self.hand[0]),Hand(game,card = self.hand[1])

class Player:
    player_number = 0
    def __init__(self,pot,mini_pause):
        self.pot = pot
        self.hands = [] #a player can have multiple hand when he split game
        #self.status = None #playing, done, won, blown_up
        self.mini_pause = mini_pause
        self.insurance_bet = 0

    def draw_first_cards(self,game):
        self.hands.append(Hand(game))



    def get_moves(self,game,dealer_card = None):
        # the current score is lower than 21
        moves = []
        hands = self.hands[:] # in case of a split, we dont want to modify the loop
        for hand in hands:
            print(f'Your score is {hand.score}.')
            move = self.get_move(game,hand,dealer_card)


    def won_hand(self):
        self.pot += 2*self.bet
        print(f'Player {self.player_id} won {self.bet}')

    def lost_hand(self):
        print(f'Player {self.player_id} lost {self.bet}')

    def won_blackjack(self):
        self.pot += 2.5*self.bet
        print(f'Player {self.player_id} won {1.5*self.bet}')


    def equal_hand(self):
        self.pot += self.bet
        print(f'Player {self.player_id} won/lost nothing')

    def choose_bet_size(self):
        if self.random_bet_size:
            self.bet = self.pot if self.pot<2 else random.randint(1,int(self.pot))
        else:
            self.bet = self.pot if self.pot<2 else int(0.2*self.pot)
        self.pot -= self.bet
        print(f'Smart Computer Player {self.player_id} bet {self.bet}$')



    def make_move(self,game,hand,move,dealer_card=None):

        if move == 'D':
            #draw a card
            hand.add_card(game)

            if hand.score>21:
                self.lost_hand()
                self.hands.remove(hand)
                hand.toss_hand(game)
            elif hand.score==21:
                #end of hand turn
                pass
            else:
                self.get_move(game,hand,dealer_card)
        elif move == 'DD':
            self.pot -= self.bet
            self.bet *= 2
            hand.add_card(game)

            if hand.score>21:
                self.lost_hand()
                self.hands.remove(hand)
                hand.toss_hand(game)
            else:
                #end turn
                pass

        elif move == 'SP':
            print(f'The hand is split.')
            self.pot -= self.bet
            hand1,hand2 = hand.split(game)
            game.hand_was_splitted = True #for debugging
            hand1_str = hand1.get_printable_card()
            hand2_str = hand2.get_printable_card()
            #check if blackjack
            print(f'First hand is [{hand1_str[0]}] and [{hand1_str[1]}]')
            print(f'With a score of {hand1.score}')
            self.hands.remove(hand)
            if hand1.blackjack():
                self.won_blackjack()
                hand1.toss_hand(game)
            else:
                self.hands.append(hand1)
                self.get_move(game,hand1,dealer_card)

            print(f'Second hand is [{hand2_str[0]}] and [{hand2_str[1]}]')
            print(f'With a score of {hand2.score}')

            if hand2.blackjack():
                self.won_blackjack()
                hand2.toss_hand(game)
            else:
                self.hands.append(hand2)
                self.get_move(game,hand2,dealer_card)


        elif move == 'S':
            #end of hand turn
            hand.status = 'done'

    @staticmethod
    def remove_loser(players):
        for player in players:
            if player.pot<=0:
                print(f'Player {player.player_id} is eliminated')
                players.remove(player)
        return players



class Dealer(Player):

    def __init__(self,mini_pause):
        super().__init__(math.inf,mini_pause)


    def draw_first_cards(self,game):
        super().draw_first_cards(game)
        hand = self.hands[0].get_printable_card()
        print('')
        print(f'Dealer draw [{hand[0]}] and [?]')
        self.players_need_insurance = False
        if self.hands[0].hand[0][0]== 1:
            self.players_need_insurance = True


    def make_move(self,game):
        hand = self.hands[0]
        hand.hand_score()
        while hand.score<17:
            time.sleep(self.mini_pause)
            hand.add_card(game)

        self.update_final_status()
        self.hands.remove(hand)
        hand.toss_hand(game)

    def update_final_status(self):
        # the score is 17 or above
        self.score = self.hands[0].hand_score()
        if self.score>21:
            self.status= 'blown_up'
            print('-----')
            print('The Dealer blow up!')
            print('-----')
        else:
            self.status = 'done'

class HumanGambler(Player):

    def __init__(self,pot,mini_pause):
        super().__init__(pot,mini_pause)
        Player.player_number += 1
        self.player_id = Player.player_number

    def choose_bet_size(self):
        self.bet = input(f'Player {self.player_id} must choose his bet size (1-{self.pot}):')

        try:
            self.bet = int(self.bet)
            if not 0<self.bet<=self.pot:
                raise ValueError
        except ValueError:
            print(f'Wrong input, the bet size must be between 1 and {self.pot}')
            self.choose_bet_size()

        self.pot -= self.bet

    def draw_first_cards(self,game):
        super().draw_first_cards(game)
        hand = self.hands[0].get_printable_card()
        print(f'Player {self.player_id} draw [{hand[0]}] and [{hand[1]}]')
        print(f'The hand score is {self.hands[0].score}')

    def get_move(self,game,hand,dealer_hand = None):
        if hand.score<21:
            if hand.can_split() and self.pot>=self.bet:
                if hand.get_card_number()==2 and self.pot>=self.bet:
                    valid_moves = ['S','D','SP','DD']
                    move = input(f'Do you want to draw (D), stop (S), Double (DD) or split (SP): ')
                    while not move in valid_moves:
                        print('This move is incorrect. You need to type : D, S, DD or SP.')
                        move = input(f'Do you want to draw (D), stop (S), Double (DD) or split (SP): ')

                else:
                    valid_moves = ['S','D','SP']
                    move = input(f'Do you want to draw (D), stop (S) or split (SP): ')
                    while not move in valid_moves:
                        print('This move is incorrect. You need to type : D,S or SP.')
                        move = input(f'Do you want to draw (D), stop (S) or split (SP): ')

            elif hand.get_card_number()==2 and self.pot>=self.bet:
                valid_moves = ['S','D','DD']
                move = input(f'Do you want to draw (D), stop (S) or double (DD): ')
                while not move in valid_moves:
                    print('This move is incorrect. You need to type : D, S or DD.')
                    move = input(f'Do you want to draw (D), stop (S) or double (DD): ')
            else:
                valid_moves = ['S','D']
                move = input(f'Do you want to draw (D) or stop (S): ')
                while not move in valid_moves:
                    print('This move is incorrect. You need to type : D or S.')
                    move = input(f'Do you want to draw (D) or stop (S): ')
            self.make_move(game,hand,move)

    def take_insurance(self):
        if self.pot >=self.bet *0.5:
            insurance = input(f'The Dealer might have a Blackjack, does Player {self.player_id} want to take an insurance (Y or N)?')
            while insurance != 'N' and insurance != 'Y':
                print('Wrong input, you must type Y or N')
                insurance = input(f'The Dealer miaght have a Blackjack, does Player {self.player_id} want to take an insurance (Y or N)?')
            if insurance == 'Y':
                self.pot -= self.bet *0.5
                self.insurance_bet = self.bet *0.5
        else:
            print(f'Player {self.player_id} don\'t have enough to get insured.')



class RandomComputerGambler(Player):

    def __init__(self,pot,mini_pause,random_bet_size=True):
        super().__init__(pot,mini_pause)
        Player.player_number += 1
        self.player_id = Player.player_number
        self.random_bet_size = random_bet_size


    def draw_first_cards(self,game):
        super().draw_first_cards(game)
        hand = self.hands[0].get_printable_card()
        print(f'Player {self.player_id} draw [{hand[0]}] and [{hand[1]}]')
        print(f'The hand score is {self.hands[0].score}')

    def get_move(self,game,hand,dealer_card = None):
        if hand.score<21:
            valid_moves = ['S','D']
            if hand.can_split() and self.pot>=self.bet:
                valid_moves.append('SP')
            if hand.get_card_number()==2 and self.pot>=self.bet:
                valid_moves = ['S','D']
            dict_move = {'S':'Stop','D':'Draw','SP':'Split','DD':'Double'}
            move = random.choice(valid_moves)
            print(f'Player {self.player_id} choose move {dict_move[move]}.')
            time.sleep(self.mini_pause)
            self.make_move(game,hand,move)

    def take_insurance(self):
        if self.pot >=self.bet *0.5:
            self.insured = random.choice([True, False])
            if self.insured == True:
                print(f'Player {self.player_id} choose the insurance.')

                self.pot -= self.bet *0.5
                self.insurance_bet = self.bet *0.5
            else:
                print(f'Player {self.player_id} didn\'t choose the insurance.')
        else:
            print(f'Player {self.player_id} don\'t have enough to get insured.')

class SmartComputerGambler(Player):
    soft_table = [['D','D','D','DD','DD','D','D','D','D','D'],#As,2
                    ['D','D','D','DD','DD','D','D','D','D','D'],#As,3
                    ['D','D','DD','DD','DD','D','D','D','D','D'],#As,4
                    ['D','D','DD','DD','DD','D','D','D','D','D'],#As,5
                    ['D','DD','DD','DD','DD','D','D','D','D','D'],#As,6
                    ['DD','DD','DD','DD','DD','S','S','D','D','D'],#As,7
                    ['S','S','S','S','DD','S','S','S','S','S'],#As,8
                    ['S','S','S','S','S','S','S','S','S','S']#As,9
    ]

    hard_table = [['D','D','D','D','D','D','D','D','D','D'],#5-8
                    ['D','DD','DD','DD','DD','D','D','D','D','D'],#9
                    ['DD','DD','DD','DD','DD','DD','DD','DD','D','D'],#10
                    ['DD','DD','DD','DD','DD','DD','DD','DD','DD','DD'],#11
                    ['D','D','S','S','S','D','D','D','D','D'],#12
                    ['S','S','S','S','S','D','D','D','D','D'],#13-16
                    ['S','S','S','S','S','S','S','S','S','S']#17-21
    ]

    split_table = [[True,True,True,True,True,True,True,True,True,True],#as
                    [True,True,True,True,True,True,False,False,False,False],#2
                    [True,True,True,True,True,True,False,False,False,False],#3
                    [False,False,False,True,True,False,False,False,False,False],#4
                    [False,False,False,False,False,False,False,False,False,False],#5
                    [True,True,True,True,True,False,False,False,False,False],#6
                    [True,True,True,True,True,True,False,False,False,False],#7
                    [True,True,True,True,True,True,True,True,True,True],#8
                    [True,True,True,True,True,False,True,True,False,False],#9
                    [False,False,False,False,False,False,False,False,False,False],#10
    ]
    def __init__(self,pot,mini_pause,random_bet_size = True):
        super().__init__(pot,mini_pause)
        Player.player_number += 1
        self.player_id = Player.player_number
        self.random_bet_size = random_bet_size


    def draw_first_cards(self,game):
        super().draw_first_cards(game)
        hand = self.hands[0].get_printable_card()
        print(f'Player {self.player_id} draw [{hand[0]}] and [{hand[1]}]')
        print(f'The hand score is {self.hands[0].score}')

    def get_move(self,game,hand,dealer_card):
        if hand.score<21:
            dict_move = {'S':'Stop','D':'Draw','SP':'Split','DD':'Double'}
            move = self.get_smart_move(hand,dealer_card)
            print(f'Player {self.player_id} choose move {dict_move[move]}.')
            time.sleep(self.mini_pause)
            self.make_move(game,hand,move,dealer_card)

    def get_smart_move(self,hand,dealer_card):
        player_cards = hand.hand
        num_of_cards = len(player_cards)
        has_as = player_cards[0][0]==1 or player_cards[1][0]==1
        if SmartComputerGambler.should_smart_split(player_cards,dealer_card) and self.pot >=self.bet:
            return 'SP'
        elif num_of_cards == 2 and has_as:
            #use soft total table
            other_card = player_cards[0][0] if player_cards[1][0]==1 else player_cards[1][0]
            col_value = SmartComputerGambler.map_col(dealer_card)
            row_value = SmartComputerGambler.map_soft_row(other_card)
            return SmartComputerGambler.soft_table[row_value][col_value]
        else:
            #use hard total table

            total_score = hand.hand_score()
            col_value = SmartComputerGambler.map_col(dealer_card)
            row_value = SmartComputerGambler.map_hard_row(total_score)
            move = SmartComputerGambler.hard_table[row_value][col_value]
            if num_of_cards != 2 and move == 'DD' and self.pot <self.bet:
                move = 'D'
            return move

    @classmethod
    def should_smart_split(cls,player_cards,dealer_card):
        if player_cards[0][0] == player_cards[0][1]:
            col_value = cls.map_col(dealer_card)
            row_value = cls.map_split_row(player_cards[0][0])
            return cls.split_table[row_value][col_value]
        else:
            return False
    @classmethod
    def map_col(cls,dealer_card):
        card_value = dealer_card[0]
        if card_value ==1:
            return 9
        elif card_value >=10:
            return 8
        else:
            return card_value-2
    @classmethod
    def map_soft_row(cls,card_value):
        print(card_value)
        if card_value>=10:
            print('Should not run here')
            raise ValueError
        return card_value-2
    @classmethod
    def map_hard_row(cls,card_value):
        if 17<=card_value<=21:
            return 6
        elif 13<=card_value<=16:
            return 5
        elif card_value<=8:
            return 0
        else:
            return card_value - 8
    @classmethod
    def map_split_row(cls,card_value):
        return card_value-1


    def take_insurance(self):
        print(f'Player {self.player_id} didn\'t choose the insurance.')
