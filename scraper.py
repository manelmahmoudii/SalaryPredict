"""
Scraper Indeed avec Selenium
Contourne les protections anti-bot d'Indeed
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import os

# Configuration
INDEED_URL = "https://fr.indeed.com"

def setup_driver():
    """Configure le driver Selenium Chrome"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Mode sans interface graphique
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Masquer que c'est Selenium
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def parse_salary(salary_text):
    """Extrait le salaire du texte et le convertit en annuel"""
    if not salary_text:
        return None
    
    # Extraire les nombres
    numbers = re.findall(r'\d+[\d\s]*', salary_text)
    if not numbers:
        return None
    
    salary = int(numbers[0].replace(' ', ''))
    
    # Convertir en annuel
    if 'heure' in salary_text.lower() or '/h' in salary_text.lower():
        salary = salary * 35 * 52
    elif 'mois' in salary_text.lower() or '/mois' in salary_text.lower():
        salary = salary * 12
    
    return salary

def scrape_indeed_selenium(job_query, location, num_pages=3):
    """
    Scrape les offres Indeed avec Selenium
    
    Args:
        job_query: Titre du poste (ex: "Développeur Python")
        location: Ville (ex: "Paris")
        num_pages: Nombre de pages à scraper
    
    Returns:
        Liste de dictionnaires avec les données des offres
    """
    jobs = []
    driver = None
    
    try:
        print(f"\n🔍 Recherche: {job_query} à {location}")
        
        # Initialiser le driver
        driver = setup_driver()
        
        for page in range(num_pages):
            try:
                # URL de recherche
                start = page * 10
                url = f"{INDEED_URL}/jobs?q={job_query}&l={location}&start={start}"
                
                print(f"  📄 Page {page + 1}/{num_pages}... ", end='')
                
                # Charger la page
                driver.get(url)
                
                # Attendre que les offres se chargent
                time.sleep(random.uniform(2, 4))
                
                # Parser le HTML avec BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Trouver toutes les cartes d'offres
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                if not job_cards:
                    # Essayer une autre classe
                    job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
                
                if not job_cards:
                    print("⚠️  Aucune offre")
                    break
                
                # Extraire les données
                page_jobs = 0
                for card in job_cards:
                    try:
                        # Titre
                        title_elem = card.find('h2', class_='jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else "N/A"
                        
                        # Entreprise
                        company_elem = card.find('span', {'data-testid': 'company-name'})
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        
                        # Localisation
                        location_elem = card.find('div', {'data-testid': 'text-location'})
                        loc = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Description
                        desc_elem = card.find('div', class_='job-snippet')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        # Salaire
                        salary_elem = card.find('div', {'data-testid': 'attribute-snippet-testid'})
                        salary_text = salary_elem.get_text(strip=True) if salary_elem else None
                        salary = parse_salary(salary_text)
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': loc,
                            'description': description,
                            'salary': salary
                        })
                        page_jobs += 1
                        
                    except Exception as e:
                        continue
                
                print(f"✅ {page_jobs} offres")
                
                # Délai entre pages
                if page < num_pages - 1:
                    time.sleep(random.uniform(3, 5))
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                continue
    
    finally:
        if driver:
            driver.quit()
    
    return jobs


