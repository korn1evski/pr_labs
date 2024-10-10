import requests

# Define the URL for the GET request
url = "https://enter.online/telefoane/smartphone-uri"

# Make the HTTP GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Get the HTML content from the response
    html_content = response.text
    html_status = "Success"
else:
    # If the request failed, show the status code
    html_content = f"Request failed with status code: {response.status_code}"
    html_status = "Failed"

# Now print the status and the first 500 characters of the content
print(html_status)
print(html_content)  # Display first 500 characters of the HTML content
