import math
import pygame
from queue import PriorityQueue

WIDTH = 600
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Visualiser")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHTGREEN = (150, 255, 150)
TURQUOISE = (64, 224, 208)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)


class Square:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.total_rows = total_rows
        self.color = WHITE
        self.neighbours = []

    def get_pos(self):
        return self.row, self.col

    def is_start(self):
        return self.color == TURQUOISE

    def is_end(self):
        return self.color == LIGHTGREEN

    def is_barrier(self):
        return self.color == BLACK
    
    def is_open(self):
        return self.color == GREEN

    def is_closed(self):
        return self.color == RED

    def is_path(self):
        return self.color == ORANGE

    def reset(self):
        self.color = WHITE

    def start(self):
        self.color = TURQUOISE

    def end(self):
        self.color = LIGHTGREEN

    def barrier(self):
        self.color = BLACK
    
    def open(self):
        self.color = GREEN

    def closed(self):
        self.color = RED

    def path(self):
        self.color = ORANGE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def  __lt__(self, other):
        return False

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col - 1])


def H(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x2 - x1) + abs(y2 - y1)


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            square = Square(i, j, gap, rows)
            grid[i].append(square)

    return grid


def draw_gridlines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows):
        pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for square in row:
            square.draw(win)
    
    draw_gridlines(win, rows, width)
    pygame.display.update()


def get_clicked_position(mouse, rows, width):
    gap = width // rows
    y, x = mouse
    row = y // gap
    col = x // gap
    return row, col


def AStar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g = {square: float("inf") for row in grid for square in row}
    g[start] = 0
    f = {square: float("inf") for row in grid for square in row}
    f[start] = g[start] + H(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        currentNode = open_set.get()[2]
        open_set_hash.remove(currentNode)

        if currentNode == end:
            path(came_from, end, draw)
            end.end()
            start.start()
            return True

        for neighbour in currentNode.neighbours:
            temp_g = g[currentNode] + 1

            if temp_g < g[neighbour]:
                came_from[neighbour] = currentNode
                g[neighbour] = temp_g
                f[neighbour] = temp_g + H(neighbour.get_pos(), end.get_pos())

                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.open()

        draw()
        if currentNode != start:
            currentNode.closed()

    return False


def path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.path()
        draw()


def main(win, width):
    ROWS = 30
    grid = make_grid(ROWS, width)

    startNode = None
    endNode = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:   # Left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                square = grid[row][col]
                if not startNode and square != endNode:
                    startNode = square
                    startNode.start()
                elif not endNode and square != startNode:
                    endNode = square
                    endNode.end()
                elif square != endNode and square != startNode:
                    square.barrier()

            elif pygame.mouse.get_pressed()[2]: # Right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                square = grid[row][col]
                square.reset()
                if square == startNode:
                    startNode = None
                elif square == endNode:
                    endNode = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and startNode and endNode:     # *Check*
                    for row in grid:
                        for square in row:
                            square.update_neighbours(grid)

                    AStar(lambda: draw(win, grid, ROWS, width), grid, startNode, endNode)

                if event.key == pygame.K_c:
                    startNode = None
                    endNode = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WINDOW, WIDTH)
    