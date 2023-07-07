from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

HEADERS = (
    {'User-Agent':
           '''Chrome/44.0.2403.157 Safari/537.36''',
                           'Accept-Language': 'en-US, en;q=0.5'}
                           )

def get_all_page_data(page_url:str):
    """
    Provides All products data from page\n
    return: titles,prices,num_ratings,ratings,urls\n
    return_type: list
    """
    webpage = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")

    try:
        titles = soup.findAll("span",attrs={"class": 'a-size-medium a-color-base a-text-normal'})
        prices = soup.findAll("span",attrs={"class": 'a-price-whole'})
        num_ratings = soup.findAll("span",attrs={"class": 'a-size-base s-underline-text'})
        ratings = soup.findAll("span",attrs={"class": 'a-icon-alt'})
        urls = soup.findAll("a",attrs={"class": 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})

        titles = [title.string for title in titles]
        titles = [product_name.strip().replace(',', '') for product_name in titles]

        prices = [price.string for price in prices]
        num_ratings = [rating.string for rating in num_ratings]
        ratings = [rating.string for rating in ratings]
        urls= [url.get('href') for url in urls]

    
           
    except AttributeError:
        return None
    
    return titles,prices,num_ratings,ratings,urls


def get__top_description(product_url):
    """
    Returns Cleaned Description
    """
    
    webpage = requests.get(product_url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")
    try:
        descriptions = soup.findAll("ul",attrs={"class": 'a-unordered-list a-vertical a-spacing-mini'})
        full_desc = ""
        for description in descriptions:
            li_el = description.select('li > span')
            for el in li_el:
                full_desc += el.string
        
        full_desc = full_desc.replace(',',' ')
    except AttributeError:
        return "NA"
    return full_desc
        
def get_product_description(url):
    """
    Returns Full cleaned Product description
    """

    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")
    full_desc = " "
    try:
        product_disc = soup.find("div",attrs={"id": 'aplus_feature_div'})
        desc_tb = product_disc.select('div > p')
        
        for desc in desc_tb:
            full_desc += str(desc.string)
        
        full_desc = full_desc.replace(","," ")
        full_desc = full_desc.replace("None"," ")
    except AttributeError:
        full_desc = "NAN"

    return full_desc

def product_page_data(product_url):
    """
    Return required data from product page
    """
    product_url = f"https://www.amazon.in{product_url}"
    description = get__top_description(product_url)
    product_description = get_product_description(product_url)
    asin = product_url[-10:]
    webpage = requests.get(product_url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")
    try:
        # little flawed
        manufacturer = soup.find("ul",attrs={"class": 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
        manufacturer = manufacturer.select('li > span > span')[5].string
    except AttributeError:
        manufacturer = "NAN"
    
    return description,asin,manufacturer,product_description

if __name__ == "__main__":
    num_pages = 20

    all_page_data = {
        'titles':[],
        'prices':[],
        'num_ratings':[],
        'ratings':[],
        'urls':[],
        'asin':[],
        'description':[],
        'manufacturer':[],
        'product_description':[]
    }
    for page_no in range(1,num_pages+1):
        print(f"==> Page No.:{page_no}")
        URL = f"https://www.amazon.in/s?k=bags&page={page_no}&crid=2M096C61O4MLT&qid=1688717001&sprefix=ba%2Caps%2C283&ref=sr_pg_{page_no}"

        titles,prices,num_ratings,ratings,urls = get_all_page_data(URL)

        all_page_data['titles'].extend(titles)
        all_page_data['prices'].extend(prices)
        all_page_data['num_ratings'].extend(num_ratings)
        all_page_data['ratings'].extend(ratings)
        all_page_data['urls'].extend(urls)

    total_urls = len(all_page_data['urls'])
    t = 0
    for url in all_page_data['urls']:
        remaining_urls = total_urls - t
        print(f"Total Urls:{total_urls} --- Remaining Urls: {remaining_urls}")
        
        description,asin,manufacturer,product_description = product_page_data(url)
        all_page_data['description'].append(description)
        all_page_data['asin'].append(asin)
        all_page_data['manufacturer'].append(manufacturer)
        all_page_data['product_description'].append(product_description)
        t+=1

    data_df = pd.DataFrame.from_dict(all_page_data)
    print(data_df)