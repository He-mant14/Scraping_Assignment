import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', {'class': 'sg-col-inner'})
    data = []

    for product in products:
        try:
            product_url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']
            product_name = product.find('span', {'class': 'a-size-medium'}).text.strip()
            product_price = product.find('span', {'class': 'a-offscreen'}).text.strip()
            rating = product.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
            num_reviews = product.find('span', {'class': 'a-size-base'}).text.strip().replace(',', '')

            data.append([product_url, product_name, product_price, rating, num_reviews])
        except:
            continue

    return data

def scrape_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        description = soup.find('div', {'id': 'productDescription'}).text.strip()
    except AttributeError:
        description = ''
    try:
        asin = soup.find('th', text='ASIN').find_next('td').text.strip()
    except AttributeError:
        asin = ''
    try:
        product_description = soup.find('div', {'id': 'feature-bullets'}).ul.text.strip().replace('\n', '')
    except AttributeError:
        product_description = ''
    try:
        manufacturer = soup.find('a', {'id': 'bylineInfo'}).text.strip()
    except AttributeError:
        manufacturer = ''

    return description, asin, product_description, manufacturer

base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
all_data = []

for page_num in range(1, 21):  # Scrape 20 pages
    url = base_url + str(page_num)
    data = scrape_product_list(url)
    all_data.extend(data)

for item in all_data:
    product_url = item[0]
    description, asin, product_description, manufacturer = scrape_product_page(product_url)
    item.extend([description, asin, product_description, manufacturer])

headers = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
           'Description', 'ASIN', 'Product Description', 'Manufacturer']

df = pd.DataFrame(all_data, columns=headers)
df.to_csv('~/Documents/product_data.csv', index=False)
