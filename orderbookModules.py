from multiprocessing import Queue, Process
from Bitfinex.client import BtfxWss
from time import sleep

### This is a script which contains functions and classes for calling and
###  conforming orderbooks through websockets

## API DETAILS AND BOOKS TO FETCH. DICT FORMAT FOR MODULARITY ##
BOOKS = {'Bitfinex':['BTCUSD','ETHUSD','ETHBTC']}
## QUEUES FOR ORDERBOOK OUTPUTS - PUT IN MAIN MODULE FOR DEPLOYMENT##
BFXQueue = Queue()


def BitfinexBooks(PAIRS, queue):
    # Function to instantiate class and subsribe to chosen orderbooks
    def instantiateAndSubscribe(pair):
        bookClass = BtfxWss()
        bookClass.start()
        sleep(2)
        if pair == 'BTCUSD':
            bookClass.subscribe_to_raw_order_book('tBTCUSD')
        elif pair =='ETHUSD':
            bookClass.subscribe_to_raw_order_book('tETHUSD')
        elif pair =='ETHBTC':
            bookClass.subscribe_to_raw_order_book('ETHBTC')
        sleep(1)
        return bookClass
    # Create classes and queues for all our orderbooks
    bookInstances = []
    for pair in PAIRS:
        instance = instantiateAndSubscribe(pair)
        queue = Queue()
        bookInstances.append((pair, instance, queue))
    # Function for building an orderbook from an initial snapshot or updates
    def buildBook(snapshot):
        """
        NOTE: FUNCTION MUST BE UPDATED TO HANDLE UPDATES
        """
        book = {'bids':[],'asks':[]}
        index_bids =0
        index_asks =0
        for i in snapshot[0][0]:
            if i[2] > 0: # Bids
                book['bids'].append({'price':i[1],'amount':i[2],'timestamp':i[0]})
                index_bids +=1
            elif i[2] < 0: # Asks
                book['asks'].append({'price':i[1],'amount':(-1*i[2]),'timestamp':i[0]})
                index_asks +=1
        return book
    #