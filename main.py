import pygame as pg
import pygame_gui
from graph import *
import math
from random import randint, sample
import json
import os
import subprocess


pg.init()
pg.display.set_caption('APS 2 - Paulo Lisecki - Editor de Grafos')
width, height = 800, 600
screen = pg.display.set_mode((width, height), pg.DOUBLEBUF | pg.RESIZABLE)
clock = pg.time.Clock()
manager = pygame_gui.UIManager((width, height))

def break_text(text, limit=33) -> list:
    lst = []
    concat = ''
    counter = 0
    for word in text.split():
        if len(word) + counter > limit:
            lst.append(concat)
            concat = ''
            counter = 0
        concat += word + ' '
        counter += len(word)+1
    lst.append(concat)
    return lst
        
def incidence_list(node_list) -> str:
    res = ""

    for node in node_list:
        res += f"<b>{str(node).ljust(9)} --> </b>"
        for edge in node.edge_list:
            if node == edge.nodes[0]:
                res += (
                    f"<font color=#00FF00>-a{str(edge.index).ljust(2,'-')}-></font>  "
                )
            else:
                res += (
                    f"<font color=#00FF00><-a{str(edge.index).ljust(2,'-')}-</font>  "
                )
        else:
            res += "\n"
    return res

def json_to_graph(data):
    nodes, edges = list(), list()
    for node in data["Nodes"]:
        nodes.append(Node(node["index"], node["position"], node["value"]))

    for edge in data["Edges"]:
        edges.append(
            Edge(
                edge["index"],
                (nodes[edge["nodes"][0]], nodes[edge["nodes"][1]]),
                edge["value"],
            )
        )
    return nodes, edges

def random_graph(node_list, edge_list, random_range, highlight_dir, weight=False):
    if weight:
        node_list = [
            Node(i, (randint(50, 300), randint(50, 300)), randint(-50, 150))
            for i in range(randint(*random_range))
        ]
    else:
        node_list = [
            Node(i, (randint(50, 300), randint(50, 300)))
            for i in range(randint(*random_range))
        ]
    edge_list = []
    cache = {}
    recount = 0
    for i in range(randint(len(node_list), len(node_list) + 8)):
        i -= recount
        a, b = sample(range(len(node_list)), 2)
        # hashmap para evitar repetições
        if a in cache and cache[a] == b:
            recount += 1
            continue
        cache[a] = b
        edge_list.append(Edge(i, (node_list[a], node_list[b])))
        if highlight_dir:
            edge_list[i].set_color((randint(0,255), randint(0,255), randint(0,255)))
        if weight:
            edge_list[i].value = randint(-50, 150)
    return node_list, edge_list


def mininal_dist(node, dist) -> dict:
    for edge in node.edge_list:
        if edge.nodes[1] == node:
            continue
        
        if edge.value < dist[edge.nodes[1]][0]:
            dist[edge.nodes[1]] = (dist[node][0] + edge.value, node, edge)
            # dist[edge.nodes[1]] = (edge.value, node)
            dist = mininal_dist(edge.nodes[1], dist)

    return dist


def search_node(node1, node2, node_list, edge_list):
    dist = dict()
    for edge in edge_list:
        edge.color = (0,255,0)
        edge.line_color = (0,255,0)
    for node in node_list:
        node.color = (255,255,255)
        dist[node] = (math.inf, node1, None)
    dist[node1] = (0, node1, None)
    
    dist = mininal_dist(node1, dist)

    path = [node2]
    node2.color = (202, 53, 232)
    if dist[node2][0] < math.inf:
        curr = dist[node2][1], dist[node2][2]
        
        for _ in range(len(node_list)):
            path.append(curr[0])
            curr[0].color = (76, 207, 174)
            if curr[1]:
                curr[1].color = (255,0,255)
                curr[1].line_color = (255,0,255)
            if curr[0] == node1:
                path.reverse()
                return path

            curr = dist[curr[0]][1], dist[curr[0]][2]
    else:
        return path

