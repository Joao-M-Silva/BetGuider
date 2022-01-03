from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
import os
import sys
from datetime import date, datetime, timedelta
import time
from pathlib import Path
import pandas as pd
import time

#Set the path for the chromedriver
#os.environ['PATH'] += r"C:/SeleniumDrivers"
#sys.path.append("/SeleniumDrivers/")

#Instantiate the driver
#driver = webdriver.Chrome()

#Get the website html architecture
#driver.get("https://oddsscanner.com/pt/")
#driver.implicitly_wait(30)

#Exploring an element
# - Accessing the text of the element with the property element.text
# - Clicking on the element with element.click()
# - Accessing an attribute with element.get_attribute('class')
# - Sending text to an input with: element.send_keys('mypassword')
#- Finding all child elements webelement.find_elements(By.CSS_SELECTOR, '*')
#- Get the text inside a tag: webelement.get_attribute('innerHTML)

#Exceptions
#try:
#    logout_button = driver.find_element_by_id("logout")
#    print('Successfully logged in')
#except NoSuchElementException:
#    print('Incorrect login/password')
    
#Wait until a condition returns True (Explicity Waiting)
#WebDriverWait(driver, 30).until(
#    EC.text_to_be_present_in_element(
#        #Element Filtration
#        (By.CLASS_NAME, 'class-value'),
#        #Expected Text
#        'text-to-match'
#        )
#    )

#driver.find_element(By.CSS_SELECTOR, "{css_element}[{key=value}]")

#Typing trick: 
#from selenium.webdriver.remote.webelement import WebElement
#def __init__(self, element:WebElement):
    

