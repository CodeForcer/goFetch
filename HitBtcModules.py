#!/usr/bin/env python

import aiohttp
import asyncio
import ujson as json

URL = 'wss://api.hitbtc.com/api/2/ws'
SUBSCRIPTION_MESSAGE = '{"method": "subscribeOrderbook","params": {"symbol": "ETHBTC"},"id": 123}'

""" 
Documentation:
https://github.com/hitbtc-com/hitbtc-api/blob/master/APIv2.md#socket-api-reference
"""

async def subscribeAndPush(session, URL, SUBSCRIPTION_MESSAGE):
    async with session.ws_connect(URL) as websocket:
        message = SUBSCRIPTION_MESSAGE
        message = json.loads(message)
        websocket.send_json(message)
        while True:
            input("Press Enter for next snapshot...")  # Debug
            response = await websocket.receive()
            #print(response)  # Debug
            responsejson = json.loads(response.data)
            print(responsejson)

def Driver(URL):
    """
    Main driver function for this script
    """
    async def main(URL):
        async with aiohttp.ClientSession() as session:
            coros = [
                    subscribeAndPush(session, URL, SUBSCRIPTION_MESSAGE)
            ]
            await asyncio.wait(coros)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(URL))