plot_area = 400, 300
node_list = [Node(0), Node(1)]
edge_list = [
    Edge(0, (node_list[0], node_list[1])),
]

current_node = len(node_list)
current_edge = len(edge_list)
debug = 0
font = pg.font.SysFont("Lucida Console", 20)
mdown = False
managing_file = False
double_click_timer = 225
last_click = 0
shift_active = False
selected_node = None
# o modo performance chega a aumentar em até 56% a taxa de quadros
performance_mode = False
random_range = (8,16)
tutorial = True
tutorial_prog = 0
if os.path.exists('tutorial'):
    tutorial = False

tutorial_text = {
    0: break_text('Crie um vértice dando dois cliques no campo (canto superior esquerdo).'),
    1: break_text('Clique no vértice para seleciona-lo!'),
    2: break_text('Agora segure SHIFT para conecta-lo em outro vértice!'),
    3: break_text('Clique em outro vértice para conectar!'),
    4: break_text('Parabéns! Você completou o Tutorial!'),
}

win_output = pygame_gui.elements.UIWindow(
    manager=manager,
    rect=pg.Rect((0, 300), (800, 310)),
    window_display_title="Output",
    resizable=True,
)

txt_incidence = pygame_gui.elements.UITextBox(
    manager=manager,
    html_text=incidence_list(node_list),
    relative_rect=pg.Rect((0, 0), (768, 220)),
    container=win_output,
    anchors={
        "left": "left",
        "right": "right",
        "bottom": "bottom",
        "top": "top",
    },
)

btn_export = pygame_gui.elements.UIButton(
    manager=manager,
    text="Exportar",
    relative_rect=pg.Rect(0, -28, 100, 26),
    container=win_output,
    anchors={"top": "bottom", "left": "left", "bottom": "bottom", "right": "left"},
)

btn_import = pygame_gui.elements.UIButton(
    manager=manager,
    text="Importar",
    relative_rect=pg.Rect(100, -28, 100, 26),
    container=win_output,
    anchors={"top": "bottom", "left": "left", "bottom": "bottom", "right": "left"},
)

fd_import = pygame_gui.windows.UIFileDialog(
    manager=manager,
    rect=pg.Rect(0, 0, 400, 400),
    window_title="Importar Grafo...",
    visible=0,
    initial_file_path="grafos",
)

check_highlight_dir = pygame_gui.elements.UIButton(
    manager= manager,
    text= '[ ] Destacar direção',
    relative_rect=pg.Rect(220, -28, 190, 26),
    container=win_output,
    anchors={"top": "bottom", "left": "left", "bottom": "bottom", "right": "left"},
)
highlight_dir = False

check_shortest_path = pygame_gui.elements.UIButton(
    manager= manager,
    text= '[ ] Caminho Mínimo',
    relative_rect=pg.Rect(410, -28, 180, 26),
    container=win_output,
    anchors={"top": "bottom", "left": "left", "bottom": "bottom", "right": "left"},
)
shortest_path_menu = False

lbl_nodes_from = pygame_gui.elements.UILabel(
    manager=manager,
    text= 'De:',
    relative_rect= pg.Rect( (10,10), (100, 24) ),
    visible=0,
    container=win_output
)

lbl_nodes_to = pygame_gui.elements.UILabel(
    manager=manager,
    text= 'Até:',
    relative_rect= pg.Rect( (10,40), (100, 24) ),
    visible=0,
    container=win_output
)

cmb_nodes_from = pygame_gui.elements.UIDropDownMenu(
    manager=manager,
    starting_option='Selecione',
    relative_rect=pg.Rect((120,10), (200, 24)),
    container=win_output,
    visible=0,
    options_list=[ f'v{node.index} ({node.value})' for node in node_list ]
)

cmb_nodes_to = pygame_gui.elements.UIDropDownMenu(
    manager=manager,
    starting_option='Selecione',
    relative_rect=pg.Rect((120,40), (200, 24)),
    container=win_output,
    visible=0,
    options_list=[ f'v{node.index} ({node.value})' for node in node_list ]
)

