# -*-coding: utf-8 -*-


import asyncio


@asyncio.coroutine
def wait_and_resolve_furture(future):
    for i in range(3):
        print("Sleep 1 second")
        yield from asyncio.sleep(1)

    future.set_result('Furture is done')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    future = asyncio.Future()
    asyncio.Task(wait_and_resolve_furture(future))

    loop.run_until_complete(future)
    print(future.result())
