import requests

def fetch_html(url):
    """
    Fetches the HTML content from the specified URL.

    Parameters:
    url (str): The URL to send the GET request to.

    Returns:
    tuple: A tuple containing the HTML content (str) and the status message (str).
    """
    try:
        # Make the HTTP GET request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.text
            return html_content, "Success"
        else:
            return None, f"Request failed with status code: {response.status_code}"
    except requests.RequestException as e:
        # Handle connection issues or request errors
        return None, f"Request failed due to an error: {str(e)}"
