from Sites.oddscanner import OddScanner
import pandas as pd
import time
import datetime

"""
DataFrame columns:
    Data
    Hour
    Country
    League
    Team1
    Team2
    Bookie1
    Odd1
    BookieX
    OddX
    Bookie2
    Odd2
    Arbitrage_Ratio
    Value1
    ValueX
    Value2
"""
def GG_NG_OddScanner():
    with OddScanner() as oc_bot:
        info_page = {'Country':[],
                     'League':[],
                     'Date':[],
                     'Hour':[],
                     'Team1':[],
                     'Team2':[],
                     'Odd_GG':[],
                     'Bookie_GG':[],
                     'Odd_NG':[],
                     'Bookie_NG':[],
                     }
        oc_bot.land_first_page()
        oc_bot.choose_ambas_marcam()
        #number_of_days = 4
        time.sleep(2)
        #for day in range(number_of_days):
        #date = oc_bot.select_date(time_delta=day+1)
        date = datetime.datetime.today()
        info_page = oc_bot.extract_lines_GG_NG(info_page, date)
        
        df = pd.DataFrame(info_page)    
        df.to_csv('C:/Users/Asus/Documents/Python Scripts/BetGuider/info_data_GG_NG.csv')
        
    return df 
        

def scrape_OddScanner():
    with OddScanner() as oc_bot:
        info_page = {'Country':[],
                     'League':[],
                     'Date':[],
                     'Hour':[],
                     'Team1':[],
                     'Team2':[],
                     'Odd1':[],
                     'Bookie1':[],
                     'OddX':[],
                     'BookieX':[],
                     'Odd2':[],
                     'Bookie2':[],
                     }
        oc_bot.land_first_page()
        #oc_bot.choose_ambas_marcam()
        number_of_days = 4
        for day in range(number_of_days):
            date = oc_bot.select_date(time_delta=day+1)
            info_page = oc_bot.extract_lines_in_the_page(info_page, date)
            
        df = pd.DataFrame(info_page)    
        #df = calculations(df)
        df.to_csv('C:/Users/Asus/Documents/Python Scripts/Selenium/info_data.csv')


def scrape_data():
    df_scrape = GG_NG_OddScanner()
    return df_scrape
    
    
