from PyQt5.QtWidgets import *
from view import *
from bs4 import BeautifulSoup
import csv
import requests
import re

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class Controller(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        """
        Function to initialize GUI with default values
        """
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.button_submit.clicked.connect(self.submit_scrape)
        self.hide_success()

    def get_raw_sentences(self):
        """
        Function to obtain unprocessed sentences from Klei's Sale page
        :return: list
        """
        url="https://shop.klei.com/sale/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        lists = soup.find_all('li', attrs={'class': re.compile('^product type-product post-*')})
        return lists


    def submit_scrape(self):
        """
        Function to scrape Klei's sale page
        """
        lists = self.get_raw_sentences()
        sentence_list = self.process_sentences(lists)
        item_names, item_prices = self.separate_listings(sentence_list)
        self.write_to_csv(item_names, item_prices)
        self.display_success()
        
    def display_success(self):
        """
        Function to reveal success message for multiple student calculation
        """
        self.label_saved.setHidden(False)
    
    def hide_success(self):
        """
        Function to hide success message for multiple student calculation
        """
        self.label_saved.setHidden(True)

    def process_sentences(self, lists):
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

    def separate_listings(self, sentence_list):
        """
        Function to separate raw sentences into a list of names and prices and further processes each
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

        for index, sentence in enumerate(item_names):
            if re.search(',', sentence):
                item_name = re.sub(',', '', sentence)
                item_names[index] = item_name

        return item_names, item_prices

    def write_to_csv(self, item_names, item_prices):
        """
        Function to write item names and prices to csv
        :param item_names: list of sale item names
        :param item_prices: list of sale item prices
        """
        with open('klei_sales.csv', 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, delimiter=',', quotechar='',escapechar='-')
            csv_writer.writerow(['Name', 'Price'])
            for index, item_name in enumerate(item_names):
                csv_writer.writerow([item_name, item_prices[index]])
