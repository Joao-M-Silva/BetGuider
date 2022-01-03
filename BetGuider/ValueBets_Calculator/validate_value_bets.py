from scipy.spatial import distance
import numpy as np


def index_range(list_indices):
    list_min = []
    list_max = []
    for indices in list_indices:
        list_min.append(indices.min())
        list_max.append(indices.max())
        
    min_ = min(list_min)
    max_ = max(list_max)
    
    return list(range(int(min_),int(max_)+1))    
        

def probability_distribution(df, team_name:str, seasons:list, home_away:str, stat:str):
    if home_away == 'home':
        df = df[df['Home Team']==team_name]
    elif home_away == 'away':
        df = df[df['Away Team']==team_name]
    else:
        raise Exception('Bad input for home_away.')
    
    list_indices = []
    list_results = []
    list_total_games = []
    for season in seasons:
        df_season = df[df['Season']==season]
        index_values = df_season[stat].value_counts().sort_index()
        list_indices.append(index_values.index)
        list_results.append(index_values)
        list_total_games.append(index_values.sum())
    
    index_vector = index_range(list_indices)
    
    probs = []
    for result, total_games in zip(list_results, list_total_games):
        probs_season = []
        for index in index_vector:
            if index not in result.index:
                count = 0
            else:
                count = result[index]
            probs_season.append(count/total_games)
        
        probs.append(probs_season)
        
    return probs


def probs_divergence(probs):
    divergences = []
    for i in range(len(probs)):
        if i < (len(probs)-1):
            divergence = distance.jensenshannon(probs[i], probs[i+1])
            divergences.append(divergence)
    
    return np.array(divergences).mean()


def calculate_divergence(x, df_hist, home_away:str, seasons):
    if home_away == 'home':
        team = x['Home Team Matched']
    elif home_away == 'away':
        team = x['Away Team Matched']
    else:
        raise Exception('Bad selection for home_away')
    
    #Get the probability distributions
    ###ADD MORE STATS###
    stats = ['Home Goals', 'Away Goals']
    divergences = []
    for stat in stats:
        probs = probability_distribution(df_hist, team_name=team, seasons=seasons, home_away=home_away, stat=stat)
        divergence = probs_divergence(probs)
        divergences.append(divergence)
    
    return np.array(divergences).mean()
    

