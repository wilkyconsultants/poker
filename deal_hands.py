#!/usr/bin/python3
import random
from poker.hand import Hand
from itertools import combinations

# optionally change num_players to a value 1 to 23
num_players=10

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.color = 'red' if suit in ['H', 'D'] else 'black'

    def __str__(self):
        rank_str = str(self.rank)
        if self.rank == 11:
            rank_str = "J"
        elif self.rank == 10:
            rank_str = "T"
        elif self.rank == 12:
            rank_str = "Q"
        elif self.rank == 13:
            rank_str = "K"
        elif self.rank == 14:
            rank_str = "A"
        return f"{rank_str}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        for suit in ['H', 'D', 'C', 'S']:
            for rank in range(2, 15):
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, card):
        self.hand.append(card)

    def show_hand(self):
        hand_str = ", ".join([str(card) for card in self.hand])
        return hand_str

class Game:
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.community_cards = []

    def add_player(self, player):
        self.players.append(player)

    def deal_initial_hands(self):
        for _ in range(2):
            for player in self.players:
                player.draw(self.deck.deal())

    def deal_community_cards(self, num_cards):
        for _ in range(num_cards):
            self.community_cards.append(self.deck.deal())

    def show_community_cards(self):
        community_str = ", ".join([str(card) for card in self.community_cards])
        return community_str

# Function to evaluate a poker hand
def evaluate_hand(hole_cards, community_cards):
    # Combine hole cards and community cards
    all_cards = hole_cards + community_cards
    
    # Define a mapping from rank letters to numerical values
    rank_mapping = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    # Extract ranks and suits
    ranks = [card[:-1] for card in all_cards]
    suits = [card[-1] for card in all_cards]
    
    # Count occurrences of each rank and suit
    rank_count = {rank: ranks.count(rank) for rank in rank_mapping.keys()}
    suit_count = {suit: suits.count(suit) for suit in SUITS}
    
    # Initialize used_cards
    used_cards = []
    
    # Check for flush
    flush_suit = None
    for suit, count in suit_count.items():
        if count >= 5:
            flush_suit = suit
            break
    
    # Straight Detection
    straight_ranks = []
    for i in range(len(RANKS) - 4):
        if set(RANKS[i:i+5]).issubset(set(ranks)):
            straight_ranks = RANKS[i:i+5]
            break
    # Consider A, 2, 3, 4, 5 as a straight
    if 'A' in ranks and '2' in ranks and '3' in ranks and '4' in ranks and '5' in ranks:
        straight_ranks = ['A', '2', '3', '4', '5']

    # Define poker hand ranks
    HAND_RANKS = {
        0: "High Card",
        1: "One Pair", 
        2: "Two Pair", 
        3: "Three of a Kind",
        4: "Straight",
        5: "Flush",
        6: "Full House",
        7: "Four of a Kind",
        8: "Straight Flush",
        9: "Royal Flush"
    }

    # Flush Detection
    if flush_suit:
        flush_cards = [card for card in all_cards if card[-1] == flush_suit]
        flush_cards.sort(key=lambda x: rank_mapping[x[:-1]], reverse=True)
        used_cards.extend(flush_cards[:5])
        hand_strength = 5
        hand_rank = HAND_RANKS[5]  # Flush

    # Straight Flush
    if straight_ranks and flush_suit:
        straight_flush_cards = [rank + flush_suit for rank in straight_ranks if rank + flush_suit in all_cards]
        if len(straight_flush_cards) >= 5:
            straight_flush_cards.sort(key=lambda x: rank_mapping[x[:-1]], reverse=True)
            straight_flush_set = set()  # Set to keep track of unique ranks in the straight flush
            for card in straight_flush_cards:
                card_rank = card[:-1]  # Extract the rank of the card
                if card_rank not in straight_flush_set:  # Check if the rank is not already in the set
                    straight_flush_set.add(card_rank)  # Add the rank to the set
                    if len(used_cards) <= 4:
                        used_cards.append(card)  # Add the card to used_cards
                    if len(used_cards) == 5 and card_rank == 'A' and used_cards[1][:-1] == 'K':
                        hand_strength = 9  # Royal Flush
                        hand_rank = HAND_RANKS[9]  # Set the hand rank to Royal Flush
                        return hand_rank, used_cards, hand_strength  # Exit the function once a Royal Flush is found

            hand_strength = 8  # Straight Flush
            hand_rank = HAND_RANKS[8]
            return hand_rank, used_cards, hand_strength  # Exit the function once a Straight Flush is found
    
    # Four of a Kind
    elif 4 in rank_count.values():
        for rank, count in rank_count.items():
            if count == 4:
                four_of_a_kind_rank = rank
                break
        for card in all_cards:
            if card[:-1] == four_of_a_kind_rank:
                used_cards.append(card)
        # Select the highest-ranking card among the remaining cards
        remaining_cards = [card for card in all_cards if card[:-1] != four_of_a_kind_rank]
        used_cards.append(max(remaining_cards, key=lambda x: rank_mapping[x[:-1]]))
        hand_strength = 7
        hand_rank = HAND_RANKS[7]  # Four of a Kind
    
    # Full House
    elif 3 in rank_count.values() and 2 in rank_count.values():
        three_of_a_kind_rank = None
        pair_rank = None
        for rank, count in rank_count.items():
            if count == 3:
                three_of_a_kind_rank = rank
            elif count >= 2:  # Changed to handle multiple pairs
                pair_rank = rank
        if three_of_a_kind_rank is not None and pair_rank is not None:
            hand_strength = 6
            hand_rank = HAND_RANKS[6]  # Full House
            used_cards = [card for card in all_cards if card[:-1] == three_of_a_kind_rank or card[:-1] == pair_rank]
    
    # Flush
    elif flush_suit:
        flush_cards = [card for card in all_cards if card[-1] == flush_suit]
        flush_cards.sort(key=lambda x: rank_mapping[x[:-1]], reverse=True)
        if len(used_cards) <= 4:
           used_cards.extend(flush_cards[:5])
        hand_strength = 5
        hand_rank = HAND_RANKS[5]  # Flush

    # Straight
    elif straight_ranks:
        straight_ranks = [rank_mapping[rank] for rank in straight_ranks]
        straight_cards = []
        for card in all_cards:
            if card[:-1] in RANKS and rank_mapping[card[:-1]] in straight_ranks and card[:-1] not in straight_cards:
                straight_cards.append(card[:-1])
                used_cards.append(card)
        hand_strength = 4
        hand_rank = HAND_RANKS[4]  # Straight
    
    # Three of a Kind
    elif 3 in rank_count.values():
        for rank, count in rank_count.items():
            if count == 3:
                three_of_a_kind_rank = rank
                break
        used_cards = [card for card in all_cards if card[:-1] == three_of_a_kind_rank]
        # Select the two highest-ranking cards among the remaining cards
        remaining_cards = [card for card in all_cards if card not in used_cards]
        used_cards.extend(sorted(remaining_cards, key=lambda x: rank_mapping[x[:-1]], reverse=True)[:2])
        hand_strength = 3
        hand_rank = HAND_RANKS[3]  # Three of a Kind
    
    # Two Pair
    elif list(rank_count.values()).count(2) >= 2:
        pair_ranks = [rank for rank, count in rank_count.items() if count == 2]
        used_cards = []
        for rank in sorted(pair_ranks, reverse=True)[:2]:
            used_cards.extend([card for card in all_cards if card[:-1] == rank])
        # Include hole cards in pairs
        for card in hole_cards:
            if card[:-1] in pair_ranks and len(used_cards) < 4:
                used_cards.append(card)
        # Select the highest-ranking card among the remaining cards
        remaining_cards = [card for card in all_cards if card[:-1] not in pair_ranks]
        used_cards.extend(sorted(remaining_cards, key=lambda x: rank_mapping[x[:-1]], reverse=True)[:1])
        hand_strength = 2
        hand_rank = HAND_RANKS[2]  # Two Pair
    
    # One Pair 
    elif 2 in rank_count.values():
         pair_ranks = [rank for rank, count in rank_count.items() if count == 2]
         used_cards = []
         for rank in pair_ranks:
             used_cards.extend([card for card in all_cards if card[:-1] == rank])
         # Select the three highest-ranking cards among the remaining cards
         remaining_cards = [card for card in all_cards if card not in used_cards]
         used_cards.extend(sorted(remaining_cards, key=lambda x: rank_mapping[x[:-1]], reverse=True)[:3])
         hand_strength = 1
         hand_rank = HAND_RANKS[1]  # One Pair

    # High Card
    else:
        # Select the five highest-ranking cards for high card
        used_cards = sorted(all_cards, key=lambda x: rank_mapping[x[:-1]], reverse=True)[:5]
        hand_strength = 0
        hand_rank = HAND_RANKS[0]  # High Card
    
    # If it's a straight, sort the used cards lowest to highest
    if hand_rank == "Straight":
        used_cards.sort(key=lambda x: rank_mapping[x[:-1]])
    
    return hand_rank, used_cards, hand_strength
    
