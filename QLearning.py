import pygame
import sys
from random import uniform,randint
import numpy as np
import random

TILE_EMPTY = 0
TILE_CRATE = 1

#El laberinto debe tener una cantidad IMPAR de filas y columnas


MAZE_WIDTH = 9 #cambiar a 25x25	
MAZE_HEIGHT = 9
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

BLOCK_HEIGHT = round(SCREEN_HEIGHT/MAZE_HEIGHT)
BLOCK_WIDTH = round(SCREEN_WIDTH/MAZE_WIDTH)


GREY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (55, 55, 255)
GREEN = (0, 200, 0)
DARKGREY = (150, 150, 150)
WHITE = (255,255,255)
BLACK = (0, 0, 0)


#movimientos posibles (encapsular despues)
movX = [-1,1,0,0]
movY = [0,0,1,-1]
prev = {}

entrada_x = entrada_y = salida_x = salida_y = 0

done = False

file = open("Rewards.txt",'w')
numEpisodes = 1000


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

def get_tile_color(tile_contents):
	#pared
	if tile_contents == "m":
		tile_color = DARKGREY
	if tile_contents == "p":
		tile_color = BLACK
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
	""" Dibuja el laberinto en pantalla """
	for i in range(len(matriz)):
		for j in range(len(matriz[i])):
			myrect = pygame.Rect(j*BLOCK_WIDTH,i*BLOCK_HEIGHT,BLOCK_WIDTH,BLOCK_HEIGHT)
			pygame.draw.rect(surface,get_tile_color(matriz[i][j]),myrect)

def draw_grid(surface):
	""" Dibuja las casillas del laberinto """
	for i in range(MAZE_WIDTH):
		new_height = round(i * BLOCK_HEIGHT)
		new_width = round(i * BLOCK_WIDTH)
		pygame.draw.line(surface ,BLACK , (0,new_height) , (SCREEN_WIDTH,new_height),2)
		pygame.draw.line(surface ,BLACK , (new_width,0) , (new_width, SCREEN_HEIGHT) ,2)

def initialize_game():
	""" Setea el ambiente inicial y devuelve el surface para poder setearlo """
	pygame.init()
	surface = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))
	pygame.display.set_caption("")
	surface.fill(WHITE)
	return surface

def game_loop(surface, matriz , enviroment):
	global done,numEpisodes,file
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
		if not done:
			#llamar a Q-Learning
			for episode in range(numEpisodes):
				pygame.display.set_caption(f"Episode number {episode}")
				enviroment.training(episode)
			done = True
			file.close()
		draw_map(surface,matriz)
		draw_grid(surface)
		pygame.display.update()


