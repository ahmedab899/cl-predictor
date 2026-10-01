from models import get_engine, Match, Team
from sqlalchemy.orm import sessionmaker
from elo import expected_score, update_rating, get_actual_score, expected_goals, match_scoreline_probabilities, match_outcome_probabilities, simulate_match, simulate_penalties

engine = get_engine()

Session = sessionmaker(bind=engine)
session = Session()

matches = session.query(Match).filter_by(status="FINISHED").order_by(Match.match_date).all()

total_count = session.query(Match).count()

sample = session.query(Match).first()

ratings = {}

for match in matches:
    home_rating = ratings.get(match.home_team_id, 1500)
    away_rating = ratings.get(match.away_team_id, 1500)

    expected_home = expected_score(home_rating, away_rating)
    actual_home = get_actual_score(match.home_goals, match.away_goals)
    new_home_rating = update_rating(home_rating, expected_home, actual_home)
    new_away_rating = update_rating(away_rating, 1- expected_home, 1- actual_home)

    ratings[match.home_team.id] = new_home_rating
    ratings[match.away_team.id] = new_away_rating


for team_id, rating in ratings.items():
    team = session.query(Team).filter_by(id = team_id).first()
    

total_goals = 0

for match in matches:
    total_goals = total_goals + match.away_goals + match.home_goals
    league_average_goals = total_goals / len(matches)




team1 = session.query(Team).filter_by(name = ("Liverpool FC")).first()
team2 = session.query(Team).filter_by(name = ("Real Madrid CF")).first()

team1_rating = ratings.get(team1.id, 1500)
team2_rating = ratings.get(team2.id, 1500)

base_goals_per_team = league_average_goals / 2


team1_expected_goals = expected_goals(team1_rating, team2_rating, base_goals_per_team)
team2_expected_goals = expected_goals(team2_rating, team1_rating, base_goals_per_team)

scoreline_probs = match_scoreline_probabilities(team1_expected_goals, team2_expected_goals)


home, draw, away = outcome_probability = match_outcome_probabilities(scoreline_probs)

home = round(home*100, 0)
draw = round(draw*100, 0)
away = round(away*100, 0)

def simulate_fixture(home_id, away_id, ratings, base_goals_per_team):
    home_rating = ratings.get(home_id , 1500)
    away_rating = ratings.get(away_id, 1500)
    
    home_expected_goals = expected_goals(home_rating, away_rating, base_goals_per_team)
    away_expected_goals = expected_goals(away_rating, home_rating, base_goals_per_team)
    
    scoreline_probs = match_scoreline_probabilities(home_expected_goals, away_expected_goals)
    
    result = simulate_match(scoreline_probs)
    
    return result

def simulate_tie(team_a, team_b, ratings, base_goals_per_team):

    leg1 = simulate_fixture(team_a, team_b, ratings, base_goals_per_team)
    leg2 = simulate_fixture(team_b, team_a, ratings, base_goals_per_team)

    a_total = leg1[0] + leg2[1]
    b_total = leg1[1] + leg2[0]

    if a_total > b_total:
        return team_a
    elif b_total > a_total:
        return team_b
    else:
        a_rating = ratings.get(team_a , 1500)
        b_rating = ratings.get(team_b, 1500)

        pen_shootout = simulate_penalties(a_rating, b_rating)

        if pen_shootout == True:
            return team_a
        else:
            return team_b

def simulate_playoffs(playoff_teams, ratings, base_goals_per_team):

    winners = []

    for i in range(8):
        team_a = playoff_teams[i][0]
        team_b = playoff_teams[15 - i][0]

        winner = simulate_tie(team_a, team_b, ratings, base_goals_per_team)

        winners.append(winner)

    return winners

def simulate_round_of_16(top_8_ids, playoff_winners, ratings, base_goals_per_team):
    winners = []

    for i in range(8):
        team_a = top_8_ids[i]
        team_b = playoff_winners[7-i]
        winner = simulate_tie(team_a, team_b, ratings, base_goals_per_team)
        winners.append(winner)

    return winners

