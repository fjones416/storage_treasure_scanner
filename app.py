from flask import Flask,request,jsonify,render_template
import psycopg2
import os
import storage_scanner_prod
from datetime import datetime,timedelta
app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']

@app.route('/twilio_add_to_text_complete',methods=['POST'])
def add_to_text_complete():
    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)
    # Get a cursor
    c = cnx.cursor()

  # Get POST Data
    auction_listing_url = str(request.json['auction_listing_url']).strip()
    yes_or_no_to_bid = 1
    max_bid_amount = str(request.json['max_bid_amount']).strip()

    todays_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    c.execute('INSERT INTO "storage_listing_text_complete" (auction_listing_url,yes_or_no_to_bid,max_bid_amount,date_completed) VALUES (%s,%s,%s,%s);',(auction_listing_url,yes_or_no_to_bid,max_bid_amount,todays_date,))
    cnx.commit()

    c.execute('DELETE FROM storage_listing_text_queue WHERE auction_listing_url = %s;',(auction_listing_url,))
    cnx.commit()

    cnx.close();

    return jsonify(msg=f"{auction_listing_url} added to complete and removed from queue")

@app.route('/twilio_delete_from_text_queue',methods=['POST'])
def delete_from_text_queue():
    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)
    # Get a cursor
    c = cnx.cursor()

    # Get POST Data
    auction_listing_url = str(request.json['auction_listing_url']).strip()

    auction_listing_delete = c.execute('DELETE FROM storage_listing_text_queue WHERE auction_listing_url = %s;',(auction_listing_url,))

    cnx.commit()

    cnx.close();

    return jsonify(msg=f"{auction_listing_url} deleted")

@app.route('/twilio_get_listing_info')
def get_auction_listing_info():

    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)
    # Get a cursor
    c = cnx.cursor()

    auction_listing_url = c.execute('SELECT auction_listing_url FROM storage_listing_text_queue')
    auction_listing_url = c.fetchone()

    listing_count_query = c.execute('SELECT count(*) from storage_listing_text_queue;')
    results = c.fetchone()
    listing_count = int(results[0] - 1)

    cnx.close()

    return jsonify(auction_listing_url=auction_listing_url,number_of_listings_remaining=listing_count)

@app.route('/run_auction_listing_scrape')
def run_auction_listing_scrape():
    storage_scanner_prod.auction_listing_scrape()
    return 'storage scrape complete'

@app.route('/get_text_queue_listings')
def get_text_queue_listings():

    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)
    # Get a cursor
    c = cnx.cursor()

    text_queue_listings = c.execute('SELECT * FROM storage_listing_text_queue')
    text_queue_listings = c.fetchall()
    text_queue_listings_list = list()

    for data in text_queue_listings:
        storage_complete_data = c.execute('SELECT total_views,total_bids,view_to_bid_ratio,high_value_kw_count,high_bid_when_scraped,countdown_timer_hours_remaining FROM storage_listing_data where auction_listing_url = %s ORDER BY "countdown_timer_hours_remaining" asc',(data[1].strip(),))
        storage_complete_data = c.fetchone()

        text_queue_listings_list.append({
          "auction_listing_url": data[1].strip(),
          "total_views": storage_complete_data[0],
          "total_bids": storage_complete_data[1],
          "bid_to_view_ratio": storage_complete_data[2],
          "high_value_kw_count": storage_complete_data[3],
          "current_high_bid": storage_complete_data[4],
          "date_added_to_queue":data[2],
          "countdown_timer_hours_remaining":storage_complete_data[5]
        })

    cnx.close();

    return render_template('queued_listings.html', title='See Listings In Text Queue',
                           auction_listing_data=text_queue_listings_list)

@app.route('/get_text_complete_listings')
def get_text_complete_listings():

    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)
    # Get a cursor
    c = cnx.cursor()

    text_complete_listings = c.execute('SELECT * FROM storage_listing_text_complete')
    text_complete_listings = c.fetchall()
    text_complete_listings_list = list()

    for data in text_complete_listings:
        storage_complete_data = c.execute('SELECT total_views,total_bids,view_to_bid_ratio,high_value_kw_count,high_bid_when_scraped,countdown_timer_hours_remaining FROM storage_listing_data where auction_listing_url = %s ORDER BY "countdown_timer_hours_remaining" asc',(data[1].strip(),))
        storage_complete_data = c.fetchone()

        text_complete_listings_list.append({
          "auction_listing_url": data[1].strip(),
          "total_views": storage_complete_data[0],
          "total_bids": storage_complete_data[1],
          "bid_to_view_ratio": storage_complete_data[2],
          "high_value_kw_count": storage_complete_data[3],
          "current_high_bid": storage_complete_data[4],
          "max_bid_amount":data[3],
          "date_completed": data[4],
          "countdown_timer_hours_remaining" :storage_complete_data[5]
        })

    cnx.close();

    return render_template('complete_listings.html', title='Auction Listings Ready To Bid On',
                           auction_listing_data=text_complete_listings_list)
if __name__ == "__main__":
  app.run()