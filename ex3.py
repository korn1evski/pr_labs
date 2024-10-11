import requests
from bs4 import BeautifulSoup
import re
from ex1 import fetch_html  # Import fetch_html from ex1.py
from ex8 import CustomSerializer  # Import CustomSerializer from ex8.py


def clean_price(price_str):
    """
    Cleans a price string by removing the currency symbol and converting it to a float.

    Parameters:
    price_str (str): The price string to clean.

    Returns:
    float: The cleaned price as a float.
    """
    cleaned_price = re.sub(r'[^\d.]', '', price_str)  # Remove any non-numeric characters except for the decimal point
    return float(cleaned_price)


def clean_book_data(book_data):
    """
    Cleans and validates the book data.

    Parameters:
    book_data (dict): A dictionary with book's name, price, and link.

    Returns:
    dict: A cleaned dictionary with whitespaces removed and price as a float.
    """
    book_data['name'] = book_data['name'].strip()
    book_data['price'] = clean_price(book_data['price'])  # Ensure price is a float by cleaning it
    return book_data


def get_product_details(product_url):
    """
    Extracts detailed product information from the product page.

    Parameters:
    product_url (str): The URL of the product page.

    Returns:
    dict: A dictionary with the detailed product information (UPC, tax, availability, etc.).
    """
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

        # Clean prices and tax values
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

        # Loop over all books, serialize and deserialize book data
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

            # Serialize the book data using CustomSerializer
            serialized_data = CustomSerializer.serialize(cleaned_book_data)
            print("Serialized Book Data:")
            print(serialized_data)

            # Deserialize the book data back to a Python dictionary
            deserialized_data = CustomSerializer.deserialize(serialized_data)
            print("\nDeserialized Book Data:")
            print(deserialized_data)

            # Display the book info
            display_book_info(deserialized_data)

    else:
        print(f"Failed to fetch the website content: {status}")


def display_book_info(book):
    """
    Displays a single book's information in a nicely formatted way.

    Parameters:
    book (dict): Dictionary containing book info.
    """
    print(f"Name: {book['name']}")
    print(f"Price: {book['price']}")
    print(f"Link: {book['link']}")

    # Print detailed information if available
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

    print("=" * 60)  # Separator line between books


# Start scraping and displaying books info
get_books_info()
