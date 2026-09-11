/**
 * Standardizes and shortens date strings into a compact format (e.g., "Do. 10.09.")
 * Handles both ISO-like numeric strings and localized text strings.
 * 
 * @param {string} dateStr - The raw date string from the API
 * @returns {string} The formatted short date string
 */
function formatShortDate(dateStr) {
    // Array mapping JavaScript day indices (0=Sunday) to localized short weekday labels
    const weekdays = ['So.', 'Mo.', 'Di.', 'Mi.', 'Do.', 'Fr.', 'Sa.'];

    // Case 1: ISO-like numeric date format from API (e.g., "10.09.2026")
    if (/^\d{2}\.\d{2}\.\d{4}$/.test(dateStr)) {
        const parts = dateStr.split('.');                
        // Month indices in JavaScript Date objects are 0-indexed (subtract 1)
        const dateObj = new Date(parts[2], parts[1] - 1, parts[0]);
        const dayName = weekdays[dateObj.getDay()]; 
        return `${dayName} ${parts[0]}.${parts[1]}.`; 
    }

    // Case 2: Localized text format (e.g., "Donnerstag, 10. September")
    const replacements = {               
        // Convert German month names to numeric representations
        ' Januar': '01.', ' Februar': '02.', ' März': '03.', ' April': '04.',
        ' Mai': '05.', ' Juni': '06.', ' Juli': '07.', ' August': '08.',
        ' September': '09.', ' Oktober': '10.', ' November': '11.', ' Dezember': '12.',                
        // Abbreviate weekday names including trailing commas
        'Montag, ': 'Mo. ', 'Dienstag, ': 'Di. ', 'Mittwoch, ': 'Mi. ', 
        'Donnerstag, ': 'Do. ', 'Freitag, ': 'Fr. '
    };
    
    for (const [longText, shortText] of Object.entries(replacements)) {
        dateStr = dateStr.replace(longText, shortText);
    }
    
    return dateStr;
}

/**
 * Renders dynamic menu items into the designated DOM container.
 * Enforces a "today-first" focus by collapsing future days behind a toggle action.
 * 
 * @param {Object} data - The JSON payload from the backend API
 * @param {string} containerId - The DOM ID where menu items will be injected
 * @param {string} buttonId - The DOM ID for the expansion toggle button
 */
function renderMenus(data, containerId, buttonId) {
    const container = document.getElementById(containerId);
    const button = document.getElementById(buttonId);
    container.innerHTML = ''; 
    
    // Extract unique dates to determine grouping and visibility logic
    const uniqueDates = [...new Set(data.daten.map(item => item.datum))];
    if (uniqueDates.length === 0) return;
    
    // Designate the earliest available date as the primary current focus
    const firstDate = uniqueDates[0];
    
    data.daten.forEach(menu => {
        const item = document.createElement('div');
        item.className = 'menu-item';
        
        // Collapse menu entries that do not match the current day's focus
        if (menu.datum !== firstDate) {
            item.classList.add('hidden-menu');
            item.style.display = 'none';
        }
        
        // Assign a specific color class index (0-4) based on the date's position
        const dateIndex = uniqueDates.indexOf(menu.datum) % 5;
        const dateClass = `date-color-${dateIndex}`;
        const preisHTML = menu.preis ? `<div class="menu-price">${menu.preis}</div>` : '';
        
        const shortDate = formatShortDate(menu.datum);
        
        // Inject sanitized markup into the DOM element
        item.innerHTML = `
            <div class="menu-header">
                <div class="badge-group">
                    <span class="menu-date ${dateClass}">${shortDate}</span>
                    <span class="menu-category">${menu.kategorie}</span>
                </div>
                ${preisHTML}
            </div>
            <div class="menu-dish">${menu.gericht}</div>
        `;
        container.appendChild(item);
    });

    // Bind toggle behavior to the expansion button if multiple dates exist
    if (uniqueDates.length > 1) {
        button.style.display = 'block';
        button.onclick = function() {
            const hiddenItems = container.querySelectorAll('.hidden-menu');
            const isHidden = hiddenItems[0].style.display === 'none';
            
            hiddenItems.forEach(el => el.style.display = isHidden ? 'block' : 'none');
            button.innerText = isHidden ? 'Weniger anzeigen' : 'Mehr anzeigen';
        };
    }
}

// Asynchronously fetch and render payloads from the cloud-hosted backend endpoints
fetch('https://menu-scraper-18yf.onrender.com/api/rampe')
    .then(response => response.json())
    .then(data => renderMenus(data, 'rampe-liste', 'rampe-btn'));

fetch('https://menu-scraper-18yf.onrender.com/api/mojo')
    .then(response => response.json())
    .then(data => renderMenus(data, 'mojo-liste', 'mojo-btn'));

fetch('https://menu-scraper-18yf.onrender.com/api/coop')
    .then(response => response.json())
    .then(data => renderMenus(data, 'coop-liste', 'coop-btn'));    

fetch('https://menu-scraper-18yf.onrender.com/api/changthai')
    .then(response => response.json())
    .then(data => renderMenus(data, 'changthai-liste', 'changthai-btn'));


/**
 * Theme Toggle Logic (Light/Dark Mode)
 * Persists user choice in browser's localStorage
 */
const themeToggleBtn = document.getElementById('theme-toggle');
const bodyElement = document.body;

// 1. Check local storage for saved preference, fallback to OS system preference
const savedTheme = localStorage.getItem('app-theme');
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    bodyElement.classList.add('dark-theme');
    updateButtonUI(true);
}

// 2. Toggle theme on button click
themeToggleBtn.addEventListener('click', () => {
    const isNowDark = bodyElement.classList.toggle('dark-theme');
    
    // Save the new preference so it survives page reloads
    localStorage.setItem('app-theme', isNowDark ? 'dark' : 'light');
    updateButtonUI(isNowDark);
});

// 3. Helper function to swap button icon and text
function updateButtonUI(isDark) {
    if (isDark) {
        themeToggleBtn.innerHTML = '<span>☀️</span> Light Mode';
    } else {
        themeToggleBtn.innerHTML = '<span>🌙</span> Dark Mode';
    }
}