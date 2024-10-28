import requests

def fetch_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
            return html_content, "Success"
        else:
            return None, f"Request failed with status code: {response.status_code}"
    except requests.RequestException as e:
        return None, f"Request failed due to an error: {str(e)}"
