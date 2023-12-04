import asyncio 

# task coroutine.
async def task_coro(): 
    print("Hey....") 

    # asyncio.sleep: to delay of 1 second the execution of print statement below it
    # sleep() always suspends the current task
    await asyncio.sleep(1) 
    print("I am here...") 


# main() function that executes task_coro() 3 times using asyncio.gather().
async def main():
    try:
       await asyncio.gather(task_coro(), task_coro(), task_coro())
    except Exception as e:
        print(f"Exception caught: {e}")
    
if __name__ == "__main__":
    # calculates the time taken to execute the async functions and print to the console
    import time
    start = time.perf_counter()
    # asyncio.run: to run the top-level entry point "main()" function 
    asyncio.run(main())
    elapsed = time.perf_counter() - start
    print(f"\n File executed in: {elapsed:0.2f} seconds")