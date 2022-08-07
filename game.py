import pygame as pg
from node import Node
import color
import json
from copy import copy

class Game:
	def __init__(self):
		self.width, self.height = (800,600)
		self.screen = pg.display.set_mode((self.width, self.height))
		self.clock = pg.time.Clock()
		self.fps = 120

		self.nodes = {}
		self.selected_node = None
		self.node_index = 0

		self.shift = False
		self.fullscreen = False


	def draw(self, screen):
		screen.fill(color.black)


		for node in self.nodes:
			self.nodes[node].update_connections(screen)

		for node in self.nodes:
			self.nodes[node].update(screen)


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


			elif event.key == pg.K_F2:
				self.export_json('nodes.json')

			elif event.key == pg.K_F3:
				self.import_json('nodes.json')

		elif event.type == pg.KEYUP:
			if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
				self.shift = False
				for node in self.nodes:
					if self.nodes[node].connecting:
						self.nodes[node].connecting = False



		elif event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1: # select node
				pos = pg.mouse.get_pos()
				connecting = False

				for node in self.nodes:
					self.nodes[node].selected = False
					# self.selected_node = None
					if self.nodes[node].connecting:
						connecting = True 

				if not self.shift or not self.selected_node:
					for node in list(reversed(self.nodes)):
						if (pos[0] - self.nodes[node].x)**2 + (pos[1] - self.nodes[node].y)**2 < self.nodes[node].radius**2:
							self.nodes[node].selected = True
							self.nodes[node].drag = True
							self.selected_node = self.nodes[node]
							if self.shift:
								connecting = True
								self.nodes[node].connecting = True
							return
				elif self.selected_node:
					for node in list(reversed(self.nodes)):
						if not connecting:
							if (pos[0] - self.nodes[node].x)**2 + (pos[1] - self.nodes[node].y)**2 < self.nodes[node].radius**2:
								self.nodes[node].selected = True
								self.nodes[node].drag = True
								self.selected_node = self.nodes[node]
								self.nodes[node].connecting = True
						else:
							if (pos[0] - self.nodes[node].x)**2 + (pos[1] - self.nodes[node].y)**2 < self.nodes[node].radius**2:
								target = self.nodes[node]
								if self.selected_node:
									self.selected_node.connections[target.index] = target
									self.selected_node = None

		elif event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				for node in self.nodes:
					self.nodes[node].drag = False


						

			elif event.button == 3: # add node
				self.add_node(pg.mouse.get_pos())



	def add_node(self, position, _node=None):
		for node in self.nodes:
			self.nodes[node].selected = False

		if not _node:
			node = Node(position, 'Node'+str(self.node_index), str(self.node_index))
		else:
			node = _node
		self.selected_node = node
		self.nodes['Node'+str(self.node_index)] = node

		self.node_index += 1

	def export_json(self, filename):
		n = copy(self.nodes)
		for node in n:
			n[node] = n[node].to_dict()

		with open(filename, 'w') as f:
			json.dump(n, f, indent=2)
		print('nodes exported')

	def import_json(self, filename):
		with open(filename, 'r') as f:
			data = json.load(f)

		for index in data:
			node = Node((data[index]['x'],data[index]['y']), index, data[index]['name'])
			node.radius = data[index]['radius']
			node.selected = False
			self.nodes[index] = node
		
		for index in data:
			for conn in data[index]['connections']:
				self.nodes[index].connections[conn] = self.nodes[conn]

		print('nodes imported')

	def start(self):
		while True:
			self.draw(self.screen)
			for event in pg.event.get():
				self.handle_event(event)

if __name__ == '__main__':
	Game().start()