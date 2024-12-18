import itertools

# Function to calculate payout for a parlay
def calculate_payout(odds, wager):
    return wager * odds

# Function to generate round robin combinations
def generate_round_robin_teams(teams, parlay_size):
    return list(itertools.combinations(teams, parlay_size))

# Main function
def round_robin_simulation():
    # Step 1: Get user input
    num_teams = int(input("Enter the number of teams: "))
    teams = []

    for i in range(num_teams):
        team_name = input(f"Enter name for Team {i + 1}: ")
        odds = float(input(f"Enter odds for Team {i + 1}: "))
        result = input(f"Enter result for Team {i + 1} (win/loss): ").strip().lower()
        teams.append({'name': team_name, 'odds': odds, 'result': result})

    wager = float(input("Enter wager amount per parlay: "))
    parlay_size = int(input("Enter parlay size (e.g., 2 for 2-team parlays): "))

    # Step 2: Generate round robin combinations
    combinations = generate_round_robin_teams(teams, parlay_size)
    total_risk = len(combinations) * wager
    max_win = 0
    situational_result = 0

    # Step 3: Simulate results for each parlay
    print("\nRound Robin Results:")
    for combo in combinations:
        parlay_odds = 1
        parlay_wins = True

        # Calculate parlay odds and determine win/loss
        for team in combo:
            if team['result'] == 'loss':
                parlay_wins = False
            parlay_odds *= team['odds']

        # If parlay wins, calculate payout
        if parlay_wins:
            payout = calculate_payout(parlay_odds, wager)
            max_win += payout
            situational_result += payout
            print(f"Parlay {', '.join([t['name'] for t in combo])}: WIN (${payout:.2f})")
        else:
            situational_result -= wager
            print(f"Parlay {', '.join([t['name'] for t in combo])}: LOSS (-${wager:.2f})")

    # Step 4: Display summary
    print("\nSummary:")
    print(f"Max Win: ${max_win:.2f}")
    print(f"Total Risk: ${total_risk:.2f}")
    print(f"Situational Result: ${situational_result:.2f}")

# Run the simulation
if __name__ == "__main__":
    round_robin_simulation()
