
import json
from tf2sku.skufy import SKU
import requests

price_list = {}

test_rates = {
    "metalPrice": [0.024, 0.025],
    "keyPrice": [69.66, 69.77],
    "hatPrice": [1.33, 1.44]
}

address = 'https://backpack.tf/api/'
KEY = '[INSERT BACKPACK.TF API KEY HERE]'

params = {
    'scope': 'read write',
    'key': KEY
}

def get_currencies():
    currency_req = access_api('IGetCurrencies/v1', address, params = params)
    # convert string response to dictionary
    currency_dict = currency_req['response']['currencies']
    metal_to_usd = (currency_dict['metal']['price']['value'], currency_dict['metal']['price']['value_high'])
    keys_to_metal = (currency_dict['keys']['price']['value'], currency_dict['keys']['price']['value_high'])
    hat_to_metal = (currency_dict['hat']['price']['value'], currency_dict['hat']['price']['value_high'])
    return {'metalPrice': metal_to_usd, 'keyPrice': keys_to_metal, 'hatPrice': hat_to_metal}

def access_api(target, address, params):
    target_add = address + target
    request = requests.get(target_add, params=params)
    try:
        data = json.loads(request.text)
        print(json.loads(request.text))
    except TypeError:
        return f'Error accessing {target}'
    return data

def pricelist_update(priceDict, itemInfo):
    sku = SKU.fromitem(itemInfo)
    # some of these price dictionaries are stored as single-item lists. No idea why
    if type(priceDict) == list:
        number = priceDict[0]['value']
        currency = priceDict[0]['currency']
    else:
        number = priceDict['value']
        currency = priceDict['currency']
    price = convert_to_money(number, currency, test_rates, True)
    price_list[sku] = price


def convert_to_money(val, currency, rates, buying=False):
    # If you're buying, you want the lowest price for metal
    if buying == True:
        price_index = 0
    else:
        price_index = 1
    if currency == None:
        dollar_cost = 0
        return dollar_cost
    if currency == 'metal':
        dollar_cost = rates['metalPrice'][price_index] * val
        return dollar_cost
    if currency == ('key' or 'keys'):
        metal_cost = rates['keyPrice'][price_index] * val
        dollar_cost = rates['metalPrice'][price_index] * metal_cost
        return dollar_cost
    if currency == 'hat':
        metal_cost = rates['hatPrice'][price_index] * val
        dollar_cost = rates['metalPrice'][price_index] * metal_cost
        return dollar_cost

def parse_bp_pricelist(bp_dictionary):
    # For each item with a name,
    for name, dict in bp_dictionary['response']['items'].items():
        # get the SKU, name, and price from every item
        # First, compile the SKU
        if len(dict['defindex']) == 0:
            continue
        def_index = dict['defindex'][0]
        # For each quality of an item,
        for quality, item in dict['prices'].items():
            # set individual characteristics
            SKU_dict = {}
            template = SKU.matchtemplate(SKU_dict)
            SKU_dict['defindex'] = def_index
            SKU_dict['quality'] = quality
            # If the item is unusual (quality 5), it comes with the prices of all of its possible effects
            if quality == '5':
                # Some items are unusual but do not have any effects. They have only one price.
                for craft_key, tradable_item in item['Tradable'].items():
                    if type(tradable_item) == list:
                        pricelist_update(tradable_item, SKU_dict)
                    else:
                        # Otherwise, iterate over the effects and update pricelist for each
                        for effect, price_info in tradable_item.items():
                            SKU_dict['effect'] = effect
                            SKU_dict['craftable'] = (craft_key == 'Craftable')
                            pricelist_update(price_info, SKU_dict)
            for craft_key, items in item['Tradable'].items():
                SKU_dict['craftable'] = (craft_key == 'Craftable')
                if type(items) == list:
                    pricelist_update(items, SKU_dict)
                    continue
                try:
                    pricelist_update(item['Tradable'][craft_key], SKU_dict)
                except KeyError:
                    for effect, price_info in tradable_item.items():
                        SKU_dict['effect'] = effect
                        SKU_dict['craftable'] = (craft_key == 'Craftable')
                        pricelist_update(price_info, SKU_dict)
    return price_list