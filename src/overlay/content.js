// This is a placeholder for the overlay content JavaScript
console.log('Overlay content loaded');

// Add new code to detect Google Maps business listings
window.addEventListener('load', function() {
  if (window.location.hostname.includes('google.com') && window.location.pathname.includes('/maps')) {
    // Find all business listing elements
    const businessElements = document.querySelectorAll('[data-local-business-id]');
    
    // Extract data from each business listing
    businessElements.forEach(element => {
      const businessData = {
        name: element.querySelector('h2').textContent.trim(),
        phone: element.querySelector('span[data-item-id="authority-phone"]')?.textContent.trim() || 'N/A',
        website: element.querySelector('a[data-item-id="authority-website"]')?.href.trim() || 'N/A',
        rating: element.querySelector('span[data-rating]')?.getAttribute('data-rating') || 'N/A'
      };
      
      console.log(`Business data: ${JSON.stringify(businessData)}`);
    });
  }
});