def simulate_knockout_round(teams, ratings, base_goals_per_team):
    winners = []
    n = len(teams)

    for i in range(n//2):
        team_a = teams[i]
        team_b = teams[(n-1) - i]
        winner = simulate_tie(team_a, team_b, ratings, base_goals_per_team)
        winners.append(winner)

    return winners

def simulate_final(team_a, team_b, ratings, base_goals_per_team):

    result = simulate_fixture(team_a, team_b, ratings, base_goals_per_team)

    if result[0] > result[1]:
        return team_a
    elif result[1] > result[0]:
        return team_b
    else:
        a_rating = ratings.get(team_a , 1500)
        b_rating = ratings.get(team_b, 1500)
        
        pen_shootout = simulate_penalties(a_rating, b_rating)
        
        if pen_shootout == True:
            return team_a
        else:
            return team_b

def simulate_tournament(matches, ratings, base_goals_per_team):

    table = build_league_table(matches, ratings, base_goals_per_team)
    standings = sorted(table.items(), key=sort_key, reverse=True)

    top_8 = standings[0:8]
    playoff_teams = standings[8:24]

    top_8_ids = []

    for top_id in top_8:
        top_8_ids.append(top_id[0])

    playoff_winners = simulate_playoffs(playoff_teams, ratings, base_goals_per_team)

    r16_winners = simulate_round_of_16(top_8_ids, playoff_winners, ratings, base_goals_per_team)

    qf_winners = simulate_knockout_round(r16_winners, ratings, base_goals_per_team)
    sf_winners = simulate_knockout_round(qf_winners, ratings, base_goals_per_team)

    champion = simulate_final(sf_winners[0], sf_winners[1], ratings, base_goals_per_team)

    return champion

    


def get_match_result(match, ratings, base_goals_per_team):
    if match.status == "FINISHED":
        return match.home_goals, match.away_goals
    else:
        
        return simulate_fixture (match.home_team_id, match.away_team_id, ratings, base_goals_per_team)


test_match = session.query(Match).filter_by(season=2026, status="TIMED").first()


finished_match = session.query(Match).filter_by(season=2026, status="FINISHED").first()

def sort_key(item):
    team_id, stats = item

    goal_difference = stats["goals_for"] - stats["goals_against"]

    return stats["points"], goal_difference, stats["goals_for"]


def build_league_table(matches, ratings, base_goals_per_team):

    table = {}

    for match in matches:
        home_id = match.home_team_id
        away_id = match.away_team_id
        if home_id not in table:
            table[home_id] = {"points": 0, "goals_for": 0, "goals_against": 0, "played": 0}
        if away_id not in table:
            table[away_id] = {"points": 0, "goals_for": 0, "goals_against": 0, "played": 0}
        home_goals, away_goals = get_match_result(match, ratings, base_goals_per_team)
        table[home_id]["played"] += 1
        table[home_id]["goals_for"] += home_goals
        table[home_id]["goals_against"] += away_goals
        table[away_id]["played"] += 1
        table[away_id]["goals_for"] += away_goals
        table[away_id]["goals_against"] += home_goals

        if home_goals > away_goals:
            table[home_id]["points"] += 3
        elif home_goals == away_goals:
            table[home_id]["points"] += 1
            table[away_id]["points"] += 1
        else:
            table[away_id]["points"] += 3       

    return table



matches_2026 = session.query(Match).filter_by(season=2026).all()

team_names = {}

for team in session.query(Team).all():
    team_names[team.id] = team.name

champion = simulate_tournament(matches_2026, ratings, base_goals_per_team)


win_counts = {}

num_simulations = 10000

for i in range(num_simulations):
    champion = simulate_tournament(matches_2026, ratings, base_goals_per_team)

    if champion not in win_counts:
        win_counts[champion] = 0

    win_counts[champion] += 1


def by_wins(item):
    team_id, count = item
    return win_counts.items, count

results = sorted(win_counts.items(), key = by_wins, reverse = True)

for position, (team_id, count) in enumerate(results, start = 1):
    percentage = (count / num_simulations)*100
    print(position, team_names[team_id], f"{percentage:.1f}%")





