import asyncio
from infocar import InfoCar
import time
import argparse


async def initialize() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--Token", help="Telegram Token. Leave empty if You don't have it")
    parser.add_argument("-i", "--Id", help="Telegram chat bot ID. Leave empty if You don't have it")
    parser.add_argument("-l", "--Login", help="Infocar.pl login")
    parser.add_argument("-p", "--Password", help="Infocar.pl password")
    args = parser.parse_args()

    infocar = InfoCar(args.Token, args.Id, args.Login, args.Password)
    infocar.login()
    while (True):
        infocar.check_term()
        await infocar.verify_dates(number_of_days=14)
        time.sleep(10)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(initialize())
