import asyncio
import logging

import aiongrok

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


async def main():
    sess = aiongrok.Session()

    tunnels = await sess.get_tunnels()
    tun0 = tunnels.any_http_tunnel
    tun1 = tunnels.any_https_tunnel

    print(tun0.public_url)
    print(tun1.public_url)

    print((await sess.get_tunnel(tun0.name)).public_url)
    print((await sess.get_tunnel(tun1.name)).public_url)

    await sess.stop_tunnel(tun0.name)
    await sess.stop_tunnel(tun1.name)

    print((await sess.start_tunnel()).public_url)

    sess.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
