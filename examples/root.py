import asyncio
import json
import logging

import aiongrok

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


async def main():
    async with aiongrok.Session() as sess:
        root = await sess.get_root()
    print(json.dumps(root, sort_keys=4, indent=True))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
