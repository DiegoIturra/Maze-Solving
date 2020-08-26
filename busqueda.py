import pygame
import sys
from pygame.locals import *
import time
import heapq
import random
import timeit
import os

TILE_EMPTY = 0
TILE_CRATE = 1

#El laberinto debe tener una cantidad IMPAR de filas y columnas
MAZE_WIDTH = 50#columnas
MAZE_HEIGHT = 25#filas
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 650
BLOCK_HEIGHT = round(SCREEN_HEIGHT/MAZE_HEIGHT)
BLOCK_WIDTH = round(SCREEN_WIDTH/MAZE_WIDTH)


GREY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (55, 55, 255)
GREEN = (0, 200, 0)
DARKGREY = (150, 150, 150)
BLACK = (0,0,0)
WHITE = (255,255,255)


#movimientos posibles (encapsular despues)
movX = [-1,1,0,0]
movY = [0,0,1,-1]
prev = {}

entrada_x = entrada_y = salida_x = salida_y = 0

done = False

def create_empty_grid(width, height, default_value=TILE_EMPTY):
    """ Create an empty grid. """
    grid = []
    for row in range(height):
        grid.append([])
        for column in range(width):
            grid[row].append(default_value)
    return grid

def create_outside_walls(maze):
    """ Create outside border walls."""

    # Create left and right walls
    for row in range(len(maze)):
        maze[row][0] = TILE_CRATE
        maze[row][len(maze[row])-1] = TILE_CRATE

    # Create top and bottom walls
    for column in range(1, len(maze[0]) - 1):
        maze[0][column] = TILE_CRATE
        maze[len(maze) - 1][column] = TILE_CRATE

def make_maze_recursive_call(maze, top, bottom, left, right):
    """
    Recursive function to divide up the maze in four sections
    and create three gaps.
    Walls can only go on even numbered rows/columns.
    Gaps can only go on odd numbered rows/columns.
    Maze must have an ODD number of rows and columns.
    """

    # Figure out where to divide horizontally
    start_range = bottom + 2
    end_range = top - 1
    y = random.randrange(start_range, end_range, 2)

    # Do the division
    for column in range(left + 1, right):
        maze[y][column] = TILE_CRATE

    # Figure out where to divide vertically
    start_range = left + 2
    end_range = right - 1
    x = random.randrange(start_range, end_range, 2)

    # Do the division
    for row in range(bottom + 1, top):
        maze[row][x] = TILE_CRATE

    # Now we'll make a gap on 3 of the 4 walls.
    # Figure out which wall does NOT get a gap.
    wall = random.randrange(4)
    if wall != 0:
        gap = random.randrange(left + 1, x, 2)
        maze[y][gap] = TILE_EMPTY

    if wall != 1:
        gap = random.randrange(x + 1, right, 2)
        maze[y][gap] = TILE_EMPTY

    if wall != 2:
        gap = random.randrange(bottom + 1, y, 2)
        maze[gap][x] = TILE_EMPTY

    if wall != 3:
        gap = random.randrange(y + 1, top, 2)
        maze[gap][x] = TILE_EMPTY

    # If there's enough space, to a recursive call.
    if top > y + 3 and x > left + 3:
        make_maze_recursive_call(maze, top, y, left, x)

    if top > y + 3 and x + 3 < right:
        make_maze_recursive_call(maze, top, y, x, right)

    if bottom + 3 < y and x + 3 < right:
        make_maze_recursive_call(maze, y, bottom, x, right)

    if bottom + 3 < y and x > left + 3:
        make_maze_recursive_call(maze, y, bottom, left, x)

