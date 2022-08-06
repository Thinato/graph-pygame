import pygame as pg
from node import Node
import color
import json

class Game:
	def __init__(self):
		self.width, self.height = (800,600)
		self.screen = pg.display.set_mode((self.width, self.height))
		self.clock = pg.time.Clock()
		self.fps = 120

		self.nodes = []
		self.selected_node = None

		self.shift = False
		self.fullscreen = False

	def draw(self, screen):
		screen.fill(color.black)


		for node in self.nodes:
			node.update_connections(screen)

		for node in self.nodes:
			node.update(screen)


		pg.display.flip()

	def handle_event(self, event):
		if event.type == pg.QUIT:
			pg.quit()
			exit()
		elif event.type == pg.KEYDOWN:
			if event.mod & pg.KMOD_SHIFT:
				self.shift = True

			elif event.key == pg.K_DELETE:
				self.nodes.remove(self.selected_node)
				for node in self.nodes:
					node.check_connections(self.selected_node)
				self.selected_node = None

			elif event.key == pg.K_F11:
				if self.fullscreen:
					self.screen = pg.display.set_mode((self.width, self.height))
					self.fullscreen = False
				else:
					self.screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
					self.fullscreen = True
				# self.camera.update_screen_size(self.screen.get_size())

		elif event.type == pg.KEYUP:
			if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
				self.shift = False
				for node in self.nodes:
					if node.connecting:
						node.connecting = False



		elif event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1: # select node
				pos = pg.mouse.get_pos()
				connecting = False

				for node in self.nodes:
					node.selected = False
					# self.selected_node = None
					if node.connecting:
						connecting = True 

				if not self.shift or not self.selected_node:
					for node in list(reversed(self.nodes)):
						if (pos[0] - node.x)**2 + (pos[1] - node.y)**2 < node.radius**2:
							node.selected = True
							node.drag = True
							self.selected_node = node
							if self.shift:
								connecting = True
								node.connecting = True
							return
				elif self.selected_node:
					for node in list(reversed(self.nodes)):
						if not connecting:
							if (pos[0] - node.x)**2 + (pos[1] - node.y)**2 < node.radius**2:
								node.selected = True
								node.drag = True
								self.selected_node = node
								node.connecting = True
						else:
							if (pos[0] - node.x)**2 + (pos[1] - node.y)**2 < node.radius**2:
								target = node
								if self.selected_node:
									self.selected_node.connections.append(target)
									self.selected_node = None

		elif event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				for node in self.nodes:
					node.drag = False


						

			elif event.button == 3: # add node
				self.add_node(pg.mouse.get_pos())



	def add_node(self, position):
		for node in self.nodes:
			node.selected = False
		node = Node(position, str(len(self.nodes)))
		self.selected_node = node
		self.nodes.append(node)

	def start(self):
		while True:
			self.draw(self.screen)
			for event in pg.event.get():
				self.handle_event(event)

if __name__ == '__main__':
	Game().start()