import pygame
import time
from queue import PriorityQueue

pygame.init()
width, height = 800, 850
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pathfinding Visualizer")

# Colors
red, green, yellow = (255, 0, 0), (0, 255, 0), (255, 255, 0)
white, black = (255, 255, 255), (0, 0, 0)
purple, grey, turquoise = (128, 0, 128), (128, 128, 128), (64, 224, 208)
blue = (0, 0, 255)

# Constants
rows = 50
buttonHeight = 50
font = pygame.font.SysFont("Arial", 20)

class Spot:
    def __init__(self, row, col, cellSize, totalRows):
        self.row = row
        self.col = col
        self.x = col * cellSize  # ✅ col → x
        self.y = row * cellSize + buttonHeight  # ✅ row → y (+ header)
        self.color = white
        self.neighbors = []
        self.cellSize = cellSize
        self.totalRows = totalRows

    def getPos(self):
        return self.row, self.col

    def isClosed(self): return self.color == red
    def isOpen(self): return self.color == green
    def isBarrier(self): return self.color == black
    def isStart(self): return self.color == purple
    def isEnd(self): return self.color == turquoise
    def reset(self): self.color = white
    def makeClosed(self): self.color = red
    def makeOpen(self): self.color = green
    def makeBarrier(self): self.color = black
    def makeStart(self): self.color = purple
    def makeEnd(self): self.color = turquoise
    def makePath(self): self.color = yellow

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.cellSize, self.cellSize))

    def updateNeighbors(self, grid):
        self.neighbors = []
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other): return False

def heuristic(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def reconstructPath(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        if current.isStart(): continue
        current.makePath()
        draw()

def dijkstra(draw, grid, start, end):
    return runAlgorithm(draw, grid, start, end, useHeuristic=False)

def aStar(draw, grid, start, end):
    return runAlgorithm(draw, grid, start, end, useHeuristic=True)

def runAlgorithm(draw, grid, start, end, useHeuristic):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}

    gScore = {spot: float("inf") for row in grid for spot in row}
    fScore = {spot: float("inf") for row in grid for spot in row}
    gScore[start] = 0
    fScore[start] = heuristic(start.getPos(), end.getPos()) if useHeuristic else 0

    openSetHash = {start}
    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = openSet.get()[2]
        openSetHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, draw)
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1
            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + (heuristic(neighbor.getPos(), end.getPos()) if useHeuristic else 0)
                if neighbor not in openSetHash:
                    count += 1
                    openSet.put((fScore[neighbor], count, neighbor))
                    openSetHash.add(neighbor)
                    neighbor.makeOpen()
        draw()
        if current != start:
            current.makeClosed()
    return False

def makeGrid(rows, width):
    cellSize = width // rows
    return [[Spot(i, j, cellSize, rows) for j in range(rows)] for i in range(rows)]

def drawGrid(win, rows, width):
    cellSize = width // rows
    for i in range(rows):
        pygame.draw.line(win, grey, (0, i * cellSize + buttonHeight), (width, i * cellSize + buttonHeight))
        for j in range(rows):
            pygame.draw.line(win, grey, (j * cellSize, buttonHeight), (j * cellSize, width + buttonHeight))

def drawHeader(win, algoName, elapsedTime):
    pygame.draw.rect(win, blue, (0, 0, width, buttonHeight))
    text = font.render(
        f"1: Dijkstra | 2: A* | 3: All | C: Clear | Current: {algoName} | Time: {elapsedTime:.4f}s",
        True, white
    )
    win.blit(text, (10, 15))

def draw(win, grid, rows, width, algoName="", elapsedTime=0):
    win.fill(white)
    drawHeader(win, algoName, elapsedTime)
    for row in grid:
        for spot in row:
            spot.draw(win)
    drawGrid(win, rows, width)
    pygame.display.update()

def getClickedPos(pos, rows, width):
    x, y = pos
    if y < buttonHeight:
        return None, None
    gap = width // rows
    row = (y - buttonHeight) // gap
    col = x // gap
    return row, col

def main(win, width):
    grid = makeGrid(rows, width)
    start = end = None
    run = True
    selectedAlgo = "dijkstra"
    elapsedTime = 0

    while run:
        draw(win, grid, rows, width, selectedAlgo, elapsedTime)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, rows, width)
                if row is None or col is None:
                    continue
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.makeStart()
                elif not end and spot != start:
                    end = spot
                    end.makeEnd()
                elif spot != start and spot != end:
                    spot.makeBarrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, rows, width)
                if row is None or col is None:
                    continue
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and start and end:
                    for rowObj in grid:
                        for spot in rowObj:
                            spot.updateNeighbors(grid)
                    startTime = time.time()
                    if event.key == pygame.K_1:
                        selectedAlgo = "dijkstra"
                        dijkstra(lambda: draw(win, grid, rows, width, selectedAlgo, elapsedTime), grid, start, end)
                    elif event.key == pygame.K_2:
                        selectedAlgo = "aStar"
                        aStar(lambda: draw(win, grid, rows, width, selectedAlgo, elapsedTime), grid, start, end)
                    elif event.key == pygame.K_3:
                        selectedAlgo = "all"
                        dijkstra(lambda: None, grid, start, end)
                        aStar(lambda: None, grid, start, end)
                    elapsedTime = time.time() - startTime

                if event.key == pygame.K_c:
                    start, end = None, None
                    elapsedTime = 0
                    grid = makeGrid(rows, width)

    pygame.quit()

main(win, width)


