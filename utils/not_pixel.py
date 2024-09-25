import json
import random
import string
import time
from typing import Union
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from faker import Faker
import requests
from utils.picture_generator import get_need_pixels, position_to_coordinates


class NotPixelBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: Union[str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.ref_token = config.REF_LINK.split('=')[1]
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector,
                                             timeout=aiohttp.ClientTimeout(120))

    async def logout(self):
        await self.session.close()


    async def get_image(self):
        resp = requests.get("https://notpx.app/api/v2/image")
        if resp.ok:
            with open("utils/map.png", "wb") as f:
                f.write(resp.content)


    async def claim_tasks(self):
        tasks = config.TASKS
        for task in tasks:
            resp = await self.session.get(f"https://notpx.app/api/v1/mining/task/check/{task}")
            if resp.status == 200:
                response_data = await resp.json()
                if response_data[task] == True:
                    logger.success(f"Thread {self.thread} | {self.account} | Claimed task {task}")
            await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))


    async def hourly_reward_stats(self) -> bool:
        resp = await self.session.get("https://notpx.app/api/v1/mining/status")
        if resp.status == 200:
            response_data = await resp.json()
            if response_data["fromStart"]>3600:
                return True
        return False


    async def claim_hourly_reward(self):
        if await self.hourly_reward_stats():
            resp = await self.session.get("https://notpx.app/api/v1/mining/claim")
            if resp.status == 200:
                logger.success(f"Thread {self.thread} | {self.account} | Claimed hourly reward!")
            else:
                logger.error(f"Thread {self.thread} | {self.account} | Error {await resp.text()}")


    async def paint_pixel(self):
        if config.PAINT_MY_IMAGE:
            await self.get_image()
            await asyncio.sleep(1)

            pixels = await get_need_pixels()
            if pixels:
                pixel = random.choice(list(pixels.items()))
                pixel_id, color = pixel[0], pixel[1]
            else:
                color = random.choice(["#e46e6e","#FFD635","#7EED56","#00CCC0","#51E9F4"])
                pixel_id = random.randint(1,1000000)
        else:
            color = random.choice(["#e46e6e","#FFD635","#7EED56","#00CCC0","#51E9F4"])
            pixel_id = random.randint(1,1000000)
        data = {
            "pixelId": pixel_id,
            "newColor": color
        }

        resp = await self.session.post("https://notpx.app/api/v1/repaint/start", data=json.dumps(data))
        if resp.status == 200:
            response_data = await resp.json()
            logger.success(f"Thread {self.thread} | {self.account} |{await position_to_coordinates(pixel_id)} Color {color} | Balance {response_data['balance']}")
        else:
            sleep = random.uniform(*config.DELAYS['PAINT_ERROR'])
            logger.info(f"Thread {self.thread} | {self.account} | Can't Paint pixel | Sleep for {sleep} sec")
            await asyncio.sleep(sleep)


    async def buy_upgrades(self):
        if config.BUY_UPGRADES:
            resp = await self.session.get("https://notpx.app/api/v1/mining/boost/check/paintReward")
            if resp.status == 200:
                response_data = await resp.json()
                logger.success(f"Thread {self.thread} | {self.account} | Bought upgrage paintReward")
            
            resp = await self.session.get("https://notpx.app/api/v1/mining/boost/check/reChargeSpeed")
            if resp.status == 200:
                response_data = await resp.json()
                logger.success(f"Thread {self.thread} | {self.account} | Bought upgrage reChargeSpeed")


    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()
        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None
        else:
            logger.success(f"Thread {self.thread} | {self.account} | Logged in")
            self.session.headers['Authorization'] = query
            return True


    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            if not (await self.client.get_me()).username:
                while True:
                    username = Faker('en_US').name().replace(" ", "") + '_' + ''.join(random.choices(string.digits, k=random.randint(3, 6)))
                    if await self.client.set_username(username):
                        logger.success(f"Thread {self.thread} | {self.account} | Set username @{username}")
                        break
                await asyncio.sleep(5)

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('notpixel'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('notpixel'), short_name="app"),
                platform='android',
                write_allowed=True,
                start_param=f'{self.ref_token}'
            ))
            await self.client.disconnect()
            auth_url = web_view.url
            query = f"initData {unquote(auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])}"
            return query
        except:
            return None
