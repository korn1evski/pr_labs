import re
from ex1 import fetch_html
from ex8 import CustomSerializer
from bs4 import BeautifulSoup
import requests
import base64
import json

# Server URL
upload_url = "http://localhost:8000/upload"

# Credentials for basic authentication
username = "301"
password = "307"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Common Headers for Authorization
auth_header = {
    "Authorization": f"Basic {encoded_credentials}"
}

def clean_price(price_str):
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    return float(cleaned_price)

def clean_book_data(book_data):
    book_data['name'] = book_data['name'].strip()
    book_data['price'] = clean_price(book_data['price'])
    return book_data

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
    all_serialized_books = []

    if html_content and status == "Success":
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        for book in books:
            name = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            product_link = book.h3.a['href']
            full_product_link = url + product_link
            book_data = {
                'name': name,
                'price': price,
                'link': full_product_link
            }
            cleaned_book_data = clean_book_data(book_data)
            product_details = get_product_details(cleaned_book_data['link'])
            cleaned_book_data.update(product_details)
            serialized_data = CustomSerializer.serialize(cleaned_book_data)
            all_serialized_books.append(serialized_data)
            deserialized_data = CustomSerializer.deserialize(serialized_data)
            display_book_info(deserialized_data)
            print("=" * 60)
        send_data_to_server(all_serialized_books)
    else:
        print(f"Failed to fetch the website content: {status}")

def display_book_info(book):
    print(f"Name: {book['name']}")
    print(f"Price: {book['price']}")
    print(f"Link: {book['link']}")
    if 'UPC' in book:
        print(f"UPC: {book['UPC']}")
    if 'Product Type' in book:
        print(f"Product Type: {book['Product Type']}")
    if 'Price (excl. tax)' in book:
        print(f"Price (excl. tax): {book['Price (excl. tax)']}")
    if 'Price (incl. tax)' in book:
        print(f"Price (incl. tax): {book['Price (incl. tax)']}")
    if 'Tax' in book:
        print(f"Tax: {book['Tax']}")
    if 'Availability' in book:
        print(f"Availability: {book['Availability']}")
    if 'Number of reviews' in book:
        print(f"Number of Reviews: {book['Number of reviews']}")

def send_data_to_server(all_serialized_books):
    deserialized_books = [CustomSerializer.deserialize(book) for book in all_serialized_books]
    json_data = json.dumps(deserialized_books)
    headers_json = {
        **auth_header,
        "Content-Type": "application/json"
    }
    response_json = requests.post(upload_url, headers=headers_json, data=json_data)
    print("\nJSON Response Status Code:", response_json.status_code)
    print("JSON Response Body:", response_json.text)

    xml_data = "<books>" + "".join([CustomSerializer.serialize(book) for book in deserialized_books]) + "</books>"
    headers_xml = {
        **auth_header,
        "Content-Type": "application/xml"
    }
    response_xml = requests.post(upload_url, headers=headers_xml, data=xml_data)
    print("\nXML Response Status Code:", response_xml.status_code)
    print("XML Response Body:", response_xml.text)

def main():
    get_books_info()

main()