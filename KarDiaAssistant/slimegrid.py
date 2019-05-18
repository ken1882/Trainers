from copy import deepcopy

directionVectors = (UP_VEC, DOWN_VEC, LEFT_VEC, RIGHT_VEC) = ((-1, 0), (1, 0), (0, -1), (0, 1))
vecIndex = [UP, DOWN, LEFT, RIGHT] = range(4)

def xrange(*args):
    return range(*args)

class Grid:
    def __init__(self, size = 4):
        self._iterX = 0
        self.size = size
        self.map = [[0] * self.size for i in xrange(self.size)]

    def __getiem__(self, indeices):
        y, x = indeices
        return self.map[y][x]
    def __setitem__(self, indeices, value):
      y, x = indeices
      self.map[y][x] = value
    
    def __iter__(self):
        self._iterX = 0
        return self

    def __next__(self):
        if self._iterX < self.size * self.size:
            re = self.map[self._iterX // self.size][self._iterX % self.size]
            self._iterX += 1
            return re
        else:
            raise StopIteration

    def __str__(self):
        re = ""
        for i in range(self.size):
            for j in range(self.size):
                re += "{:>6}".format(self.map[i][j])
            re += '\n'
        return re

    def grids(self, flatten=False):
        if flatten:
            return [self.map[j][i] for j in range(self.size) for i in range(self.size)]
        else:
            return self.map

    def setGrid(self, _grid):
        for i in range(4):
            for j in range(4):
                self.map[i][j] = _grid[i][j]

    def setGridA(self, _grid):
        for i in range(4):
            for j in range(4):
                self.map[i][j] = _grid[i*4+j]
                
    # Make a Deep Copy of This Object
    def clone(self):
        gridCopy = Grid()
        gridCopy.map = deepcopy(self.map)
        gridCopy.size = self.size

        return gridCopy

    # Insert a Tile in an Empty Cell
    def insertTile(self, pos, value):
        self.setCellValue(pos, value)

    def setCellValue(self, pos, value):
        x, y = pos
        self.map[x][y] = value

    # Return All the Empty c\Cells
    def getAvailableCells(self):
        cells = []

        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.map[x][y] == 0:
                    cells.append((x,y))

        return cells

    # Return the Tile with Maximum Value
    def getMaxTile(self):
        maxTile = 0

        for x in xrange(self.size):
            for y in xrange(self.size):
                maxTile = max(maxTile, self.map[x][y])

        return maxTile

    # Check If Able to Insert a Tile in Position
    def canInsert(self, pos):
        return self.getCellValue(pos) == 0

    # Move the Grid
    def move(self, dir):
        dir = int(dir)

        if dir == UP:
            return self.moveUD(False)
        if dir == DOWN:
            return self.moveUD(True)
        if dir == LEFT:
            return self.moveLR(False)
        if dir == RIGHT:
            return self.moveLR(True)

    # Move Up or Down
    def moveUD(self, down):
        r = range(self.size -1, -1, -1) if down else range(self.size)

        moved = False

        for j in range(self.size):
            cells = []

            for i in r:
                cell = self.map[i][j]

                if cell != 0:
                    cells.append(cell)

            self.merge(cells)

            for i in r:
                value = cells.pop(0) if cells else 0

                if self.map[i][j] != value:
                    moved = True

                self.map[i][j] = value

        return moved

    # move left or right
    def moveLR(self, right):
        r = range(self.size - 1, -1, -1) if right else range(self.size)

        moved = False

        for i in range(self.size):
            cells = []

            for j in r:
                cell = self.map[i][j]

                if cell != 0:
                    cells.append(cell)

            self.merge(cells)

            for j in r:
                value = cells.pop(0) if cells else 0

                if self.map[i][j] != value:
                    moved = True

                self.map[i][j] = value

        return moved

    # Merge Tiles
    def merge(self, cells):
        if len(cells) <= 1:
            return cells

        i = 0

        while i < len(cells) - 1:
            if cells[i] == cells[i+1]:
                cells[i] *= 2

                del cells[i+1]

            i += 1

    def canMove(self, dirs = vecIndex):

        # Init Moves to be Checked
        checkingMoves = set(dirs)

        for x in xrange(self.size):
            for y in xrange(self.size):

                # If Current Cell is Filled
                if self.map[x][y]:

                    # Look Ajacent Cell Value
                    for i in checkingMoves:
                        move = directionVectors[i]

                        adjCellValue = self.getCellValue((x + move[0], y + move[1]))

                        # If Value is the Same or Adjacent Cell is Empty
                        if adjCellValue == self.map[x][y] or adjCellValue == 0:
                            return True

                # Else if Current Cell is Empty
                elif self.map[x][y] == 0:
                    return True

        return False

    # Return All Available Moves
    def getAvailableMoves(self, dirs = vecIndex):
        availableMoves = []

        for x in dirs:
            gridCopy = self.clone()

            if gridCopy.move(x):
                availableMoves.append(x)

        return availableMoves

    def crossBound(self, pos):
        x, y = pos
        return x < 0 or x >= self.size or y < 0 or y >= self.size

    def getCellValue(self, pos):
        if not self.crossBound(pos):
            return self.map[pos[0]][pos[1]]
        else:
            return None