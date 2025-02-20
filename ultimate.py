import random
from collections import Counter

# define card set
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {rank: i for i, rank in enumerate(ranks, start=2)}

deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

budget = 1000

# remove a card from the deck and return it "deal a card"
def deal_card(deck):
    return deck.pop(random.randint(0, len(deck) - 1))

# function for determining whether a player shoudl bet before flop - maybe changed to bool return value
def should_raise_pre_flop(card1, card2):
    higher, lower = sorted([card1, card2], key=lambda c: ranks.index(c['rank']))

    if higher['rank'] == lower['rank'] and ranks.index(higher['rank']) >= ranks.index('3'):
        return 4

    decision_table = {
        ('A', '2'): 'Y', ('A', '3'): 'Y', ('A', '4'): 'Y', ('A', '5'): 'Y', ('A', '6'): 'Y', ('A', '7'): 'Y', ('A', '8'): 'Y', ('A', '9'): 'Y', ('A', '10'): 'Y', ('A', 'J'): 'Y', ('A', 'Q'): 'Y', ('A', 'K'): 'Y',
        ('K', '2'): 'S', ('K', '3'): 'S', ('K', '4'): 'S', ('K', '5'): 'S', ('K', '6'): 'S', ('K', '7'): 'S', ('K', '8'): 'S', ('K', '9'): 'S', ('K', '10'): 'Y', ('K', 'J'): 'Y', ('K', 'Q'): 'Y',
        ('Q', '6'): 'S', ('Q', '7'): 'S', ('Q', '8'): 'S', ('Q', '9'): 'S', ('Q', '10'): 'Y', ('Q', 'J'): 'Y',
        ('J', '8'): 'S', ('J', '9'): 'S', ('J', '10'): 'Y',
        ('10', '9'): 'S', ('10', 'J'): 'Y'}
    
    decision = decision_table.get((higher['rank'], lower['rank']), 'N')
    return 4 if decision == 'Y' else 4 if decision == 'S' and higher['suit'] == lower['suit'] else 0


# function that returns the best hand from available cards
def get_best_hand(cards):
    counts = Counter(card['rank'] for card in cards)
    suits = Counter(card['suit'] for card in cards)
    sorted_ranks = sorted([rank_values[card['rank']] for card in cards], reverse=True)
    
    # check for royal flush - wrong
    if {'10', 'J', 'Q', 'K', 'A'}.issubset(counts.keys()) and any(suits[suit] >= 5 for suit in suits):
        return "Royal Flush"

    # check for straight flush - check, propably not specific enough
    for suit in suits:
        suited_cards = [rank_values[card['rank']] for card in cards if card['suit'] == suit]
        if len(suited_cards) >= 5 and max(suited_cards) - min(suited_cards[:5]) == 4:
            return "Straight Flush"

    # check for poker
    if 4 in counts.values():
        return "Four of a Kind"

    # check for full house
    if 3 in counts.values() and 2 in counts.values():
        return "Full House"

    # check for flush
    if any(suits[suit] >= 5 for suit in suits):
        return "Flush"

    unique_ranks = sorted(set(sorted_ranks), reverse=True)
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i + 4] == 4:
            return "Straight"

    # check for three of a kind
    if 3 in counts.values():
        return "Three of a Kind"

    # check for 2 pairs
    if list(counts.values()).count(2) == 2:
        return "Two Pair"

    # check for pair
    if 2 in counts.values():
        return "One Pair"

    return "High Card"

# check for ante condition
def dealer_has_pair_or_better_or_ace(dealer_hand, community_cards):
    combined_cards = dealer_hand + community_cards
    hand_strength = get_best_hand(combined_cards)
    stronger_hands = ["One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
    dealer_has_ace = any(card['rank'] == 'A' for card in dealer_hand)

    return hand_strength in stronger_hands or dealer_has_ace


def has_blind(blind, player_combination):
    if player_combination == "Straight":
        blind *= 2
    elif player_combination == "Flush":
        blind *= 2.5
    elif player_combination == "Full House":
        blind *= 4
    elif player_combination == "Four of a Kind":  
        blind *= 11
    elif player_combination == "Straight Flush":
        blind *= 51
    elif player_combination == "Royal Flush":
        blind *= 501

    return blind


def play_game():
    global budget

    ante = 10 # set ante value
    blind = 10 # set blind value
    current_bet = 0 # variable for bet
    has_bet = False # has already bet or not
    betting_history = [] # save betting history to be printed 

    # copy deck so its not ruined
    deck_copy = deck.copy()

    # shuffle copied deck
    random.shuffle(deck_copy)
    
    # subtract ante, blind - always
    budget -= ante
    budget -= blind

    # deal hands to player and dealer 
    player_hand = [deal_card(deck_copy), deal_card(deck_copy)]
    dealer_hand = [deal_card(deck_copy), deal_card(deck_copy)]
    
    # pre flop
    if not has_bet: 
        # returns 4 if should raise pre flop
        bet_multiplier = should_raise_pre_flop(player_hand[0], player_hand[1])
        if bet_multiplier > 0:
            current_bet = ante * bet_multiplier
            budget -= current_bet
            has_bet = True
            betting_history.append(f"Preflop: Stavil(a) ste {current_bet}.")

    # after flop
    community_cards = [deal_card(deck_copy) for _ in range(3)]
    if not has_bet:  
        combined_cards = player_hand + community_cards
        if get_best_hand(combined_cards) in ["One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]:
            current_bet = ante * 2
            budget -= current_bet
            has_bet = True
            betting_history.append(f"Flop: Stavil(a) ste {current_bet}.")

    # after river
    community_cards += [deal_card(deck_copy), deal_card(deck_copy)]
    if not has_bet:  
        combined_cards = player_hand + community_cards
        player_has_pair_or_better = get_best_hand(combined_cards) != "High Card"
        player_has_high_card = any(rank_values[card['rank']] >= 10 for card in player_hand)
        
        if player_has_pair_or_better or player_has_high_card:
            current_bet = ante * 1
            budget -= current_bet
            has_bet = True
            betting_history.append(f"Turn & River: Stavil(a) ste {current_bet}.")

    # take all available cards for evalueation
    player_final_hand = player_hand + community_cards
    dealer_final_hand = dealer_hand + community_cards

    # evaluate cards
    player_combination = get_best_hand(player_final_hand)
    dealer_combination = get_best_hand(dealer_final_hand)

    print("\n--- REZULTATI IGRE ---")
    print(f"Vaša roka: {player_hand}, Kombinacija: {player_combination}")
    print(f"Delivčeva roka: {dealer_hand}, Kombinacija: {dealer_combination}")
    print(f"River (5 skupnih kart): {community_cards}")
    
    print("\nZgodovina stav:")
    for bet in betting_history:
        print(bet)     

    # set ordered winning combinations
    winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
   
    if winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
        
        print("Čestitke, zmagali ste!") 

        dealer_has_something = dealer_has_pair_or_better_or_ace(dealer_hand, community_cards)
        blind_won = has_blind(blind, player_combination)
        
        winnings = current_bet * 2 + blind_won + (ante * 2 if dealer_has_something else ante)
        budget += winnings
        winnings -= (current_bet + blind + ante)
       
        print(f"Vaš dobitek: {winnings}")

    elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
        print("Izenačeno! Stavljeni denar vam je povrnjen.")
        budget += current_bet + ante + blind
    else:
        print("Žal ste izgubili. Poskusite znova!")

    print(f"\nPreostali proračun: {budget}")

if __name__ == "__main__":
    play_game()





















