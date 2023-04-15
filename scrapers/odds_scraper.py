from .utils import get_soup, names_are_similar, clean_name

URL = 'https://www.bestfightodds.com'

def find_event(event_name):
    search_url = URL+'/search'
    clean_event_name = event_name.lstrip('UFC ESPN').lstrip('UFC Fight NIght')
    soup = get_soup(search_url, params={"query":clean_event_name})
    div_headers = soup.find_all('div', class_='content-header')
    event_header = None
    for header in div_headers:
        if 'Events' in header.get_text():
            event_header = header
            break
        
    if not event_header:
        print("Couldn't get event from search")
        return None
    
    event_table = event_header.find_next_sibling('table')
    for row in event_table.find_all('tr'):
        cells = row.find_all('td')
        if names_are_similar(cells[1].get_text(), clean_event_name, 0.7):
            event = cells[1].find('a')
            event_url = event.attrs['href']
            return URL+event_url
    
    print("Couldn't get event from search")
    return None


def find_fighter(name, fighters):
    for fighter in fighters:
        if names_are_similar(name, fighter):
            return fighter
        
    return None

def scrape_odds_data(event_name, fighters):
    event_url = find_event(event_name)
    if not event_url:
        return None
    
    soup = get_soup(event_url)
    
    # there is a hidden table first, we want to grab the second one
    tables = soup.find_all(class_="odds-table")
    odds_table = tables[1]
    thead = odds_table.find('thead')
    header_th_list = thead.find_all('th')
    headers = []
    # skip the first header as that is the fighter name column
    for th in header_th_list[1:]:
        if a:= th.find('a'):
            headers.append(a.get_text())
        else:
            headers.append(None)
    
    tbody = odds_table.find('tbody')  
    fighters_odds = {}
    bad_fighter_ctr = 0
    rows = tbody.find_all('tr', class_=lambda c: not 'pr' in c if c else True)
    for row in rows:  
        row_fighter = row.find('th').get_text()
        if row_fighter not in fighters:
            fighter = find_fighter(row_fighter, fighters)
        else:
            fighter = row_fighter
            
        if fighter:
            fighter_name = clean_name(fighter)
            cells = row.find_all('td')
            fighters_odds.update({fighter_name:[]})
            for i, cell in enumerate(cells):
                if i < len(headers) and headers[i]:
                    odds = cell.get_text()
                    if odds:
                        odds = odds.replace('▲', '').replace('▼', '')

                        fighters_odds[fighter_name].append({'odds':odds,'company':headers[i]})
        else:
            bad_fighter_ctr+=1
            
    # couldnt match more than half the fighters, we're probably looking at the wrong event  
    if bad_fighter_ctr > (len(fighters) // 2):
        print(bad_fighter_ctr)
        print('Too many mismatches fighters, no odds')
        return None     
    return fighters_odds

if __name__ == "__main__":
    event = 'UFC on ESPN: Holloway vs. Allen'
    fighters = [
        'Max Holloway',
        'Arnold Allen',
        'Dustin Jacoby',
        'Tanner Boser'
    ]
    odds = scrape_odds_data(event, fighters)