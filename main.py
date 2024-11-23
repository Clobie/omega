# main.py

import asyncio
from core.omega import Omega

async def main():
    omega = Omega()
    await omega.run()

asyncio.run(main())