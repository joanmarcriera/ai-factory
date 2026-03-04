// ==UserScript==
// @name Local Business Visibility Platform
// @namespace https://www.google.com/maps/*
// @version 1.7
// @description Overlay for Google Maps to extract business data
// @match https://www.google.com/maps/*
// @grant none
// @updateURL https://raw.githubusercontent.com/joanmarcriera/ai-factory/refs/heads/main/src/overlay/content.js
// @downloadURL https://raw.githubusercontent.com/joanmarcriera/ai-factory/refs/heads/main/src/overlay/content.js
// ==/UserScript==

let overlayInjected = false;
let loadingText = null;

/**
 * Injects the self-contained UI overlay into the page.
 */
function injectSelfContainedUI() {
  if (overlayInjected) return;
  overlayInjected = true;

  // Create loading text element
  loadingText = document.createElement('div');
  loadingText.textContent = 'Scanning Map for Business Listings...';
  loadingText.classList.add('overlay-loading');
  loadingText.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: rgba(255, 255, 255, 0.9);
    padding: 15px 30px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    z-index: 999999 !important;
    font-family: sans-serif;
    font-weight: bold;
    color: #333;
  `;
  document.body.appendChild(loadingText);

  const overlayContent = document.createElement('div');
  overlayContent.id = 'overlay-content';
  overlayContent.classList.add('overlay-panel');

  const title = document.createElement('h1');
  title.textContent = 'Business Listings';
  overlayContent.appendChild(title);

  const businessListings = document.createElement('div');
  businessListings.id = 'business-listings';
  overlayContent.appendChild(businessListings);

  const styles = document.createElement('style');
  styles.textContent = `
    .overlay-panel {
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: rgba(255, 255, 255, 0.85);
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      backdrop-filter: blur(12px);
      max-width: 350px;
      max-height: 85vh;
      overflow-y: auto;
      z-index: 999999 !important;
      font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .business-listing {
      background: rgba(255, 255, 255, 0.5);
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 15px;
      border: 1px solid rgba(0, 0, 0, 0.05);
      transition: transform 0.2s;
    }
    .business-listing:hover {
      transform: translateY(-2px);
      background: rgba(255, 255, 255, 0.8);
    }
    .business-listing h3 { margin: 0 0 8px 0; font-size: 16px; color: #1a73e8; }
    .business-listing p { margin: 4px 0; font-size: 13px; color: #555; }
    .export-button {
      width: 100%;
      padding: 10px;
      background: #1a73e8;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
      margin-top: 10px;
    }
  `;

  document.head.appendChild(styles);
  document.body.appendChild(overlayContent);
}

/**
 * Extracts a phone number using regex.
 */
function extractPhoneNumber(text) {
  const phoneRegex = /(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4,5})/;
  const match = text.match(phoneRegex);
  return match ? match[0] : 'N/A';
}

/**
 * Extracts relevant data from a business listing element.
 */
function extractData(element) {
  // Use the container's aria-label for the name (most robust in Maps)
  const name = element.getAttribute('aria-label') || 'N/A';

  // Scrape address from common Map patterns
  const addressElement = element.querySelector('[aria-label*="Address"], .W4P4ne');
  const address = addressElement ? addressElement.textContent.trim() : 'N/A';

  // Scrape website by looking for external outbound links
  const websiteElement = element.querySelector('a[href*="://"]:not([href*="google.com"])');
  const website = websiteElement ? websiteElement.href : 'N/A';

  // Extract phone number via regex from the entire text blob
  const phone = extractPhoneNumber(element.textContent);

  return { name, address, phone, website };
}

/**
 * Calculates the lead score based on completeness.
 */
function calculateLeadScore(businessData) {
  if (businessData.name === 'N/A') return 0; // Filter out non-businesses
  let score = 0;
  if (businessData.website === 'N/A') score += 2;
  if (businessData.phone === 'N/A') score += 2;
  return score;
}

/**
 * Processes the listings and updates the UI.
 */
function processBusinessData() {
  const robustBusinessElements = document.querySelectorAll('[role="article"]');
  if (robustBusinessElements.length === 0) return;

  const businessData = [];
  robustBusinessElements.forEach(element => {
    const data = extractData(element);
    data.leadScore = calculateLeadScore(data);
    businessData.push(data);
  });

  if (loadingText) {
    loadingText.remove();
    loadingText = null;
  }

  const listingsContainer = document.getElementById('business-listings');
  if (!listingsContainer) return;
  listingsContainer.innerHTML = '';

  businessData.forEach(data => {
    const item = document.createElement('div');
    item.classList.add('business-listing');
    item.innerHTML = `
      <h3>${data.name}</h3>
      <p><b>Address:</b> ${data.address}</p>
      <p><b>Phone:</b> ${data.phone}</p>
      <p><b>Website:</b> ${data.website}</p>
      <p><b>Lead Score:</b> ${data.leadScore}</p>
    `;
    listingsContainer.appendChild(item);
  });

  addExportButton(businessData);
  applyVisualHighlights(robustBusinessElements, businessData);
}

/**
 * Adds marker class to elements to prevent infinite loops.
 */
function applyVisualHighlights(elements, data) {
  elements.forEach((el, i) => {
    if (el.classList.contains('ai-processed')) return;
    el.classList.add('ai-processed');

    if (data[i].leadScore >= 2) {
      el.style.border = '2px solid #ff6b6b';
      el.style.position = 'relative';
      const badge = document.createElement('div');
      badge.textContent = '🔥 High Value Lead';
      badge.style.cssText = 'position: absolute; bottom: 5px; right: 5px; background: #ff6b6b; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 10px; z-index: 100;';
      el.appendChild(badge);
    }
  });
}

function addExportButton(data) {
  const panel = document.getElementById('overlay-content');
  if (!panel || panel.querySelector('.export-button')) return;

  const btn = document.createElement('button');
  btn.className = 'export-button';
  btn.textContent = 'Export Qualifed Leads (CSV)';
  btn.onclick = () => {
    const csv = "Name,Address,Phone,Website,Score\n" + data.map(d => `"${d.name}","${d.address}","${d.phone}","${d.website}",${d.leadScore}`).join("\n");
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'leads.csv';
    a.click();
  };
  panel.appendChild(btn);
}

function init() {
  if (!window.location.href.includes('/maps')) return;
  setInterval(() => {
    const list = document.querySelectorAll('[role="article"]');
    if (list.length > 0) {
      injectSelfContainedUI();
      processBusinessData();
    }
  }, 2000);
}

init();
