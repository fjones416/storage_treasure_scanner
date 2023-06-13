# Scraping Storage Auction Listings from Storage Treasures

This is a web application designed to scrape Storage Treasures auction listings. It uses a PostgreSQL database for data storage and persistence, and provides a set of HTTP APIs to view the data on the frontend.

## Features

1. Connects to a PostgreSQL database to store and manage auction data.
2. Uses Selenium with a headless Chrome browser to scrape storage auction listings.
3. Extracts various attributes of each auction, such as the number of bids, number of views, highest bid, countdown timer, etc.
4. Applies filters to the scraped listings based on specified criteria like the high bid, countdown timer, and high-value keywords present in the auction description.
5. Inserts the scraped and filtered data into the database.
6. Updates the database to indicate if an auction has ended or been cancelled.
7. Adds eligible listings to a queue, which are later sent as SMS notifications via Twilio.

## Setup and Installation

### Requirements

- Python 3.6 or higher.
- Packages: selenium, pandas, psycopg2, twilio, datetime, re, and os.
- Chrome Driver corresponding to your installed Chrome version.
- A PostgreSQL database.
- Twilio account and a valid Twilio phone number for sending SMS notifications.
- Set the environment variables for the database URL, chrome driver path, chrome binary path, Twilio account SID, Twilio auth token, Twilio phone numbers (to and from).

### Installation

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/fjones416/storage_treasure_scanner/
   ```

2. Install the necessary Python dependencies:

   ```
   pip install selenium pandas psycopg2 twilio datetime re os
   ```

3. Run the app.py script for the front end:

   ```
   python app.py
   ```
4. Run the storage_scanner_prod.py as a cron job:

   ```
   python storage_scanner_prod.py
   ```

## API Endpoints

- `POST /twilio_add_to_text_complete` - Adds an auction listing URL to the "complete" list in the database.
- `POST /twilio_delete_from_text_queue` - Deletes an auction listing URL from the "queue" in the database.
- `GET /twilio_get_listing_info` - Retrieves a single auction listing URL and the total count of URLs in the queue from the database.
- `GET /run_auction_listing_scrape` - Initiates an auction listing scraping operation.
- `GET /get_text_queue_listings` - Retrieves all auction listings currently in the queue from the database.
- `GET /get_text_complete_listings` - Retrieves all completed auction listings from the database.

## Notes

- app.py is for the website front end.
- storage_scanner_prod.py is the script that I ran on Cron job every day to get freshly scraped data.
- The script expects certain DOM structures in the target webpage, and therefore, it may not work as expected if the webpage structure changes.
- Make sure to handle the database and Twilio credentials securely.
- The frequency of running the script depends on your use case and the update frequency of the auction website. Be aware that excessive scraping could potentially lead to being blocked by the website. Always respect the target website's terms of use and consider using delays between requests if necessary.
- This script uses Twilio Studio flow to handle the SMS notification logic, make sure the studio flow ID ('FW8e33b5971834730782809e736c34551f') is replaced by your actual Twilio studio flow ID.
- I deployed to Heroku when I had it live.

## License

[MIT](https://choosealicense.com/licenses/mit/)
