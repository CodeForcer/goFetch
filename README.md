# goFetch
Pluggable modules for collecting raw crypto orderbook data

The aim of this module is to develop self-contained functions which can be imported into another script. Each function will continuously gather orderbook data from a specific exchange. The functions are designed to be executed through multiprocessing for parralel concurrency.

Each function should take 2 arguments, a list of pairs and a queue. Each function will subscribe to the relevant crypto exchange and begin returning complete orderbook snapshots of the chosen pairs in the format:

book = {'pair name 1':{'bids':[list],'asks':[list]}, 'pair name 2':{'bids':[list],'asks':[list]}, etc...}

Although the overriding format is dictionary based the choice of list objects for the actual bids and asks is for the sake of making quicker analysis possible.

Example function:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def BitfinexBooks(pairs, queue):
  while True:
      # function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
 
Example script utilising such a function:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from goFetch import BitfinexBooks
from multiprocessing import Queue, Process

PAIRS = ['BTCUSD','ETHUSD','ETHBTC']
BitfinexBookOutput = Queue()

getBooks = Process(target=BitfinexBooks, args=(PAIRS, BitfinexBookOutput,))
getBooks.start()

while True:
  print(BitfinexBookOutput.get())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Such a script should continuously print a current snapshot of the Bitfinex orderooks for BTCUSD, ETHUSD & ETHBTC.

It is intended that these functions should be as simple as possible, with no features other than the ability to gather and return orderbooks into a queue at the fastest possible speed. The aim is to develop such functions for as many different cryptocurrency exchanges as possible.