btn_search_node = pygame_gui.elements.UIButton(
    manager=manager,
    text= 'Procurar',
    relative_rect= pg.Rect((10, 70), (100, 24)),
    visible=0,
    container=win_output
)

lbl_search_result = pygame_gui.elements.UILabel(
    manager=manager,
    text= '',
    relative_rect= pg.Rect((120, 70), (400, 24)),
    visible=0,
    container=win_output
)

def update_controls():
    cmb_nodes_from.remove_options(cmb_nodes_from.options_list)
    cmb_nodes_from.selected_option = 'Selecione'
    cmb_nodes_from.add_options(['Selecione'])
    cmb_nodes_from.add_options([ f'V{str(node.index).ljust(2)} ({node.value})' for node in node_list ])

    cmb_nodes_to.remove_options(cmb_nodes_to.options_list)
    cmb_nodes_to.selected_option = 'Selecione'
    cmb_nodes_to.add_options(['Selecione'])
    cmb_nodes_to.add_options([ f'V{str(node.index).ljust(2)} ({node.value})' for node in node_list ])

    txt_incidence.clear()
    txt_incidence.append_html_text(incidence_list(node_list))


while True:
    dt = clock.tick() / 1000
    mpos = pg.mouse.get_pos()
    for event in pg.event.get():
        manager.process_events(event)
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        elif event.type == pg.VIDEORESIZE:
            manager.set_window_resolution((event.w, event.h))
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_k:
                node_list.append(Node(current_node))
                current_node += 1
                txt_incidence.clear()
                txt_incidence.append_html_text(incidence_list(node_list))
            elif event.key == pg.K_LSHIFT:
                if tutorial and tutorial_prog == 2:
                    tutorial_prog = 3
                shift_active = True
            elif event.key == pg.K_c:
                node_list = []
                edge_list = []
                current_node = 0
                current_edge = 0
                txt_incidence.clear()
                txt_incidence.append_html_text(incidence_list(node_list))
            elif event.key == pg.K_F1:
                debug += 1
                debug = debug % 3
            elif event.key == pg.K_F2:
                performance_mode = not performance_mode
            elif event.key == pg.K_F3:
                for node in node_list:
                    if node.acc == 20:
                        node.acc = 0.01
                    else:
                        node.acc = 20
            elif event.key == pg.K_DELETE:
                if selected_node:
                    to_remove = []
                    for edge in edge_list:
                        if edge.nodes[0] == selected_node or edge.nodes[1] == selected_node:
                            to_remove.append(edge)
                    
                    for edge in to_remove:
                        edge_list.remove(edge)

                    for node in node_list:
                        for edge in to_remove:
                            if edge in node.edge_list:
                                node.edge_list.remove(edge)
                                

                    

                    node_list.remove(selected_node)

                    txt_incidence.clear()
                    txt_incidence.append_html_text(incidence_list(node_list))
            elif event.key == pg.K_F5:  # gerar grafo aleatório
                selected_node = None
                node_list, edge_list = random_graph(node_list, edge_list, random_range, highlight_dir)
                update_controls()
                
                current_node = len(node_list)
                current_edge = len(edge_list)
            elif event.key == pg.K_F6:  # gerar grafo aleatório com pesos
                selected_node = None
                node_list, edge_list = random_graph(node_list, edge_list, random_range, highlight_dir, True)
                update_controls()
                current_node = len(node_list)
                current_edge = len(edge_list)
            elif event.key == pg.K_1:
                random_range = (8,16)
            elif event.key == pg.K_2:
                random_range = (16,24)
            elif event.key == pg.K_3:
                random_range = (24,32)
            elif event.key == pg.K_4:
                random_range = (32,40)
            elif event.key == pg.K_5:
                random_range = (40,50)
        elif event.type == pg.KEYUP:
            if event.key == pg.K_LSHIFT:
                if tutorial:
                    if tutorial_prog == 3:
                        tutorial_prog = 2
                shift_active = False

        elif event.type == pg.MOUSEBUTTONUP:
            if managing_file:
                continue
            tick = pg.time.get_ticks()
            if tick < last_click + double_click_timer and not shift_active:
                if mpos[0] < 400 and mpos[1] < 300 and event.button == 1:
                    node_list.append(Node(current_node, mpos))
                    current_node += 1
                    txt_incidence.clear()
                    txt_incidence.append_html_text(incidence_list(node_list))
                    if tutorial and tutorial_prog == 0:
                        tutorial_prog = 1
                # para evitar 3 cliques
                last_click = tick - double_click_timer
            else:
                last_click = tick
            mdown = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            if tutorial_prog == 4:
                tutorial_prog = 0
                tutorial = False
                open('tutorial', 'w').close()
                subprocess.check_call(['attrib','+H','tutorial']) 
            if managing_file:
                continue
            if event.button == 1:
                mdown = True
                for node in node_list:
                    if not shift_active:
                        selected_node = None
                    node.selected = False
                    if tutorial and tutorial_prog == 2:
                        tutorial_prog = 1
                if mpos[0] < plot_area[0] and mpos[1] < plot_area[1]:
                    for node in node_list:
                        if (
                            math.hypot(node.pos.x - mpos[0], node.pos.y - mpos[1])
                            < node.radius
                        ):
                            if shift_active and selected_node:
                                for edge in selected_node.edge_list:
                                    if edge.nodes[1] == node:
                                        break
                                else:
                                    if tutorial and tutorial_prog == 3:
                                        tutorial_prog = 4
                                    edge_list.append(Edge( current_edge, (selected_node, node) ))
                                    update_controls()
                                    current_node = len(node_list)
                                    current_edge = len(edge_list)
                            if tutorial and tutorial_prog == 1:
                                tutorial_prog = 2
                            selected_node = node
                            node.selected = True
                            break

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == btn_export:
                count = len(os.listdir("grafos/"))
                path = f"grafos/grafo{count}.json"
                data = {
                    "Nodes": [i.to_dict() for i in node_list],
                    "Edges": [i.to_dict() for i in edge_list],
                }
                with open(path, "w") as f:
                    f.write(json.dumps(data, indent=2))
                    f.close()
            elif event.ui_element == btn_import:
                managing_file = True
                fd_import = pygame_gui.windows.UIFileDialog(
                    manager=manager,
                    rect=pg.Rect(0, 0, 400, 400),
                    window_title="Importar Grafo...",
                    visible=1,
                    initial_file_path="grafos",
                )
            elif event.ui_element == check_highlight_dir:
                highlight_dir = not highlight_dir
                if highlight_dir:
                    check_highlight_dir.set_text('[X] Destacar direção')
                    for edge in edge_list:
                        edge.set_color((randint(0,255), randint(0,255), randint(0,255)))
                else:
                    check_highlight_dir.set_text('[ ] Destacar direção')
                    for edge in edge_list:
                        edge.set_color()
            elif event.ui_element == check_shortest_path:
                shortest_path_menu = not shortest_path_menu
                if shortest_path_menu:
                    check_shortest_path.set_text('[X] Caminho Mínimo')
                    update_controls()
                    current_node = len(node_list)
                    current_edge = len(edge_list)
                    txt_incidence.hide()
                    cmb_nodes_from.show()
                    cmb_nodes_to.show()
                    lbl_nodes_from.show()
                    lbl_nodes_to.show()
                    btn_search_node.show()
                    lbl_search_result.show()
                else:
                    check_shortest_path.set_text('[ ] Caminho Mínimo')
                    txt_incidence.show()
                    cmb_nodes_from.hide()
                    cmb_nodes_to.hide()
                    lbl_nodes_from.hide()
                    lbl_nodes_to.hide()
                    btn_search_node.hide()
                    lbl_search_result.hide()

            elif event.ui_element == btn_search_node:
                if cmb_nodes_from.selected_option == 'Selecione' or cmb_nodes_to.selected_option == 'Selecione':
                    lbl_search_result.set_text('Selecione dois Vértices, por favor.')
                    continue
                for node in node_list:
                    if node.index == int(cmb_nodes_from.selected_option[1:3]):
                        node1 = node
                    if node.index == int(cmb_nodes_to.selected_option[1:3]):
                        node2 = node

                if node1 and node2:
                    result = search_node(node1, node2, node_list, edge_list)
                    print(result)
                    result = [str(i) for i in result]
                    lbl_search_result.set_text(str(result))
                else:
                    lbl_search_result.set_text(f'Não foi possível encontrar {cmb_nodes_from.selected_option} ou {cmb_nodes_to.selected_option}')


        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == fd_import:
                managing_file = False
                data = ""
                with open(event.text, "r") as f:
                    data = f.read()
                    f.close()
                node_list, edge_list = json_to_graph(json.loads(data))
                update_controls()
                current_node = len(node_list)
                current_edge = len(edge_list)

    screen.fill((0, 0, 0))
    pg.draw.rect(screen, (255, 255, 255), ((0, 0), (400, 300)), 1)

    for edge in edge_list:
        edge.update(screen, debug, performance_mode)

    if shift_active and selected_node:
        pg.draw.line(screen, (0,255,0), selected_node.pos, mpos, 2)
        
        if not performance_mode:
            angle = math.atan2(
                selected_node.pos.y - mpos[1],
                selected_node.pos.x - mpos[0]
            )
            dx = math.cos(angle)
            dy = math.sin(angle)
            a = pg.math.Vector2(mpos[0] + dx, mpos[1] + dy)
            ax = math.cos(angle + 0.5) * 15
            ay = math.sin(angle + 0.5) * 15
            pg.draw.line(screen, (0, 255, 0), a, a + (ax, ay), 2)
            ax = math.cos(angle - 0.5) * 15
            ay = math.sin(angle - 0.5) * 15
            pg.draw.line(screen, (0, 255, 0), a, a + (ax, ay), 2)



    for i, node in enumerate(node_list):
        if not performance_mode:
            for nodex in node_list:
                if nodex == node:
                    continue
                dx = node.pos.x - nodex.pos.x
                dy = node.pos.y - nodex.pos.y
                dist = math.hypot(dx, dy)
                if dist < node.threshold:
                    speed = 50 * dt
                    node.speed.xy  = (speed, speed)
                    nodex.speed.xy = (speed, speed)
                    angle = (math.pi / 2) * math.atan2(dy, dx)
                    node.dir.x += math.sin(angle)
                    node.dir.y -= math.cos(angle)
                    nodex.dir.x -= math.sin(angle)
                    nodex.dir.y += math.cos(angle)
        if mdown:
            node.update(screen, dt, debug, (mpos), performance_mode)
        else:
            node.update(screen, dt, debug, performance=performance_mode)

    if tutorial:
        for i, txt in enumerate(tutorial_text[tutorial_prog]):
            screen.blit(
                font.render(txt, True, (255, 255, 255), (0, 0, 0)), (405, 150 + 24 * i)
            )
    
    if debug > 0:
        debug_info = [
            f"FPS: {int(clock.get_fps())}",
            f"Nodes: {len(node_list)}",
            f"Edges: {len(edge_list)}",
            f"PM: {performance_mode}",
            f"Random Range: {random_range}",
        ]
        if selected_node:
            debug_info.append(f'Node Index: {selected_node.index}')
            debug_info.append(f'Node Value: {selected_node.value}')
            debug_info.append(f'Node Edges: {len(selected_node.edge_list)}')
        for i, info in enumerate(debug_info):
            screen.blit(
                font.render(info, True, (255, 255, 255), (0, 0, 0)), (405, 5 + 16 * i)
            )


    manager.update(dt)
    manager.draw_ui(screen)

    pg.display.update()
