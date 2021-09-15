# Prasing Information
from bs4 import BeautifulSoup
import requests

# Read and store information
import csv

# Eamil System - Notifcations
# import os
# import smtplib

# Chrome
from selenium import webdriver
from selenium.webdriver.support.select import Select

from datetime import datetime

import time


Directory_CSV_File_Search = 'search/item_links.csv'
Directory_CSV_File_Recorded = 'recorded_results/'
Directory_Driver = r'C:\Chrome\chromedriver.exe'
application_delay = 3600  # 1 hour between each web scrap
List_search_terms = []


beginning_url = 'https://www.amazon.co.uk/'


# Method to take in links from CSV file
def gather_links_from_csv():
    with open(Directory_CSV_File_Search) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:

            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                print("Link: " + str(line_count))
                print(
                    f'\t {row[0]}')

                List_search_terms.append(row[0])

                line_count += 1


# A method to store the data for each time

# create an object

def get_url(search_term):
    """Generate a url from search term"""
    template = 'https://www.amazon.co.uk/s?k={}&ref=nb_sb_ss_ts-doa-p_1_7'
    search_term = search_term.replace(' ', '+')
    return template.format(search_term)


def extract_data(item):
    # RECORD OF OBJECT
    atag = item.h2.a

    # Description
    item_description = atag.text.strip()
    # URL link
    item_url = beginning_url + \
        atag.get('href')

    try:
        # Price Tag Parent
        item_price_tag_parent = item.find(
            'span', 'a-price')
        # Price
        item_price = item_price_tag_parent.find(
            'span', 'a-offscreen').text

    except AttributeError:
        item_price = ''

    try:
        # Ratings
        item_ratings = item.i.text
        # Review Count
        item_review_count = item.find(
            'span', {'class': 'a-size-base'}).text
    except:
        item_ratings = ''
        item_review_count = ''

    # Construct Information
    results = (item_description, item_price,
               item_ratings, item_review_count, item_url)

    return results


def store_records(data, name):
    today = datetime.today().strftime('%Y-%m-%d-%H.%M.%S')

    header = ['Description', 'Price', 'Ratings', 'Review Count', 'URL']

    with open(Directory_CSV_File_Recorded + name + ' - ' + str(today) + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

# needs updated


def getNextPage(soup):
    page = soup.find('ul', {'class': 'a-pagination'})
    if not page.find('li', {'class': 'a-disabled a-last'}):
        url = 'http://www.amazon.co.uk' + \
            str(page.find('li', {'class': 'a-last'}).find('a')['href'])
        return url
    else:
        return


if __name__ == "__main__":
    while True:
        gather_links_from_csv()
        # Go through all of the CSV file links

        # Start Chrome Driver
        print("Loading... CHROME DRIVER")
        driver_chrome = webdriver.Chrome(
            executable_path=Directory_Driver)
        driver_chrome.get(beginning_url)
        print("CHROME DRIVER - SUCESSFUL")

        for search in List_search_terms:
            url = get_url(search)
            driver_chrome.get(url)

            records = []  # Records for extracting information

            soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')

            results = soup.find_all(
                'div', {'data-component-type': 's-search-result'})
            # print(len(results))

            for item in results:
                records.append(extract_data(item))

            # Searching all pages possible
            while True:
                url = getNextPage(soup)
                if not url:
                    break

                driver_chrome.get(url)
                soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')

                results = soup.find_all(
                    'div', {'data-component-type': 's-search-result'})
                # print(len(results))

                for item in results:
                    records.append(extract_data(item))

            store_records(records, search)  # Put information into csv file

        time.sleep(application_delay)
