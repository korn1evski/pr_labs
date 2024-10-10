from bs4 import BeautifulSoup


def extract_product_info(html_content):
    """
    Extracts product names and prices from the given HTML content.

    Parameters:
    html_content (str): The HTML content to parse.

    Returns:
    list: A list of dictionaries with product names and prices.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []

    # Find product items based on the structure you provided
    for product in soup.find_all('div', class_='grid-item'):
        name_tag = product.find('span', class_='product-title')  # Product name
        price_new_tag = product.find('span', class_='price-new')  # New price
        price_old_tag = product.find('span', class_='price-old')  # Old price (optional)
        discount_tag = product.find('span', class_='discount')  # Discount (optional)

        # Extract name and prices if available
        if name_tag and price_new_tag:
            name = name_tag.text.strip()
            price_new = price_new_tag.text.strip()

            # Get the old price and discount if they exist
            price_old = price_old_tag.text.strip() if price_old_tag else None
            discount = discount_tag.text.strip() if discount_tag else None

            # Store product info in a dictionary
            product_info = {
                'name': name,
                'price_new': price_new,
                'price_old': price_old,
                'discount': discount
            }

            products.append(product_info)

    return products


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
            print("-" * 40)
    else:
        print("No products found.")
else:
    print(f"Failed to retrieve content: {status}")
