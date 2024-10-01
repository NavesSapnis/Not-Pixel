import random
import time
from typing import Union
from utils.not_pixel import NotPixelBot
from asyncio import sleep
from random import uniform
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio
from aiohttp.client_exceptions import ContentTypeError
import xlsxwriter
import os


async def start(thread: int, session_name: str, phone_number: str, proxy: Union[str, None]):
    not_pixel = NotPixelBot(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))
    
    logged = False
    while not logged:
        try:
            await not_pixel.login()
            await not_pixel.buy_upgrades()
            await not_pixel.claim_tasks()
            start_time = time.time()
            logged = True
        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e} | Sleep for 10 sec.")
            await asyncio.sleep(5)

    relogin = random.uniform(*config.DELAYS['RELOGIN'])
    while True:
        try:
            if time.time()-start_time>relogin:
                await sleep(uniform(2, 8))
                await not_pixel.login()
                await not_pixel.buy_upgrades()
                await not_pixel.claim_tasks()
                start_time = time.time()


            await not_pixel.claim_hourly_reward()
            await sleep(uniform(2, 8))

            await not_pixel.paint_pixel()
            await sleep(uniform(2, 8))

            await sleep(60)
        except ContentTypeError as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(NotPixelBot(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['id', 'firstName', 'balance', 'isBetaTester', 'friends']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")