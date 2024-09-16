import random
import time
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


async def start(thread: int, session_name: str, phone_number: str, proxy: list[str, None]):
    not_pixel = NotPixelBot(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))
    
    await not_pixel.login()
    start_time = time.time()

    relogin = random.uniform(*config.DELAYS['RELOGIN'])
    while True:
        try:
            if time.time()-start_time>relogin:
                await not_pixel.logout()
                await sleep(uniform(2, 8))
                await not_pixel.login()
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

