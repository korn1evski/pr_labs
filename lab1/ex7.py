import requests
from bs4 import BeautifulSoup
import re
from ex1 import fetch_html
import base64
import xml.sax.saxutils as saxutils

username = "301"
password = "307"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

upload_url = "http://localhost:8000/upload"

auth_header = {
    "Authorization": f"Basic {encoded_credentials}"
}

class Book:
    def __init__(self, name, price, link, details=None):
        self.name = name
        self.price = price
        self.link = link
        self.details = details or {}

    def add_details(self, details):
        if 'Number of reviews' in details:
            details['Number of reviews'] = int(details['Number of reviews'])
        self.details.update(details)

    def serialize_to_json(self):
        json_str = '{\n'
        json_str += f'  "name": "{self.name}",\n'
        json_str += f'  "price": {self.price:.2f},\n'
        json_str += f'  "link": "{self.link}",\n'
        for key, value in self.details.items():
            if isinstance(value, (int, float)):
                json_str += f'  "{key}": {value},\n'
            else:
                json_str += f'  "{key}": "{value}",\n'
        json_str = json_str.rstrip(',\n') + '\n}'
        return json_str

    def serialize_to_xml(self):
        xml_str = '<book>\n'
        xml_str += f'  <name>{saxutils.escape(self.name)}</name>\n'
        xml_str += f'  <price>{self.price:.2f}</price>\n'
        xml_str += f'  <link>{saxutils.escape(self.link)}</link>\n'
        for key, value in self.details.items():
            tag_name = key.replace(' ', '_').replace('(', '').replace(')', '')
            if isinstance(value, (int, float)):
                xml_str += f'  <{tag_name}>{value}</{tag_name}>\n'
            else:
                xml_str += f'  <{tag_name}>{saxutils.escape(str(value))}</{tag_name}>\n'
        xml_str += '</book>'
        return xml_str

    def display(self):
        print(f"Name: {self.name}")
        print(f"Price: {self.price}")
        print(f"Link: {self.link}")
        for key, value in self.details.items():
            print(f"{key}: {value}")
        print("=" * 60)

def clean_price(price_str):
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    return float(cleaned_price)

def get_product_details(product_url):
    product_html, status = fetch_html(product_url)
    if product_html and status == "Success":
        soup = BeautifulSoup(product_html, 'html.parser')
        product_table = soup.find('table', class_='table table-striped')
        product_details = {}
        if product_table:
            rows = product_table.find_all('tr')
            for row in rows:
                th = row.find('th').text.strip()
                td = row.find('td').text.strip()
                product_details[th] = td
        if 'Price (excl. tax)' in product_details:
            product_details['Price (excl. tax)'] = clean_price(product_details['Price (excl. tax)'])
        if 'Price (incl. tax)' in product_details:
            product_details['Price (incl. tax)'] = clean_price(product_details['Price (incl. tax)'])
        if 'Tax' in product_details:
            product_details['Tax'] = clean_price(product_details['Tax'])
        return product_details
    else:
        return {}

def get_books_info():
    url = "http://books.toscrape.com/"
    html_content, status = fetch_html(url)
    if html_content and status == "Success":
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        for book in books:
            name = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            product_link = book.h3.a['href']
            full_product_link = url + product_link
            cleaned_price = clean_price(price)
            book_obj = Book(name, cleaned_price, full_product_link)
            product_details = get_product_details(book_obj.link)
            book_obj.add_details(product_details)
            book_obj.display()
            json_data = book_obj.serialize_to_json()
            xml_data = book_obj.serialize_to_xml()
            print("Serialized to JSON:")
            print(json_data)
            print("Serialized to XML:")
            print(xml_data)
            send_data_to_server(json_data, xml_data)
    else:
        print(f"Failed to fetch the website content: {status}")

def send_data_to_server(json_data, xml_data):
    headers_json = {
        **auth_header,
        "Content-Type": "application/json"
    }
    response_json = requests.post(upload_url, headers=headers_json, data=json_data)
    print("\nJSON Response Status Code:", response_json.status_code)
    print("JSON Response Body:", response_json.text)
    headers_xml = {
        **auth_header,
        "Content-Type": "application/xml"
    }
    print("\nXML Data Being Sent:")
    print(xml_data)
    response_xml = requests.post(upload_url, headers=headers_xml, data=xml_data)
    print("XML Response Status Code:", response_xml.status_code)
    print("XML Response Body:", response_xml.text)

def main():
    get_books_info()

main()
