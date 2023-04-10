import requests
from bs4 import BeautifulSoup
import re
import json

import shortuuid

def get_soup(url: str, params: dict = {}):
    """
        Get BeautifulSoup object from a given URL and parameters.

        Args:
            url (str): The URL to fetch the page from.
            params (dict): Query parameters to include in the request (default: {}).

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the page.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, params=params, headers=headers)
    return BeautifulSoup(resp.content, "lxml")

def clean_string(string: str):
    """
    Remove any unnecessary characters from a string.

    Args:
        string (str): The string to clean up.

    Returns:
        str: The cleaned up string.
    """
    clean_str = re.sub(r"(\\n+)", "", string)
    return clean_str.strip()

def json_pprint(json_obj):
    print(json.dumps(json_obj, indent=4, sort_keys=True))
    
    
def get_short_uuid():
    return shortuuid.uuid()