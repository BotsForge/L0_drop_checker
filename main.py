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


def get_my_wallets():
    with open('wallets.txt') as file:
        wallets = [i.strip().lower() for i in file.readlines() if i.strip()]
    return wallets


def check_wallet(wallet):
    url = f'https://www.layerzero.foundation/api/allocation/{wallet}'

    r = session.get(url).json()

    if amount := int(r.get('zroAllocation', {}).get('asBigInt', 0)):
        amount = round(amount / 10 ** 18, 2)
        logger.success(f"{wallet} --> {amount} ZRO")
    else:
        logger.error(f"{wallet} --> not eligible")

    return amount


def main():
    wallets = get_my_wallets()
    logger.info(f"total wallets = {len(wallets)}")

    total = 0
    for wallet in wallets:
        total += check_wallet(wallet)
        sleep(0.1)

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
