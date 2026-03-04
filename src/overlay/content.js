// ==UserScript==
// @name Local Business Visibility Platform
// @namespace https://www.google.com/maps/*
// @version 1.5
// @description Overlay for Google Maps to extract business data
// @match https://www.google.com/maps/*
// @grant none
// @updateURL https://raw.githubusercontent.com/joanmarcriera/ai-factory/refs/heads/main/src/overlay/content.js
// @downloadURL https://raw.githubusercontent.com/joanmarcriera/ai-factory/refs/heads/main/src/overlay/content.js
// ==/UserScript==

let overlayInjected = false;
let loadingText = null;

/**
 * Injects the self-contained UI overlay.
 */
function injectSelfContainedUI() {
  if (overlayInjected) return;
  overlayInjected = true;

  // Create loading text element
  loadingText = document.createElement('div');
  loadingText.textContent = 'Scanning Map...';
  loadingText.classList.add('overlay-loading');
  loadingText.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: rgba(255, 255, 255, 0.8);
    padding: 10px 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    z-index: 999999 !important;
  `;

  // Append loading text to the body
  document.body.appendChild(loadingText);

  // Create the overlay content
  const overlayContent = document.createElement('div');
  overlayContent.id = 'overlay-content';
  overlayContent.classList.add('overlay-panel');
  overlayContent.style.zIndex = '999999 !important';

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
      background-color: rgba(255, 255, 255, 0.8);
      padding: 20px;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
      backdrop-filter: blur(10px);
      max-width: 300px;
      max-height: 80vh;
      overflow-y: auto;
      z-index: 999999 !important;
    }
    .business-listing {
      border: 1px solid #ccc;
      padding: 10px;
      margin-bottom: 10px;
    }
  `;

  document.head.appendChild(styles);
  document.body.appendChild(overlayContent);
}

/**
 * Extracts relevant data from a business listing element.
 * @param {Element} element - The business listing element.
 * @returns {Object} - An object containing the extracted business data.
 */
function extractData(element) {
  const nameElement = element.querySelector('[aria-label^="Name:"]');
  const addressElement = element.querySelector('[aria-label^="Address:"]');
  const phoneElement = element.querySelector('[aria-label^="Phone:"]');
  const websiteElement = element.querySelector('[aria-label^="Website:"]');

  return {
    name: nameElement ? nameElement.textContent.trim() : 'N/A',
    address: addressElement ? addressElement.textContent.trim() : 'N/A',
    phone: phoneElement ? phoneElement.textContent.trim() : 'N/A',
    website: websiteElement ? websiteElement.textContent.trim() : 'N/A'
  };
}

/**
 * Calculates the lead score for a given business data object.
 * @param {Object} businessData - The business data object.
 * @returns {number} - The lead score.
 */
function calculateLeadScore(businessData) {
  let score = 0;
  
  // Add points if the website is 'N/A' or missing
  if (businessData.website === 'N/A' || !businessData.website) {
    score += 2;
  }
  
  // Add points if the phone is 'N/A' or missing
  if (businessData.phone === 'N/A' || !businessData.phone) {
    score += 2;
  }
  
  return score;
}

/**
 * Processes the extracted business data and updates the UI.
 */
function processBusinessData() {
  // Find all business listing elements using a more robust selector
  const robustBusinessElements = document.querySelectorAll('[role="article"]');
  
  // Extract data from each business listing
  const businessData = [];
  robustBusinessElements.forEach(element => {
    const data = extractData(element);
    // Calculate the lead score for the business data
    data.leadScore = calculateLeadScore(data);
    businessData.push(data);
  });
  
  // Remove the loading text
  if (loadingText) {
    loadingText.remove();
    loadingText = null;
  }

  // Display the business data in the overlay panel
  const businessListingsElement = document.getElementById('business-listings');
  businessListingsElement.innerHTML = '';

  businessData.forEach(data => {
    const businessElement = document.createElement('div');
    businessElement.classList.add('business-listing');

    const nameElement = document.createElement('h3');
    nameElement.textContent = data.name;
    businessElement.appendChild(nameElement);

    const addressElement = document.createElement('p');
    addressElement.textContent = data.address;
    businessElement.appendChild(addressElement);

    const phoneElement = document.createElement('p');
    phoneElement.textContent = `Phone: ${data.phone}`;
    businessElement.appendChild(phoneElement);

    const websiteElement = document.createElement('p');
    websiteElement.textContent = `Website: ${data.website}`;
    businessElement.appendChild(websiteElement);

    const leadScoreElement = document.createElement('p');
    leadScoreElement.textContent = `Lead Score: ${data.leadScore}`;
    businessElement.appendChild(leadScoreElement);

    businessListingsElement.appendChild(businessElement);
  });

  // Apply visual highlights
  applyVisualHighlights(robustBusinessElements, businessData);

  // Aggregate competitor stats
  aggregateCompetitorStats(businessData);
}

function checkForBusinessElements() {
  if (window.location.hostname.includes('google.com') && window.location.pathname.includes('/maps')) {
    const robustBusinessElements = document.querySelectorAll('[role="article"]');
    if (robustBusinessElements.length > 0) {
      injectSelfContainedUI();
      processBusinessData();
    }
  }
}

setInterval(checkForBusinessElements, 1000);

/**
 * Applies visual highlights to the Google Maps DOM elements.
 * @param {NodeListOf<Element>} businessElements - The business listing elements.
 * @param {Object[]} businessData - An array of business data objects.
 */
function applyVisualHighlights(businessElements, businessData) {
  businessElements.forEach((element, index) => {
    const data = businessData[index];
    if (data.leadScore >= 4) {
      element.style.border = '2px solid #ff6b6b';
      const highValueText = document.createElement('span');
      highValueText.textContent = '🔥 High Value Lead';
      highValueText.style.color = '#ff6b6b';
      highValueText.style.fontWeight = 'bold';
      highValueText.style.marginLeft = '5px';
      element.appendChild(highValueText);
    }
  });
}

/**
 * Aggregates competitor statistics from the business data.
 * @param {Object[]} businessData - An array of business data objects.
 */
function aggregateCompetitorStats(businessData) {
  let totalBusinesses = 0;
  let averageLeadScore = 0;
  let highValueLeads = 0;

  businessData.forEach(data => {
    totalBusinesses++;
    averageLeadScore += data.leadScore;

    if (data.leadScore >= 4) {
      highValueLeads++;
    }
  });

  averageLeadScore /= totalBusinesses;

  console.log(`Total Businesses: ${totalBusinesses}`);
  console.log(`Average Lead Score: ${averageLeadScore.toFixed(2)}`);
  console.log(`High Value Leads: ${highValueLeads}`);
}

/**
 * Generates a CSV file from the provided business data.
 * @param {Object[]} businessData - An array of business data objects.
 */
function generateCSV(businessData) {
  const headers = ['Business Name', 'Address', 'Phone', 'Website', 'Lead Score'];
  const rows = businessData.map(data => [
    data.name,
    data.address,
    data.phone || 'N/A',
    data.website || 'N/A',
    data.leadScore
  ]);

  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += headers.join(",") + "\n";
  rows.forEach(row => {
    csvContent += row.join(",") + "\n";
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', 'business_data.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Adds an "Export CSV" button to the overlay panel.
 * @param {Object[]} businessData - An array of business data objects.
 */
function addExportButton(businessData) {
  const exportButton = document.createElement('button');
  exportButton.textContent = 'Export CSV';
  exportButton.addEventListener('click', () => {
    generateCSV(businessData);
  });

  const overlayContent = document.getElementById('overlay-content');
  overlayContent.appendChild(exportButton);
}
