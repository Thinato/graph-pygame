import pygame as pg
import pygame_gui as gui

class GUI:
	def __init__(self, screen):
		pg.init()
		self.manager = gui.UIManager(screen.get_size())
		
		self.file_window = gui.elements.UIWindow(rect=pg.Rect((screen.get_size()[0]-200, 10), (200, 215)),
			manager=self.manager, window_display_title='File Manager')
		
		self.btn_export_json = gui.elements.UIButton(relative_rect=pg.Rect((10, 10), (150, 30)),
			manager=self.manager, text='Export JSON', container=self.file_window)
		self.btn_import_json = gui.elements.UIButton(relative_rect=pg.Rect((10, 45), (150, 30)),
			manager=self.manager, text='Import JSON', container=self.file_window)
		self.btn_export_xml = gui.elements.UIButton(relative_rect=pg.Rect((10, 80), (150, 30)),
			manager=self.manager, text='Export XML', container=self.file_window)
		self.btn_import_xml = gui.elements.UIButton(relative_rect=pg.Rect((10, 115), (150, 30)),
			manager=self.manager, text='Import XML', container=self.file_window)

