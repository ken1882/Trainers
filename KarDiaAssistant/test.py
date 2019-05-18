import slimeai, slimegrid

AI = slimeai.AI()
grid = slimegrid.Grid()
def mid2dir(mid):
  if mid == 0:
    return 8
  elif mid == 1:
    return 2
  elif mid == 2:
    return 4
  elif mid == 3:
    return 6
  return -1
grid.setGridA([
  4,2,4,2,
  2,4,2,4,
  4,2,4,8,
  2,4,2,4
])
print(grid)
bdir = AI.getMove(grid)
print("best:", bdir)
grid.move(bdir)
print(grid)