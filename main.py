# main.py

import asyncio
from core.omega import omega

async def main():
    await omega.run()

asyncio.run(main())