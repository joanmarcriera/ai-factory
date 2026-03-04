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
 * Injects the self-contained UI overlay.
 */
function injectSelfContainedUI() {
  // ... (existing code) ...
}

/**
 * Extracts relevant data from a business listing element.
 * @param {Element} element - The business listing element.
 * @returns {Object} - An object containing the extracted business data.
 */
function extractData(element) {
  const nameElement = element;
  const name = nameElement ? nameElement.getAttribute('aria-label') || 'N/A' : 'N/A';

  const addressElement = element.querySelector('[aria-label^="Address:"]');
  const address = addressElement ? addressElement.textContent.trim() : 'N/A';

  const phoneElement = element;
  const phone = phoneElement ? extractPhoneNumber(phoneElement.textContent) : 'N/A';

  const websiteElement = element.querySelector('a[href*="://"]');
  const website = websiteElement ? websiteElement.href : 'N/A';

  return {
    name,
    address,
    phone,
    website
  };
}

/**
 * Extracts a phone number from the given text.
 * @param {string} text - The text to search for a phone number.
 * @returns {string} - The extracted phone number, or 'N/A' if not found.
 */
function extractPhoneNumber(text) {
  const phoneRegex = /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/;
  const match = text.match(phoneRegex);
  return match ? match[0] : 'N/A';
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
  
  // Add points if the name is 'N/A' or missing
  if (businessData.name === 'N/A' || !businessData.name) {
    score += 2;
  }
  
  return score;
}

// ... (existing code) ...
