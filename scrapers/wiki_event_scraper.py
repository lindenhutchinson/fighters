from .utils import get_soup, clean_string, json_pprint, get_short_uuid, clean_name

MAIN_URL = "https://en.wikipedia.org"

def get_event_fighters(event_url):
    soup = get_soup(event_url)
    if not soup.find(id="Fight_card") or soup.find(id="Results"):
        print("No fight card found for fight")
        return False

    event_data = {"main": [], "prelim": []}
    fighters = []
    on_main_card = True
    table = soup.find("table", class_="toccolours")
    rows = table.find_all("tr")
    for row in rows:
        headers = row.find_all("th")
        if headers and len(headers) == 1:
            if "Main" in headers[0].get_text():
                on_main_card = True
            elif "Preliminary" in headers[0].get_text():
                on_main_card = False

        cells = row.find_all("td")
        if len(cells) == 8:
            weight_class = clean_string(cells[0].get_text())
            fighter_1 = clean_string(cells[1].get_text())
            fighter_2 = clean_string(cells[3].get_text())
            fighters.extend((clean_name(fighter_1), clean_name(fighter_2)))

            event_data["main" if on_main_card else "prelim"].append(
                {
                    "weight_class": weight_class,
                    "fighter_1": fighter_1,
                    "fighter_2": fighter_2,
                }
            )
            
        event_data['fighters'] = fighters

    return event_data


def scrape_upcoming_events(num_events=3):
    event_url = MAIN_URL + "/wiki/List_of_UFC_events"
    soup = get_soup(event_url)

    event_table = soup.find("table", id="Scheduled_events")
    event_rows = event_table.find_all("tr")
    events = []

    # reverse the order of the rows to get the most recent events first
    for row in event_rows[::-1]:
        cells = row.find_all("td")
        if len(cells):

            event_url = MAIN_URL + cells[0].find("a").attrs["href"]
            name = clean_string(cells[0].get_text())
            date = clean_string(cells[1].get_text())
            event = {
                "name": name,
                "date": date,
                "id": get_short_uuid()
            }
            fighters = get_event_fighters(event_url)

            if fighters:
                event.update(**fighters)

            if len(events) == num_events:
                break

            events.append(event)

    return events

if __name__ == "__main__":
    json_pprint(scrape_upcoming_events())
