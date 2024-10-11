from bs4 import BeautifulSoup
import re
from ex6 import retrieve_page_body
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
    # Use socket-based HTTP request to get the HTML content
    host = "books.toscrape.com"
    port = 80
    path = "/"

    # Fetch the page content using sockets
    html_content = retrieve_page_body(host, port, path)
    # html_content, status = fetch_html("https://books.toscrape.com/")

    if html_content:
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
            full_product_link = f"http://{host}/{product_link}"

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
        print("Failed to fetch the website content.")
        return []


def display_books_info(books_info):
    """
    Displays the books information in a nicely formatted way.

    Parameters:
    books_info (list): List of dictionaries containing book info.
    """
    # Display each book's information
    for book in books_info:
        name = book['name']
        price = book['price']
        link = book['link']

        # Print each book's information on a new line with a separator
        print(f"Name: {name}\nPrice: {price}\nLink: {link}\n")
        print("=" * 60)  # Separator line between books


# Get book info
book_info = get_books_info()

# Display book info in a more beautiful and structured way
display_books_info(book_info)
