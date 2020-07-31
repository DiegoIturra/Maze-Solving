import pygame
import sys
from pygame.locals import *
import constants
import time
import heapq

#movimientos posibles (encapsular despues)
movX = [-1,1,0,0]
movY = [0,0,1,-1]
prev = {}

done = False


def getStart(mapfile):
	"""
	retorna la posicion inicial del agente antes de iniciar la exploracion del laberinto
	recibe el fichero que contiene el mapa
	"""
	with open(mapfile , 'r') as f:
		world_map = f.readlines()
	world_map = [line.strip() for line in world_map]

	x = 0
	y = 0
	for i in range(constants.NUMBER_OF_BLOCKS_HIGH):
		for j in range(constants.NUMBER_OF_BLOCKS_WIDE):
			if world_map[i][j] == 'a':
				x = i
				y = j
				break
	return (x,y)


def getPath(position,path=[]):
	"""
	Retorna una lista con los padres desde la posicion final hasta la 
	posicion de partida del agente
	"""
	global prev
	if position not in prev:
		return path
	else:
		parent = prev[position]
		path.append(parent)
		return getPath(parent,path)


def buidPath(matriz,surface,endPos):
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


def heuristica(matriz):## posición de s: X=10, Y=11 HEURÍSTICA A USAR: DISTANCIA MANHATTAN
	heu = []
	for i in range(12):
		heu.append([])
		for j in range(12):
			if matriz[i][j] != "m":
				heu[i].append(abs(i - 11) + abs(j - 10))
			else:
				heu[i].append("m")
	return heu

def generarVisitados(matriz):
	visitados = []
	for i in range(constants.NUMBER_OF_BLOCKS_HIGH):
		visitados.append([])
		for j in range(constants.NUMBER_OF_BLOCKS_WIDE):
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
		if rr >=12 or cc >= 12: continue

		if visitados[rr][cc] == True: continue
		if matriz[rr][cc] == "m": continue

		"""
		Para evitar tope de recursion, comprobar que el estado inicial
		no tenga un estado padre
		"""
		start = getStart(constants.MAPFILE)
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
		if rr >=12 or cc >= 12: continue

		if visitados[rr][cc] == True: continue
		if matriz[rr][cc] == "m": continue

		start = getStart(constants.MAPFILE)
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
	startPos = [1,1]
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
			buidPath(matriz,surface,(x,y))
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
	startPos = [1, 1]
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
			buidPath(matriz,surface,(x,y))
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
	startPos = [1, 1]
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
			buidPath(matriz,surface,(x,y))
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
			#al oprimir botones del mouse
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					print(event.pos)
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
	tile_color = constants.GOLD
	#pared
	if tile_contents == "m":
		tile_color = constants.DARKGREY
	if tile_contents == "p":
		tile_color = constants.BLACK
	#agente
	if tile_contents == "a":
		tile_color = constants.RED
	#camino
	if tile_contents == ".":
		tile_color = constants.GREEN
	#salida
	if tile_contents == "s":
		tile_color = constants.BLUE
	return tile_color

def draw_map(surface, matriz):
	for i in range(len(matriz)):
		for j in range(len(matriz[i])):
			myrect = pygame.Rect(j*constants.BLOCK_WIDTH,i*constants.BLOCK_HEIGHT,constants.BLOCK_WIDTH,constants.BLOCK_HEIGHT)
			pygame.draw.rect(surface,get_tile_color(matriz[i][j]),myrect)

def draw_grid(surface):
	for i in range(constants.NUMBER_OF_BLOCKS_WIDE):
		new_height = round(i * constants.BLOCK_HEIGHT)
		new_width = round(i * constants.BLOCK_WIDTH)
		pygame.draw.line(surface , constants.BLACK , (0,new_height) , (constants.SCREEN_WIDTH,new_height),2)
		pygame.draw.line(surface , constants.BLACK , (new_width,0) , (new_width,constants.SCREEN_HEIGHT) ,2)

def initialize_game():
	pygame.init()
	surface = pygame.display.set_mode((constants.SCREEN_WIDTH , constants.SCREEN_HEIGHT))
	pygame.display.set_caption("")
	surface.fill(constants.WHITE)
	return surface

def read_map(mapfile):
	with open(mapfile , 'r') as f:
		world_map = f.readlines()
	world_map = [line.strip() for line in world_map]
	matriz = []
	for i in range(constants.NUMBER_OF_BLOCKS_HIGH):
	    matriz.append([])
	    for j in range(constants.NUMBER_OF_BLOCKS_WIDE):
	        matriz[i].append(0)
	for i in range(len(world_map)):
		for j in range(len(world_map[i])):
			matriz[i][j] = world_map[i][j]

	return matriz #aquí se imprime el laberinto almacenado en matriz



def main():
	matriz = read_map(constants.MAPFILE)
	heu = heuristica(matriz)
	surface = initialize_game()
	game_loop(surface, matriz, heu)

if __name__ =="__main__":
	main()