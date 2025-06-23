import pygame
import time
from queue import PriorityQueue

pygame.init()
WINDOW_WIDTH, GRID_HEIGHT, HEADER_HEIGHT = 800, 780, 70
WINDOW_HEIGHT = GRID_HEIGHT + HEADER_HEIGHT
ROWS = 50
FONT = pygame.font.SysFont("consolas", 18)

RED, GREEN, YELLOW = (255, 0, 0), (0, 255, 0), (255, 255, 0)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PURPLE, GREY, TURQUOISE = (128, 0, 128), (128, 128, 128), (64, 224, 208)
CYAN = (0, 255, 255)

win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pathfinding Visualizer")

ALGORITHMS = {
    "Dijkstra": {"key": pygame.K_1, "h": False},
    "A*": {"key": pygame.K_2, "h": True},
}

class Spot:
    def __init__(self, row, col, cellSize, totalRows):
        self.row = row
        self.col = col
        self.x = col * cellSize
        self.y = row * cellSize + HEADER_HEIGHT
        self.color = WHITE
        self.neighbors = []
        self.cellSize = cellSize
        self.totalRows = totalRows

    def getPos(self): return self.row, self.col
    def isClosed(self): return self.color == RED
    def isOpen(self): return self.color == GREEN
    def isBarrier(self): return self.color == BLACK
    def isStart(self): return self.color == PURPLE
    def isEnd(self): return self.color == TURQUOISE
    def reset(self): self.color = WHITE
    def makeClosed(self): self.color = RED
    def makeOpen(self): self.color = GREEN
    def makeBarrier(self): self.color = BLACK
    def makeStart(self): self.color = PURPLE
    def makeEnd(self): self.color = TURQUOISE
    def makePath(self): self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.cellSize, self.cellSize))

    def updateNeighbors(self, grid):
        self.neighbors = []
        if self.row < self.totalRows - 1 and not grid[self.row+1][self.col].isBarrier(): self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].isBarrier(): self.neighbors.append(grid[self.row-1][self.col])
        if self.col < self.totalRows - 1 and not grid[self.row][self.col+1].isBarrier(): self.neighbors.append(grid[self.row][self.col+1])
        if self.col > 0 and not grid[self.row][self.col-1].isBarrier(): self.neighbors.append(grid[self.row][self.col-1])
    
    def __lt__(self): return False

def h(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def reconstructPath(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        if current.isStart(): continue
        current.makePath()
        draw()

def runAlgorithm(draw, grid, start, end, useH):
    count, openSet = 0, PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {spot: float("inf") for row in grid for spot in row}
    fScore = {spot: float("inf") for row in grid for spot in row}
    gScore[start] = 0
    fScore[start] = h(start.getPos(), end.getPos()) if useH else 0
    openSetHash = {start}

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        current = openSet.get()[2]
        openSetHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, draw)
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            tempG = gScore[current] + 1
            if tempG < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempG
                fScore[neighbor] = tempG + (h(neighbor.getPos(), end.getPos()) if useH else 0)
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
    size = width // rows
    return [[Spot(i, j, size, rows) for j in range(rows)] for i in range(rows)]

def drawGrid(win, rows, width):
    size = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * size + HEADER_HEIGHT), (width, i * size + HEADER_HEIGHT))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * size, HEADER_HEIGHT), (j * size, width + HEADER_HEIGHT))

def drawHeader(win, selection, times):
    pygame.draw.rect(win, (30, 30, 60), (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
    pygame.draw.line(win, CYAN, (0, HEADER_HEIGHT-1), (WINDOW_WIDTH, HEADER_HEIGHT-1))
    pygame.draw.line(win, (0, 180, 255), (0, HEADER_HEIGHT-2), (WINDOW_WIDTH, HEADER_HEIGHT-2))

    options = ' | '.join([f"[{pygame.key.name(v['key']).upper()}] {k}" for k, v in ALGORITHMS.items()])
    lines = [
        f"{options} | [3] Compare | [C] Clear",
        f"Selected: {selection or '---'} " + ' | '.join([f"{k}: {times.get(k.lower(), '---')}s" for k in ALGORITHMS])
    ]
    for idx, text in enumerate(lines):
        surf = FONT.render(text, True, (255, 255, 255))
        win.blit(surf, (20, 5 + idx * 24))

def draw(win, grid, headerSel, headerTimes):
    win.fill(WHITE)
    drawHeader(win, headerSel, headerTimes)
    for row in grid:
        for spot in row:
            spot.draw(win)
    drawGrid(win, ROWS, WINDOW_WIDTH)
    pygame.display.update()

def getClickedPos(pos):
    x, y = pos
    if y < HEADER_HEIGHT: return None, None
    size = WINDOW_WIDTH // ROWS
    return (y - HEADER_HEIGHT) // size, x // size

def clearSearch(grid):
    for row in grid:
        for spot in row:
            if not (spot.isStart() or spot.isEnd() or spot.isBarrier()):
                spot.reset()

def main():
    grid = makeGrid(ROWS, WINDOW_WIDTH)
    start = end = None
    algoSelection = ""
    times = {}
    run = True

    while run:
        draw(win, grid, algoSelection, times)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                row, col = getClickedPos(pygame.mouse.get_pos())
                if row is None: continue
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
                row, col = getClickedPos(pygame.mouse.get_pos())
                if row is None: continue
                spot = grid[row][col]
                if spot == start: start = None
                elif spot == end: end = None
                spot.reset()

            if event.type == pygame.KEYDOWN and start and end:
                clearSearch(grid)
                for rowList in grid:
                    for spot in rowList:
                        spot.updateNeighbors(grid)

                if event.key == pygame.K_3:
                    algoSelection = "Compare"
                    for name, config in ALGORITHMS.items():
                        clearSearch(grid)
                        start.makeStart(); end.makeEnd()
                        for rowList in grid:
                            for spot in rowList:
                                spot.updateNeighbors(grid)
                        t0 = time.time()
                        runAlgorithm(lambda: draw(win, grid, algoSelection, times), grid, start, end, config["h"])
                        times[name.lower()] = round(time.time() - t0, 4)

                else:
                    for name, config in ALGORITHMS.items():
                        if event.key == config["key"]:
                            algoSelection = name
                            t0 = time.time()
                            runAlgorithm(lambda: draw(win, grid, algoSelection, times), grid, start, end, config["h"])
                            times[name.lower()] = round(time.time() - t0, 4)
                            break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                start = end = None
                algoSelection = ""
                times.clear()
                grid = makeGrid(ROWS, WINDOW_WIDTH)

    pygame.quit()

main()


