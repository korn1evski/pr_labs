from bs4 import BeautifulSoup


def clean_price(price_str):
    """
    Cleans the price string by removing non-numeric characters and converts it to an integer.

    Parameters:
    price_str (str): The price string to clean.

    Returns:
    int: The cleaned price as an integer.
    """
    # Remove all non-numeric characters
    price_str = ''.join([ch for ch in price_str if ch.isdigit()])
    return int(price_str) if price_str else 0


def extract_product_info(html_content):
    """
    Extracts and cleans product names, prices, and links from the given HTML content.

    Parameters:
    html_content (str): The HTML content to parse.

    Returns:
    list: A list of dictionaries with cleaned and validated product names, prices, and links.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []

    # Find product items based on the structure
    for product in soup.find_all('div', class_='grid-item'):
        name_tag = product.find('span', class_='product-title')  # Product name
        price_new_tag = product.find('span', class_='price-new')  # New price
        price_old_tag = product.find('span', class_='price-old')  # Old price (optional)
        discount_tag = product.find('span', class_='discount')  # Discount (optional)
        link_tag = product.find('a', href=True)  # Product link

        # Extract name, prices, and link if available
        if name_tag and price_new_tag and link_tag:
            name = name_tag.text.strip()  # Clean name (remove extra spaces)
            price_new = clean_price(price_new_tag.text)  # Clean new price and convert to integer
            price_old = clean_price(price_old_tag.text) if price_old_tag else None  # Clean old price
            discount = discount_tag.text.strip() if discount_tag else None  # Clean discount
            link = link_tag['href']  # Extract the link

            # Store cleaned product info in a dictionary
            product_info = {
                'name': name,
                'price_new': price_new,
                'price_old': price_old,
                'discount': discount,
                'link': link
            }

            products.append(product_info)

    return products



# URL for the products page
url = "https://enter.online/telefoane/smartphone-uri"

# Fetch the HTML content using the function from ex1.py
from ex1 import fetch_html

html_content, status = fetch_html(url)

if html_content and status == "Success":
    # Extract product names and prices
    product_list = extract_product_info(html_content)

    if product_list:
        # Display the extracted product info
        for product in product_list:
            print(f"Product Name: {product['name']}")
            print(f"New Price: {product['price_new']}")
            if product['price_old']:
                print(f"Old Price: {product['price_old']}")
            if product['discount']:
                print(f"Discount: {product['discount']}")
            if product['link']:
                print(f"Link: {product['link']}")
            print("-" * 40)
    else:
        print("No products found.")
else:
    print(f"Failed to retrieve content: {status}")
