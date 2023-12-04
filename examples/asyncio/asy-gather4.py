import asyncio
# pprint: module provides a capability to "pretty-print" arbitrary Python data structures in a form which can be used as input to the interpreter
from pprint import pprint

import random


async def task_coro(tag):
    print("> task", tag)
    await asyncio.sleep(random.uniform(1, 3))
    print("< task", tag)
    return tag


loop = asyncio.get_event_loop()

# many Coroutines in a List
# create a list of tasks in group 1
group1 = asyncio.gather(*[task_coro("group 1.{}".format(i)) for i in range(1, 6)])
# create a list of tasks in group 2
group2 = asyncio.gather(*[task_coro("group 2.{}".format(i)) for i in range(1, 4)])
# create a list of tasks in group 3
group3 = asyncio.gather(*[task_coro("group 3.{}".format(i)) for i in range(1, 10)])

all_groups = asyncio.gather(group1, group2, group3)

results = loop.run_until_complete(all_groups)

loop.close()

pprint(results)