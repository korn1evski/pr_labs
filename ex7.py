import requests
from bs4 import BeautifulSoup
import re

# Import fetch_html from ex1.py
from ex1 import fetch_html


class Book:
    def __init__(self, name, price, link, details=None):
        """
        Initialize a Book object.

        Parameters:
        name (str): Name of the book.
        price (float): Price of the book.
        link (str): URL link to the book details.
        details (dict): Optional additional product details like UPC, tax, etc.
        """
        self.name = name
        self.price = price
        self.link = link
        self.details = details or {}

    def add_details(self, details):
        """Adds or updates additional book details."""
        # Ensure "Number of reviews" is an integer if available
        if 'Number of reviews' in details:
            details['Number of reviews'] = int(details['Number of reviews'])
        self.details.update(details)

    def serialize_to_json(self):
        """Serializes the book object to JSON format."""
        json_str = '{\n'
        json_str += f'  "name": "{self.name}",\n'
        json_str += f'  "price": {self.price:.2f},\n'  # No quotes around numbers
        json_str += f'  "link": "{self.link}",\n'
        for key, value in self.details.items():
            if isinstance(value, (int, float)):  # Check if the value is a number
                json_str += f'  "{key}": {value},\n'
            else:
                json_str += f'  "{key}": "{value}",\n'
        json_str = json_str.rstrip(',\n') + '\n}'  # Remove trailing comma and close JSON object
        return json_str

    def serialize_to_xml(self):
        """Serializes the book object to XML format."""
        xml_str = '<book>\n'
        xml_str += f'  <name>{self.name}</name>\n'
        xml_str += f'  <price>{self.price:.2f}</price>\n'
        xml_str += f'  <link>{self.link}</link>\n'
        for key, value in self.details.items():
            xml_str += f'  <{key}>{value}</{key}>\n'
        xml_str += '</book>'
        return xml_str

    def display(self):
        """Displays the book's information in a human-readable format."""
        print(f"Name: {self.name}")
        print(f"Price: {self.price}")
        print(f"Link: {self.link}")
        for key, value in self.details.items():
            print(f"{key}: {value}")
        print("=" * 60)  # Separator line between books


def clean_price(price_str):
    """Cleans a price string by removing the currency symbol and converting it to a float."""
    cleaned_price = re.sub(r'[^\d.]', '', price_str)  # Remove any non-numeric characters except the decimal point
    return float(cleaned_price)


def get_product_details(product_url):
    """Extracts detailed product information from the product page."""
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

        # Clean prices (excl. and incl. tax) and tax
        if 'Price (excl. tax)' in product_details:
            product_details['Price (excl. tax)'] = clean_price(product_details['Price (excl. tax)'])
        if 'Price (incl. tax)' in product_details:
            product_details['Price (incl. tax)'] = clean_price(product_details['Price (incl. tax)'])
        if 'Tax' in product_details:
            product_details['Tax'] = clean_price(product_details['Tax'])  # Clean the Tax value

        return product_details
    else:
        return {}


def get_books_info():
    url = "http://books.toscrape.com/"
    html_content, status = fetch_html(url)

    if html_content and status == "Success":
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all book items (they are in <article class="product_pod">)
        books = soup.find_all('article', class_='product_pod')

        # Loop over all books and extract name, price, and link
        for book in books:
            name = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            product_link = book.h3.a['href']
            full_product_link = url + product_link

            # Clean the price and create a Book instance
            cleaned_price = clean_price(price)
            book_obj = Book(name, cleaned_price, full_product_link)

            # Scrape additional details from the product page and add them to the Book instance
            product_details = get_product_details(book_obj.link)
            book_obj.add_details(product_details)

            # Display and serialize each book immediately after processing
            book_obj.display()  # Display book information
            print("Serialized to JSON:")
            print(book_obj.serialize_to_json())
            print("Serialized to XML:")
            print(book_obj.serialize_to_xml())

    else:
        print(f"Failed to fetch the website content: {status}")


# Main function to start processing
def main():
    # Process and display each book one by one
    get_books_info()


# Start scraping and displaying books info
main()
