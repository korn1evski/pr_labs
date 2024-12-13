import time
import pika
import os
import requests
import re
import json
from bs4 import BeautifulSoup

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

def clean_book_data(book_data):
    book_data['name'] = book_data['name'].strip()
    price_str = re.sub(r'[^\d.]', '', book_data['price'])
    book_data['price'] = float(price_str)
    return book_data

def get_books_info():
    url = "http://books.toscrape.com/"
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        books_info = []

        for book in books:
            name = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            product_link = book.h3.a['href']
            full_product_link = f"{url}{product_link}"

            book_data = {
                'name': name,
                'price': price,
                'link': full_product_link,
                'author': 'Unknown'  # since original data does not have author info
            }

            cleaned_book_data = clean_book_data(book_data)
            books_info.append(cleaned_book_data)
        return books_info
    else:
        print("Failed to fetch the website content.")
        return []

def publish_books_to_rabbitmq(books_info):
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 5s...")
            time.sleep(5)
    else:
        print("Could not connect to RabbitMQ after several retries, exiting.")
        exit(1)

    channel.queue_declare(queue='books_queue', durable=True)
    for book in books_info:
        message = json.dumps(book)
        try:
            channel.basic_publish(exchange='', routing_key='books_queue', body=message)
            print(f"Published: {message}")
        except Exception as e:
            print(f"Failed to publish message: {e}")

    connection.close()

if __name__ == "__main__":
    books = get_books_info()
    if books:
        publish_books_to_rabbitmq(books)
