from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import io
from pypdf import PdfReader

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

@app.get("/api/coop")
def get_coop_menu():
    """
    Scrapes the daily menus from Coop Telli Restaurant's HTML website.
    Extracts dish categories, descriptions, and prices from the DOM tables.
    """
    url = "https://www.coop-restaurant.ch/de/restaurantfinder/finderdetailpage.2039.html"
    antwort = requests.get(url)
    menues_liste = []

    # Fallback date in case the DOM traversal fails
    heute_string = datetime.now().strftime("%d.%m.%Y")

    if antwort.status_code == 200:
        # Parse the HTML DOM
        soup = BeautifulSoup(antwort.text, "html.parser")

        # Target the specific tables generated for daily menus
        tables = soup.select("table.menues__table[data-restaurant-menues='day']")

        for table in tables:
            try:
                datum_element = table.select_one(".menues__table-caption")
                
                # Safely extract the date or use the fallback
                datum = datum_element.get_text(" ", strip=True) if datum_element else heute_string

                for row in table.select("tr.menues__row"):
                    cells = row.select("td")

                    # Skip header rows or malformed rows that don't have exactly 3 columns
                    if len(cells) != 3:
                        continue

                    # Extract dish name and price
                    gericht = cells[0].get_text(" ", strip=True)
                    preis = cells[2].get_text(" ", strip=True)

                    if gericht != "":
                        menues_liste.append({
                            "datum": datum,
                            "kategorie": "Tagesangebot",
                            "gericht": gericht,
                            "preis": f"CHF {preis}" if preis else ""
                        })
            except AttributeError:
                # Silently skip malformed DOM nodes
                continue

        return {"restaurant": "Coop Restaurant Aarau Telli", "status": "ok", "daten": menues_liste}

    # Fallback return when the HTTP request fails
    return {"restaurant": "Coop Restaurant Aarau Telli", "status": "fehler", "daten": []}

@app.get("/api/changthai")
def get_changthai_menu():
    """
    Scrapes the daily menu from Chang Thai's dynamically linked PDF.
    Extracts the date range, categories (Super, Normal, Vegi), and dish details.
    """
    try:
        # 1. Fetch the main HTML page to locate the current PDF link
        html_url = "https://www.changthaifood.ch/aarau"
        html_resp = requests.get(html_url)
        soup = BeautifulSoup(html_resp.text, 'html.parser')

        # Scan all links to find the PDF (fallback to known path if not found)
        pdf_link = "/assets/Uploads/ChangThaiRestaurant_Mittagsmenu.pdf"
        for a in soup.find_all('a', href=True):
            if 'Mittagsmenu.pdf' in a['href'] or 'Mittagsmenue.pdf' in a['href']:
                pdf_link = a['href']
                break

        # Ensure the URL is absolute
        if not pdf_link.startswith('http'):
            pdf_link = "https://www.changthaifood.ch" + pdf_link

        # 2. Download the PDF directly into RAM (BytesIO) without saving it to disk
        pdf_resp = requests.get(pdf_link)
        pdf_file = io.BytesIO(pdf_resp.content)
        
        # 3. Extract text from the PDF pages
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # 4. Parse the unstructured text using Regex and string matching
        # Extract the validity date range (e.g., "08.09 - 11.09.2026")
        date_match = re.search(r'(\d{2}\.\d{2}\s*-\s*\d{2}\.\d{2}\.\d{4})', text)
        datum = date_match.group(1).strip() if date_match else datetime.now().strftime("%d.%m.%Y")

        menues_liste = []
        categories = ["Menü Super", "Menü Normal", "Menü Vegi"]
        
        lines = text.split('\n')
        current_cat = None
        current_price = ""
        current_desc = []
        
        for line in lines:
            line = line.strip()
            if not line: 
                continue
            
            # Identify if the current line starts a new menu category
            matched_cat = next((cat for cat in categories if line.startswith(cat)), None)
                    
            if matched_cat:
                # Save the previously accumulated menu before starting a new one
                if current_cat:
                    menues_liste.append({
                        "datum": datum,
                        "kategorie": current_cat,
                        "gericht": " ".join(current_desc).strip(),
                        "preis": current_price
                    })
                
                current_cat = matched_cat
                current_desc = []
                
                # Extract the price (e.g., "CHF 22.-") from the header line
                price_match = re.search(r'(CHF\s*\d+\.-)', line)
                current_price = price_match.group(1) if price_match else ""
                
                # Strip the category name and price to isolate the dish name
                desc_part = re.sub(r'^' + matched_cat + r'\s*(CHF\s*\d+\.-)?', '', line).strip()
                if desc_part:
                    current_desc.append(desc_part)
            
            elif current_cat:
                # Stop reading descriptions when hitting footer terms
                if "Rabatt" in line or "Herkunftsfleisch" in line:
                    continue
                current_desc.append(line)

        # Append the final menu block after the loop concludes
        if current_cat:
            menues_liste.append({
                "datum": datum,
                "kategorie": current_cat,
                "gericht": " ".join(current_desc).strip(),
                "preis": current_price
            })

        return {"restaurant": "Chang Thai", "status": "ok", "daten": menues_liste}

    except Exception as e:
        # Return a graceful error structure if PDF parsing fails
        return {"restaurant": "Chang Thai", "status": "fehler", "daten": [], "error": str(e)}