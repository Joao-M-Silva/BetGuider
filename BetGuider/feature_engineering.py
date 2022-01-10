import pandas as pd
from datetime import date, timedelta


def league_average_goals(x, df, home_away:str, seasons:list):
    """
    Average goals per league

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    df : pd.DataFrame
        historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    seasons : list
        seasons of interest.
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away')
        
    #League
    div = x['Div']
    #Date
    game_date = x['Date']
    #Only consider games that happened before and including
    #the prior week
    limit_date = game_date - timedelta(weeks=1)
    df = df.query('(Date<=@limit_date) and (Season in @seasons) and (Div==@div)')
    total_goals = df[f'{home_away} Goals'].sum()
    total_matchs = df.shape[0]
    avg_goals = total_goals / total_matchs
    
    return avg_goals
    

def team_average_goals(x, df, home_away:str, seasons:list, 
                       sample:int=None, scored_conceded:str='scored'):
    """
    Average Goals Scored or Conceded per Team

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    df : pd.DataFrame
        historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    seasons : list
        seasons of interest.
    sample : int, optional
        Number of games to include in the calculations. 
        The default is None.
    scored_conceded:str, optional
        indicator to calculate average goals scored or conceded
        The default is scored.
        Options:
            scored, conceded
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away.')
    
    if scored_conceded not in ['scored', 'conceded']:
        raise Exception('Bad scored_conceded argument. options are scored and conceded.')
    
    game_date = x['Date']
    limit_date = game_date - timedelta(weeks=1)
    team = x[f'{home_away} Team']
    query = f'(Date<=@limit_date) and (Season in @seasons) and (`{home_away} Team`==@team)'
    query = query.replace('\n','')
    df = df.query(query)

    if sample:
        df = df.sort_values('Date', ascending=False).head(sample)
     
    if scored_conceded == 'scored':
        conv_ = {'Home':'Home',
                 'Away':'Away',}
    elif scored_conceded == 'conceded':
        conv_ = {'Home':'Away',
                 'Away':'Home',}
    
    home_away = conv_[home_away]
    total_goals = df[f'{home_away} Goals'].sum()
    total_matchs = df.shape[0]
    avg_goals = total_goals / total_matchs
    
    return avg_goals
        

def calculate_strenght(x, home_away:str, attack:bool, cs:bool, number_games:int=None):
    """
    Calculate offense and defense strenght

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    attack : bool
        boolean to define attach or defense calculations.
    cs : bool
        boolean to define global or current season calculations.
    number_games : int
        number of games period
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away.')
    
    if cs == False and number_games:
        raise Exception('While considering a sample of games the current season must be set to True (cs=True)')
    
    if home_away == 'Home':
        if attack:
            if cs:
                if not number_games:
                    return x['HT_Avg_G_Scored_CS'] / x['L_Avg_G_Sco_Home_CS']
                else:
                    return x[f'HT_Avg_G_Scored_{number_games}Games'] / x['L_Avg_G_Sco_Home_CS']
            else:
                return x['HT_Avg_G_Scored'] / x['L_Avg_G_Sco_Home']
        else:
            if cs:
                if not number_games:
                    return x['HT_Avg_G_Conceded_CS'] / x['L_Avg_G_Sco_Away_CS']
                else:
                    return x[f'HT_Avg_G_Conceded_{number_games}Games'] / x['L_Avg_G_Sco_Away_CS']
            else:
                return x['HT_Avg_G_Conceded'] / x['L_Avg_G_Sco_Away']
    
    elif home_away == 'Away':
        if attack:
            if cs:
                if not number_games:
                    return x['AT_Avg_G_Scored_CS'] / x['L_Avg_G_Sco_Away_CS']
                else:
                    return x[f'AT_Avg_G_Scored_{number_games}Games'] / x['L_Avg_G_Sco_Away_CS']
            else:
                return x['AT_Avg_G_Scored'] / x['L_Avg_G_Sco_Away']
        else:
            if cs:
                if not number_games:
                    return x['AT_Avg_G_Conceded_CS'] / x['L_Avg_G_Sco_Home_CS']
                else:
                    return x[f'AT_Avg_G_Conceded_{number_games}Games'] / x['L_Avg_G_Sco_Home_CS']
            else:
                return x['AT_Avg_G_Conceded'] / x['L_Avg_G_Sco_Home']
                

def goal_expectancy(x, home_away:str, cs:bool, number_games:int=None):
    """
    Calculate Goal Expectancy for the Home or Away Team

    Parameters
    ----------
    x : 
        row of the historical data dataframe.
    home_away : str
        reference to calculations
        Options: Home, Away.
    cs : bool
        boolean to define global or current season calculations.
    number_games : int
        number of games period
    """
    if home_away not in ['Home', 'Away']:
        raise Exception('Bad home_away argument. Options are Home and Away.')
    
    if cs == False and number_games:
        raise Exception('While considering a sample of games the current season must be set to True (cs=True)')
        
    if home_away == 'Home':
        if cs:
            if not number_games:
                home_attack_strenght = x['HT_Att_Strenght_CS']
                away_defense_strenght = x['AT_Def_Strenght_CS']
                goal_expectancy = home_attack_strenght*away_defense_strenght*x['L_Avg_G_Sco_Home_CS']
                return goal_expectancy
            else:
                home_attack_strenght = x[f'HT_Att_Strenght_{number_games}Games']
                away_defense_strenght = x[f'AT_Def_Strenght_{number_games}Games']
                goal_expectancy = home_attack_strenght*away_defense_strenght*x['L_Avg_G_Sco_Home_CS']
                return goal_expectancy
            
        else:
            home_attack_strenght = x['HT_Att_Strenght']
            away_defense_strenght = x['AT_Def_Strenght']
            goal_expectancy = home_attack_strenght*away_defense_strenght*x['L_Avg_G_Sco_Home']
            return goal_expectancy
        
    elif home_away == 'Away':
        if cs:
            if not number_games:
                away_attack_strenght = x['AT_Att_Strenght_CS']
                home_defense_strenght = x['HT_Def_Strenght_CS']
                goal_expectancy = away_attack_strenght*home_defense_strenght*x['L_Avg_G_Sco_Away_CS']
                return goal_expectancy
            else:
                away_attack_strenght = x[f'AT_Att_Strenght_{number_games}Games']
                home_defense_strenght = x[f'HT_Def_Strenght_{number_games}Games']
                goal_expectancy = away_attack_strenght*home_defense_strenght*x['L_Avg_G_Sco_Away_CS']
                return goal_expectancy
        else:
            away_attack_strenght = x['AT_Att_Strenght']
            home_defense_strenght = x['HT_Def_Strenght']
            goal_expectancy = away_attack_strenght*home_defense_strenght*x['L_Avg_G_Sco_Away']
            return goal_expectancy
    
    