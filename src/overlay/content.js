// ==UserScript==
// @name Local Business Visibility Platform
// @namespace https://www.google.com/maps/*
// @version 1.2
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

  // Rest of the injectSelfContainedUI function remains the same
}

/**
 * Extracts relevant data from a business listing element.
 * @param {Element} element - The business listing element.
 * @returns {Object} - An object containing the extracted business data.
 */
function extractData(element) {
  // Rest of the extractData function remains the same
}

/**
 * Processes the extracted business data and updates the UI.
 * @param {Object[]} businessData - An array of extracted business data.
 */
function processBusinessData(businessData) {
  // Remove the loading text
  if (loadingText) {
    loadingText.remove();
    loadingText = null;
  }

  // Rest of the processBusinessData function remains the same
}

// Rest of the code remains the same
