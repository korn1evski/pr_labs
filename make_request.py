import base64
import requests

# Server URL
url = "http://localhost:8000/upload"

# Credentials
username = "301"
password = "307"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Common Headers for Authorization
auth_header = {
    "Authorization": f"Basic {encoded_credentials}"
}

# JSON Request
headers_json = {
    **auth_header,  # Merge the Authorization header
    "Content-Type": "application/json"
}

json_data = {
    "name": "Test Name",
    "value": 123
}

# Send JSON POST request
response_json = requests.post(url, headers=headers_json, json=json_data)
print("JSON Response Status Code:", response_json.status_code)
print("JSON Response Body:", response_json.text)

# XML Request
headers_xml = {
    **auth_header,  # Merge the Authorization header
    "Content-Type": "application/xml"
}

xml_data = """<data><name>Test Name</name><value>123</value></data>"""

# Send XML POST request
response_xml = requests.post(url, headers=headers_xml, data=xml_data)
print("XML Response Status Code:", response_xml.status_code)
print("XML Response Body:", response_xml.text)
