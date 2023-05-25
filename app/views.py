from django.shortcuts import render

# Create your views here.
import csv
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def scrape_data(request):
    pages_to_scrape = 20
    base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'
    all_product_details = []

    for page_number in range(1, pages_to_scrape + 1):
        url = base_url.format(page_number)
        product_details = scrape_listing_page(url)
        all_product_details.extend(product_details)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="product_details.csv"'

    fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews'
                  ]
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_product_details)

    return response

def scrape_listing_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_details = []
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    for product in products:
        product_url = product.find('a', class_='a-link-normal s-no-outline')['href']
        if '/dp/' in product_url:
            product_url = 'https://www.amazon.in' + product_url
            product_name_element = product.find('span', class_='a-size-base-plus')
            product_name = product_name_element.text.strip() if product_name_element else ''
            product_price = product.find('span', class_='a-offscreen').text.strip()
            rating_element = product.find('span', class_='a-icon-alt')
            rating = rating_element.text.split()[0] if rating_element else 'Not rated'
            reviews_count_element = product.find('span', class_='a-size-base')
            reviews_count = reviews_count_element.text.strip().replace(',', '') if reviews_count_element else ''

            product_details.append({
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': rating,
                'Number of Reviews': reviews_count,
            })

    return product_details


