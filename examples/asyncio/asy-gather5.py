
import asyncio
import random
import time

# System call
import os
os.system("")
# Class of different styles
class c():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


async def coro1(n: int) -> str:
    i = random.randint(0, 10)
    print(f"{c.CYAN}task1({n}) sleeping for {i} seconds.{c.RESET}")
    await asyncio.sleep(i)
    result = f"result{n}-1"
    print(f"{c.CYAN}Returning task1({n}) == {result}.{c.RESET}")
    return result

async def coro2(n: int, arg: str) -> str:
    i = random.randint(0, 10)
    print(f"{c.GREEN}task2{n, arg} sleeping for {i} seconds.{c.RESET}")
    await asyncio.sleep(i)
    result = f"result{n}-2 derived from {arg}"
    print(f"{c.GREEN}Returning task2{n, arg} == {result}.{c.RESET}")
    return result

async def chain(n: int) -> None:
    start = time.perf_counter()
    p1 = await coro1(n)
    p2 = await coro2(n, p1)
    end = time.perf_counter() - start
    print(f"--> Chained result{n} => {p2} (took {end:0.2f} seconds).")

async def main(*args):
    try:
        # asyncio.gather() function will wait for a collection of tasks to complete and retrieve all return values.
        # The asyncio.gather() module function allows the caller to group multiple awaitables together.
        # Once grouped, the awaitables can be executed concurrently, awaited, and canceled.
        #
        # The gather() function allows:
        # - Getting results from all grouped awaitables to be retrieved later via the result() method.
        # - The group of awaitables to be canceled via the cancel() method.
        # - Checking if all awaitables in the group are done via the done() method.
        #
        # If any awaitable in aws is a coroutine, it is automatically scheduled as a Task.
        # The first argument is a sequence of coroutines to be executed concurrently.
        # The * operator unpacks the sequence of coroutines into individual arguments, allowing them to be passed to the gather function as separate arguments
        # If return_exceptions is False (default), the first raised exception is immediately propagated to the task that awaits on gather(). Other awaitables in the aws sequence won’t be cancelled and will continue to run.
        # If return_exceptions is True, exceptions are treated the same as successful results, and aggregated in the result list.
        # If gather() is cancelled, all submitted awaitables (that have not completed yet) are also cancelled.
        await asyncio.gather(*(chain(n) for n in args), return_exceptions=False)
    except Exception as e:
        print(f"Exception caught: {e}")

# checks whether the script is being run as the main program
if __name__ == "__main__":
    import sys
    random.seed(54321)
    args = [1, 2, 3] if len(sys.argv) == 1 else map(int, sys.argv[1:])
    # time.perf_counter() statement records the start time of the script
    start = time.perf_counter()
    asyncio.run(main(*args))
    end = time.perf_counter() - start
    print(f"\nProgram finished in {end:0.2f} seconds.")