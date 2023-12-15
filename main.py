import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import locale
import os
import tweepy
import yaml

######################################################################################################################################
# API_KEY = 
# API_SECRET = 
# BEARER_TOKEN = 
# ACCESS_TOKEN = 
# ACCESS_TOKEN_SECRET = 

#Connexion API Twitter
client = tweepy.Client(consumer_key=API_KEY,
                       consumer_secret=API_SECRET,
                       access_token=ACCESS_TOKEN,
                       access_token_secret=ACCESS_TOKEN_SECRET)
#######################################################################################################################################

# Définir la localisation en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
today = date.today()

#Fonction envoi tweet
def send_tweet_notification(competition, equipe_domicile, equipe_exterieur, horaire, stade, chaine, hashtag):
    response = client.create_tweet(text=  '🏆 : ' + competition + '\n⚽️ : '+ equipe_domicile + ' - ' + equipe_exterieur + '\n🕐 : ' + horaire + '\n🏟 : ' + stade.strip() + '\n📺 : '+ chaine.strip() + "\n" + "#" + hashtag)
    print(response)

# Convertir une chaîne de date au format "jour dd/mm" en datetime
def string_to_datetime(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

def get_match_links(url, headers):
    with open("path/headers.yml") as f_headers:
        browser_headers = yaml.safe_load(f_headers)
    browser_headers["Firefox"]
    match_links = []
    response = requests.get(url, headers=browser_headers["Firefox"])
    
    if response.ok:
        soup = BeautifulSoup(response.text, "lxml")
        match_cards = soup.find_all("div", class_="card--matchWithDate")

        for card in match_cards:
            match_date_elem = card.find("div", class_="match__topDate")
            if match_date_elem:
                match_date = match_date_elem.get_text().strip()
                if match_date == today.strftime("%A %d/%m").lower():
                    match_link_elem = card.find("a", class_="match__teams")
                    if match_link_elem:
                        match_link = match_link_elem["href"]
                        match_links.append('https://www.footballwebsite.com' + match_link)
    return match_links

def process_match_page(url):
    response = requests.get(url)
    
    if response.ok:
        soup = BeautifulSoup(response.text, "lxml")
        soup = BeautifulSoup(response.text, "lxml") 
        competition = soup.find("div", class_="matchHeader__top").find("span")
        equipe_domicile = soup.find("div", class_="matchHeader__team matchHeader__team--home").find("span")
        equipe_exterieur = soup.find("div", class_="matchHeader__team matchHeader__team--away").find("span")
        
        horaire = soup.find("div", class_="matchHeader__date").select_one(":nth-child(2)")
        jour_du_match = soup.find("div", class_="matchHeader__date")
        stade = soup.find("div", class_="venue__title")
        chaine = soup.find("div", class_="card card--withSpace card--faq").select_one(":nth-child(2)")
        hashtag_element_span = soup.find('span', text='Code')
        hashtag = hashtag_element_span.find_next('strong').text.replace('-','')

        #Mise en forme correcte de la chaîne
        chaine = chaine.text.replace('\n','')
        #Cas où le match est diffusé sur 2 chaînes
        if "        " in chaine:
            chaine = chaine.replace('        ',' ')
        
        if "     " in chaine:
            chaine = chaine.replace('     ',' ')

        #Suppression des premiers caractères de la phrase pour les chaînes
        chaine = chaine[50:]
        return competition.text, equipe_domicile.text, equipe_exterieur.text, horaire.text, jour_du_match.text, stade.text.strip(), chaine.strip(), hashtag
    return None

def main():
    headers = {
        # Your headers here
    }
    team_url = 'https://www.footballwebsite.com/team/fc-barcelona'
    match_links = get_match_links(team_url, headers)
    
    if match_links:
        with open('urls.txt', 'w') as file:
            for link in match_links:
                file.write(link + '\n')
        
        with open('urls.txt', 'r') as file:
            for row in file:
                match_info = process_match_page(row.strip())
                if match_info:
                    competition = match_info[0]
                    equipe_domicile = match_info[1]
                    equipe_exterieur = match_info[2]
                    horaire = match_info[3]
                    jour_du_match = match_info[4]
                    stade = match_info[5]
                    chaine = match_info[6]
                    hashtag = match_info[7]

                    # Obtenir la date actuelle
                    aujourdhui = datetime.now()

                    # Traiter la date du prochain match
                    prochain_match_str = jour_du_match.replace('\n', ' ').strip()
                    prochain_match_date = string_to_datetime(prochain_match_str)
                    prochain_match_time = datetime.strptime(prochain_match_str, "%d/%m/%Y %H:%M")

                    # Définir le délai de notification
                    delai_notification = timedelta(hours=1.5)
                    notification_prochain_match = prochain_match_time - delai_notification

                    # Afficher les dates
                    print('#######  Dates #######')
                    print(f"Maintenant : {aujourdhui}")
                    print(f"Prochain match : {prochain_match_time}")
                    print(f"Tweet prévu : {notification_prochain_match}")
                    print(' ')

                    # Afficher les informations du match
                    print('Prochain match')
                    print(f'🏆 : {competition}')
                    print(f'⚽️ : {equipe_domicile} - {equipe_exterieur}')
                    print(f'🕐 : {horaire}')
                    print(f'🏟  : {stade}')
                    print(f'📺 : {chaine}')
                    print(f"#{hashtag}")
                    print(' ')

                    # Vérifier si l'heure actuelle est dans la plage de notification
                    if notification_prochain_match <= aujourdhui < prochain_match_time:
                        print("Match aujourd'hui")
                        send_tweet_notification(competition, equipe_domicile, equipe_exterieur, horaire, stade, chaine, hashtag)
                    elif aujourdhui >= prochain_match_time:
                        print("Match aujourd'hui tweet envoyé à :", notification_prochain_match)
                    else:
                        print("Pas de match aujourd'hui")
                    pass
                else:
                    print("Failed to fetch match page:", row.strip())
    else:
        print("No matches found for today.")

if __name__ == "__main__":
    main()
