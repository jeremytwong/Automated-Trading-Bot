import requests
import time
import hmac
import hashlib
from datetime import datetime, timedelta


class BinanceClient:
    def __init__(self):
        self.api_key = ''
        self.api_secret = ''
        self.base_url = "https://testnet.binancefuture.com"
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def generate_signature(self, params):
        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        params['signature'] = signature.hexdigest()
        return params
    
    def check_open_orders(self):
        timestamp = int(time.time() * 1000)
        params = {
            'timestamp': timestamp
        }
        params = self.generate_signature(params)
        try:
            response = self.session.get(self.base_url + "/fapi/v1/openOrders", params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
    
    def check_open_orders(self):
        timestamp = int(time.time() * 1000)
        params = {
            'timestamp': timestamp
        }
        params = self.generate_signature(params)
        try:
            response = self.session.get(self.base_url + "/fapi/v1/openOrders", params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def place_order(self, symbol, side, type, timeInForce, quantity, price):
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': timeInForce,
            'quantity': quantity,
            'price': price,
            'timestamp': timestamp
        }
        params = self.generate_signature(params)
        try:
            response = self.session.post(self.base_url + "/fapi/v1/order", params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def cancel_order(self, symbol, orderId):
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': symbol,
            'orderId': orderId,
            'timestamp': timestamp
        }
        params = self.generate_signature(params)
        try:
            response = self.session.delete(self.base_url + "/fapi/v1/order", params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_historical_klines(self, symbol, interval, start_time, end_time):
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time
        }

        response = requests.get(self.base_url + "/fapi/v1/klines", headers=self.headers, params=params)
        klines = response.json()
        closing_prices = [float(kline[4]) for kline in klines]

        return closing_prices
        
    def calculate_ema(self, data, window):
        if len(data) < 2 * window:
            raise ValueError("Data is too short")
        c = 2.0 / (window + 1)
        current_ema = sum(data[:window]) / window
        for value in data[window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema

    def calculate_dema(self, data, window):
        ema = self.calculate_ema(data, window)
        ema_of_ema = self.calculate_ema([ema for _ in range(window)] + list(data[window:]), window)
        dema = 2 * ema - ema_of_ema
        return dema

    def backtest(self, symbol, interval, start_time, end_time, window = 4, threshold = 0.01, closing_prices=None):
        if closing_prices is None:
            closing_prices = self.get_historical_klines(symbol, interval, start_time, end_time)

        balance = 100.0 
        position = 0.0  
        buy_price = 0.0  

        for i in range(window, len(closing_prices)):
            dema = self.calculate_dema(closing_prices, window)
            
            if closing_prices[i] > dema * (1 - threshold) and position == 0:
                buy_price = closing_prices[i]
                position = balance / buy_price
                balance = 0.0
                #print(f"Bought at {buy_price}")

            elif closing_prices[i] < dema and position > 0:
                sell_price = closing_prices[i]
                balance = position * sell_price
                position = 0.0
                #print(f"Sold at {sell_price}")

        total_value = balance + position * closing_prices[-1]
        print(f"Total balance: {total_value}")
        return(total_value)
    
    def optimize(self, symbol, interval, start_time, end_time, window_range, threshold_range):
        max_gain = 0
        best_window = 0
        best_threshold = 0

        closing_prices = client.get_historical_klines(symbol, interval, start_time, end_time)

        for window in window_range:
            for threshold in threshold_range:
                print(f"Testing window: {window}, threshold: {threshold}")
                total_value = self.backtest(symbol, interval, start_time, end_time, window, threshold, closing_prices)
                if total_value > max_gain:
                    max_gain = total_value
                    best_window = window
                    best_threshold = threshold

        print(f"Max gain: {max_gain} with window: {best_window} and threshold: {best_threshold}")

    def run(self, symbol, interval, window=4, threshold=0.01, profit_threshold=0, sleep_timer=6):
        bought_price = None
        quantity = 0.5

        while True:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(minutes=60)).timestamp() * 1000)

            closing_prices = self.get_historical_klines(symbol, interval, start_time, end_time)
            dema = self.calculate_dema(closing_prices, window)

            if bought_price is None and closing_prices[-1] > dema * (1 - threshold):
                bought_price = closing_prices[-1]
                self.place_order(symbol, 'BUY', 'LIMIT', 'GTC', quantity, bought_price)
                print(f"Buying {symbol} now at {bought_price} and at {datetime.now()}")
            elif bought_price is not None and closing_prices[-1] > bought_price * (1 + profit_threshold):
                self.place_order(symbol, 'SELL', 'LIMIT', 'GTC', quantity, closing_prices[-1])
                print(f"Selling {symbol} now at {closing_prices[-1]} and at {datetime.now()}")
                bought_price = None  # Reset the bought price
            else:
                print(f"Not buying or selling {symbol} now.")

            time.sleep(sleep_timer)

client = BinanceClient()
client.run('BTCUSDT', '1m', 6, 0.01, 2)

#Optimization ---------------------------------------------------------------
#end_time = int(datetime.now().timestamp() * 1000)
#start_time = int((datetime.now() - timedelta(minutes=1000)).timestamp() * 1000)
#window_range = range(2, 12)
#threshold_range = [0.01 * i for i in range(1, 5)]
#client.optimize('BTCUSDT', '5m', start_time, end_time, window_range, threshold_range)