class Enviroment():

	def __init__(self,numEpisodes,matriz,surface):
		""" establecer parametros """
		self.numEpisodes = numEpisodes
		#alto y ancho del laberinto
		self.height = MAZE_HEIGHT
		self.width = MAZE_WIDTH
		self.learning_rate = 0.1 #taza de aprendizaje
		self.discount_factor = 0.99 #factor de descuento
		self.exp_rate = 0.3

		#matriz de valores de Q
		self.Qvalues = np.zeros(shape=[MAZE_HEIGHT,MAZE_WIDTH,4])
		#matriz de recompensas
		self.rewards = np.zeros(shape=(MAZE_HEIGHT,MAZE_WIDTH))
		#matriz que indica posiciones con muros
		self.blocked = np.zeros(shape=(MAZE_HEIGHT,MAZE_WIDTH))
		#matriz con caracteres
		self.maze = matriz


		self.x_pos = entrada_x
		self.y_pos = entrada_y

		self.prev_x_pos = 0
		self.prev_y_pos = 0

		self.action_taken = 0

		self.cum_reward = 0.0

		self.surface = surface



	def initialize_enviroment(self):
		""" setear entorno inicial """
		self.init_x_pos = entrada_x
		self.init_y_pos = entrada_y
		self.goalX = salida_x
		self.goalY = salida_y

		for i in range(self.height):
			for j in range(self.width):
				self.rewards[i,j] = -0.04
				if self.maze[i][j] == 'm': #si hay una pared , marcarlo
					self.blocked[i,j] = 1

				if self.maze[i][j] == 's':
					self.rewards[i,j] = 10000.0 # si llega a la salida la recompensa sera mejor

				for k in range(4):
					self.Qvalues[i,j,k] = uniform(0,10)


	def getBestAction(self):
		""" estando en un estado Q , ver cual es la mejor accion
		a partir de ese estado Q"""
		action = 0
		maxQvalue = self.Qvalues[self.x_pos,self.y_pos,0]
		for i in range(4):
			if self.Qvalues[self.x_pos,self.y_pos,i] > maxQvalue:
				maxQvalue = self.Qvalues[self.x_pos,self.y_pos,i]
				action = i
		return action

		

	def action_selection(self):
		""" retorna la accion selecionada segun una politica , en este caso
		epsilon greedy""" 
		aleatorio = randint(1, 100)
		action = 0

		if aleatorio >= 1 and aleatorio <= 70:
			action = self.getBestAction()
		else: action = randint(0, 3)

		return action


	def move(self,action):
		""" efectuar un movimiento dentro de la casilla """
		self.prev_x_pos = self.x_pos
		self.prev_y_pos = self.y_pos

		self.action_taken = action


		#acciones deterministicas
		if action == 0: #arriba 
			if self.x_pos-1 >= 0 and self.blocked[self.x_pos-1 , self.y_pos] == 0:
				self.x_pos -= 1
			#print("mueve hacia arriba")
		if action == 1: #derecha
			if self.y_pos+1 < self.width and self.blocked[self.x_pos,self.y_pos+1] == 0:
				self.y_pos += 1
			#print("mueve hacia la derecha")
		if action == 2: #abajo
			if self.x_pos+1 < self.height and self.blocked[self.x_pos+1,self.y_pos] == 0:
				self.x_pos += 1
			#print("mueve hacia abajo")
		if action == 3: #izquierda
			if self.y_pos-1 >= 0 and self.blocked[self.x_pos,self.y_pos-1] == 0:
				self.y_pos -= 1
			#print("mueve hacia la izquierda")		
		
		#una vez se mueve el agente ,setear el valor de la matriz en el estado anterior
		if self.maze[self.x_pos][self.y_pos] == "s":
			print(self.cum_reward)
		
		#marcar el estado previo y modificar el nuevo estado del agente
		#pygame.time.delay(5)
		self.maze[self.prev_x_pos][self.prev_y_pos] = "."
		self.maze[self.x_pos][self.y_pos] = "a"		



	def update_q_prev_state(self):
		bestAction = self.getBestAction()		#verificar que haya llegado a un estado terminal
		if not(self.x_pos == self.goalX and self.y_pos == self.goalY) or self.maze[self.x_pos][self.y_pos] == 'p':
			self.Qvalues[self.prev_x_pos, self.prev_y_pos, self.action_taken] = (1 - self.learning_rate) * self.Qvalues[self.prev_x_pos, self.prev_y_pos, self.action_taken] + self.learning_rate * (self.rewards[self.x_pos, self.y_pos] + self.discount_factor * self.Qvalues[self.x_pos, self.y_pos, bestAction])
		else:
			self.Qvalues[self.prev_x_pos, self.prev_y_pos, self.action_taken] = (1 - self.learning_rate) * self.Qvalues[self.prev_x_pos, self.prev_y_pos, self.action_taken] + self.learning_rate * (self.rewards[self.x_pos, self.y_pos] + self.Qvalues[self.x_pos, self.y_pos, bestAction])


	def Q_Learning(self):
		self.move(self.action_selection())
		self.update_q_prev_state()
		self.cum_reward += self.rewards[self.x_pos,self.y_pos]

	def training(self,numEpisode):
		global file
		while not(self.x_pos==self.goalX and self.y_pos==self.goalY):
			self.Q_Learning()
			#update de la parte grafica
			draw_map(self.surface,self.maze)
			draw_grid(self.surface)
			pygame.display.update()

		#una vez terminado un episodio,guardar episodio-recompensa,cambiar segun la recompensa sea mayor o menor
		#file.write(str(numEpisode) + " " + str(-(10000.0 -self.cum_reward)) +'\n')
		file.write(str(numEpisode) + " " + str(self.cum_reward) + '\n')

		#resetear el ambiente de entrenamiento
		self.x_pos = entrada_x
		self.y_pos = entrada_y
		self.goalX = salida_x
		self.goalY = salida_y
		self.maze[self.x_pos][self.y_pos] = "a"
		self.maze[self.goalX][self.goalY] = "s"
		self.cum_reward = 0

#metodo auxiliar para imprimir matriz
def main():
	matriz = make_maze_recursion(MAZE_WIDTH, MAZE_HEIGHT)
	surface = initialize_game()
	enviroment = Enviroment(2,matriz,surface)
	enviroment.initialize_enviroment()
	game_loop(surface, matriz , enviroment)

if __name__ == '__main__':
	main()

