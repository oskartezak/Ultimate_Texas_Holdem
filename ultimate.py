import random
from collections import Counter

# define card set
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {rank: i for i, rank in enumerate(ranks, start=2)}

deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

budget = 1000
combinations = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", 
                "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]
combinations_values = {combination: i for i, combination in enumerate(combinations, start=1)}

# remove a card from the deck and return it "deal a card"
def deal_card(deck):
    return deck.pop(random.randint(0, len(deck) - 1))

# function for determining whether a player shoudl bet before flop - maybe changed to bool return value
def should_raise_pre_flop(card1, card2):
    higher, lower = sorted([card1, card2], key=lambda c: ranks.index(c['rank']), reverse=True)

    if higher['rank'] == lower['rank'] and ranks.index(higher['rank']) >= ranks.index('3'):
        return 4

    decision_table = {
        ('A', '2'): 'Y', ('A', '3'): 'Y', ('A', '4'): 'Y', ('A', '5'): 'Y', ('A', '6'): 'Y', ('A', '7'): 'Y', ('A', '8'): 'Y', ('A', '9'): 'Y', ('A', '10'): 'Y', ('A', 'J'): 'Y', ('A', 'Q'): 'Y', ('A', 'K'): 'Y',
        ('K', '2'): 'S', ('K', '3'): 'S', ('K', '4'): 'S', ('K', '5'): 'Y', ('K', '6'): 'Y', ('K', '7'): 'Y', ('K', '8'): 'S', ('K', '9'): 'S', ('K', '10'): 'Y', ('K', 'J'): 'Y', ('K', 'Q'): 'Y',
        ('Q', '6'): 'S', ('Q', '7'): 'S', ('Q', '8'): 'Y', ('Q', '9'): 'Y', ('Q', '10'): 'Y', ('Q', 'J'): 'Y',
        ('J', '8'): 'S', ('J', '9'): 'S', ('J', '10'): 'Y'}
    
    decision = decision_table.get((higher['rank'], lower['rank']), 'N')
    return 4 if decision == 'Y' else 4 if decision == 'S' and higher['suit'] == lower['suit'] else 0


# function that returns the best hand from available cards
def get_best_hand(cards):
    counts = Counter(card['rank'] for card in cards)
    suits = Counter(card['suit'] for card in cards)
    sorted_ranks = sorted([rank_values[card['rank']] for card in cards], reverse=True)
    
    most_common_suit, highest_count = suits.most_common(1)[0]
    suited_cards = [rank_values[card['rank']] for card in cards if card['suit'] == most_common_suit]
    suited_ranks = [card['rank'] for card in cards if card['suit'] == most_common_suit]
    # check for royal flush
    if {'10', 'J', 'Q', 'K', 'A'}.issubset(suited_ranks):
        return "Royal Flush"

    # check for straight flush
    unique_ranks = sorted(set(suited_cards), reverse=True)
    if len(suited_cards) >= 5:
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i + 4] == 4:
                return "Straight Flush"

    # check for poker
    if 4 in counts.values():
        return "Four of a Kind"

    # check for full house, 3 and 2 or 3 and 3
    if 3 in counts.values() and 2 in counts.values() or list(counts.values()).count(3) == 2:
        return "Full House"

    # check for flush
    if highest_count >= 5:
        return "Flush"

    unique_ranks = sorted(set(sorted_ranks), reverse=True)
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i + 4] == 4:
            return "Straight"

    # check for three of a kind
    if 3 in counts.values():
        return "Three of a Kind"

    # check for 2 pairs
    if list(counts.values()).count(2) >= 2:
        return "Two Pair"

    # check for pair
    if 2 in counts.values():
        return "One Pair"

    return "High Card"

