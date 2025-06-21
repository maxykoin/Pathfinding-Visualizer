import pygame
from queue import PriorityQueue

pygame.init()
win = pygame.display.set_mode((800,800))
pygame.display.set_caption('A* Path Finding Algorithm')

RED = (255, 0, 0) # for the search area we don't consider
GREEN = (0, 255, 0) # for the search area we do consider
YELLOW = (255, 255, 0) # for the chosen path
WHITE = (255, 255, 255) # for the canvas
BLACK = (0, 0, 0) # for the barriers 
PURPLE = (128, 0, 128) # for the start
GREY = (128, 128, 128) # grid lines
TURQUOISE = (64, 224, 208) # for the end

class Spot:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        self.x = row  * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.totalRows = totalRows
    
    def getPos(self):
        return self.row, self.col 
    
    def isClosed(self):
        return self.color == RED

    def isOpen(self):
        return self.color == GREEN
    
    def isBarrier(self):
        return self.color == BLACK
    
    def isStart(self):
        return self.color == PURPLE
    
    def isEnd(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE
    
    def makeClosed(self):
        self.color = RED

    def makeOpen(self):
        self.color = GREEN
    
    def makeBarrier(self):
        self.color = BLACK
    
    def makeStart(self):
        self.color = PURPLE
    
    def makeEnd(self):
        self.color = TURQUOISE
    
    def makePath(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid): # every single node needs a valid neighbor (not barriers)
        self.neighbors = []
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier(): # moving down 
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier(): # moving up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier(): # moving right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier(): # moving left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other): # the other spot is always greater than this spot
        return False    

def h(p1, p2): # calculating the manhatthan distance (movement is restricted to horizontal and vertical directions)
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstructPath(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        
        if current.isStart():
            continue

        current.makePath()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    openSet = PriorityQueue() # efficient way to always get the smallest element out of it
    openSet.put((0, count, start)) # add the start node with its f score into the open set (adding count to implement fifo)
    cameFrom = {} # keeping track of the path, which node came before the one i am currently in 
    
    # stores the path from the start node to the current node
    gScore = {spot: float("inf") for row in grid for spot in row}
    gScore[start] = 0

    # keep score of our predicted distance to the end node
    fScore = {spot: float("inf") for row in grid for spot in row} 
    fScore[start] = h(start.getPos(), end.getPos()) # initial estimate of how far the start node is from the end node

    openSetHash = {start}

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        
        current = openSet.get()[2] # just the node
        openSetHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, draw)
            end.makeEnd()
            return True
        
        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1
            if tempGScore < gScore[neighbor]: # if we found a better path, update the old path
                cameFrom[neighbor] =  current
                gScore[neighbor] = tempGScore 
                fScore[neighbor] = tempGScore + h(neighbor.getPos(), end.getPos())
                if neighbor not in openSetHash:
                    count += 1
                    openSet.put((fScore[neighbor], count, neighbor)) # now we are going to consider this neighbor cause it has a better path than before
                    openSetHash.add(neighbor)
                    neighbor.makeOpen() # opening it so we consider it
        
        draw()

        if current != start: 
            current.makeClosed() # we already considered it and didn't stick with it 

    return False

def makeGrid(rows, width):
    grid = []
    gap = width // rows

    for row in range(rows):
        grid.append([])
        for col in range(rows):
            spot = Spot(row, col, gap, rows)
            grid[row].append(spot)
    
    return grid

def drawGrid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    drawGrid(win, rows, width)
    pygame.display.update()

def getClickedPosition(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    rows = 50
    grid = makeGrid(rows, width)
    start = None
    end = None
    run = True
    started = False

    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                run = False
            if started:
                continue
            if pygame.mouse.get_pressed()[0]: # left click to draw
                pos = pygame.mouse.get_pos()
                row, col = getClickedPosition(pos, rows, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.makeStart()

                elif not end and spot != start:
                    end = spot
                    end.makeEnd()
                
                elif spot != start and spot != end:
                    spot.makeBarrier()

            elif pygame.mouse.get_pressed()[2]: # right click to delete
                pos = pygame.mouse.get_pos()
                row, col = getClickedPosition(pos, rows, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.updateNeighbors(grid)
                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end) # lambda! anonymous functions
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = makeGrid(rows, width)

    pygame.quit()

main(win, 800)