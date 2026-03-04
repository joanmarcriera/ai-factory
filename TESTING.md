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

## Verifying Visual Highlights for High Value Leads

1. Observe the business listings in the overlay.
2. Identify any listings that have a '🔥 High Value Lead' label.
3. Verify that the corresponding business element on the Google Maps page has a red border, indicating it is a high value lead.

## Verifying Lead Scores in the CSV Export

1. Generate the CSV export by clicking the "Export CSV" button.
2. Open the downloaded CSV file.
3. Verify that the "Lead Score" column contains the correct lead score values for each business listing. A higher lead score indicates a higher value lead.
