import pygame as pg
import math
import color

class Node:
	def __init__(self, pos, name='Node'):
		pg.font.init()

		self._circle_cache = {}
		self.font_size = 14
		self.font = pg.font.SysFont('Segoe UI', self.font_size)

		self.name_width = 0
		self.name = self.render(name, self.font, color.white)
		self.x = pos[0]
		self.y = pos[1]
		self.radius = 20
		self.connections = []
		self.connecting = False
		self.selected = True

		self.drag = False

	def update_connections(self, screen):
		for connection in self.connections:
			pg.draw.line(screen, color.white, (self.x, self.y), (connection.x, connection.y))

	def update(self, screen):
		if self.selected:
			if self.connecting:
				pg.draw.line(screen, color.connecting, (self.x, self.y), pg.mouse.get_pos())
			if self.drag:
				mouse = pg.mouse.get_pos()
				self.x = mouse[0]
				self.y = mouse[1]
			pg.draw.circle(screen, color.selected, (self.x, self.y), self.radius+3)
		

		pg.draw.circle(screen, color.white, (self.x, self.y), self.radius)

		screen.blit(self.name, (self.x - self.name_width//2, self.y - self.font_size))

	def check_connections(self, deleted_node):
		for node in self.connections:
			if node == deleted_node:
				self.connections.remove(node)


	def _circlepoints(self, r):
		r = int(round(r))
		if r in self._circle_cache:
			return self._circle_cache[r]
		x, y, e = r, 0, 1 - r
		self._circle_cache[r] = points = []
		while x >= y:
			points.append((x, y))
			y += 1
			if e < 0:
				e += 2 * y - 1
			else:
				x -= 1
				e += 2 * (y - x) - 1
		points += [(y, x) for x, y in points if x > y]
		points += [(-x, y) for x, y in points if x]
		points += [(x, -y) for x, y in points if y]
		points.sort()
		return points

	def render(self, text, font, gfcolor=(255,0,0), ocolor=(0,0,0), opx=2):
		textsurface = font.render(text, True, gfcolor).convert_alpha()
		w = textsurface.get_width() + 2 * opx
		self.name_width = w
		h = font.get_height()

		osurf = pg.Surface((w, h + 2 * opx)).convert_alpha()
		osurf.fill((0, 0, 0, 0))

		surf = osurf.copy()

		osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

		for dx, dy in self._circlepoints(opx):
			surf.blit(osurf, (dx + opx, dy + opx))

		surf.blit(textsurface, (opx, opx))
		return surf