# Define card ranks and suits
RANKS = '23456789TJQKA'
SUITS = 'CDHS'

# Define poker hand ranks
HAND_RANKS = {
    0: "High Card",
    1: "One Pair",
    2: "Two Pair",
    3: "Three of a Kind",
    4: "Straight",
    5: "Flush",
    6: "Full House",
    7: "Four of a Kind",
    8: "Straight Flush",
    9: "Royal Flush"
}


game = Game()

game.deal_community_cards(5)
community_cardsX=game.show_community_cards()
community_cards = community_cardsX.split(", ")
suit_mapping = {'H': '♡', 'D': '♢', 'C': '♣', 'S': '♠'}
community_cards_with_suits = [card[:-1] + suit_mapping[card[-1]] for card in community_cards]
print("")
print("  --------- Community cards:",str(community_cards_with_suits)," ----------")
print("")

players = [Player(f"Player {i+1}") for i in range(num_players)]
for player in players:
    game.add_player(player)

game.deal_initial_hands()
ctr=0
for player in game.players:
    ctr=ctr+1
    hole_cardsX=player.show_hand()
    hole_cards = hole_cardsX.split(", ")
    hand_rank, used_cards, hand_strength=evaluate_hand(hole_cards, community_cards)
    hole_cards_with_suits = [card[:-1] + suit_mapping[card[-1]] for card in hole_cards]
    used_cards_with_suits = [card[:-1] + suit_mapping[card[-1]] for card in used_cards]
    print("#"+str(ctr).zfill(2),"Hole cards:",str(hole_cards_with_suits)," Hand: ",used_cards_with_suits," ",hand_strength,hand_rank)

print("")
