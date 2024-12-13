import pika
import json
import requests
import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
LAB2_HOST = os.environ.get('LAB2_HOST', 'lab2_webserver')

def consume_messages():
    print("Some consumes text")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='books_queue', durable=True)
    for method, properties, body in channel.consume(queue='books_queue', inactivity_timeout=5):
        if body:
            print("Consuming body:", body)
            book_data = json.loads(body)
            response = requests.post(f"http://{LAB2_HOST}:5000/books", data=book_data)
            print("Posted to LAB2:", response.text)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("No messages found, timeout reached.")
            break

    channel.cancel()
    connection.close()
