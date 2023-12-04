import asyncio
# pprint: module provides a capability to "pretty-print" arbitrary Python data structures in a form which can be used as input to the interpreter
from pprint import pprint

import random


async def task_coro(tag):
    print("> task", tag)
    await asyncio.sleep(random.uniform(1, 3))
    print("< task", tag)
    return tag

# coroutine usate for entry point
async def main():
    # create a list of tasks in group 1
    group1 = asyncio.gather(task_coro(1),task_coro(2), task_coro(3))
    # create a list of tasks in group 2
    group2 = asyncio.gather(task_coro(4),task_coro(5))
    # create a list of tasks in group 3
    group3 = asyncio.gather(task_coro(6),task_coro(7), task_coro(8))
    group4 = asyncio.gather(group1, group2, group3)
    results= await group4
    pprint(results)
    print('main completed!')
    
# start the asyncio program
asyncio.run(main())