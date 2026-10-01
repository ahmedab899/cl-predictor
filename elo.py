import math

import random

def get_actual_score(home_goals, away_goals):

    if home_goals > away_goals:
        actual_score = 1
    elif home_goals < away_goals:
        actual_score = 0
    else:
        actual_score = 0.5

    return actual_score


def expected_score(rating_a, rating_b):

    exponent = ( rating_b - rating_a) / 400

    denominator_part = 10** exponent

    result = 1/ (1 + denominator_part)

    return result

def update_rating(rating, expected, actual, k =32):

    outcome = (actual - expected)

    k_part = k*outcome

    new_rating = rating + k_part

    return new_rating

def expected_goals(rating_a, rating_b, base_goals_per_team):

    probability = expected_score(rating_a, rating_b)

    return base_goals_per_team * 2 * probability



def poisson_probability(k, expected_goals):

    first_part = expected_goals**k

    second_part = math.exp(- expected_goals)

    RHS = first_part*second_part

    final = RHS / math.factorial(k)

    return final


def match_scoreline_probabilities(home_expected_goals, away_expected_goals, max_goals = 6):

    scoreline_probs = {}
    
    for h in range(0, max_goals + 1):
        for a in range(0, max_goals + 1):
            prob_h = poisson_probability(h, home_expected_goals)
            prob_a = poisson_probability(a, away_expected_goals)

            scoreline_probs[(h,a)] = prob_h* prob_a

    return scoreline_probs

probs = match_scoreline_probabilities(1.8, 1.2)

def match_outcome_probabilities(scoreline_probs):

    home_win_prob = 0
    draw_prob = 0 
    away_win_prob = 0

    for (h,a), prob in scoreline_probs.items():
        if h > a:
            home_win_prob = home_win_prob + prob
        elif h == a:
            draw_prob = draw_prob + prob
        else:
            away_win_prob = away_win_prob + prob


    return home_win_prob, draw_prob, away_win_prob


def simulate_match(scoreline_probs):
    outcomes = list(scoreline_probs.keys())
    weights = list(scoreline_probs.values())

    result = random.choices(outcomes, weights, k = 1)

    return result[0]

def simulate_penalties(rating_a, rating_b):
    p = expected_score(rating_a, rating_b)

    pen_prob = 0.5 + (p - 0.5)*0.2

    if pen_prob > random.random():
        return True
    else:
        return False




    


    


