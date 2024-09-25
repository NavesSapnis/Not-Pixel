# api id, hash
API_ID = 1234
API_HASH = '1234'

REF_LINK = 'https://t.me/notpixel/app?startapp=f720116934'

PAINT_MY_IMAGE = False # if you have image that you need to paint. You'll need map picture 1000x1000
X = range(453,582) # start/end x in your map picture
Y = range(771,878) # start/end y in your map picture
BUY_UPGRADES = True # auto buy

TASKS = ["channel:notcoin","channel:notpixel_channel","joinSquad","leagueBonusSilver","x:notcoin","x:notpixel","paint20pixels"]

DELAYS = {
    "RELOGIN": [1800, 3600],  # relogin delay
    'ACCOUNT': [3, 7],  # delay between connections to accounts (the more accounts, the longer the delay)
    'PAINT_ERROR': [400, 500], # delay while paint
    'TASK':[1,3]
}

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "http",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
