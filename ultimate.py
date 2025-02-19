import random
from collections import Counter

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {rank: i for i, rank in enumerate(ranks, start=2)}

deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

budget = 1000

def deal_card(deck):
    return deck.pop(random.randint(0, len(deck) - 1))

def should_raise_pre_flop(card1, card2):
    higher, lower = sorted([card1, card2], key=lambda c: ranks.index(c['rank']))
    decision_table = {
        ('A', '2'): 'Y', ('A', '3'): 'Y', ('A', '4'): 'Y', ('A', '5'): 'Y', ('A', '6'): 'Y', ('A', '7'): 'Y', ('A', '8'): 'Y', ('A', '9'): 'Y', ('A', '10'): 'Y', ('A', 'J'): 'Y', ('A', 'Q'): 'Y', ('A', 'K'): 'Y',
        ('K', '10'): 'Y', ('K', 'J'): 'Y', ('K', 'Q'): 'Y',
        ('Q', '10'): 'Y', ('Q', 'J'): 'Y',
        ('J', '10'): 'Y'}
    return 4 if decision_table.get((higher['rank'], lower['rank']), 'N') == 'Y' else 0

def get_best_hand(cards):
    counts = Counter(card['rank'] for card in cards)
    suits = Counter(card['suit'] for card in cards)
    sorted_ranks = sorted([rank_values[card['rank']] for card in cards], reverse=True)

    if {'10', 'J', 'Q', 'K', 'A'}.issubset(counts.keys()) and any(suits[suit] >= 5 for suit in suits):
        return "Royal Flush"

    for suit in suits:
        suited_cards = [rank_values[card['rank']] for card in cards if card['suit'] == suit]
        if len(suited_cards) >= 5 and max(suited_cards) - min(suited_cards[:5]) == 4:
            return "Straight Flush"

    if 4 in counts.values():
        return "Four of a Kind"

    if 3 in counts.values() and 2 in counts.values():
        return "Full House"

    if any(suits[suit] >= 5 for suit in suits):
        return "Flush"

    unique_ranks = sorted(set(sorted_ranks), reverse=True)
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i + 4] == 4:
            return "Straight"

    if 3 in counts.values():
        return "Three of a Kind"

    if list(counts.values()).count(2) == 2:
        return "Two Pair"

    if 2 in counts.values():
        return "One Pair"

    return "High Card"

def play_game():
    global budget

    ante = 10
    current_bet = 0
    has_bet = False  
    betting_history = []  

    deck_copy = deck.copy()
    random.shuffle(deck_copy)

    player_hand = [deal_card(deck_copy), deal_card(deck_copy)]
    dealer_hand = [deal_card(deck_copy), deal_card(deck_copy)]

    if not has_bet: 
        bet_multiplier = should_raise_pre_flop(player_hand[0], player_hand[1])
        if bet_multiplier > 0:
            current_bet = ante * bet_multiplier
            budget -= current_bet
            has_bet = True
            betting_history.append(f"Preflop: Stavil(a) ste {current_bet}.")

    community_cards = [deal_card(deck_copy) for _ in range(3)]
    if not has_bet:  
        combined_cards = player_hand + community_cards
        if get_best_hand(combined_cards) in ["One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]:
            current_bet = ante * 2
            budget -= current_bet
            has_bet = True
            betting_history.append(f"Flop: Stavil(a) ste {current_bet}.")

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

    player_final_hand = player_hand + community_cards
    dealer_final_hand = dealer_hand + community_cards

    player_combination = get_best_hand(player_final_hand)
    dealer_combination = get_best_hand(dealer_final_hand)

    print("\n--- REZULTATI IGRE ---")
    print(f"Vaša roka: {player_hand}, Kombinacija: {player_combination}")
    print(f"Delivčeva roka: {dealer_hand}, Kombinacija: {dealer_combination}")
    print(f"River (5 skupnih kart): {community_cards}")
    
    print("\nZgodovina stav:")
    for bet in betting_history:
        print(bet)

    dealer_pair_or_ace = any(card['rank'] in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] for card in dealer_hand)
    ante_win = ante  

    if dealer_pair_or_ace:
        ante = ante * 2 

    winning_hands = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
    if winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
        print("Čestitke, zmagali ste!")
        winnings = current_bet * 2 + ante  
        budget += winnings
        print(f"Vaš dobitek: {winnings}")
    elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
        print("Izenačeno! Stavljeni denar vam je povrnjen.")
        budget += current_bet  
    else:
        print("Žal ste izgubili. Poskusite znova!")

    print(f"\nPreostali proračun: {budget}")

if __name__ == "__main__":
    play_game()





