def make_maze_recursion(maze_width, maze_height):
    """ Make the maze by recursively splitting it into four rooms. """
    global entrada_x, entrada_y, salida_x, salida_y
    maze = create_empty_grid(maze_width, maze_height)
    # Fill in the outside walls
    create_outside_walls(maze)

    # Start the recursive process
    make_maze_recursive_call(maze, maze_height - 1, 0, 0, maze_width - 1)
    
    #cambia los 1 por m y los 0 por .
    for i in range(MAZE_HEIGHT):
    	for j in range(MAZE_WIDTH):
    		if maze[i][j] == 1:
    			maze[i][j] = 'm'
    		if maze[i][j] == 0:
    			maze[i][j] = '.'

   	#establece la entrada y salida del laberinto
    entrada_x = 1
    entrada_y = 0
    if maze[entrada_x][entrada_y + 1] == 'm':
    	entrada_x = entrada_x + 1
    	maze[entrada_x][entrada_y] = 'a'

    maze[entrada_x][entrada_y] = 'a'

    salida_x = MAZE_HEIGHT - 1
    salida_y = MAZE_WIDTH - 2

    if maze[salida_x - 1][salida_y] == 'm':
    	salida_y = salida - 1
    	maze[salida_x][salida_y] = 's'

    maze[salida_x][salida_y] = 's'

    return maze

def getPath(position,path=[]):
	"""
	Retorna una lista con los padres desde la posicion final hasta la 
	posicion de partida del agente
	"""
	while position in prev:
		parent = prev[position]
		path.append(parent)
		position = parent
	return path

def buildPath(matriz,surface,endPos):
	"""
	Reconstruir camino
	"""
	path = getPath(endPos)
	path.append(endPos)
	path.reverse() #revertir la lista original
	for node in path:
		x,y = node
		matriz[x][y] = "s" #setear camino en azul
		draw_map(surface, matriz)
		draw_grid(surface)
		pygame.display.update()
		pygame.time.delay(100)

def heuristica(matriz):#HEURÍSTICA A USAR: DISTANCIA MANHATTAN
	heu = []
	for i in range(MAZE_HEIGHT):
		heu.append([])
		for j in range(MAZE_WIDTH):
			if matriz[i][j] != "m":
				heu[i].append(abs(i - salida_y) + abs(j - salida_x))
			else:
				heu[i].append("m")
	return heu

def generarVisitados(matriz):
	visitados = []
	for i in range(MAZE_HEIGHT):
		visitados.append([])
		for j in range(MAZE_WIDTH):
			if matriz[i][j] == "m":
				visitados[i].append(None)
			elif matriz[i][j] == "." or matriz[i][j] == "s" or matriz[i][j] == "a":
				visitados[i].append(False)
	return visitados

def generarVecinos(x, y, matriz, visitados, queue):
	global prev
	for i in range(4):
		rr = x + movX[i]
		cc = y + movY[i]

		if rr < 0 or cc < 0: continue
		if rr >= MAZE_HEIGHT or cc >= MAZE_WIDTH: continue

		if visitados[rr][cc] == True: continue
		if matriz[rr][cc] == "m": continue

		"""
		Para evitar un ciclo en la reconstruccion del camino final
		"""
		start = (entrada_x, entrada_y)
		if (rr,cc) == (start[0],start[1]):
			continue

		#agregar nodos padres
		prev[(rr,cc)] = (x,y)


		queue.append([rr,cc])
		visitados[rr][cc] = True

	matriz[x][y] = "a"

def generarVecinosGreedy(x, y, heu, matriz, visitados, pq):
	global prev
	for i in range(4):
		rr = x + movX[i]
		cc = y + movY[i]

		if rr < 0 or cc < 0: continue
		if rr >= MAZE_HEIGHT or cc >= MAZE_WIDTH: continue

		if visitados[rr][cc] == True: continue
		if matriz[rr][cc] == "m": continue

		start = (entrada_x, entrada_y)
		if (rr,cc) == (start[0],start[1]):
			continue
		#agregar nodos padres
		prev[(rr,cc)] = (x,y)

		heapq.heappush(pq, (heu[rr][cc], [rr,cc]))
		visitados[rr][cc] = True
	matriz[x][y] = "a"

def DFS(matriz, surface):
	global done
	global prev
	visitados = generarVisitados(matriz)
	startPos = (entrada_x, entrada_y)
	stack = []
	stack.append(startPos)

	while len(stack) > 0:
		current = stack.pop()
		x = current[0]
		y = current[1]

		if matriz[x][y] == "s":
			matriz[x][y] = "a"
			stack.clear()
			pygame.time.delay(100)
			done = True
			buildPath(matriz,surface,(x,y))
			sys.exit()

		generarVecinos(x, y, matriz, visitados, stack)
		draw_map(surface, matriz)
		draw_grid(surface)
		pygame.display.update()
		pygame.time.delay(100)

	draw_map(surface, matriz)
	draw_grid(surface)
	pygame.display.update()
	pygame.time.delay(100)
	done = True

