from time import sleep, time
import asyncio

async def f1():
  print("f1-1-blocking")
  sleep(1) # blocking
  print("f1-2-external-call")
  await asyncio.sleep(5) # yilds control to another coroutine
  print("f1-3-blocking")
  sleep(1)
  return "f1-result"
  
  
async def f2():
  print("f2-1-blocking")
  sleep(1)
  print("f2-2-external-call")
  await asyncio.sleep(5) # yields control to another coroutine
  print("f2-3-blocking")
  sleep(1)
  return "f2-result"
  
async def f3():
  print("f3-1-blocking")
  sleep(1)
  print("f3-2-external-call")
  await asyncio.sleep(5) # yields control to another coroutine
  print("f3-3-blocking")
  sleep(1)
  return "f3-result"
  
async def main():
  r1, r2, r3 = await asyncio.gather(f2(), f3(), f1())
  print(r1, r2, r3)
  return
  

if __name__ == '__main__':
  print('Running asyncio test')
  start_time = time()  
  asyncio.run(main())
  elapsed_time = time() - start_time
  print('Done in {:.1f}s'.format(elapsed_time))
  
