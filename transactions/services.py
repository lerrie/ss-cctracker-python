import os
import requests
import json
from operator import itemgetter
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def get_exchanges():
    
    exchanges = ()
    quote_url = os.getenv('BASE_URL') + '/v1/exchange/map?sort=volume_24h'
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
        exchanges_list.sort(key=itemgetter(1))
        exchanges = tuple(exchanges_list)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return exchanges

def get_coins():
    
    coins = ()
    quote_url = os.getenv('BASE_URL') + '/v1/cryptocurrency/map?sort=cmc_rank'
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
        coins_list.sort(key=itemgetter(1))
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

def get_latest():
    latest_list = ()
    quote_url = os.getenv('BASE_URL') + '/v1/cryptocurrency/listings/latest?convert=' + os.getenv('LOCAL_CURRENCY') + '&sort=market_cap'
    HEADER = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CC_ACCESS_TOKEN')
    }
    try:
        request = requests.get(quote_url, headers=HEADER)
        results = request.json()

        latest = []
        data = results['data']
        for coin in data:
            symbol = coin['symbol']
            quote = coin['quote'][os.getenv('LOCAL_CURRENCY')]

            hour_change = round(quote['percent_change_1h'],2)
            day_change = round(quote['percent_change_24h'],2)
            week_change = round(quote['percent_change_7d'],2)

            market_cap = quote['market_cap']
            volume = quote['volume_24h']
            price = quote['price']

            coin_latest = ( symbol, price, market_cap, volume, hour_change, day_change, week_change )
            latest.append(coin_latest)
        latest_list = tuple(latest)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return latest_list