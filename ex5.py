import requests
from bs4 import BeautifulSoup
import re
from functools import reduce
from datetime import datetime
from ex1 import fetch_html

def clean_book_data(book_data):
    book_data['name'] = book_data['name'].strip()
    price_str = re.sub(r'[^\d.]', '', book_data['price'])
    book_data['price'] = float(price_str)
    return book_data

def get_books_info():
    url = "http://books.toscrape.com/"
    html_content, status = fetch_html(url)

    if html_content and status == "Success":
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        books_info = []

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
            books_info.append(cleaned_book_data)

        return books_info
    else:
        print(f"Failed to fetch the website content: {status}")
        return []

def convert_gbp_to_mdl(books_info):
    gbp_to_mdl_rate = 22.5

    def convert_price(book):
        book['price_gbp'] = book['price']
        book['price_mdl'] = book['price'] * gbp_to_mdl_rate
        return book

    return list(map(convert_price, books_info))

def filter_books_by_price(books_info, min_price, max_price):
    return list(filter(lambda book: min_price <= book['price_mdl'] <= max_price, books_info))

def sum_of_filtered_prices(filtered_books):
    return reduce(lambda acc, book: acc + book['price_mdl'], filtered_books, 0)

def process_books(min_price, max_price):
    books_info = get_books_info()
    converted_books = convert_gbp_to_mdl(books_info)
    filtered_books = filter_books_by_price(converted_books, min_price, max_price)
    total_price_sum = sum_of_filtered_prices(filtered_books)

    result = {
        'filtered_books': filtered_books,
        'total_price_sum': total_price_sum,
        'timestamp': datetime.utcnow().isoformat()
    }

    return result

min_price = float(input("Enter the minimum price in MDL: "))
max_price = float(input("Enter the maximum price in MDL: "))

processed_data = process_books(min_price, max_price)

print(f"Total Price Sum: {processed_data['total_price_sum']:.2f} MDL")
print(f"Timestamp: {processed_data['timestamp']}")
print(f"Filtered Books:")

for book in processed_data['filtered_books']:
    print(f"Name: {book['name']}, Price in GBP: £{book['price_gbp']:.2f}, Price in MDL: {book['price_mdl']:.2f} MDL, Link: {book['link']}")
