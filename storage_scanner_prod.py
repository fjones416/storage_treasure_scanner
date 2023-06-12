#!/usr/bin/env python
# coding: utf-8

# ## Import Packages

# In[2]:

def auction_listing_scrape():

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from datetime import datetime,timedelta
    import pandas as pd
    import re
    import psycopg2
    import os
    from twilio.rest import Client

    # ## Connect to Database

    # In[9]:

    DATABASE_URL = os.environ['DATABASE_URL']

    # Connect to DB
    cnx = psycopg2.connect(DATABASE_URL)

    # Get a cursor
    c = cnx.cursor()

    # ## Chrome Driver Options

    # In[10]:

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # ## Scrape New Storage Treasure Auction Listings

    # In[11]:

    driver = webdriver.Chrome(options=chrome_options,executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    driver.get('https://www.storagetreasures.com/auctions?sort_column_index=0&type=zipcode&term=37066&radius=25&filter_types=1&filter_types=2&filter_types=3&sort_column=expire_date&sort_direction=asc')

    # Wait for auction listings to be visible. If not, throw exception.
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "auction-tile"))
        )
    except:
        'Auction Listings Not Visible'

    # Get list of upcoming auctions
    auction_tile_listings = driver.find_elements(By.CLASS_NAME,"auction-tile")
    upcoming_auction_links = set()

    # Loop through auction listings to collect auction listing url's

    for i,auction_listing in enumerate(auction_tile_listings):
        if i < 30:
            upcoming_auction_links.add(auction_listing.get_attribute('href'))

    def getElementInnerTextByClassName(class_name):
        return driver.find_element(By.CLASS_NAME,class_name).get_attribute('innerText')

    all_scraped_listings = list();

    for auction_listing_link in upcoming_auction_links:
        driver.get(auction_listing_link)
        iso_time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        auction_listing_data = {
        "auction_listing_url":auction_listing_link,
        "date_scraped": iso_time_string,
        "total_bids":int(re.sub('Bids on this unit: |,','',getElementInnerTextByClassName('total-bids'))),
        "total_views":int(re.sub('Visitors to this page: |,','',getElementInnerTextByClassName('total-views'))),
        "high_bid":int(re.sub('\$|,', '', getElementInnerTextByClassName('auction-tile-high-bid'))),
        "countdown_timer_hours":(int(driver.find_element(By.ID,'countdown-timer-days').find_element_by_class_name('countdown-lg').get_attribute('innerText')) * 24) + int(driver.find_element(By.ID,'countdown-timer-hours').find_element_by_class_name('countdown-lg').get_attribute('innerText')),
        "auction_contains_description":getElementInnerTextByClassName('auction-contains-info')
        }
        all_scraped_listings.append(auction_listing_data)

    print(f'Successfully Scraped {len(all_scraped_listings)} Auction Listings')
    driver.quit()

    # ## Create dataframe with Pandas. Filter by high_bid over 100. Extract High Value Keywords Into Set.

    # In[12]:

    df = pd.DataFrame(all_scraped_listings)

    df_mask = df['high_bid'] > 100
    filtered_df = df[df_mask]
    filtered_df = filtered_df.sort_values(by='high_bid',ascending=False)

    # Split auction descriptions into separate lists
    auction_descriptions = list(filtered_df['auction_contains_description'])
    high_value_kws_list = [x.split(',') for x in auction_descriptions]
    unique_high_value_kws = set();

    # Keywords we want to be filtered out for the high value keywords list
    negative_exact_kws = [
        "bed",
        "box spring",
        "headboard",
        "footboard",
        "head/footboard",
        "couch",
        "rug vcr",
        "clothes",
        "wall decoration",
        "pictures",
        "bucket",
        "chair",
        "personal effects",
        "stool",
        "jacket",
        "box",
        "rug",
        "sprayers",
        "shelf",
        "yamaha clavinova keyboard",
        "bed and box spring",
        "lamp",
        "arm chair",
        "table",
        "rugs",
        "water bottles",
        "wagon",
        "drink containers",
        "boxes",
        "totes",
        "shoes",
        "clothing",
        "chairs",
        "dresser",
        "bed frame",
        "cabinets & shelves; household items; personal effects unit must be picked up between business hrs",
        "9am-4pm",
        'trunk',
        "metal stand",
        "art",
        "paintings",
        "mon-fri and 9am-2pm sat.",
        "nightstand",
        "colletibles",
        "art painting",
        "plus boxes",
        "nightstands",
        "appliances; boxes",
        "car seat",
        "shelves",
        "kitchen chairs",
        "walker",
        "desk",
        "bean bag",
        "wall shelf",
        "tables",
        "night stands",
        "dresser chest and guitar box",
        "mattress",
        'boxes / bags / totes',
        'mattresses',
        'bedding / clothing',
        'coffee table',
        'barrel',
        'hutch',
        'love seat',
        'atvs arcade machine',
        'head board',
        'boxes. unit is full',
        'household furniture',
        'this is a manager special - it appears to contain rugs',
        'ironing board',
        'dressers',
        'rolling carts',
        'auto seats',
        'wooden barrel',
        'canopy',
        'show boxes',
        'furniture',
        'mattress and bedding',
        'hhgs',
        'head and foot board',
        'extension cord',
        'bedding',
        'chest of drawers',
        'folding tables',
        'sofa',
        'seat cushions',
        'dishes',
        'bookshelves',
        'bags',
        'and boxes',
        'office setup! desk',
        'table and chairs',
        'folding table',
        'end tables',
        'table lamps',
        'folding tables',
        'small tables',
        'end table',
        'side table',
        'patio side table',
        'foyer table',
        'accent table',
        "6' folding table",
        'changing table',
        'coffee tables',
        'end table coffee table',
        '11+ boxes',
        '4+ baskets',
        '9am-1pm.',
        'adult walkers',
        'air mattresses',
        'amazon stock',
        'and boxes',
        'and much more!',
        'and sat',
        'and totes',
        'artwork',
        'b',
        'bag',
        'bag/briefcase',
        'bags of clothes',
        'bags and totes',
        'bar stools',
        'bedding. tools',
        'basket',
        'baskets',
        'bed frames',
        'bed rails',
        'bedroom furniture',
        'bedside commode chairs',
        'betting',
        'bicycle/totes/shoe boxes/tv box/',
        'blues',
        'bolts of fabric',
        'bonnet dryer',
        'boxes.',
        'boxes and totes',
        'boxes and wall decorations',
        'boxes. totes. games. collectables',
        "box's",
        'boxsprings',
        'box springs (twin/full?)',
        'broom',
        'buckets',
        'buckets.',
        'cabinet',
        'cabinets',
        'car door',
        'carpet tiles',
        'car wheels & tires',
        'cases',
        'cd changer',
        'cd player',
        "cd's",
        "chairs.",
        'chairs and stools',
        "chest drawers",
        "christmas tree",
        "close",
        "clothes flat tv's",
        'clothing.',
        'clothing/shoes',
        "clothing & personal effects",
        'comforter',
        'computer accessories',
        'computer keyboards',
        'cooler',
        'coolers',
        'couches',
        'crates',
        'crutches',
        'crutches.',
        'cushions',
        'd',
        'decor',
        'decorations',
        'decorative items',
        'dolls',
        'doors',
        'drawer file cabinet',
        'drawer storage',
        'duffle bags',
        'duraflame outdoor',
        'dvd players',
        'dvds',
        'end table coffee table',
        'etc',
        'entertainment center',
        'ever start',
        'file boxes',
        'file cabinet',
        'file cabinets',
        'filing cabinet',
        'filing cabinets',
        'foam mattress',
        'folding chairs',
        'football',
        'furniture.',
        'futon',
        'games',
        'grandfather clock. furniture',
        'hamper',
        'head and foot board',
        'headboard and footboard',
        'holiday decor',
        'home window screens',
        'household',
        'kids rocker',
        'kids furniture',
        'kids stuff',
        'king mattress',
        'kitchen table',
        'kitchen table and chairs',
        'lamp mattress',
        'lamps',
        'lamp shades',
        'lawn chair',
        'loveseat',
        'magic cards',
        'mannequins',
        'mattresses & box springs',
        'mattresses (twin/full?)',
        'mattress topper',
        'microwave',
        'microwave.',
        'microwave oven',
        'mirror',
        'mirrors',
        'mon-fri',
        'mop bucket and toys',
        "movie dvd's",
        'new and used stock',
        'night stand',
        'office supplies',
        'okyno',
        'oriental furniture room divider',
        'ottoman',
        'outdoor chairs',
        'oversized footstool',
        'pack and play',
        'padded wooden chairs',
        'party décor',
        'patio chairs',
        'patio ottoman',
        'pillow'
        'pillows',
        'plants',
        'plastic bin',
        'plastic filing bins',
        'plastic shelves',
        'plates',
        'pre-lit palm tree',
        'puzzles',
        'railings',
        '(refrig',
        'rocking chair; upholstered chairs;',
        'rolling clothing rack',
        'rose bear',
        'rug boxes bags clothes',
        'school desk',
        'seasonal decor',
        'set of drums. boxes',
        'sectional',
        'shoe boxes clothes',
        'ship',
        'shelving and cabinets',
        'stand',
        'steamer trunk',
        'stilts',
        'stoller',
        'stool.',
        'stools',
        'suitcase. guitar case',
        'throw pillows',
        'tires and more!',
        'tire',
        'tires',
        'tires/wheels',
        'titans bucket',
        'toll boxes',
        'tons of board games',
        'tote',
        'totes. games collectables',
        'toys/games',
        'toys and collectibles',
        'trunks',
        't.v. center',
        "tv's couch",
        'twin bed',
        'tv stand',
        'twin mattress'
        'twin size bed headboard',
        'van bucket seats',
        'vase',
        'vice',
        'wall art',
        'wall clock',
        'washer?) household goods',
        'washing machineturkey fryer',
        'white headboard/footboard',
        'wheels',
        'wicker tote',
        'with slate',
        'wood',
        'wooden drawers',
        'xmas tree',
        'yard decor'
    ];

    # Loop through high value kws list and remove whitespace and transform strings to lowercase
    for li in high_value_kws_list:
        for v in li:
            v = v.strip();
            v = v.lower();
            v = re.sub('\d+\s', '', v)
            if (v not in negative_exact_kws):
                if ('misc' not in v and  'etc.' not in v):
                    if (v.count(' ') < 4):
                        if (v != ''):
                            unique_high_value_kws.add(v)

    print(f'{unique_high_value_kws} filtered from crawled listings')

    # ### Insert or Replace Unique High Value Keywords

    # In[19]:

    for kw in unique_high_value_kws:
        c.execute('INSERT INTO storage_listing_high_value_kws(high_value_kw) VALUES (%s) ON CONFLICT DO NOTHING',(kw,))

    high_value_kw_db_query = c.execute('SELECT high_value_kw FROM storage_listing_high_value_kws')
    high_value_kw_db_query_rows = c.fetchall()
    high_value_kws_list = list()

    for row in high_value_kw_db_query_rows:
            high_value_kws_list.append(row[0])

    print(f'{high_value_kws_list} added to db')

    # ### Insert Auction Listings Data

    # In[20]:

    for listing in all_scraped_listings:
        listing_description = listing['auction_contains_description'].strip()
        listing_description = listing['auction_contains_description'].lower()
        listing_description = re.sub(',\s', ',', listing_description)
        description_keyword_list = listing_description.split(',')
        high_value_kw_count = len([kw for kw in high_value_kws_list if kw in description_keyword_list])
        view_to_bid_ratio = round(listing['total_bids'] / listing['total_views'],2)

        c.execute("INSERT INTO storage_listing_data (auction_listing_url,date_scraped,total_bids,total_views,high_bid_when_scraped,countdown_timer_hours_remaining,auction_contains_description,high_value_kw_count,view_to_bid_ratio) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (listing['auction_listing_url'], listing['date_scraped'], listing['total_bids'],listing['total_views'],listing['high_bid'],listing['countdown_timer_hours'],listing['auction_contains_description'],high_value_kw_count,view_to_bid_ratio))

    print('scraped listing data inserted in storage_listing_data')

    # ## Filter & Open All Tabs In Selenium Browser For Viewing

    # ### Check the listings to see if the auctions are still available to bid on and not cancelled or ended. If there are cancelled or ended listings, update that in the db.

    # In[21]:

    auction_listings_to_view = c.execute('SELECT DISTINCT auction_listing_url FROM storage_listing_data where auction_has_ended = 0')
    auction_listings_to_view_rows = c.fetchall()
    auction_listings_to_view_set = set()

    for row in auction_listings_to_view_rows:
            auction_listings_to_view_set.add(row[0])

    if(len(auction_listings_to_view_set)):
        driver = webdriver.Chrome(options=chrome_options,executable_path=os.environ.get("CHROMEDRIVER_PATH"))

        for i,listing_url in enumerate(auction_listings_to_view_set):
            driver.get(listing_url)
            print(f"Crawling {listing_url} to check auction bidding title")
            auction_bidding_title = getElementInnerTextByClassName('auction-bidding-title')
            if 'This auction has ended.' in auction_bidding_title or 'This auction has been canceled' in auction_bidding_title or 'This auction has ended with no bids' in auction_bidding_title:
                c.execute('UPDATE storage_listing_data set auction_has_ended = 1 where auction_listing_url = %s',(listing_url,))
                c.execute('DELETE FROM "storage_listing_text_queue" where auction_listing_url = %s',(listing_url,))

        driver.quit()

        print('cancelled and ended auctions have been filtered, db has been updated')

    else:
        print('No Results Matching Criteria In DB')

    # ### Add Filtered Listings To Text Queue

    # In[1]:
    todays_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    auction_listings_to_add_to_queue = c.execute('SELECT auction_listing_url FROM storage_listing_data where auction_has_ended = 0 AND countdown_timer_hours_remaining < 32 AND high_bid_when_scraped < 60 AND view_to_bid_ratio < 0.09 AND high_value_kw_count > 0 ORDER BY high_value_kw_count DESC LIMIT 10')
    auction_listings_to_add_to_queue = c.fetchall()
    auction_listings_to_add_to_queue_set = set()

    for row in auction_listings_to_add_to_queue:
            auction_listings_to_add_to_queue_set.add(row[0])

    listings_added_count = 0

    for listing_url in auction_listings_to_add_to_queue_set:
        update_storage_listing_data_query = c.execute('UPDATE storage_listing_data SET added_to_queue = 1 WHERE auction_listing_url = %s ',(listing_url,))
        add_to_queue_query = c.execute('INSERT INTO "storage_listing_text_queue" (auction_listing_url,date_added_to_queue) VALUES (%s,%s) ON CONFLICT (auction_listing_url) DO NOTHING;',(listing_url,todays_date,))
        print(listing_url + ' added to queue')
        listings_added_count = listings_added_count + 1

    print(f'total listings added to text queue:{listings_added_count}')

    total_listings_in_queue_count = c.execute('SELECT COUNT(auction_listing_url) FROM storage_listing_text_queue;')
    total_listings_in_queue_count_row = c.fetchone()
    total_listings_in_queue = total_listings_in_queue_count_row[0]

    print(f'total listings in queue {total_listings_in_queue}')

    # close the communication with the database server by calling the close()
    if cnx is not None:
        cnx.commit()
        cnx.close()
        print('Database connection closed.')

    # set Twilio environment variables.
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    twilio_to_phone_number_list = str(os.environ['TWILIO_TO_PHONE_NUMBERS']).split(',')
    twilio_from_phone_number = os.environ['TWILIO_FROM_PHONE_NUMBER']

    def create_twilio_flow_execution(phone):
        execution = client.studio \
                    .flows('FW8e33b5971834730782809e736c34551f') \
                    .executions \
                    .create(to=phone, from_=twilio_from_phone_number, parameters={"new_listing_added_count":listings_added_count,"total_listings_in_queue_count":total_listings_in_queue})
        print (f'twilio execution id:{execution.sid} created')
        print (f'parameters sent to twilio execution: new_listing_added_count:{listings_added_count}, total_listings_in_queue_count:{total_listings_in_queue}')

    if (twilio_to_phone_number_list):
        for phone in twilio_to_phone_number_list:
            create_twilio_flow_execution(phone)