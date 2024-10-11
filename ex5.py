import requests
from bs4 import BeautifulSoup
import re
from functools import reduce
from datetime import datetime

# Import fetch_html from ex1.py
from ex1 import fetch_html


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

    # Ensure price is a float by stripping non-numeric characters (e.g., £ sign)
    price_str = re.sub(r'[^\d.]', '', book_data['price'])  # Remove non-numeric characters
    book_data['price'] = float(price_str)  # Convert to float

    return book_data


def get_books_info():
    url = "http://books.toscrape.com/"
    html_content, status = fetch_html(url)

    if html_content and status == "Success":
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all book items (they are in <article class="product_pod">)
        books = soup.find_all('article', class_='product_pod')

        books_info = []

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
            books_info.append(cleaned_book_data)

        return books_info
    else:
        print(f"Failed to fetch the website content: {status}")
        return []


# Step 1: Convert GBP to MDL (constant conversion rate)
def convert_gbp_to_mdl(books_info):
    """
    Converts book prices from GBP to MDL using a constant rate and keeps original price in GBP.

    Parameters:
    books_info (list): List of dictionaries containing book info.

    Returns:
    list: List of dictionaries with both GBP and MDL prices.
    """
    gbp_to_mdl_rate = 22.5  # Constant exchange rate for GBP to MDL

    def convert_price(book):
        # Store the original price in GBP
        book['price_gbp'] = book['price']
        # Convert GBP to MDL and store the converted price
        book['price_mdl'] = book['price'] * gbp_to_mdl_rate
        return book

    # Apply map to convert prices
    return list(map(convert_price, books_info))


# Step 2: Filter products within a given price range (in MDL)
def filter_books_by_price(books_info, min_price, max_price):
    """
    Filters books within a specific price range in MDL.

    Parameters:
    books_info (list): List of dictionaries containing book info.
    min_price (float): Minimum price to filter.
    max_price (float): Maximum price to filter.

    Returns:
    list: Filtered list of dictionaries within the price range.
    """
    return list(filter(lambda book: min_price <= book['price_mdl'] <= max_price, books_info))


# Step 3: Reduce to sum up the prices of filtered products
def sum_of_filtered_prices(filtered_books):
    """
    Sums the prices of the filtered books.

    Parameters:
    filtered_books (list): List of filtered books.

    Returns:
    float: The sum of prices of the filtered books.
    """
    return reduce(lambda acc, book: acc + book['price_mdl'], filtered_books, 0)


# Main function to process the books
def process_books(min_price, max_price):
    # Get book info from ex2
    books_info = get_books_info()

    # Step 1: Convert prices to MDL
    converted_books = convert_gbp_to_mdl(books_info)

    # Step 2: Filter books within the price range
    filtered_books = filter_books_by_price(converted_books, min_price, max_price)

    # Step 3: Sum the prices of the filtered books
    total_price_sum = sum_of_filtered_prices(filtered_books)

    # Step 4: Attach the UTC timestamp and total sum to the filtered data
    result = {
        'filtered_books': filtered_books,
        'total_price_sum': total_price_sum,
        'timestamp': datetime.utcnow().isoformat()  # Attach UTC timestamp
    }

    return result


# Get user input for price constraints from the keyboard
min_price = float(input("Enter the minimum price in MDL: "))
max_price = float(input("Enter the maximum price in MDL: "))

# Process books with the input constraints
processed_data = process_books(min_price, max_price)

# Display processed data
print(f"Total Price Sum: {processed_data['total_price_sum']:.2f} MDL")
print(f"Timestamp: {processed_data['timestamp']}")
print(f"Filtered Books:")

for book in processed_data['filtered_books']:
    print(f"Name: {book['name']}, Price in GBP: £{book['price_gbp']:.2f}, Price in MDL: {book['price_mdl']:.2f} MDL, Link: {book['link']}")