class OddScanner(webdriver.Chrome):
    def __init__(self, driver_path=Path.cwd(), teardown=False):
        self.teardown = teardown
        self.driver_path = driver_path
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        super(OddScanner, self).__init__(options=options)
        self.implicitly_wait(20)
    
    def __exit__(self,  exc_type, exc_val, exc_tb):
        """
        Function that defines what to do when exiting the context manager
        (With Statement)

        Returns
        -------
        None.

        """
        if self.teardown:
            self.quit()
        
    def land_first_page(self):
        self.get("https://oddsscanner.com/pt/")
        
    def choose_ambas_marcam(self):
        market = self.find_element(By.CLASS_NAME, 'market-filter')
        market.click()
        selected_market = self.find_element(By.CSS_SELECTOR, 
                                            """option[value='{"category":"Goals","type":"Both Teams to Score","timeline":"Full Time"}']""")
        selected_market.click()
        
    def select_date(self, time_delta=1):
        #Date to analyse
        date_analysis = datetime.now() + timedelta(days=int(time_delta))
        current_date = date_analysis - timedelta(days=1)
        if time_delta==1:
            #Click on the calendar logo
            calendar = self.find_element(By.CSS_SELECTOR, 
                                         'div[onclick="openCloseCalendar(this)"]')
            #Click on the logo using Javascript
            self.execute_script("arguments[0].click();", calendar)
        
        current_month = current_date.month
        print('Current Month:', current_month)
        current_year = current_date.year
        print('Current Year:', current_year)
            
        #Month to analyse
        analysis_month = date_analysis.month
        print('Analysis Month:', analysis_month)
        analysis_year = date_analysis.year
        print('Analysis Year:', analysis_year)
        
        if analysis_month > current_month or analysis_year > current_year:
            #Select next page in the calendar
            date_datetime = datetime.strptime(f'{analysis_year}-{analysis_month}-01', '%Y-%m-%d')
            date_to_click = date_datetime.strftime('%Y-%m-%d')
                
            #Click the next month in the calendar
            click_next_month = self.find_element(By.CSS_SELECTOR,
                                                 f'div[data-date="{date_to_click}"]')
            click_next_month.click()
        
        date_str = date_analysis.strftime('%Y-%m-%d')
        select_date = self.find_element(By.CSS_SELECTOR, 
                                        f'span[data-current_day="{date_str}"]')
        self.execute_script("arguments[0].click();", select_date)
        return date_str
    
        
    def extract_lines_in_the_page(self, info_page, date_analysis):
        """
        Function that scrapes the current page of the website

        Returns
        -------
        None.

        """
        
        competitions = self.find_elements(By.CSS_SELECTOR, 
                                          'div[class="competition"]')
        print('Number of competitions:', len(competitions))
        for index, competition in enumerate(competitions):
            #print(info_page)
            print(f'Competition {index+1}')
            #Get the competition country
            try:
                country = competition.find_element(By.CSS_SELECTOR,
                                                   'span[class="geographical-area name"]')
            except Exception as e:
                print(e)
            else:
                country_name = country.text.lower().strip()
                #Get the competition league name
                league = competition.find_element(By.CSS_SELECTOR,
                                                  'span[class="competition name"]')
                
                league_name = league.text.lower().strip()
                #Get the competition date
                hour = competition.find_element(By.CSS_SELECTOR,
                                                'span[class="datetime"')
                hour_name = hour.text.strip()
                if ':' not in hour_name:
                    games = []
                else:
                    #Get the games
                    #Only Pre-Matches
                    games = competition.find_elements(By.CSS_SELECTOR,
                                                      'div[class="fixture ns"]')
                print('Number of games:', len(games))
                for game in games:
                    info_page['Country'].append(country_name)
                    info_page['League'].append(league_name)
                    info_page['Hour'].append(hour_name)
                    info_page['Date'].append(date_analysis)
                    
                    #print(game.find_elements(By.CSS_SELECTOR, '*'))
                    event = game.find_element(By.CSS_SELECTOR,
                                              'div[class="event"]')
                    teams = event.text
                    team1 = teams.split('\n')[0].lower().strip()
                    team2 = teams.split('\n')[1].lower().strip()
                    
                    info_page['Team1'].append(team1)
                    info_page['Team2'].append(team2)
                    
                    odds_checker = True
                    while odds_checker:
                        try:
                            odds_text = game.find_element(By.CSS_SELECTOR,
                                                  'div[class="odds"]')
                            odds_text = odds_text.text
                            odds_checker = False
                        except StaleElementReferenceException:
                            print('Inside Infinite Loop')
                            time.sleep(2)
                            
                    #print('-----> ', odds_text.text.strip())
                        
                    flag = (odds_text.strip() != "Odds Indisponíveis")
                        
                    if flag:
                        print('Game with Odds')
                    
                        odds = game.find_elements(By.CSS_SELECTOR,
                                                      'div[class="market1"]')
                            
                        if odds:
                            print('ODDS READ')
                            odds_list = []
                            bookies_list = []
                            for i, odd in enumerate(odds):
                                append_check = True
                                counter = 0
                                while append_check:
                                    try:
                                        odd_str = odd.text.strip()
                                        odds_list.append(odd_str)
                                        append_check = False
                                    except StaleElementReferenceException:
                                        counter += 1
                                        if counter > 10:
                                            break
                                        print('Inside Append Infinite Loop')
                                        time.sleep(2)
                                if counter > 10:
                                    continue
                                
                                timeout_check = True
                                counter_timeout = 0
                                while timeout_check:
                                    try:           
                                        css_str = 'a[rel="nofollow"]'
                                        ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)
                                        bookie = WebDriverWait(odd, 
                                                               5, 
                                                               ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                                                                                                                          css_str)))
                                        timeout_check = False                                                                                                    
                                    except TimeoutException:  
                                        counter_timeout += 1
                                        if counter_timeout > 10:
                                            break
                                        print('Inside Timout Infinite Loop')
        
                                if counter_timeout > 10:
                                    continue
                                        
                                    
                                #bookie = odd.find_element(By.CSS_SELECTOR,
                                #                          'a[rel="nofollow"]')
                                        
                                bookie_name = bookie.get_attribute('title').strip()
                                bookies_list.append(bookie_name)
                                    
                            if not append_check and not timeout_check:            
                                odd1 = odds_list[0]
                                bookie1 = bookies_list[0]
                                oddX = odds_list[1]
                                bookieX = bookies_list[1]
                                odd2 = odds_list[2]
                                bookie2 = bookies_list[2]
                            else:
                                odd1 = '-'
                                bookie1 = '-'
                                oddX = '-'
                                bookieX = '-'
                                odd2 ='-'
                                bookie2 = '-'
                                
                        else:
                            odd1 = '-'
                            bookie1 = '-'
                            oddX = '-'
                            bookieX = '-'
                            odd2 ='-'
                            bookie2 = '-'
                    else:
                        odd1 = '-'
                        bookie1 = '-'
                        oddX = '-'
                        bookieX = '-'
                        odd2 ='-'
                        bookie2 = '-'
                                
                            
                    info_page['Odd1'].append(odd1)
                    info_page['Bookie1'].append(bookie1)
                    info_page['OddX'].append(oddX)
                    info_page['BookieX'].append(bookieX)
                    info_page['Odd2'].append(odd2)
                    info_page['Bookie2'].append(bookie2)
                    
                    #print('here')
                    #description_str = description.get_attribute('title')
                    #print(description_str)
                    #print('here2')
                
        
        return info_page
    
    def extract_lines_GG_NG(self, info_page, date_analysis):
        """
        Function that scrapes the current page of the website for GG/NG Odds

        """
        
        competitions = self.find_elements(By.CSS_SELECTOR, 
                                          'div[class="competition"]')
        print('Number of competitions:', len(competitions))
        for index, competition in enumerate(competitions):
            #print(info_page)
            print(f'Competition {index+1}')
            #Get the competition country
            try:
                country = competition.find_element(By.CSS_SELECTOR,
                                                   'span[class="geographical-area name"]')
            except Exception as e:
                print(e)
            else:
                countries ={'Germany':'alemanha',
                             'Italy':'itália',
                             'Spain':'espanha',
                             'England':'inglaterra',
                             'France':'frança',
                             'Netherlands':'países baixos',
                             'Belgium':'bélgica',
                             'Portugal':'portugal',
                             'Turkey':'turquia',
                             'Greece':'grécia',
                             'Scotland':'escócia',
                             'Argentina':'argentina',
                             'Austria':'austria',
                             'Brazil':'brasil',
                             'China':'china',
                             'Denmark':'dinamarca',
                             'Finland':'finlândia',
                             'Ireland':'irlanda',
                             'Japan':'japão',
                             'Mexico':'méxico',
                             'Norway':'noruega',
                             'Poland':'polónia',
                             'Romania':'roménia',
                             'Russia':'rússia',
                             'Sweden':'suécia',
                             'Switzerland':'suiça',
                             'USA':'usa',
                             }
                
                country_name = country.text.lower().strip()
                print(country_name)
                if country_name in list(countries.values()):
                    #Get the competition league name
                    league = competition.find_element(By.CSS_SELECTOR,
                                                      'span[class="competition name"]')
                    
                    league_name = league.text.lower().strip()
    
                    #Get the competition first hour 
                    #hour_first_game = competition.find_element(By.CSS_SELECTOR,
                    #                                           'span[class="datetime"')
                    #hour_name = hour_first_game.text.strip()
                    #print(hour_name)
                    #if ':' not in hour_name:
                    #    games = []
                    #else:
                        #Get the games
                        #Only Pre-Matches
                    games = competition.find_elements(By.CSS_SELECTOR,
                                                      'div[class="fixture ns"]')
                    
                    print('Number of games:', len(games))
                    for game in games:
                        info_page['Country'].append(country_name)
                        info_page['League'].append(league_name)
                        hour_game = game.find_element(By.CSS_SELECTOR,
                                                      'span[class="datetime"')
                        info_page['Hour'].append(hour_game)
                        info_page['Date'].append(date_analysis)
                        
                        #print(game.find_elements(By.CSS_SELECTOR, '*'))
                        event = game.find_element(By.CSS_SELECTOR,
                                                  'div[class="event"]')
                        teams = event.text
                        team1 = teams.split('\n')[0].lower().strip()
                        team2 = teams.split('\n')[1].lower().strip()
                        
                        
                        info_page['Team1'].append(team1)
                        info_page['Team2'].append(team2)
                        
                        odds_checker = True
                        while odds_checker:
                            try:
                                odds_text = game.find_element(By.CSS_SELECTOR,
                                                      'div[class="odds"]')
                                odds_text = odds_text.text
                                odds_checker = False
                            except StaleElementReferenceException:
                                print('Inside Infinite Loop')
                                time.sleep(2)
                                
                        #print('-----> ', odds_text.text.strip())
                            
                        flag = (odds_text.strip() != "Odds Indisponíveis")
                            
                        if flag:
                            print('Game with Odds')
                        
                            odds = game.find_elements(By.CSS_SELECTOR,
                                                          'div[class="market1"]')
                                
                            if odds:
                                print('ODDS READ')
                                odds_list = []
                                bookies_list = []
                                for i, odd in enumerate(odds):
                                    append_check = True
                                    counter = 0
                                    while append_check:
                                        try:
                                            odd_str = odd.text.strip()
                                            odds_list.append(odd_str)
                                            append_check = False
                                        except StaleElementReferenceException:
                                            counter += 1
                                            if counter > 10:
                                                break
                                            print('Inside Append Infinite Loop')
                                            time.sleep(2)
                                    if counter > 10:
                                        continue
                                    
                                    timeout_check = True
                                    counter_timeout = 0
                                    while timeout_check:
                                        try:           
                                            css_str = 'a[rel="nofollow"]'
                                            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException,)
                                            bookie = WebDriverWait(odd, 
                                                                   5, 
                                                                   ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                                                                                                                              css_str)))
                                            timeout_check = False                                                                                                    
                                        except TimeoutException:  
                                            counter_timeout += 1
                                            if counter_timeout > 10:
                                                break
                                            print('Inside Timout Infinite Loop')
            
                                    if counter_timeout > 10:
                                        continue
                                            
                                        
                                    #bookie = odd.find_element(By.CSS_SELECTOR,
                                    #                          'a[rel="nofollow"]')
                                            
                                    bookie_name = bookie.get_attribute('title').strip()
                                    bookies_list.append(bookie_name)
                                        
                                if not append_check and not timeout_check:            
                                    odd_GG = odds_list[0]
                                    bookie_GG = bookies_list[0]
                                    odd_NG = odds_list[1]
                                    bookie_NG = bookies_list[1]
                                    
                                else:
                                    odd_GG = '-'
                                    bookie_GG = '-'
                                    odd_NG = '-'
                                    bookie_NG = '-'
                                   
                                    
                            else:
                                odd_GG = '-'
                                bookie_GG = '-'
                                odd_NG = '-'
                                bookie_NG = '-'
                        else:
                            odd_GG = '-'
                            bookie_GG = '-'
                            odd_NG = '-'
                            bookie_NG = '-'
                                    
                                
                        info_page['Odd_GG'].append(odd_GG)
                        info_page['Bookie_GG'].append(bookie_GG)
                        info_page['Odd_NG'].append(odd_NG)
                        info_page['Bookie_NG'].append(bookie_NG)
    
                        
                        #print('here')
                        #description_str = description.get_attribute('title')
                        #print(description_str)
                        #print('here2')
                    
            
        return info_page
            
            
            
            
            
            
            
            
        
    

    

