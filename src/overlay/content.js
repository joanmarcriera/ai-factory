// This is a placeholder for the overlay content JavaScript
console.log('Overlay content loaded');

// Add new code to detect Google Maps business listings
window.addEventListener('load', function() {
  if (window.location.hostname.includes('google.com') && window.location.pathname.includes('/maps')) {
    // Find all business listing elements
    const businessElements = document.querySelectorAll('[data-local-business-id]');
    
    // Extract data from each business listing
    const businessData = [];
    businessElements.forEach(element => {
      const data = extractData(element);
      businessData.push(data);
    });
    
    // Display the business data in the overlay panel
    displayBusinessData(businessData);

    // Add the Export CSV button
    addExportButton(businessData);
  }
});

/**
 * Extracts data from a business listing element.
 * @param {Element} element - The business listing element.
 * @returns {Object} - An object containing the extracted data.
 */
function extractData(element) {
  return {
    name: element.querySelector('h2').textContent.trim(),
    phone: element.querySelector('span[data-item-id="authority-phone"]')?.textContent.trim() || 'N/A',
    website: element.querySelector('a[data-item-id="authority-website"]')?.href.trim() || 'N/A',
    rating: element.querySelector('span[data-rating]')?.getAttribute('data-rating') || 'N/A'
  };
}

/**
 * Displays the business data in the overlay panel.
 * @param {Object[]} businessData - An array of business data objects.
 */
function displayBusinessData(businessData) {
  const listingsContainer = document.getElementById('business-listings');
  listingsContainer.innerHTML = '';

  businessData.forEach(data => {
    const listItem = document.createElement('div');
    listItem.classList.add('business-listing');

    const nameElement = document.createElement('h3');
    nameElement.textContent = data.name;

    const phoneElement = document.createElement('p');
    phoneElement.textContent = `Phone: ${data.phone}`;

    const websiteElement = document.createElement('p');
    websiteElement.textContent = `Website: ${data.website}`;

    const ratingElement = document.createElement('p');
    ratingElement.textContent = `Rating: ${data.rating}`;

    listItem.appendChild(nameElement);
    listItem.appendChild(phoneElement);
    listItem.appendChild(websiteElement);
    listItem.appendChild(ratingElement);
    listingsContainer.appendChild(listItem);
  });

  // Inject the overlay panel into the Google Maps page
  document.body.appendChild(document.getElementById('overlay-content'));
}

/**
 * Adds an "Export CSV" button to the overlay panel.
 * @param {Object[]} businessData - An array of business data objects.
 */
function addExportButton(businessData) {
  const exportButton = document.createElement('button');
  exportButton.textContent = 'Export CSV';
  exportButton.classList.add('export-button');
  exportButton.addEventListener('click', () => {
    const csvData = generateCSV(businessData);
    downloadCSV(csvData, 'business_leads.csv');
  });

  const overlayHeader = document.querySelector('#overlay-content h2');
  overlayHeader.parentNode.insertBefore(exportButton, overlayHeader.nextSibling);
}

/**
 * Generates a CSV string from the business data.
 * @param {Object[]} businessData - An array of business data objects.
 * @returns {string} - The CSV string.
 */
function generateCSV(businessData) {
  const headers = ['Name', 'Phone', 'Website', 'Rating'];
  const rows = businessData.map(data => [data.name, data.phone, data.website, data.rating]);
  const csvData = [headers, ...rows].map(row => row.join(',')).join('\n');
  return csvData;
}

/**
 * Triggers a browser download for the CSV file.
 * @param {string} csvData - The CSV data.
 * @param {string} filename - The filename for the CSV file.
 */
function downloadCSV(csvData, filename) {
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
