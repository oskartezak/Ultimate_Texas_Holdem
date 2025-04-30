# import libraries
import numpy as np
import torch
import ultimate_for_NN as ultimate
import random 
from collections import deque
from itertools import chain

# define card set
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {rank: i for i, rank in enumerate(ranks, start=2)}

deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

combinations = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", 
                "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]
combinations_values = {combination: i for i, combination in enumerate(combinations, start=1)}
# set ordered winning combinations
winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", 
                "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
#enumerate the deck
enumerated_deck = dict(enumerate(deck, start=1))
num_deck = np.arange(1, 53)

# define split card dict, num_of_cards: (num of color, num of rank) ex. 13: (1, 13)
split_card_dict={}
num_card_dict={}
for i in num_deck:
    split_card_dict[i] = ((i - 1) // 13 + 1, (i-1) % 13 + 1)
    num_card_dict[i] = (ranks[(i-1) % 13], suits[(i - 1) // 13]) # for human

#########################################################

# function for generating a game (all cards) - output a list of all cards in game cards
# cards are interpreted as: 2 for each player, 5 for the table, last 2 for the dealer
def generate_game(num_of_players = 1):
    game_size = 7 + 2*num_of_players

    return np.random.choice(np.arange(1, 53), size=game_size, replace=False)

#########################################################
# next state and next cards - returns next state input, game is 7-14 with split info for cards
# each cards ha info about suit (1-4) and rank (1-13)
#hardcoded for one player

""" # for 4_13 version
def state_to_tensor(round, whole_game):
    split_card_info = [element for i in whole_game for element in split_card_dict[i]]

    cards_len = len(split_card_info) - 4
    if round == 0:
        cards = np.array(split_card_info[:4])
    elif round == 1:
        cards = np.array(split_card_info[:10])
    elif round == 2:
        cards = np.array(split_card_info[:14])
    else:
        cards = np.array([]) # irrelevant just for filler

    cards = np.pad(cards, (0, cards_len - len(cards)), mode='constant')
    state = np.array([round])
    full_state = np.concatenate([state, cards])
    return torch.from_numpy(full_state).unsqueeze(0).float() """
round_card_mapping = {0: 4, 1: 10, 2: 14}
def state_to_tensor(round, whole_game):
    # Efficiently flatten `split_card_dict` values using chain.from_iterable
    split_card_info = list(chain.from_iterable(split_card_dict[i] for i in whole_game))
 
    # Get the correct number of cards (default to 0 if round is out of range)
    num_cards = round_card_mapping.get(round, 0)
    cards = np.array(split_card_info[:num_cards], dtype=np.float32)

    # Efficient padding if necessary
    pad_length = len(split_card_info) - num_cards
    if pad_length > 0:
        cards = np.pad(cards, (0, pad_length), mode='constant')

    # Concatenate round information
    full_state = np.concatenate(([round], cards))

    # Convert to Tensor
    return torch.tensor(full_state, dtype=torch.float32).unsqueeze(0)

""" # for embedded version
def state_to_tensor_embedding(round, whole_game):

    cards_len = len(whole_game) - 2
    if round == 0:
        cards = np.array(whole_game[:2])
    elif round == 1:
        cards = np.array(whole_game[:5])
    elif round == 2:
        cards = np.array(whole_game[:7])
    else:
        cards = np.array([]) # irrelevant just for filler

    cards = np.pad(cards, (0, cards_len - len(cards)), mode='constant')
    return torch.from_numpy(cards).unsqueeze(0), torch.tensor([round]).unsqueeze(0) """
# Define how many cards should be used at each round
round_card_mapping_emb = {0: 2, 1: 5, 2: 7}
def state_to_tensor_embedding(round, whole_game):
  
    # Get the correct number of cards (default to 0 if round is out of range)
    num_cards = round_card_mapping_emb.get(round, 0)
    cards = np.array(whole_game[:num_cards], dtype=np.int64)  # Ensure dtype is int64 for embedding layers

    # Efficient padding
    pad_length = len(whole_game) - num_cards - 2
    if pad_length > 0:
        cards = np.pad(cards, (0, pad_length), mode='constant')

    # Convert to Tensors
    cards_tensor = torch.tensor(cards, dtype=torch.long).unsqueeze(0)  # Needed for embedding layers
    round_tensor = torch.tensor([round], dtype=torch.long).unsqueeze(0)  # Also long if used as an index

    return cards_tensor, round_tensor

#########################################################
hand_ranking = {hand: rank for rank, hand in enumerate(winning_hands)}
# reward function - target is where the reward was biggest
def reward_function(round, whole_game, action, norm=True):
    # normalize reward values (royal flush and straight flusch 
    # will be more than 1 but its tolerable)
    
    """ def normalize_reward(r, min_r=-6, max_r=11):
        if norm == True:
            return (r - min_r) / (max_r - min_r)
        else: 
            return r """
        
    normalize_reward = lambda r: (r + 6) / 17 if norm else r
    # blind and ante are set to be 1
    blind, ante = 1, 1

    # if we fold in third round - we lose 
    if round == 2 and action == 1:
        return normalize_reward(- blind - ante)
        #return  - blind - ante
    # if we say check in first or second round - the reward is neutral 
    elif round != 2 and action == 1:
        return normalize_reward(0)
        #return 0
    
    # in all other cases we need to know who won and if the ante or blind are valid
    player_hand = [enumerated_deck[card] for card in whole_game[:7]]
    dealer_hand = [enumerated_deck[card] for card in whole_game[2:]]
    #print(player_hand)
    #print(dealer_hand)
    player_combination = ultimate.get_best_hand(player_hand)
    dealer_combination = ultimate.get_best_hand(dealer_hand)
    #print(player_combination, dealer_combination)
    # find the victor (Player, Dealer, Tie)
    victor = ""
    if hand_ranking[player_combination] > hand_ranking[dealer_combination]:
        victor = "Player"
    elif hand_ranking[player_combination] == hand_ranking[dealer_combination]:
        result = ultimate.decider(player_combination, player_hand, 
                                  dealer_combination, dealer_hand)
        if result == "player":
            victor = "Player"
        elif result == "dealer":	
            victor = "Dealer"	
        else:
            return normalize_reward(0) # the reward for game is 0 if tie
            #return 0
    else:
        victor = "Dealer"

    # Reward logic for different betting rounds
    bet_multiplier = [4, 2, 1]  # Multipliers for ante depending on round (0,1,2)
    bet_penalty = [5, 3, 2]     # Penalty for losing per round

    if victor == "Player":
        ante_valid = ultimate.has_ante(dealer_combination)  # boolean
        blind_pay = ultimate.net_blind_payout(blind, player_combination)  # value if won
        reward = bet_multiplier[round] * ante + blind_pay + (ante if ante_valid else 0)
    else:
        reward = -blind - bet_penalty[round] * ante

    return normalize_reward(reward)

    """ # we bet in third round
    if round == 2:
        if victor == "Player":
            # calculate ante and blind
            ante_valid = ultimate.has_ante(dealer_combination) # boolean
            blind_pay = ultimate.net_blind_payout(blind, player_combination) # value if won
            return normalize_reward(ante + blind_pay + (ante if ante_valid else 0))
            #return ante + blind_pay + (ante if ante_valid else 0)
        else:
            return normalize_reward(- blind - 2*ante)
            #return - blind - 2*ante
    # we bet in second round
    elif round == 1:
        if victor == "Player":
            # calculate ante and blind
            ante_valid = ultimate.has_ante(dealer_combination) # boolean
            blind_pay = ultimate.net_blind_payout(blind, player_combination) # value if won
            return normalize_reward(2 * ante + blind_pay + (ante if ante_valid else 0))
            #return 2 * ante + blind_pay + ante if ante_valid else 0
        else:
            return normalize_reward(- blind - 3*ante)
            #return - blind - 3*ante
    # we bet in first round
    elif round == 0:
        if victor == "Player":
            # calculate ante and blind
            ante_valid = ultimate.has_ante(dealer_combination) # boolean
            blind_pay = ultimate.net_blind_payout(blind, player_combination) # value if won
            return normalize_reward(4 * ante + blind_pay + (ante if ante_valid else 0))
            #return 4 * ante + blind_pay + (ante if ante_valid else 0)
        else:
            return normalize_reward(- blind - 5*ante)
            #return - blind - 5*ante """

#########################################################
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)  # Stores experiences up to `capacity`
    
    def reset(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    # store games in buffer
    def add(self, action, reward, round_input_tensor, next_round_input_tensor, end):
        self.buffer.append((action, reward, round_input_tensor, next_round_input_tensor, end))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)  # Random mini-batch
        actions, rewards, round_input_tensors, next_round_input_tensors, end = zip(*batch)
        
        # Convert to NumPy arrays for easier tensor conversion
        return (np.array(actions), np.array(rewards), np.array(round_input_tensors),
                np.array(next_round_input_tensors), np.array(end))

    def size(self):
        return len(self.buffer)  # Current number of experiences stored
    
class ReplayBufferEmbedding:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)  # Stores experiences up to `capacity`
    
    def reset(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    # store games in buffer
    def add(self, action, reward, cards_input_tensor, round_input_tensor, 
            next_cards_input_tensor, next_round_input_tensor, end):
        self.buffer.append((action, reward, cards_input_tensor, round_input_tensor, 
                            next_cards_input_tensor, next_round_input_tensor, end))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)  # Random mini-batch
        actions, rewards, cards_input_tensor, round_input_tensors, next_cards_input_tensor, next_round_input_tensors, end = zip(*batch)
        
        # Convert to NumPy arrays for easier tensor conversion
        return (np.array(actions), np.array(rewards), np.array(cards_input_tensor), np.array(round_input_tensors),
                np.array(next_cards_input_tensor), np.array(next_round_input_tensors), np.array(end))

    def size(self):
        return len(self.buffer)  # Current number of experiences stored

#########################################################
# testing model
def testing_embedding(model, games=10000):
    model.eval()  # Set model to evaluation mode
    model
    budget = 0
    betted = 0
    betted4x = 0
    betted2x = 0
    betted1x = 0
    folded = 0
    for i in range(games):
        round = 0

        whole_game = generate_game()
        while True:
            state_tensor, round_tensor = state_to_tensor_embedding(round, whole_game)
            
            with torch.no_grad():
                q_values = model(state_tensor, round_tensor)
                action = q_values.argmax().item()

            # if action is no (check/fold) we move to the next round
            if action == 1 and round != 2:
                round += 1
            else:
                budget += reward_function(round, whole_game, action, norm=False)
                if action == 1 and round == 2:
                    folded += 1
                    betted += 2 # currently hardcoded
                elif round == 2:
                    betted1x += 1
                    betted += 3
                elif round == 1:
                    betted2x += 1
                    betted += 4
                elif round == 0:
                    betted4x += 1
                    betted += 6
                break
        
        #print(f"Game: {i+1}, Budget: {budget}")

    print(f"Total Budget: {budget}")
    print(f"Total Betted: {betted}")
    print(f"Folded: {folded}-times")
    print(f"Betted 4x: {betted4x}-times")
    print(f"Betted 2x: {betted2x}-times")
    print(f"Betted 1x: {betted1x}-times")

# testing model
def testing(model, games=10000):
    model.eval()  # Set model to evaluation mode
    model
    budget = 0
    betted = 0
    betted4x = 0
    betted2x = 0
    betted1x = 0
    folded = 0
    for i in range(games):
        round = 0

        whole_game = generate_game()
        while True:
            state_tensor = state_to_tensor(round, whole_game)
            
            with torch.no_grad():
                q_values = model(state_tensor)
                action = q_values.argmax().item()

            # if action is no (check/fold) we move to the next round
            if action == 1 and round != 2:
                round += 1
            else:
                budget += reward_function(round, whole_game, action, norm=False)
                if action == 1 and round == 2:
                    folded += 1
                    betted += 2 # currently hardcoded
                elif round == 2:
                    betted1x += 1
                    betted += 3
                elif round == 1:
                    betted2x += 1
                    betted += 4
                elif round == 0:
                    betted4x += 1
                    betted += 6
                break
        
        #print(f"Game: {i+1}, Budget: {budget}")

    print(f"Total Budget: {budget}")
    print(f"Total Betted: {betted}")
    print(f"Folded: {folded}-times")
    print(f"Betted 4x: {betted4x}-times")
    print(f"Betted 2x: {betted2x}-times")
    print(f"Betted 1x: {betted1x}-times")

#########################################################
# save and load model - not used
def save_model(model, optimizer, file_path):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, file_path)

def load_model(model, optimizer, file_path):
    checkpoint = torch.load(file_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return model, optimizer