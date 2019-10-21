import asyncio

loop = asyncio.get_event_loop()

f1 = loop.create_future()


async def asyncx():
    r = await f1
    print('FINISH l1', r)

async def finish():
    print('hello')
    await asyncio.sleep(10)
    print('world')
    await asyncio.sleep(1)
    f1.set_result('DONE')

# asyncio.gather(
#     asyncx(),
#     finish()
# )

loop.run_until_complete(asyncio.gather(
    asyncx(),
    finish()
))
