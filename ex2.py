from bs4 import BeautifulSoup
import re
from ex6 import retrieve_page_body
from ex1 import fetch_html

def clean_book_data(book_data):
    book_data['name'] = book_data['name'].strip()
    price_str = re.sub(r'[^\d.]', '', book_data['price'])
    book_data['price'] = float(price_str)
    return book_data

def get_books_info():
    host = "books.toscrape.com"
    port = 80
    path = "/"
    # html_content = retrieve_page_body(host, port, path)
    html_content, status= fetch_html("https://books.toscrape.com/")

    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        books_info = []

        for book in books:
            name = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            product_link = book.h3.a['href']
            full_product_link = f"http://{host}/{product_link}"

            book_data = {
                'name': name,
                'price': price,
                'link': full_product_link
            }

            cleaned_book_data = clean_book_data(book_data)
            books_info.append(cleaned_book_data)

        return books_info
    else:
        print("Failed to fetch the website content.")
        return []

def display_books_info(books_info):
    for book in books_info:
        name = book['name']
        price = book['price']
        link = book['link']
        print(f"Name: {name}\nPrice: {price}\nLink: {link}\n")
        print("=" * 60)

book_info = get_books_info()
display_books_info(book_info)
