# Aarau Lunch Menu Aggregator 🍽️

A lightweight, full-stack web application designed to aggregate daily lunch menus from local restaurants in Aarau, Switzerland. 

This project was built to simplify daily lunch planning. Instead of manually checking multiple websites and PDF documents, this application provides a centralized, mobile-responsive dashboard.

## 🏗️ Architecture & Tech Stack

This project follows a decoupled Microservice Architecture, separating data extraction from the user interface.

**Backend (API)**
* **Framework:** Python / FastAPI
* **Data Parsing:** `BeautifulSoup4` (HTML Scraping) & `xml.etree.ElementTree` (XML Parsing)
* **Hosting:** Deployed as a web service on [Render](https://render.com/)
* **Features:** CORS-Middleware integration, error handling, string sanitization (Regex)

**Frontend (Client)**
* **Core:** HTML5, CSS3, Vanilla JavaScript
* **Hosting:** [GitHub Pages](https://pages.github.com/)
* **Features:** Asynchronous API fetching (`fetch`), dynamic DOM manipulation, automated color-coding based on unique dates, responsive layout.

## ✨ Key Features

* **Multi-Format Aggregation:** Seamlessly handles and unifies data from different sources (HTML DOM traversal for Kantine Rampe, XML parsing for Lunchgate/Mojo).
* **Dynamic Date Handling:** Automatically extracts actual menu dates (or falls back to the current day) and groups them visually with dynamic color mapping.
* **Corporate Integration:** Specifically filters out internal pricing and highlights a custom discount notification for employees utilizing the corporate badge.
* **Cross-Origin Resource Sharing:** Fully configured CORS policy allowing the static frontend to independently query the cloud-hosted API.

## 🚀 API Endpoints

The FastAPI backend exposes the following endpoints returning standardized JSON payloads:

* `GET /api/rampe` - Returns the weekly menu for Kantine Rampe (scraped via HTML).
* `GET /api/mojo` - Returns today's and tomorrow's menus for Mojo Aarau (parsed via XML).

## 💻 Local Development Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/Gau-dii/menu-scraper.git](https://github.com/Gau-dii/menu-scraper.git)