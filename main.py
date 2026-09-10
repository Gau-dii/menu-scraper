from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# Initialize FastAPI application instance
app = FastAPI(title="Aarau Menü API")

# Configure CORS to allow cross-origin requests from the frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rampe")
def get_rampe_menu():
    """
    Scrapes the weekly menu from Kantine Rampe's HTML website.
    Extracts dish categories, descriptions, and external prices.
    """
    url = "https://rampe-aarau.ch/"
    antwort = requests.get(url)
    menues_liste = []
    
    # Fallback date in case the DOM traversal fails
    heute_string = datetime.now().strftime("%d.%m.%Y")
    
    if antwort.status_code == 200:
        # Parse the HTML DOM
        soup = BeautifulSoup(antwort.text, 'html.parser')
        
        # Target the specific CSS class generated for menu items
        alle_menues = soup.find_all('div', class_="rmp_daily-menu")
        
        for menu in alle_menues:
            try:
                kategorie = menu.find('h2', class_="bricks-type-lead").text.strip()
                gericht_name = menu.find('div', class_="rmp_daily-menu__text").text.strip()
                
                # Extract pricing nodes and filter for external prices only
                preise = menu.find_all('div', class_="rmp_daily-menu__price")
                externe_preise = []
                for p in preise:
                    text = p.text.strip()
                    if "Extern" in text:
                        # Clean up the string to expose only the raw currency value
                        externe_preise.append(text.replace("Extern ", ""))
                
                preis_str = " | ".join(externe_preise)
                
                # Traverse the DOM backward to find the closest preceding weekday header
                datum_node = menu.find_previous(string=re.compile(r'(Montag|Dienstag|Mittwoch|Donnerstag|Freitag)', re.IGNORECASE))
                datum_str = datum_node.strip() if datum_node else heute_string
                
                if gericht_name != "":
                    menues_liste.append({
                        "datum": datum_str,
                        "kategorie": kategorie,
                        "gericht": gericht_name,
                        "preis": preis_str
                    })
            except AttributeError:
                # Silently skip malformed DOM nodes that lack expected tags
                continue
                
        return {"restaurant": "Kantine Rampe", "status": "ok", "daten": menues_liste}
    
    return {"restaurant": "Kantine Rampe", "status": "fehler", "daten": []}

@app.get("/api/mojo")
def get_mojo_menu():
    """
    Fetches today's and tomorrow's menus from the Lunchgate XML API.
    Uses HTTP Basic Auth for API access.
    """
    url = "https://api2.lunchgate.ch/restaurant/menu"
    menues_liste = []
    api_status = "ok" 
    
    # Iterate through day=0 (today) and day=1 (tomorrow)
    for day in [0, 1]:
        parameter = {"restaurant_id": 15901, "day": day}
        antwort = requests.get(url, params=parameter, auth=HTTPBasicAuth('api.demo@lunchgate.ch', 'demo'))
        
        if antwort.status_code == 200:
            # Parse the XML response tree
            xml_baum = ET.fromstring(antwort.text)
            
            # Extract the date node specific to the current iteration
            date_element = xml_baum.find('.//date')
            datum = date_element.text if date_element is not None else datetime.now().strftime("%d.%m.%Y")
            
            menu_block = xml_baum.find('.//menu')
            
            if menu_block is not None:
                for gericht in menu_block:
                    titel_element = gericht.find('title')
                    preis_element = gericht.find('price')
                    beilage_element = gericht.find('line2')
                    
                    # Safely handle potentially missing XML tags
                    titel = titel_element.text if titel_element is not None else ""
                    preis = preis_element.text if preis_element is not None else ""
                    beilage = " " + beilage_element.text if beilage_element is not None and beilage_element.text is not None else ""
                    
                    voller_name = (titel + beilage).strip()
                    
                    if voller_name != "":
                        menues_liste.append({
                            "datum": datum, 
                            "kategorie": "Tagesmenü", 
                            "gericht": voller_name,
                            "preis": "CHF " + preis if preis else "" 
                        })
        else:
            # Flag partial failures if one of the days returns a non-200 status
            api_status = "fehler"
            
    return {"restaurant": "Mojo Aarau", "status": api_status, "daten": menues_liste}