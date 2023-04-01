import pygame as pg
from typing import Type
import os
from random import randint
import math

pg.init()


class Node:
    """
    Usada para representar as Vértices do Grafo
    cada vértice possuí um índice (index) para identificação

    """

    def __init__(self, index: int, pos: tuple = (100, 100), value: int = 0):
        self.index = index
        self.edge_list = []
        self.value = value

        # variaveis gráficas para o pygame
        self.radius = 10
        # self.pos = pg.math.Vector2(randint(100,300), randint(50,250))
        self.pos = pg.math.Vector2(pos)
        self.dir = pg.math.Vector2()
        self.color = (255, 255, 255)
        self.speed = pg.math.Vector2()
        self.threshold = 40
        self.boundaries = (400, 300)
        self.selected = False
        self.selected_color = (255, 128, 0)
        self.font = pg.font.SysFont("Lucida Console", 10)
        if self.value:
            self.rendered = self.font.render(str(self.value), True, (0, 0, 0))
        else:
            self.rendered = self.font.render(str(self.index), True, (0, 0, 0))
        self.acc = 20

    def __str__(self) -> str:
        return f"Vértice{self.index}"

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "position": (self.pos.x, self.pos.y),
            "value": self.value,
        }

    # métodos para o pygame
    def update(self, screen, dt, debug, mpos=None, performance=False) -> None:
        if mpos and self.selected:
            self.pos.xy = mpos
        elif not performance:
            self.move(dt)
        if self.selected:
            pg.draw.circle(screen, self.selected_color, self.pos, self.radius + 3)
        pg.draw.circle(screen, self.color, self.pos, self.radius)
        if debug > 1:
            pg.draw.circle(screen, (0, 0, 255), self.pos, self.threshold, 1)
        if not performance:
            screen.blit(
                self.rendered,
                self.pos - (self.rendered.get_width() / 2, self.rendered.get_height() / 2),
            )

    def move(self, dt):
        if self.dir.magnitude() > 0:
            self.pos += (self.dir.x * self.speed.x * dt, self.dir.y * self.speed.y * dt)

        if self.pos.x < 0 + self.radius:
            self.dir.x *= -1
            self.pos.x = self.radius + 1
        elif self.pos.x > 400 - self.radius:
            self.dir.x *= -1
            self.pos.x = 400 - self.radius - 1

        if self.pos.y < 0 + self.radius:
            self.dir.y *= -1
            self.pos.y = self.radius + 1
        elif self.pos.y > 300 - self.radius:
            self.dir.y *= -1
            self.pos.y = 300 - self.radius - 1
        
        if self.speed.x > 0:
            self.speed.x -= self.acc * dt
            if self.speed.x < 0:
                self.speed.x = 0
        if self.speed.y > 0:
            self.speed.y -= self.acc * dt
            if self.speed.y < 0:
                self.speed.y = 0



class Edge:
    def __init__(self, index: int, nodes: tuple, value: int = 0):
        self.index = index
        self.nodes = nodes
        self.value = value
        self.nodes[0].edge_list.append(self)
        self.nodes[1].edge_list.append(self)

        # pygame
        self.thickness = 2
        self.line_color = (0,255,0)
        self.color = (0,255,0)
        self.font = pg.font.SysFont("Lucida Console", 10)

    def __str__(self) -> str:
        return f"{self.nodes[0]} -> {self.nodes[1]}"

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "nodes": (self.nodes[0].index, self.nodes[1].index),
            "value": self.value,
        }
    
    def set_color(self, color: tuple = (0,255,0)) -> None:
        self.color = color

    def update(self, screen, debug, performance=False):
        pg.draw.line(
            screen, self.line_color, self.nodes[0].pos, self.nodes[1].pos, self.thickness
        )
        angle = math.atan2(
            self.nodes[0].pos.y - self.nodes[1].pos.y,
            self.nodes[0].pos.x - self.nodes[1].pos.x,
        )
        dx = math.cos(angle) * 10
        dy = math.sin(angle) * 10
        if performance:
            pg.draw.rect(screen, (0,255,0), (self.nodes[1].pos+(dx-10,dy-10), (20,20)))
        else:
            a = self.nodes[1].pos + (dx, dy)
            ax = math.cos(angle + 0.5) * 15
            ay = math.sin(angle + 0.5) * 15
            pg.draw.line(screen, self.color, a, a + (ax, ay), self.thickness)
            ax = math.cos(angle - 0.5) * 15
            ay = math.sin(angle - 0.5) * 15
            pg.draw.line(screen, self.color, a, a + (ax, ay), self.thickness)
            if self.value:
                txt = self.font.render(str(self.value), True, self.color)
                screen.blit(
                    txt, 
                    ((self.nodes[0].pos.x + self.nodes[1].pos.x + ax*-2)/2,
                    (self.nodes[0].pos.y + self.nodes[1].pos.y + ay*-2)/2)
                )


if __name__ == "__main__":
    # limpa a tela caso esteja usando windows
    if os.name == "nt":
        os.system("cls")
    nodes = int(input("Quantos vértices tem o seu Grafo? "))
    edges = int(input("Quantas arestas tem o seu Grafo? "))

    node_list = [Node(i) for i in range(nodes)]

    print()
    for node in node_list:
        print(f"{node} -->")
    print()

    for i in range(edges):
        node1 = int(input("De qual vértice SAI esta aresta? "))
        node2 = int(input("Em qual vértice INCIDE esta aresta? "))

        Edge(i, (node_list[node1], node_list[node2]))
    print()

    for node in node_list:
        print(f"{node} --> ", end="")
        # print(*node.edge_list, sep=', ')

        for edge in node.edge_list:
            if node == edge.nodes[0]:
                print(edge, end="  ")
            else:
                print(f"{edge.nodes[1]} <- {edge.nodes[0]}", end="  ")
        else:
            print()
