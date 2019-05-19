import slimeai, slimegrid
import time, threading

cnt = 0
def test(n=5):
  global cnt
  for _ in range(n):
    cnt += 1
    time.sleep(1)

th = threading.Thread(target=test)
th.start()

for i in range(8):
  print(i, cnt)
  i += 1
  time.sleep(1)