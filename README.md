# Aarau Lunch Menu Aggregator 🍽️

A lightweight, full-stack web application designed to aggregate daily lunch menus from local restaurants in Aarau, Switzerland. 

This project was built to simplify daily lunch planning. Instead of manually checking multiple websites and PDF documents, this application provides a centralized, mobile-responsive dashboard.

## 🏗️ Architecture & Tech Stack

This project follows a decoupled Microservice Architecture, separating data extraction from the user interface.

**Backend (API)**
* **Framework:** Python / FastAPI
* **Data Parsing:** `BeautifulSoup4` (HTML Scraping), `xml.etree.ElementTree` (XML Parsing), and      `pypdf` (In-Memory PDF Extraction)
* **Hosting:** Deployed as a web service on [Render](https://render.com/)
* **Features:** Strict CORS-Middleware integration, robust error handling, regex-based string sanitization.

**Frontend (Client)**
* **Core:** HTML5, CSS3, Vanilla JavaScript (Separation of Concerns applied)
* **Hosting:** [GitHub Pages](https://pages.github.com/)
* **Features:** Asynchronous API fetching (`fetch`), dynamic DOM manipulation, automated color-coding for dates.

## ✨ Key Features

* **Multi-Format Aggregation:** Seamlessly handles and unifies data from vastly different sources: HTML DOM traversal (Kantine Rampe, Coop), XML parsing via API (Lunchgate/Mojo), and dynamic PDF downloading/parsing (Chang Thai).
* **Progressive Web App (PWA):** Includes a `manifest.json` and adaptive icons. Users can add the application to their iOS or Android home screen for a native, full-screen app experience.
* **Smart Dark Mode:** Automatically detects the user's OS-level color scheme preference, supplemented by a manual, floating toggle button that persists the choice via `localStorage`.
* **Dynamic Date Handling:** Automatically extracts actual menu dates (or falls back to the current day) and groups them visually with a multi-day collapsing toggle.
* **Corporate Integration:** Specifically filters out internal pricing and highlights custom discount notifications for employees utilizing the corporate badge or environmental packaging.

## 🚀 API Endpoints

The FastAPI backend exposes the following endpoints, all returning standardized JSON payloads:

* `GET /api/rampe` - Returns the weekly menu for Kantine Rampe (scraped via HTML).
* `GET /api/mojo` - Returns today's and tomorrow's menus for Mojo Aarau (parsed via XML).
* `GET /api/coop` - Returns the daily menus from Coop Restaurant Telli (scraped via HTML tables).
* `GET /api/changthai` - Extracts the daily menu dynamically from a downloaded PDF using Regex.

## 💻 Local Development Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/Gau-dii/menu-scraper.git](https://github.com/Gau-dii/menu-scraper.git)

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt

3. Start the local Uvicorn server:
   ```bash
   uvicorn main:app --reload

4. Open index.html in your preferred web browser.
 