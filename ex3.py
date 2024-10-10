import requests
from bs4 import BeautifulSoup
from ex1 import fetch_html
from ex2 import extract_product_info


def fetch_additional_data(product_url):
    """
    Fetches additional data (e.g., specifications) from the product's individual page.

    Parameters:
    product_url (str): The URL of the product page to scrape.

    Returns:
    dict: A dictionary with additional product details (e.g., battery capacity, memory, RAM, etc.).
    """
    response = requests.get(product_url)

    if response.status_code == 200:
        product_page = response.text
        soup = BeautifulSoup(product_page, 'html.parser')

        # Find the promo-text div where product specifications are located
        promo_text_div = soup.find('div', class_='promo-text')

        if promo_text_div:
            # Create a dictionary to store product specifications
            product_specs = {}

            # Find all table rows in the promo-text div
            for row in promo_text_div.find_all('tr'):
                columns = row.find_all('td')
                if len(columns) == 2:
                    spec_name = columns[0].text.strip()
                    spec_value = columns[1].find('b').text.strip()
                    product_specs[spec_name] = spec_value

            return product_specs
        else:
            return {}
    else:
        print(f"Failed to retrieve additional data from {product_url}")
        return {}


if __name__ == "__main__":
    # URL for the products page
    url = "https://enter.online/telefoane/smartphone-uri"

    # Fetch the HTML content using the function from ex1.py
    html_content, status = fetch_html(url)

    if html_content and status == "Success":
        # Extract product names, prices, and links
        product_list = extract_product_info(html_content)

        if product_list:
            # Display the extracted product info and fetch additional details
            for product in product_list:
                print(f"Product Name: {product['name']}")
                print(f"New Price: {product['price_new']}")
                if product['price_old']:
                    print(f"Old Price: {product['price_old']}")
                if product['discount']:
                    print(f"Discount: {product['discount']}")
                if product['link']:
                    print(f"Link: {product['link']}")

                    # Fetch and display additional product details from the product page
                    additional_data = fetch_additional_data(product['link'])
                    if additional_data:
                        print("Additional Product Information:")
                        for spec_name, spec_value in additional_data.items():
                            print(f"{spec_name}: {spec_value}")
                    else:
                        print("No additional product information found.")
                print("-" * 40)
        else:
            print("No products found.")
    else:
        print(f"Failed to retrieve content: {status}")
