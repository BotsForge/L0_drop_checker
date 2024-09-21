# pyinstaller -n "L0_drop_checker" -F -i "../BF.ico" --add-data "../BF.ico;." main.py

import sys
import ctypes
from time import sleep
import traceback

from loguru import logger
import requests

from utils import LOGO


logger.remove(0)
logger.add(sys.stderr, level='DEBUG', colorize=True, format="{time:HH:mm:ss}<level> | {level: <7} | {message}</level>",)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Priority': 'u=1, i',
    'Referer': 'https://www.layerzero.foundation/eligibility',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
}

session = requests.Session()
session.headers.update(headers)


def get_rnd_proxy():
    with open('proxies.txt') as file:
        proxies = [i.strip() for i in file.readlines() if i.strip()]
    while True:
        for proxy in proxies:
            proxy = {'http': f"http://{proxy}", 'https': f"http://{proxy}"}
            yield proxy
        yield None


Proxy = get_rnd_proxy()


def get_my_wallets():
    with open('wallets.txt') as file:
        wallets = [i.strip().lower() for i in file.readlines() if i.strip()]
    unique = []
    for wallet in wallets:
        if wallet not in unique:
            unique.append(wallet)
    return unique


def check_wallet(wallet):
    url = f'https://www.layerzero.foundation/api/allocation/{wallet}'
    url = f"https://www.layerzero.foundation/api/proof/{wallet}"

    session.proxies = next(Proxy)

    r = session.get(url)
    # print(r.text)
    r = r.json()
    # print(r)

    if amount := int(r.get('amount', 0)):
        amount = round(amount / 10 ** 18, 2)
        logger.success(f"{wallet} --> {amount} ZRO")
    else:
        logger.error(f"{wallet} --> not eligible")

    return amount


def main():
    wallets = get_my_wallets()
    logger.info(f"total wallets = {len(wallets)}")

    total = 0
    amount_good = 0
    for wallet in wallets:
        try:
            if amount := check_wallet(wallet):
                total += amount
                amount_good += 1

        except Exception as er:
            logger.warning(f"{wallet} --> {er}")
        # sleep(0.1)

    print(amount_good)
    if total:
        logger.success(f"Total drop amount = {round(total, 2)} ZRO")
    else:
        logger.warning(f"Your have not eligible wallets")


if __name__ == '__main__':
    ctypes.windll.kernel32.SetConsoleTitleW('L0_drop_checker')
    print(LOGO)
    try:
        main()
    except Exception as er:
        logger.warning(er)
        logger.debug(traceback.format_exc())
    finally:
        input('Press <Enter> to close...')
