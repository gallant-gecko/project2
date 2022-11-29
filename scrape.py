from bs4 import BeautifulSoup
import requests
import re
import csv

def main():
    lists = get_raw_sentences()
    sentence_list = process_sentences(lists)
    item_names, item_prices = separate_listings(sentence_list)
    write_to_csv(item_names, item_prices)

def get_raw_sentences():
    """
    Function to obtain unprocessed sentences from Klei's Sale page
    :return: list
    """
    url="https://shop.klei.com/sale/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    lists = soup.find_all('li', attrs={'class': re.compile('^product type-product post-*')})
    return lists

def process_sentences(lists):
    """
    Function to roughly process each sentence and remove empty strings from list
    :param lists: container of raw string data for sale item names and prices
    :return: list
    """
    sentence_list = []
    for list in lists:
        sections = list.find('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')
        for section in sections:
            if not section.text.isspace():
                sentence_list.append("".join(section.text))
    
    while "" in sentence_list:
        sentence_list.remove("")

    return sentence_list

def separate_listings(sentence_list):
    """
    Function to separate raw sentences into a list of names and prices
    :param sentence_list: raw sentence list of item names and prices
    :return: list, list
    """ 
    item_names = []
    item_prices = []
    for index, sentence in enumerate(sentence_list):
        if index % 2 == 0:
            item_names.append(sentence)
        else:
            item_prices.append(sentence)

    for index, sentence in enumerate(item_prices):
        if re.search('USD \$\d*\.\d* USD', sentence):
            sale_price = re.sub('USD \$\d*\.\d* USD \$', '', sentence)
            item_prices[index] = sale_price
    return item_names, item_prices

def write_to_csv(item_names, item_prices):
    """
    Function to write item names and prices to csv
    :param item_names: list of sale item names
    :param item_prices: list of sale item prices
    """
    with open('dst_prices.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Name', 'Price'])
        for index, item_name in enumerate(item_names):
            csv_writer.writerow([item_name, item_prices[index]])

if __name__ == '__main__':
    main()