def BFS(matriz, surface):
	global done
	visitados = generarVisitados(matriz)
	startPos = (entrada_x, entrada_y)
	queue = []
	queue.append(startPos)

	while len(queue) > 0:
		current = queue.pop(0)
		x = current[0]
		y = current[1]
		#llega a la salida
		if matriz[x][y] == "s":
			matriz[x][y] = "a"
			queue.clear()
			done = True
			buildPath(matriz,surface,(x,y))
			sys.exit()
		
		generarVecinos(x, y, matriz, visitados, queue)
		draw_map(surface, matriz)
		draw_grid(surface)
		pygame.display.update()
		pygame.time.delay(100)

	draw_map(surface, matriz)
	draw_grid(surface)
	pygame.display.update()
	pygame.time.delay(100)
	done = True

def greedy(matriz, heu, surface):
	global done
	visitados = generarVisitados(matriz)
	startPos = (entrada_x, entrada_y)
	pq = []
	heapq.heappush(pq, (19, startPos))

	while len(pq) > 0:
		current = heapq.heappop(pq)
		x = current[1][0]
		y = current[1][1]

		#llega a la meta
		if matriz[x][y] == "s":
			matriz[x][y] = "a"
			pq.clear()
			done = True
			buildPath(matriz,surface,(x,y))
			sys.exit()

		generarVecinosGreedy(x, y, heu, matriz, visitados, pq)
		draw_map(surface, matriz)
		draw_grid(surface)
		pygame.display.update()
		pygame.time.delay(100)

	draw_map(surface, matriz)
	draw_grid(surface)
	pygame.display.update()
	pygame.time.delay(100)
	done = True

def game_loop(surface, matriz, heu):
	global done
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
		if done == False:
			if sys.argv[1] == "dfs":
				pygame.display.set_caption("DFS")
				DFS(matriz,surface)
			elif sys.argv[1] == "bfs":
				pygame.display.set_caption("BFS")
				BFS(matriz,surface)
			elif sys.argv[1] == "greedy":
				pygame.display.set_caption("Greedy")
				greedy(matriz,heu,surface)

			"""
			Reemplazar con algoritmos de busqueda DFS() y BFS()
			"""
		draw_map(surface,matriz)
		draw_grid(surface)
		pygame.display.update()

def get_tile_color(tile_contents):
	#pared
	if tile_contents == "m":
		tile_color = DARKGREY
	#agente
	if tile_contents == "a":
		tile_color = RED
	#camino
	if tile_contents == ".":
		tile_color = GREEN
	#salida
	if tile_contents == "s":
		tile_color = BLUE
	return tile_color

def draw_map(surface, matriz):
	for i in range(len(matriz)):
		for j in range(len(matriz[i])):
			myrect = pygame.Rect(j*BLOCK_WIDTH,i*BLOCK_HEIGHT,BLOCK_WIDTH,BLOCK_HEIGHT)
			pygame.draw.rect(surface,get_tile_color(matriz[i][j]),myrect)

def draw_grid(surface):
	for i in range(MAZE_WIDTH):
		new_height = round(i * BLOCK_HEIGHT)
		new_width = round(i * BLOCK_WIDTH)
		pygame.draw.line(surface , BLACK , (0,new_height) , (SCREEN_WIDTH,new_height),2)
		pygame.draw.line(surface , BLACK , (new_width,0) , (new_width,SCREEN_HEIGHT) ,2)

def initialize_game():
	pygame.init()
	surface = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))
	pygame.display.set_caption("")
	surface.fill(WHITE)
	return surface

def main():
	matriz = make_maze_recursion(MAZE_WIDTH, MAZE_HEIGHT)
	"""
	for i in range(MAZE_HEIGHT):
		for j in range(MAZE_WIDTH):
			print(matriz[i][j], end = " ")
		print()
	"""
	heu = heuristica(matriz)
	surface = initialize_game()
	game_loop(surface, matriz, heu)

if __name__ =="__main__":
	main()