stronger_hands = ["One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
# check for ante condition
def dealer_has_pair_or_better_or_ace(dealer_hand, community_cards):
    combined_cards = dealer_hand + community_cards
    hand_strength = get_best_hand(combined_cards)
    dealer_has_ace = any(card['rank'] == 'A' for card in dealer_hand)

    return hand_strength in stronger_hands or dealer_has_ace

# check for ante with whole combination
def has_ante(dealer_hand, dealer_combination):
    dealer_has_ace = any(card['rank'] == 'A' for card in dealer_hand[:2])

    return dealer_combination in stronger_hands or dealer_has_ace

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

# for machine learning algorithms
def net_blind_payout(blind, player_combination):
    if player_combination == "Straight":
        return blind * 1
    elif player_combination == "Flush":
        return blind * 1.5
    elif player_combination == "Full House":
        return blind * 3
    elif player_combination == "Four of a Kind":  
        return blind * 10
    elif player_combination == "Straight Flush":
        return blind * 50
    elif player_combination == "Royal Flush":
        return blind * 500

    return 0

# decides kicker / draw
def decider(player_combination, player_final_hand, dealer_combination, dealer_final_hand):

    player_counts = Counter(card['rank'] for card in player_final_hand)
    dealer_counts = Counter(card['rank'] for card in dealer_final_hand)

    if player_combination != dealer_combination:
        return None 

    # Winner if both player and dealer have nothing
    elif player_combination == "High Card":
        player_kickers = sorted(
            (rank_values[card['rank']] for card in player_final_hand),
            reverse=True
        )[:5]  

        dealer_kickers = sorted(
            (rank_values[card['rank']] for card in dealer_final_hand),
            reverse=True
        )[:5]

    # Winner if both player and dealer have one pair
    elif player_combination == "One Pair":
        # Pair values
        player_pair = max((rank for rank, count in player_counts.items() if count == 2), key=rank_values.get)
        dealer_pair = max((rank for rank, count in dealer_counts.items() if count == 2), key=rank_values.get)

        if rank_values[player_pair] > rank_values[dealer_pair]:
            return "player"
        elif rank_values[player_pair] < rank_values[dealer_pair]:
            return "dealer"

        # Biggest 3 kickers for each player and dealer
        player_kickers = sorted(
            (rank_values[card['rank']] for card in player_final_hand if card['rank'] != player_pair),
            reverse=True
        )[:3]  

        dealer_kickers = sorted(
            (rank_values[card['rank']] for card in dealer_final_hand if card['rank'] != dealer_pair),
            reverse=True
        )[:3]  # ni nujno 3, kaj ce je par v teh treh - je nujno ker imas pogoj card['rank'] != player_pair


    # Winner if both player and dealer have two pair
    elif player_combination == "Two Pair":
        player_pairs = sorted(
            (rank_values[rank] for rank, count in player_counts.items() if count == 2),
            reverse=True
        )[:2]  # Only take the top two pairs if three exist

        dealer_pairs = sorted(
            (rank_values[rank] for rank, count in dealer_counts.items() if count == 2),
            reverse=True
        )[:2]  

        # Comparing the highest pair first
        if player_pairs[0] > dealer_pairs[0]:
            return "player"
        elif player_pairs[0] < dealer_pairs[0]:
            return "dealer"

        # If the highest pair is the same, compare the second pair
        if player_pairs[1] > dealer_pairs[1]:
            return "player"
        elif player_pairs[1] < dealer_pairs[1]:
            return "dealer"

        # If both pairs are the same, compare the highest kicker - zloraba mnozine
        player_kickers = sorted(
            (rank_values[card['rank']] for card in player_final_hand if rank_values[card['rank']] not in player_pairs),
            reverse=True)[:1]
        dealer_kickers = sorted(
            (rank_values[card['rank']] for card in dealer_final_hand if rank_values[card['rank']] not in dealer_pairs),
            reverse=True)[:1]

    # Winner if both player and dealer have threee of a kind
    elif player_combination == "Three of a Kind":
        player_three_of_a_kind = max((rank for rank, count in player_counts.items() if count == 3), key=rank_values.get)
        dealer_three_of_a_kind = max((rank for rank, count in dealer_counts.items() if count == 3), key=rank_values.get)

        if rank_values[player_three_of_a_kind] > rank_values[dealer_three_of_a_kind]:
            return "player"
        elif rank_values[player_three_of_a_kind] < rank_values[dealer_three_of_a_kind]:
            return "dealer"

        player_kickers = sorted(
            (rank_values[card['rank']] for card in player_final_hand if card['rank'] != player_three_of_a_kind),
            reverse=True
        )[:2]

        dealer_kickers = sorted(
            (rank_values[card['rank']] for card in dealer_final_hand if card['rank'] != dealer_three_of_a_kind),
            reverse=True
        )[:2]

    # kicker for straight draw
    elif player_combination == "Straight":
        sorted_ranks_player = sorted({rank_values[card['rank']] for card in player_final_hand}, reverse=True)
        sorted_ranks_dealer = sorted({rank_values[card['rank']] for card in dealer_final_hand}, reverse=True)

        # go backwards and stop at the biggest
        for i in range(len(sorted_ranks_player) - 4):
            if sorted_ranks_player[i] - sorted_ranks_player[i + 4] == 4:
                for j in range(len(sorted_ranks_dealer) - 4):
                    if sorted_ranks_dealer[j] - sorted_ranks_dealer[j + 4] == 4:
                        if sorted_ranks_player[i] > sorted_ranks_dealer[j]:
                            return "player"
                        elif sorted_ranks_player[i] < sorted_ranks_dealer[j]:
                            return "dealer"

        # they have to be initialised
        player_kickers = []
        dealer_kickers = []

    # kicker for flush draw
    elif player_combination == "Flush":
        # just one suit possible
        suits = Counter(card['suit'] for card in player_final_hand)

        # one highest valued card
        most_common_suit, highest_count = suits.most_common(1)[0]
        player_kickers = sorted([rank_values[card['rank']] for card in player_final_hand 
                               if card['suit'] == most_common_suit],
                               reverse=True)[:5]
        dealer_kickers = sorted([rank_values[card['rank']] for card in dealer_final_hand 
                               if card['suit'] == most_common_suit],
                               reverse=True)[:5]

    # kicker for full house draw
    elif player_combination == "Full House":
        # check three of a kind first
        player_three_of_a_kind = max((rank_values[rank] for rank, count in player_counts.items() if count == 3))
        dealer_three_of_a_kind = max((rank_values[rank] for rank, count in dealer_counts.items() if count == 3))

        if player_three_of_a_kind > dealer_three_of_a_kind:
            return "player"
        elif player_three_of_a_kind < dealer_three_of_a_kind:
            return "dealer"
        
        # secondly check pair
        player_pair = max((rank_values[rank] for rank, count in player_counts.items() 
                           if count >= 2 and rank_values[rank] != player_three_of_a_kind))
        dealer_pair = max((rank_values[rank] for rank, count in dealer_counts.items() 
                           if count >= 2 and rank_values[rank] != player_three_of_a_kind))
        
        if player_pair > dealer_pair:
            return "player"
        elif player_pair < dealer_pair:
            return "dealer"
        
        # they have to be initialised
        player_kickers = []
        dealer_kickers = []

    # kicker for poker
    elif player_combination == "Four of a Kind":  
        # check what rank is in poker
        rank = list((rank_values[rank] for rank, count in player_counts.items() if count == 4))[0]

        # check just one kicker
        player_kickers = sorted(
            (rank_values[card['rank']] for card in player_final_hand if rank_values[card['rank']] != rank),
            reverse=True)[:1]
        dealer_kickers = sorted((
            rank_values[card['rank']] for card in dealer_final_hand if rank_values[card['rank']] != rank),
            reverse=True)[:1]
    
    # kicker for straight flush
    elif player_combination == "Straight Flush":
        # just one suit possible
        suits = Counter(card['suit'] for card in player_final_hand)

        # one highest valued card
        most_common_suit, highest_count = suits.most_common(1)[0]
        sorted_ranks_player = sorted({rank_values[card['rank']] for card in player_final_hand 
                                      if card["suit"] == most_common_suit}, 
                                      reverse=True)
        sorted_ranks_dealer = sorted({rank_values[card['rank']] for card in dealer_final_hand 
                                      if card["suit"] == most_common_suit}, 
                                      reverse=True)
        # they have to be initialised
        player_kickers = []
        dealer_kickers = []

        # go backwards and stop at the biggest
        for i in range(len(sorted_ranks_player) - 4):
            if sorted_ranks_player[i] - sorted_ranks_player[i + 4] == 4:
                for j in range(len(sorted_ranks_dealer) - 4):
                    if sorted_ranks_dealer[j] - sorted_ranks_dealer[j + 4] == 4:
                        if sorted_ranks_player[i] > sorted_ranks_dealer[j]:
                            return "player"
                        elif sorted_ranks_player[i] < sorted_ranks_dealer[j]:
                            return "dealer"
                        else:
                            return "tie"

    # kicker for royal flush
    elif player_combination == "Royal Flush":
        #not possible unless on river
        return "tie"

    # Comparing kickers if still undecided, kickers are already sorted
    for p_kicker, d_kicker in zip(player_kickers, dealer_kickers):
        if p_kicker > d_kicker:
            return "player"
        elif p_kicker < d_kicker:
            return "dealer"

    return "tie"



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
        combined_cards = player_hand + community_cards  # Combine player hand and community cards
        
        # Get the best hand using both player's hole cards and community cards
        player_best_hand = get_best_hand(combined_cards)
        # Get best community hand  
        community_best_hand = get_best_hand(community_cards)

        # if best hand is not on the table
        if player_best_hand != community_best_hand:  
            if player_best_hand in ["One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", 
                                    "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]:
                current_bet = ante * 2
                budget -= current_bet
                has_bet = True
                betting_history.append(f"Flop: Stavil(a) ste {current_bet}.")


    # after river
    community_cards += [deal_card(deck_copy), deal_card(deck_copy)]
    if not has_bet:  

        combined_cards = player_hand + community_cards  # Combine player hand and community cards
        
        # Get the best hand using both player's hole cards and community cards
        player_best_hand = get_best_hand(combined_cards)
        # Get best community hand  
        community_best_hand = get_best_hand(community_cards) 
        player_has_high_card = any(rank_values[card['rank']] >= 10 for card in player_hand)

        if player_best_hand == community_best_hand:
            if player_has_high_card:
                current_bet = ante * 1
                budget -= current_bet
                has_bet = True
                betting_history.append(f"Turn & River: Stavil(a) ste {current_bet}.")
            else:
                has_bet = False
                betting_history.append("Fold")
        elif combinations_values[player_best_hand] > combinations_values[community_best_hand]:
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
    print(f"River (5 skupnih kart): {community_cards[:3]} \n                        {community_cards[3:]}")
    
    print("\nZgodovina stav:")
    for bet in betting_history:
        print(bet)     

    # set ordered winning combinations
    winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", 
                     "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
    
    if not has_bet:
        print("Žal ste izgubili. Poskusite znova!")
    elif winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
        
        print("Čestitke, zmagali ste!") 

        dealer_has_something = dealer_has_pair_or_better_or_ace(dealer_hand, community_cards)
        blind_won = has_blind(blind, player_combination)
        
        winnings = current_bet * 2 + blind_won + (ante * 2 if dealer_has_something else ante)
        budget += winnings
        winnings -= (current_bet + blind + ante)
    
        print(f"Vaš dobitek: {winnings}")

    elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
        result = decider(player_combination, player_final_hand, dealer_combination, dealer_final_hand)

        if result == "player":
            print("Čestitke, zmagali ste!")  
            
            dealer_has_something = dealer_has_pair_or_better_or_ace(dealer_hand, community_cards)
            blind_won = has_blind(blind, player_combination)
            
            winnings = current_bet * 2 + blind_won + (ante * 2 if dealer_has_something else ante)
            budget += winnings
            winnings -= (current_bet + blind + ante)
        
            print(f"Vaš dobitek: {winnings}")

        elif result == "dealer":
            print("Žal ste izgubili. Poskusite znova!")

        else: 
            print("Izenačeno! Stavljeni denar vam je povrnjen.")
            budget += current_bet + ante + blind

    else:
        print("Žal ste izgubili. Poskusite znova!")


    print(f"\nPreostali proračun: {budget}")

def test(player_hand, dealer_hand, community_cards):
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

    # set ordered winning combinations
    winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", 
                     "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]

    if winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
        
        print("Čestitke, zmagali ste!") 

    elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
        result = decider(player_combination, player_final_hand, dealer_combination, dealer_final_hand)

        if result == "player":
            print("Čestitke, zmagali ste!")  

        elif result == "dealer":
            print("Žal ste izgubili. Poskusite znova!")

        else: 
            print("Izenačeno! Stavljeni denar vam je povrnjen.")

    else:
        print("Žal ste izgubili. Poskusite znova!")

def combination_counter(iter = 1000):
    dealer_count = {}
    player_count = {}

    for i in range(iter):
        
        # copy deck so its not ruined
        deck_copy = deck.copy()

        # shuffle copied deck
        random.shuffle(deck_copy)
        
        # deal hands to player and dealer 
        player_hand = [deal_card(deck_copy), deal_card(deck_copy)]
        dealer_hand = [deal_card(deck_copy), deal_card(deck_copy)]
        
        # after flop
        community_cards = [deal_card(deck_copy) for _ in range(3)]

        # after river
        community_cards += [deal_card(deck_copy), deal_card(deck_copy)]
    
        # take all available cards for evalueation
        player_final_hand = player_hand + community_cards
        dealer_final_hand = dealer_hand + community_cards

        # evaluate cards
        player_combination = get_best_hand(player_final_hand)
        dealer_combination = get_best_hand(dealer_final_hand)
        if player_combination not in player_count:
            player_count[player_combination] = 1
        else:
            player_count[player_combination] += 1
        
        if dealer_combination not in dealer_count:
            dealer_count[dealer_combination] = 1
        else:
            dealer_count[dealer_combination] += 1
    player_count = {key: value / iter for key, value in player_count.items()}
    dealer_count = {key: value / iter for key, value in dealer_count.items()}
    print(player_count)
    print(dealer_count)

def simulation_payout(iter = 1000): 
    global budget
    budget = 0
    bets = 0
    pre = 0
    flop = 0
    river = 0
    fold = 0
    for i in range(iter):

        ante = 10 # set ante value
        blind = 10 # set blind value
        current_bet = 0 # variable for bet
        has_bet = False # has already bet or not

        # copy deck so its not ruined
        deck_copy = deck.copy()

        # shuffle copied deck
        random.shuffle(deck_copy)
        
        # subtract ante, blind - always
        budget -= ante
        budget -= blind
        bets += 20

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
                bets += current_bet
                has_bet = True
                pre += 1
               

        # after flop
        community_cards = [deal_card(deck_copy) for _ in range(3)]

        if not has_bet:
            combined_cards = player_hand + community_cards  # Combine player hand and community cards
            
            # Get the best hand using both player's hole cards and community cards
            player_best_hand = get_best_hand(combined_cards)
            # Get best community hand  
            community_best_hand = get_best_hand(community_cards)

            # if best hand is not on the table
            if player_best_hand != community_best_hand:  
                if player_best_hand in ["One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", 
                                        "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]:
                    current_bet = ante * 2
                    bets += current_bet
                    budget -= current_bet
                    has_bet = True
                    flop += 1

        # after river
        community_cards += [deal_card(deck_copy), deal_card(deck_copy)]
        if not has_bet:  

            combined_cards = player_hand + community_cards  # Combine player hand and community cards
            
            # Get the best hand using both player's hole cards and community cards
            player_best_hand = get_best_hand(combined_cards)
            # Get best community hand  
            community_best_hand = get_best_hand(community_cards) 
            player_has_high_card = any(rank_values[card['rank']] >= 10 for card in player_hand)

            if player_best_hand == community_best_hand:
                if player_has_high_card:
                    current_bet = ante * 1
                    bets += 1
                    river += 1
                    budget -= current_bet
                    has_bet = True
                    
                else:
                    has_bet = False
                    
            elif combinations_values[player_best_hand] > combinations_values[community_best_hand]:
                current_bet = ante * 1
                bets += current_bet
                river += 1
                budget -= current_bet
                has_bet = True
            
        # take all available cards for evalueation
        player_final_hand = player_hand + community_cards
        dealer_final_hand = dealer_hand + community_cards

        # evaluate cards
        player_combination = get_best_hand(player_final_hand)
        dealer_combination = get_best_hand(dealer_final_hand)
         # set ordered winning combinations
        winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", 
                        "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
        
        if not has_bet:
            fold += 1
        elif winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
            
            dealer_has_something = dealer_has_pair_or_better_or_ace(dealer_hand, community_cards)
            blind_won = has_blind(blind, player_combination)
            
            winnings = current_bet * 2 + blind_won + (ante * 2 if dealer_has_something else ante)
            budget += winnings

        elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
            result = decider(player_combination, player_final_hand, dealer_combination, dealer_final_hand)
            if result == "player":  
                dealer_has_something = dealer_has_pair_or_better_or_ace(dealer_hand, community_cards)
                blind_won = has_blind(blind, player_combination)
                
                winnings = current_bet * 2 + blind_won + (ante * 2 if dealer_has_something else ante)
                budget += winnings
            elif result == "dealer":
                pass
            else: 
                budget += current_bet + ante + blind
    print(f"preflop {pre}")
    print(f"flop {flop}")
    print(f"river {river}")
    print(f"fold {fold}")
    print(f"Betted: {bets}")
    print(f"Preostali proračun: {budget}")
    print(f"Edge {(budget/bets) * 100}")

if __name__ == "__main__":
    play_game()





















