import requests


def get_page(page_url):
    """
    Retrieve the text content of a webpage.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
