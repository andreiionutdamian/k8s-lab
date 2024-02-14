from time import sleep, time
import asyncio

SLEEPS = [1,1,5,1,1]

async def sleeper(time, name):
  print(f"{name} working for {time} seconds")
  await asyncio.sleep(time)
  return

async def f1():
  print("calling f1-1-blocking")
  sleep(SLEEPS[0]) # blocking
  print("calling f1-2-blocking")
  sleep(SLEEPS[1]) # blocking
  print("calling f1-external-call")
  await sleeper(SLEEPS[2], "f1") #asyncio.sleep(5) # yilds control to another coroutine
  print("calling f1-3-blocking")
  sleep(SLEEPS[3])
  print("calling f1-4-blocking")
  sleep(SLEEPS[4])
  return "f1-result"
  
  
async def f2():
  print("calling f2-1-blocking")
  sleep(SLEEPS[0]) # blocking
  print("calling f2-2-blocking")
  sleep(SLEEPS[1]) # blocking
  print("calling f2-external-call")
  await sleeper(SLEEPS[2], "f2") #await asyncio.sleep(5) # yields control to another coroutine
  print("calling f2-3-blocking")
  sleep(SLEEPS[3])
  print("calling f2-4-blocking")
  sleep(SLEEPS[4])
  return "f2-result"
  
async def f3():
  print("calling f3-1-blocking")
  sleep(SLEEPS[0])
  print("calling f3-2-blocking")
  sleep(SLEEPS[1])
  print("calling f3-external-call")
  await sleeper(SLEEPS[2], "f3") #await asyncio.sleep(5) # yields control to another coroutine
  print("calling f3-3-blocking")
  sleep(SLEEPS[3])
  print("calling f3-4-blocking")
  sleep(SLEEPS[4])
  return "f3-result"
  
async def main():
  r1, r2, r3 = await asyncio.gather(f1(), f2(), f3(),)
  print(r1, r2, r3)
  return
  

if __name__ == '__main__':
  print('Running asyncio test...')
  start_time = time()  
  asyncio.run(main())
  elapsed_time = time() - start_time
  print('Done in {:.1f}s vs {:.1f}s'.format(elapsed_time, 3 * sum(SLEEPS)))
  
