import requests
from bs4 import BeautifulSoup
import re

# Import fetch_html from ex1.py
from ex1 import fetch_html


def clean_price(price_str):
    """
    Cleans a price string by removing the currency symbol and converting it to a float.

    Parameters:
    price_str (str): The price string to clean.

    Returns:
    float: The cleaned price as a float.
    """
    # Remove any non-numeric characters except for the decimal point
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    return float(cleaned_price)


def clean_book_data(book_data):
    """
    Cleans and validates the book data.

    Parameters:
    book_data (dict): A dictionary with book's name, price, and link.

    Returns:
    dict: A cleaned dictionary with whitespaces removed and price as a float.
    """
    # Remove whitespaces from the name
    book_data['name'] = book_data['name'].strip()

    # Ensure price is a float by cleaning it
    book_data['price'] = clean_price(book_data['price'])

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

        # Find the table with class "table table-striped"
        product_table = soup.find('table', class_='table table-striped')

        product_details = {}

        # Extract data from the table
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
            # Extract the name of the book (in <h3> tag)
            name = book.h3.a['title']

            # Extract the price of the book (in <p class="price_color">)
            price = book.find('p', class_='price_color').text

            # Extract the product link (inside the <a> tag, needs to be appended to the base URL)
            product_link = book.h3.a['href']
            full_product_link = url + product_link

            # Add the book's info to the list
            book_data = {
                'name': name,
                'price': price,
                'link': full_product_link
            }

            # Clean and validate the book data
            cleaned_book_data = clean_book_data(book_data)

            # Scrape additional details from the product page
            product_details = get_product_details(cleaned_book_data['link'])
            cleaned_book_data.update(product_details)  # Merge the detailed info into the book data

            # Display the book info immediately after processing
            display_book_info(cleaned_book_data)

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
