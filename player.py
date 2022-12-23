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
    def __str__(self):
        return self.get_printable_card()
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
    def draw_first_cards(self,game):
        self.hands.append(Hand(game))



    def get_moves(self,game):
        # the current score is lower than 21
        moves = []
        hands = self.hands[:] # in case of a split, we dont want to modify the loop
        for hand in hands:
            print(f'Your score is {hand.score}.')
            move = self.get_move(game,hand)


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



    def make_move(self,game,hand,move):

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
                self.get_move(game,hand)
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
                self.get_move(game,hand1)

            print(f'Second hand is [{hand2_str[0]}] and [{hand2_str[1]}]')
            print(f'With a score of {hand2.score}')

            if hand2.blackjack():
                self.won_blackjack()
                hand2.toss_hand(game)
            else:
                self.hands.append(hand2)
                self.get_move(game,hand2)


        elif move == 'D':
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

    def get_move(self,game,hand):
        if hand.score<21:
            if hand.can_split() and self.pot>=self.bet:
                valid_moves = ['S','D','SP']
                move = input(f'Do you want to draw (D), stop (S) or split (SP): ')
                while not move in valid_moves:
                    print('This move is incorrect. You need to type : D,S or SP.')
                    move = input(f'Do you want to draw (D), stop (S) or split (SP): ')

            else:
                valid_moves = ['S','D']
                move = input(f'Do you want to draw (D) or stop (S): ')
                while not move in valid_moves:
                    print('This move is incorrect. You need to type : D or S.')
                    move = input(f'Do you want to draw (D) or stop (S): ')
            self.make_move(game,hand,move)

class RandomComputerGambler(Player):

    def __init__(self,pot,mini_pause):
        super().__init__(pot,mini_pause)
        Player.player_number += 1
        self.player_id = Player.player_number

    def choose_bet_size(self):
        print(self.pot)
        self.bet = self.pot if self.pot<2 else random.randint(1,int(self.pot))
        self.pot -= self.bet
        print(f'Random Computer player bet {self.bet}$')

    def draw_first_cards(self,game):
        super().draw_first_cards(game)
        hand = self.hands[0].get_printable_card()
        print(f'Player {self.player_id} draw [{hand[0]}] and [{hand[1]}]')
        print(f'The hand score is {self.hands[0].score}')

    def get_move(self,game,hand):
        if hand.score<21:
            if hand.can_split() and self.pot>=self.bet:
                valid_moves = ['S','D','SP']
            else:
                valid_moves = ['S','D']
            dict_move = {'S':'Stop','D':'Draw','SP':'Split'}
            move = random.choice(valid_moves)
            print(f'Player {self.player_id} choose move {dict_move[move]}.')
            time.sleep(self.mini_pause)
            self.make_move(game,hand,move)
