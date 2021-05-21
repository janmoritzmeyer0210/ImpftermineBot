import asyncio
import time

runners = [1, 2, 3, 4]



async def postNumbers():
    for x in range(0, 100):
        print(x)
        await asyncio.sleep(1)

async def startAsync():
    for runner in runners:
        asyncio.create_task(postNumbers())
        await asyncio.sleep(1)

# async def startAsync():
#     asyncio.create_task(postNumbers())
#     while True:
#         await asyncio.sleep(3)
#         asyncio.create_task(postNumbers())

asyncio.run(startAsync())