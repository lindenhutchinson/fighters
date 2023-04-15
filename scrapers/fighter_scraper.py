from bs4 import BeautifulSoup
import re
import json
from .utils import clean_name, get_soup, clean_string, names_are_similar

import unidecode
SEARCH_URL = "http://ufcstats.com/statistics/fighters/search"



def get_fighter_detail(soup: BeautifulSoup, header_name: str):
    """
    Extract a fighter detail from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the fighter's page.
        header_name (str): The name of the detail to extract (e.g. "height:", "DOB:", etc.).

    Returns:
        str: The value of the requested fighter detail.
    """
    pattern = re.compile(header_name, re.IGNORECASE)
    header = soup.find("i", string=pattern)
    detail = re.sub(pattern, "", header.parent.get_text())
    return clean_string(detail)


def get_fighter_stats(soup: BeautifulSoup):
    """
    Extract basic stats for a fighter from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the fighter's page.

    Returns:
        dict: A dictionary containing the fighter's name, height, date of birth, weight, reach, record, and a list of recent fights.
    """

    record = clean_string(
        soup.find("span", class_="b-content__title-record")
        .get_text()
        .replace("Record:", "")
    )
    name = clean_string(
        soup.find("span", class_="b-content__title-highlight").get_text()
    )
    height = get_fighter_detail(soup, "height:")
    dob = get_fighter_detail(soup, "DOB:")
    weight = get_fighter_detail(soup, "weight:")
    reach = get_fighter_detail(soup, "reach:")

    return {
        "name": name,
        "height": height,
        "dob": dob,
        "weight": weight,
        "reach": reach,
        "record": record,
        "fights": [],
    }


def get_fight_stats(soup: BeautifulSoup, num_fights: int):
    """
    Extract details for a fighter's recent fights from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the fighter's page.
        num_fights (int): The number of fights to include in the results.

    Returns:
        list: A list of dictionaries, each containing details about a recent fight.
    """
    fights = []
    fight_rows = soup.find_all("tr", class_="js-fight-details-click")
    for i, row in enumerate(fight_rows):
        if i == num_fights:
            break
        
        cells = row.find_all("td")

        result = clean_string(cells[0].get_text())
        opponent = clean_string(cells[1].find_all("p")[-1].get_text())
        strikes_landed = clean_string(cells[3].find_all("p")[0].get_text())
        strikes_taken = clean_string(cells[3].find_all("p")[-1].get_text())
        takedowns_landed = clean_string(cells[4].find_all("p")[0].get_text())
        takedowns_taken = clean_string(cells[4].find_all("p")[-1].get_text())
        date = clean_string(cells[6].find_all("p")[-1].get_text())
        method = clean_string(" ".join([clean_string(c.get_text()) for c in cells[7].find_all("p")]))
        
        fights.append(
            {
                "opponent": opponent,
                "result": result,
                "date": date,
                "strikes_landed": strikes_landed,
                "strikes_taken": strikes_taken,
                "takedowns_landed": takedowns_landed,
                "takedowns_taken": takedowns_taken,
                "method": method,
            }
        )
        

    return fights


def get_fighter_data(fighter_url, retrieve_num_fights=5):
    """
    Get a dictionary of fighter stats and their recent fight data.

    Args:
        fighter_url (str): The URL of the fighter's page on UFC Stats website.
        retrieve_num_fights (int): The number of fights to retrieve data for. Defaults to 5.

    Returns:
        dict: A dictionary containing the fighter's stats and their recent fight data.
    """
    soup = get_soup(fighter_url)
    data = get_fighter_stats(soup)
    data["fights"] = get_fight_stats(soup, retrieve_num_fights)

    return data


def get_fighter_url(fighter_name):
    """
    Search for a fighter on the UFC website and return their profile URL.

    Args:
        fighter_name (str): The name of the fighter to search for.

    Returns:
        str: The URL for the fighter's profile page on the UFC website.
    """
    # fighter_name is guaranteed to be the first and last name with a space inbetween (it is coming from our own data)
    # do a search using the last_name as that should be more unique
 
    split_name = fighter_name.split(" ")
    last_name = split_name[-1]
    # last names with a hyphen seem to use the first part of the last name
    if '-' in last_name:
        last_name = last_name.split('-')[0]  
    # some combined names use the full combination, others only use the last part
    # capture the combined so we can compare it if necessary
    elif len(split_name) > 2:
        combined_last_name = ' '.join(split_name[1:])
    
        
    soup = get_soup(SEARCH_URL, {"query": last_name})
    result_rows = soup.find_all("tr", class_="b-statistics__table-row")
    if len(result_rows) == 2:
        print("No results for that fighter")
        return 0

    if len(result_rows) > 3:
        
        clean_fighter_name = clean_name(fighter_name).split(' ')
        clean_first = clean_fighter_name[0]
        clean_last = clean_fighter_name[-1]
        # skip the first two row as they are not important
        for row in result_rows[2:]:
            cells = row.find_all("td")
            first = clean_string(cells[0].get_text()).lower()
            last = clean_string(cells[1].get_text()).lower()
            url = cells[0].find("a").attrs["href"]
            if names_are_similar(first, clean_first) and (names_are_similar(last, clean_last) or names_are_similar(last, last_name) or names_are_similar(last, combined_last_name)):
                return url

        print("Couldn't deduce fighter from name")
        return 0
    else:
        # only one result - pick it off the table and continue
        fighter_row = result_rows[2]
        return fighter_row.find_all("td")[0].find("a").attrs["href"]


def scrape_fighter_data(fighter_name, retrieve_num_fights=5):
    """
    Extracts fighter data and fight details for a given fighter name.

    Args:
        fighter_name (str): The name of the fighter to search for.
        retrieve_num_fights (int, optional): The number of fights to retrieve data for. Default is 5.

    Returns:
        dict: A dictionary containing details about the fighter and their recent fights.
    """
    fighter_url = get_fighter_url(fighter_name)
    if fighter_url:
        return get_fighter_data(fighter_url, retrieve_num_fights)

if __name__ == "__main__":
    data = scrape_fighter_data("Max Holloway")

    print(json.dumps(data, indent=4, sort_keys=True))
