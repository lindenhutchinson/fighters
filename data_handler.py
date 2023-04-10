from cache_manager import cache
from scrapers import scrape_upcoming_events, scrape_fighter_data



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
    
    if events_by_id is None:
            events = get_events()
            events_by_id = {event['id']: event for event in events}
            cache.set("events_by_id", events_by_id, timeout=3600)

    return events_by_id.get(event_id)
    
def get_fighter_data(fighter_name):
    fighter_data = cache.get(fighter_name)
    if fighter_data is None:
        try:
            fighter_data = scrape_fighter_data(fighter_name)
            cache.set(fighter_name, fighter_data, timeout=3600)
        except Exception as e:
            print(f"Error scraping fighter data for {fighter_name}: {e}")
            fighter_data = {}
            
    return fighter_data
