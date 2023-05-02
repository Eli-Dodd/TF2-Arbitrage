from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import json

import time

# USE THIS CHROME WEBDRIVER. Modified and added to PATH.
# https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver
options = Options()
# These are options to pass to the webdriver
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_argument(r"put-the-path-to-the-chrome-driver-here")
browser = webdriver.Chrome(options=options)

targetList = {
    'normalHats': 'stype=Hat&ssortfield=min_price&ssortdir=1',
    'strangeHats': 'squality=11&stype=Hat&ssortfield=min_price&ssortdir=1',
    'killstreaks': 'skillstreak=1&ssortfield=min_price&ssortdir=1',
    'uncraftableHats': 'stype=Hat&scraftable=0&ssortfield=min_price&ssortdir=1'

}

def scrape(targetList = targetList):
    address = 'https://marketplace.tf/browse/tf2?'
    priceList = {}
    for name, target in targetList.items():
        browser.get(address + target)
        # get a list of each 'card' in the target address
        cardList = browser.find_elements(By.CSS_SELECTOR, '#all-items .item-box.appid-440')
        for card in cardList:
            # Look for the href in each .item-box-name-link to do regex on it and get the SKU
            linkThing = card.find_element(By.CLASS_NAME, 'item-box-name-link').get_attribute('href')
            SKU = re.search(r'tf2\/(.*)', linkThing).group(1)
            # Look for the price
            name = card.find_element(By.CSS_SELECTOR, '.item-box-name .inner-name').text
            price = card.find_element(By.CLASS_NAME, 'item-box-price').text
            priceNum = float(price[1:])
            print(SKU + ' ' + str(priceNum))
            priceList[SKU] = priceNum
    return priceList

prices = scrape()
# write the card to a file for examination
outputFile = open('MarketplaceList.json', 'w')
print(prices)
priceListJSON = json.dumps(prices)
outputFile.write(priceListJSON)
