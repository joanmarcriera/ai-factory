# Manual Testing Guide

## Installing the Tampermonkey Script

1. Install the Tampermonkey browser extension for your web browser.
2. Create a new script in Tampermonkey.
3. Copy the contents of the `src/overlay/content.js` file and paste it into the new Tampermonkey script.
4. Save the Tampermonkey script.

## Testing the Overlay on Google Maps

1. Navigate to Google Maps in your web browser.
2. The Tampermonkey script should automatically inject the overlay onto the Google Maps page.
3. Verify that the overlay is displayed correctly and that the "Export CSV" button is present.
4. Test the functionality of the overlay, including:
   - Extracting business data from the map
   - Displaying the business data in the overlay
   - Generating and downloading the CSV file
5. Ensure that the overlay does not interfere with the normal functionality of Google Maps.
