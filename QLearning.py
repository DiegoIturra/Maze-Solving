import pygame
import sys
from random import uniform,randint
import constants
import numpy as np

done = False

def read_map(mapfile):
	""" Lee el fichero con los caracteres y devuelve una matriz en base a ese fichero """
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

#decorador para obtener posiciones de simbolos dentro del laberinto
def getPosition(mapfile,simbolo):
	def decoradorFuncion(funcion):
		def funcionDecorada():
			with open(mapfile , 'r') as f:
				world_map = f.readlines()
			world_map = [line.strip() for line in world_map]
			x = y = 0
			for i in range(constants.NUMBER_OF_BLOCKS_HIGH):
				for j in range(constants.NUMBER_OF_BLOCKS_WIDE):
					if world_map[i][j] == simbolo:
						x = i
						y = j
						break
			return (x,y)
		return funcionDecorada
	return decoradorFuncion

#devuelve la posicion del agente en el inicio
@getPosition(constants.MAPFILE,'a')
def getStart():
	pass

#devuelve la posicion del estado objetivo
@getPosition(constants.MAPFILE,'s')
def getGoalPosition():
	pass


def get_tile_color(tile_contents):
	""" retorna el tipo de color segun el caracter 
	leido en una casilla """
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
	""" Dibuja el laberinto en pantalla """
	for i in range(len(matriz)):
		for j in range(len(matriz[i])):
			myrect = pygame.Rect(j*constants.BLOCK_WIDTH,i*constants.BLOCK_HEIGHT,constants.BLOCK_WIDTH,constants.BLOCK_HEIGHT)
			pygame.draw.rect(surface,get_tile_color(matriz[i][j]),myrect)

def draw_grid(surface):
	""" Dibuja las casillas del laberinto """
	for i in range(constants.NUMBER_OF_BLOCKS_WIDE):
		new_height = round(i * constants.BLOCK_HEIGHT)
		new_width = round(i * constants.BLOCK_WIDTH)
		pygame.draw.line(surface , constants.BLACK , (0,new_height) , (constants.SCREEN_WIDTH,new_height),2)
		pygame.draw.line(surface , constants.BLACK , (new_width,0) , (new_width,constants.SCREEN_HEIGHT) ,2)

def initialize_game():
	""" Setea el ambiente inicial y devuelve el surface para poder setearlo """
	pygame.init()
	surface = pygame.display.set_mode((constants.SCREEN_WIDTH , constants.SCREEN_HEIGHT))
	pygame.display.set_caption("")
	surface.fill(constants.WHITE)
	return surface

def game_loop(surface, matriz , enviroment):
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
		if not done:
			#llamar a Q-Learning
			for i in range(200):
				pygame.display.set_caption(f"Episode number {i+1}")
				enviroment.training()
			done = True
		draw_map(surface,matriz)
		draw_grid(surface)
		pygame.display.update()


class Enviroment():

	def __init__(self,numEpisodes,matriz,surface):
		""" establecer parametros """
		self.numEpisodes = numEpisodes
		#alto y ancho del laberinto
		self.height = constants.NUMBER_OF_BLOCKS_HIGH
		self.width = constants.NUMBER_OF_BLOCKS_WIDE
		self.learning_rate = 0.1 #taza de aprendizaje
		self.discount_factor = 0.99 #factor de descuento
		self.exp_rate = 0.3

		#matriz de valores de Q
		self.Qvalues = np.zeros(shape=[20,20,4])
		#matriz de recompensas
		self.rewards = np.zeros(shape=(20,20))
		#matriz que indica posiciones con muros
		self.blocked = np.zeros(shape=(20,20))
		#matriz con caracteres
		self.maze = matriz


		self.x_pos,self.y_pos = getStart()

		self.prev_x_pos = 0
		self.prev_y_pos = 0

		self.action_taken = 0

		self.cum_reward = 0.0

		self.surface = surface



	def initialize_enviroment(self):
		""" setear entorno inicial """
		self.init_x_pos,self.init_y_pos = getStart()
		self.goalX,self.goalY = getGoalPosition()

		for i in range(self.height):
			for j in range(self.width):
				self.rewards[i,j] = -0.04
				if self.maze[i][j] == 'm': #si hay una pared , marcarlo
					self.blocked[i,j] = 1

				if self.maze[i][j] == 'p':
					self.rewards[i,j] = -300.0 #si hay un agujero ,la recompensa disminuye baastante

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


		#no hay acciones estocasticas
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
		pygame.time.delay(10)
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

	def training(self):
		while not(self.x_pos==self.goalX and self.y_pos==self.goalY):
			self.Q_Learning()
			#update de la parte grafica
			draw_map(self.surface,self.maze)
			draw_grid(self.surface)
			pygame.display.update()
		#resetear el ambiente de entrenamiento
		self.x_pos,self.y_pos = getStart()
		self.goalX,self.goalY = getGoalPosition()
		self.maze[self.x_pos][self.y_pos] = "a"
		self.maze[self.goalX][self.goalY] = "s"
		self.cum_reward = 0

#metodo auxiliar para imprimir matriz
def printMaze(matriz):
	for i in range(constants.NUMBER_OF_BLOCKS_HIGH):
		for j in range(constants.NUMBER_OF_BLOCKS_WIDE):
			print(matriz[i,j],end=" ")
		print()
	print()

def main():
	matriz = read_map(constants.MAPFILE)
	surface = initialize_game()
	enviroment = Enviroment(2,matriz,surface)
	enviroment.initialize_enviroment()
	game_loop(surface, matriz , enviroment)

if __name__ == '__main__':
	main()

