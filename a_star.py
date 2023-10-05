import pygame
import math
from queue import PriorityQueue

HEIGHT = 500
pygame.display.set_caption("Path Tracer")
WINDOW = pygame.display.set_mode((HEIGHT, HEIGHT))


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)  
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
'''

'''
class Cell:
	def __init__(self, row, col, height, total_rows):
		self.row = row; self.col = col; self.x=height*row; self.y=height*col
		self.colour = WHITE
		self.neighbours = []
		self.height = height
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.colour == RED

	def is_open(self):
		return self.colour == GREEN

	def is_barrier(self):
		return self.colour == BLACK

	def is_start(self):
		return self.colour == ORANGE

	def is_end(self):
		return self.colour == TURQUOISE

	def reset(self):
		self.colour = WHITE

	def make_start(self):
		self.colour = ORANGE

	def make_closed(self):
		self.colour = RED

	def make_open(self):
		self.colour = GREEN

	def make_barrier(self):
		self.colour = BLACK

	def make_end(self):
		self.colour = TURQUOISE

	def make_path(self):
		self.colour = PURPLE

	def draw(self, window):
		pygame.draw.rect(window, self.colour, (self.x, self.y, self.height, self.height))

	def update_neighbors(self, grid):
		self.neighbours = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbours.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbours.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbours.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbours.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def heuristic(p1, p2):
	x1,y1=p1
	x2,y2=p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count=0
	open_set=PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score={}
	f_score={}
	for row in grid:
		for cell in row:
			# g_score={cell:float("inf")}
			g_score[cell]=float("inf")
			f_score[cell]=float("inf")
	# g_score = {cell: float("inf") for row in grid for cell in row}
	g_score[start] = 0
	# f_score = {cell: float("inf") for row in grid for cell in row}
	f_score[start] = heuristic(start.get_pos(), end.get_pos())
	open_set_hash = {start}
	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbours:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, height):
	grid = []
	gap = height // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			cell = Cell(i, j, gap, rows)
			grid[i].append(cell)

	return grid


def draw_grid(window, rows, height):
	gap = height // rows
	for i in range(rows):
		pygame.draw.line(window, GREY, (0, i * gap), (height, i * gap))
		for j in range(rows):
			pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, height))


def draw(window, grid, rows, height):
	window.fill(WHITE)
	for row in grid:
		for cell in row:
			cell.draw(window)

	draw_grid(window, rows, height)
	pygame.display.update()


def clicking_position(pos, rows, height):
	gap = height // rows
	x,y = pos

	row = x // gap
	col = y // gap

	return row, col

if __name__ == "__main__":
	window=WINDOW
	height=HEIGHT
	ROWS=50
	grid=make_grid(ROWS, height) # make grid with cells appended in it
	start=None
	end=None
	running=True
	while running:
		draw(window, grid, ROWS, height) # draws celss, calls draw_grid which draws lines of the grid
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if pygame.mouse.get_pressed()[0]: 
				pos = pygame.mouse.get_pos()
				row, col = clicking_position(pos, ROWS, height)
				cell = grid[row][col]
				if not start and cell != end:
					start = cell
					start.make_start()

				elif not end and cell != start:
					end = cell
					end.make_end()

				elif cell != end and cell != start:  # make a barrier
					cell.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = clicking_position(pos, ROWS, height)
				cell = grid[row][col]
				cell.reset()
				if cell == start:
					start = None
				elif cell == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for cell in row:
							cell.update_neighbors(grid)

					algorithm(lambda: draw(window, grid, ROWS, height), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, height)

	pygame.quit()

