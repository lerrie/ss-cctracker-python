import os
import requests
import json
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_exchanges():
    
    exchanges = ()
    quote_url = os.getenv('BASE_URL') + '/v1/exchange/map'
    HEADER = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CC_ACCESS_TOKEN')
    }
    try:
        request = requests.get(quote_url, headers=HEADER)
        results = request.json()

        exchanges_list = []
        data = results['data']
        for exchange in data:
            exhange_name = ( exchange['name'], exchange['name'] )
            exchanges_list.append(exhange_name)
        exchanges = tuple(exchanges_list)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return exchanges

def get_coins():
    
    coins = ()
    quote_url = os.getenv('BASE_URL') + '/v1/cryptocurrency/map'
    HEADER = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CC_ACCESS_TOKEN')
    }
    try:
        request = requests.get(quote_url, headers=HEADER)
        results = request.json()

        coins_list = []
        data = results['data']
        for coin in data:
            coin_symbol = ( coin['symbol'], coin['symbol'] )
            coins_list.append(coin_symbol)
        coins = tuple(coins_list)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return coins

def get_coin_latest_price(coin_symbol):
    price = 0
    quote_url = os.getenv('BASE_URL') + '/v1/cryptocurrency/quotes/latest?convert=' + os.getenv('LOCAL_CURRENCY') + '&symbol=' + coin_symbol
    HEADER = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CC_ACCESS_TOKEN')
    }
    try:
        request = requests.get(quote_url, headers=HEADER)
        results = request.json()

        currency = results['data'][coin_symbol]
        quote = currency['quote'][os.getenv('LOCAL_CURRENCY')]
        price = float(quote['price'])
        
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return price
