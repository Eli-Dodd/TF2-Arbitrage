import json
import datagrab

# NEEDED PARAMS: {'scope': 'read write', 'key': KEY} then, POST or GET depending on what endpoint
CLIENT_ID = ''
CLIENT_SECRET = ''

# Backpack.tf

# API Key
KEY = '[BACKPACK.TF API KEY]'

params = {
    'scope': 'read write',
    'key': KEY
}

currency_conversion = open('bpCurrencies.json', 'r')
conversion_dict = json.loads(currency_conversion.read())
backpack_prices = open('backpackPriceList.json', 'r')
bp_price_dict = json.loads(backpack_prices.read())
bp_prices = datagrab.parse_bp_pricelist(bp_price_dict)
marketplace_prices = open('MarketplaceList.json', 'r')
m_prices = json.loads(marketplace_prices.read())


def refresh_currencies():
    currencies = open('bpCurrencies.json', 'w')
    data = json.dumps(datagrab.get_currencies())
    currencies.write(data)


def compare_prices(buying, selling):
    count = 0
    deals = []
    # For every item, find the same SKU price in the other dictionary
    for sku, price in buying.items():
        buy_price = buying[sku]
        try:
            sell_price = selling[sku]
        except KeyError:
            print('None Found ' + str(count))
            continue
        if buy_price < sell_price:
            print(str(buy_price) + ' < ' + str(sell_price) + ' , ' + str(count))
            deals.append(sku)
        else:
            print('No deal! ' + str(count))
        count += 1
    return deals

deals = compare_prices(m_prices, bp_prices)
print(deals)



