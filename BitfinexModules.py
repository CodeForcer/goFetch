import asyncio
import aiohttp
import ujson as json
from copy import deepcopy
import time
from multiprocessing import Process, Queue

async def subscribeAndPush(pair, queue, session, save='No',queue2=None):
    """
    Handles basic websocket interaction for a given currency pair on Bitfinex
    
    Arguments:-
        pair (string): The currency pair to subscribe to
        queue (queue class): The queue to push the orderbook into
        session (session class): Aiohttp coroutine
        save (string): Whether to save the orderbook output to a file
        queue2 (queue class): An optional queue to push the server data
            in for debugging the orderbook
    """
    async with session.ws_connect('wss://api.bitfinex.com/ws/2') as websocket:
        connection_message = await websocket.receive() # Ignore connection message 
        # Template for the subscription message
        message_start = '{"event": "subscribe","channel": "book","symbol": "'
        message_end   = '","prec": "P0","freq": "F0","len": 25}'       
        # format the pair for update and complete the subscription message   
        message = message_start + str(pair) + message_end
        message = json.loads(message)
        await websocket.send_json(message)
        book = {'bids':{},'asks':{}}
        while True:
            response = await websocket.receive()
            responsejson = json.loads(response.data)
            if type(responsejson) ==list:
                book = deepcopy(buildBook(book, responsejson))
                if queue2!=None:
                    queue2.put(responsejson) # Debug queue
                queue.put(book) # Main book queue
                if save=='Yes':
                    csv_format = deepcopy(bookDictToList(book))
                    saveBook(csv_format, 'Bitfinex_'+str(pair)+'.csv')

def buildBook(book, updates):
    if type(updates[1][1])==str:
        # Heartbeat messages
        pass
    elif len(updates[1])>10:
        # Initial snapshot
        for i in updates[1]:
            if i[2] > 0: # Bids
                level = {'amount':i[2]}                
                book['bids'].update({i[0]:level})
            elif i[2] < 0: # Asks
                level = {'amount':(-1*i[2])}
                book['asks'].update({i[0]:level})
    elif len(updates[1])<10:
        # Updates
        if updates[1][1]==0:
            # remove from book
            if updates[1][2]==1:
                # remove from bids
                book['bids'].pop(updates[1][0])
            if updates[1][2]==-1:
                # remove from asks
                book['asks'].pop(updates[1][0])
        elif updates[1][1]>0:
            if updates[1][2]>0:
                # update bids
                level = {'amount':updates[1][2]}
                book['bids'].update({updates[1][0]:level})
            elif updates[1][2]<0:
                # update asks
                level = {'amount':(updates[1][2]*-1)}
                book['asks'].update({updates[1][0]:level})
    return book

def bookDictToList(book):
    """
    Takes the above dict format for the orderbook and returns it in list format
    """
    output = {'bids':[],'asks':[]}
    for i in book['bids']:
        append = [i,book['bids'][i]['amount']]
        output['bids'].append(append)
    for i in book['asks']:
        append = [i,book['asks'][i]['amount']]
        output['asks'].append(append)
    return output

def saveBook(book, filename):
    """
    This function will take an orderbook in the following format:
        {'bids':[[price,amount],....],'asks':[[price,amount],....]}
        
    And append the data to the chosen csv file with the following columns:
        time | bid/ask | price | amount
    """
    timestamp = time.time()
    csv = open(filename,'a')
    
    for i in book['bids']:
        fields = [str(timestamp),str(1),str(i[0]),str(i[1])]
        csv.seek(0,2)
        csv.writelines("\r")
        csv.writelines( (',').join(fields))
    for i in book['asks']:
        fields = [str(timestamp),str(0),str(i[0]),str(i[1])]
        csv.seek(0,2)
        csv.writelines("\r")
        csv.writelines( (',').join(fields))    


def Bitfinex(pairs_queues, save='No'):
    """
    Main driver function for this script
    
    Arguments:-
        pairs_queues (list): contains pairs of currencies with an associated
            queue.
        save (str): Either Yes/No or raw, saves data to file
    """
    async def main(pairs_queues, save):
        async with aiohttp.ClientSession() as session:
            coros = [
                    subscribeAndPush(pair[0], pair[1], session, save, None)
                    for pair in pairs_queues
            ]
            await asyncio.wait(coros)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(pairs_queues,save))        
    
if  __name__ == "__main__":
    PAIRS = [
        'BTCUSD',
        'ETCBTC',
         'ETCUSD',
         'ETHBTC',
         'ETHUSD',
        # 'XMRBTC',
        # 'XMRUSD',
        # 'ZECBTC',
        # 'ZECUSD'
    ]
    pairs_queues=[]
    for pair in PAIRS:
        queue = Queue()
        pairs_queue = [pair,queue]
        pairs_queues.append(pairs_queue)
    save='Yes'
    p=Process(target=Bitfinex, args=(pairs_queues,save,))
    p.start()
    