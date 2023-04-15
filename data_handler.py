from cache_manager import cache
from scrapers import scrape_upcoming_events, scrape_fighter_data, scrape_odds_data, clean_name
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)
event_odds_futures = {}

def get_events():
    events = cache.get("events")
    if events is None:
        try:
            events = scrape_upcoming_events()
            cache.set("events", events, timeout=3600)  # set timeout to 1 hour
            # Create a dictionary to index the events on event id
            events_by_id = {event['id']: event for event in events}
            cache.set("events_by_id", events_by_id, timeout=3600)
            
        except Exception as e:
            print(f"Error scraping events: {e}")
            events = []
    return events

def get_event_by_id(event_id):
    events_by_id = cache.get("events_by_id")
    
    if not events_by_id:
        events = get_events()
        events_by_id = {event['id']: event for event in events}
        cache.set("events_by_id", events_by_id, timeout=3600)

    event = events_by_id.get(event_id)
           
    if not cache.has('event_odds'):
        cache.set('event_odds', {})
    
    event_odds = cache.get('event_odds')
       
    if not event_odds.get(event['id']):
        future = executor.submit(set_event_odds, event)
        event_odds_futures[event['id']] = future  # Store the Future object in the shared dictionary
    
    
    return event

def set_event_odds(event):
    print('setting odds for event', event['name'])
    odds = scrape_odds_data(event['name'], event['fighters'])
    if odds:
        print(event['fighters'])
        cache.set("event_odds", {event['id']: {name:odds[name] for name in event['fighters']}}, timeout=3600)   
        print('added odds for event', event['name'])
    else:
        print('no odds retrieved for event', event['id'])


def get_fighter_data(fighter_name, event_id):
    clean_fname = clean_name(fighter_name)
    fighter_data = cache.get(clean_fname)
    fighter_odds = {}
    if not fighter_data:
        try:
            fighter_data = scrape_fighter_data(clean_fname)
            cache.set(clean_fname, fighter_data, timeout=3600)
        except Exception as e:
            print(f"Error scraping fighter data for {fighter_name}: {e}")
            fighter_data = {}
    

    future = event_odds_futures.get(event_id)
    if future and not future.done():
        future.result()  # Block and wait for the set_event_odds to finish
        del event_odds_futures[event_id]  # Remove the Future object from the shared dictionary
        
    cached_odds = cache.get("event_odds")
    odds = cached_odds.get(event_id)
    if odds:
        fighter_odds = odds.get(clean_fname)
    else: fighter_odds = None
    return fighter_data, fighter_odds
