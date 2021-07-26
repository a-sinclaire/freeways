import random
import time

import matplotlib.pyplot as plt
import shapely
import copy
import networkx as nx
from shapely.geometry import LineString, Point
import pygame
import numpy as np

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode([800, 600])
myfont = pygame.font.SysFont('Comic Sans MS', 30)

segment_list = []


def dist(x1, y1, x2, y2):
    return np.sqrt(np.power(x1-x2, 2)+np.power(y1-y2, 2))


def angle_diff(ang1, ang2):
    return min((2*np.pi) - abs(ang1 - ang2), abs(ang1 - ang2))


class Segment:
    def __init__(self, _x, _y, _screen, _color=(255, 255, 255), _node=False):
        self.x = _x
        self.y = _y
        self.screen = _screen
        self.radius = 3
        self.color = _color
        self.node = _node
        # if self.node:
        #     print("NODE!")

    def draw(self):
        if not self.node:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            return
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius*2)


class Road:
    def __init__(self, _screen, _segments):
        self.screen = _screen
        self.segment_list = _segments
        self.min_dist = 20
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def add_seg(self, node=False, x=0, y=0, all_other_roads=[]):
        _x, _y = pygame.mouse.get_pos()
        if node:
            _x = x
            _y = y
        new_road = False
        min_node_distance = 10
        # go through all existing nodes to check if we can connect to existing nodes
        for road in all_other_roads:
            for seg in road.segment_list:
                if seg.node:
                    if dist(_x, _y, seg.x, seg.y) < min_node_distance:
                        if len(self.segment_list) >= 1:
                            if seg == self.segment_list[-1]:
                                continue
                        # close enough to existing node to combine with it
                        new_road = True
                        node = True
                        _x = seg.x
                        _y = seg.y
                        # add node at end of this road
                        self.segment_list.append(Segment(_x, _y, self.screen, self.color, _node=True))
                        # need to start a new road
                        roads.append(Road(screen, []))
                        roads[-1].segment_list.insert(0, Segment(_x, _y, self.screen, self.color, _node=True))
                        return

        length = len(self.segment_list)
        if length == 0 or node:
            self.segment_list.append(Segment(_x, _y, self.screen, self.color, _node=True))
        elif dist(_x, _y, self.segment_list[-1].x, self.segment_list[-1].y) > self.min_dist:
            self.segment_list.append(Segment(_x, _y, self.screen, self.color, node))

    def draw(self, draw_points=False, draw_arrow=False, width=1):
        for i in range(len(self.segment_list)):
            self.segment_list[i].color = self.color
            seg = self.segment_list[i]
            if i-1 >= 0:
                prev_seg = self.segment_list[i-1]
                if width > 1:
                    ang = np.arctan2(seg.y - prev_seg.y, seg.x - prev_seg.x)
                    arrow_breadth = np.pi / 2
                    arrow_length = width  #road width
                    if i-2 >= 0:
                        prev_prev_seg = self.segment_list[i-2]
                        prev_ang = np.arctan2(prev_seg.y - prev_prev_seg.y, prev_seg.x - prev_prev_seg.x)
                        pygame.draw.polygon(screen, self.color,
                                          points=[(prev_seg.x, prev_seg.y),
                                                  (prev_seg.x + arrow_length * np.cos(prev_ang + arrow_breadth), prev_seg.y + arrow_length * np.sin(prev_ang + arrow_breadth)),
                                                  (prev_seg.x + arrow_length * np.cos(ang + arrow_breadth), prev_seg.y + arrow_length * np.sin(ang + arrow_breadth)),
                                                  (seg.x + arrow_length * np.cos(ang + arrow_breadth), seg.y + arrow_length * np.sin(ang + arrow_breadth)),
                                                  (seg.x, seg.y),
                                                  (seg.x + 10 * np.cos(ang - arrow_breadth), seg.y + arrow_length * np.sin(ang - arrow_breadth)),
                                                  (prev_seg.x + 10 * np.cos(ang - arrow_breadth), prev_seg.y + arrow_length * np.sin(ang - arrow_breadth)),
                                                  (prev_seg.x + 10 * np.cos(prev_ang - arrow_breadth), prev_seg.y + arrow_length * np.sin(prev_ang - arrow_breadth))])
                    else:
                        pygame.draw.polygon(screen, self.color,
                                            points=[(prev_seg.x, prev_seg.y),
                                                    (prev_seg.x + arrow_length * np.cos(ang + arrow_breadth),
                                                     prev_seg.y + arrow_length * np.sin(ang + arrow_breadth)),
                                                    (seg.x + arrow_length * np.cos(ang + arrow_breadth),
                                                     seg.y + arrow_length * np.sin(ang + arrow_breadth)),
                                                    (seg.x, seg.y),
                                                    (seg.x + 10 * np.cos(ang - arrow_breadth),
                                                     seg.y + arrow_length * np.sin(ang - arrow_breadth)),
                                                    (prev_seg.x + 10 * np.cos(ang - arrow_breadth),
                                                     prev_seg.y + arrow_length * np.sin(ang - arrow_breadth))])
                elif draw_arrow:
                    # draw arrow instead of line
                    ang = np.arctan2(seg.y-prev_seg.y, seg.x-prev_seg.x)
                    arrow_breadth = 3*np.pi/4
                    arrow_length = 8
                    pygame.draw.lines(screen, self.color, closed=False, points=[(prev_seg.x, prev_seg.y), (seg.x, seg.y), (seg.x+arrow_length*np.cos(ang+arrow_breadth), seg.y+arrow_length*np.sin(ang+arrow_breadth)), (seg.x, seg.y), (seg.x+10*np.cos(ang-arrow_breadth), seg.y+arrow_length*np.sin(ang-arrow_breadth))], width=width)
                else:
                    pygame.draw.line(screen, self.color, (seg.x, seg.y), (prev_seg.x, prev_seg.y), width)
            if draw_points:
                self.segment_list[i].draw()

    def get_weight(self):
        turn_ammount = 0
        prev_ang = 0
        for i in range(len(self.segment_list)):
            if i == 0:
                continue
            seg = self.segment_list[i]
            prev_seg = self.segment_list[i - 1]
            ang = np.arctan2(seg.y-prev_seg.y, seg.x-prev_seg.x)
            turn_ammount += angle_diff(ang, prev_ang)
            prev_ang = ang
        return round(turn_ammount * len(self.segment_list), 2)


class Node:
    def __init__(self, number, x, y):
        self.number = number
        self.x = x
        self.y = y


class Edge:
    def __init__(self, startNode, endNode, weight):
        self.startNode = startNode
        self.endNode = endNode
        self.weight = weight


G = nx.DiGraph()
roads = [Road(screen, [])]
nodes = []
edges = []

no_loop = False
running = True
DRAW_POINTS = True
WIDE_ROADS = False
DRAW_ARROW = True
while running:
    if no_loop:
        continue
    # draw background
    screen.fill((20, 20, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # reset
            roads = [Road(screen, [])]
            nodes = []
            edges = []
            G = nx.DiGraph()
            print("---")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            # show points
            DRAW_POINTS = not DRAW_POINTS
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            # show points
            DRAW_ARROW = not DRAW_ARROW
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # make roads wide
            WIDE_ROADS = not WIDE_ROADS
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            # calculate graph
            # convert roads into a graph
            for road in roads:
                for seg in road.segment_list:
                    exists = False
                    if seg.node:
                        for node in nodes:
                            if seg.x == node.x and seg.y == node.y:
                                # node exists in node list already
                                exists = True
                        if exists is False:
                            nodes.append(Node(len(nodes), seg.x, seg.y))

            for road in reversed(roads):
                if len(road.segment_list) <= 1:
                    # road is too short! (skip this one and remove it)
                    roads.remove(road)
                    continue
                all_nodes = True
                for seg in road.segment_list:
                    if not seg.node:
                        all_nodes = False
                if all_nodes:
                    # road is ALL nodes! (skip this one and remove it)
                    roads.remove(road)
                    continue
                for node in nodes:
                    if node.x == road.segment_list[0].x and node.y == road.segment_list[0].y:
                        startNode = node
                    if node.x == road.segment_list[-1].x and node.y == road.segment_list[-1].y:
                        endNode = node
                edges.append(Edge(startNode, endNode, weight=road.get_weight()))
            for e in edges:
                G.add_edge(e.startNode.number, e.endNode.number, weight=e.weight)

            print("Number of roads: ")
            print(len(roads))
            print("Nodes of graph: ")
            print(G.nodes())
            print("Edges of graph: ")
            print(G.edges())
            # pos = nx.nx_pydot.graphviz_layout(G)
            pos = nx.planar_layout(G)
            nx.draw(G, pos=pos, with_labels=True)
            labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
            plt.savefig("graph_test.png")
            plt.show()
        if pygame.mouse.get_pressed()[0]:
            # if mouse is down add segments to current road (last road in list)
            _x, _y = pygame.mouse.get_pos()
            intersected = False
            if len(roads[-1].segment_list) == 0:
                # this is first segment to be added.
                # if close enough to existing segment make a node and connect there
                min_seg_dist = 10
                for i in range(len(roads)):
                    for j in range(len(roads[i].segment_list)):
                        seg = roads[i].segment_list[j]
                        if dist(_x, _y, seg.x, seg.y) < min_seg_dist:
                            _x = seg.x
                            _y = seg.y
                            # add a node at the start of this new road
                            roads[-1].add_seg(node=True, x=_x, y=_y, all_other_roads=roads)

                            # find segments in road i where the node was placed
                            # split road i into two roads at node intersection
                            for k in range(len(roads[i].segment_list)):
                                if roads[i].segment_list[k].x == _x and roads[i].segment_list[k].y == _y :
                                    # new node is at segment k in road i
                                    pre_segments = (roads[i].segment_list[0:k:1])
                                    post_segments = (roads[i].segment_list[k::1])
                                    roads[i].segment_list = pre_segments
                                    roads[i].add_seg(node=True, x=_x, y=_y, all_other_roads=roads)
                                    roads.append(Road(screen, post_segments))
                                    roads[-1].segment_list.insert(0, Segment(_x, _y, screen, roads[-1].color, _node=True))
                                    break
                            # Now we are on a new road (add a node at start)
                            roads.append(Road(screen, []))
                            roads[-1].add_seg(node=True, x=_x, y=_y, all_other_roads=roads)
                            intersected = True
                            break
                    if intersected:
                        break

            # check if new segment will intersect any previous segments
            if len(roads[-1].segment_list) >= 2 and not intersected:
                A = roads[-1].segment_list[-1]
                for i in range(len(roads)):
                    for j in range(len(roads[i].segment_list)):
                        if A.node or no_loop:
                            continue
                        if i == len(roads)-1 and j == len(roads[-1].segment_list)-1:
                            continue
                        if i == len(roads)-1 and j == len(roads[-1].segment_list)-2:
                            continue
                        if j == 0:
                            continue
                        seg_list = roads[i].segment_list
                        C = seg_list[j]
                        D = seg_list[j-1]

                        # check intersection
                        line1 = LineString([[_x, _y], [A.x, A.y]])
                        line2 = LineString([[C.x, C.y], [D.x, D.y]])
                        R = line1.intersection(line2)
                        if R:
                            x, y = R.x, R.y
                            intersected = True

                            # add a node to the end of this road
                            roads[-1].add_seg(node=True, x=x, y=y, all_other_roads=roads)
                            # find 2 segments in road i where the intersection occurred
                            # split road i into two roads at node intersection
                            for k in range(len(roads[i].segment_list)):
                                if k-1 < 0:
                                    continue
                                if roads[i].segment_list[k].x <= x <= roads[i].segment_list[k-1].x or roads[i].segment_list[k].x >= x >= roads[i].segment_list[k-1].x:
                                    if roads[i].segment_list[k].y <= y <= roads[i].segment_list[k-1].y or roads[i].segment_list[k].y >= y >= roads[i].segment_list[k-1].y:
                                        # new node is between segments k and k-1 in road i
                                        pre_segments = (roads[i].segment_list[0:k:1])
                                        post_segments = (roads[i].segment_list[k::1])
                                        roads[i].segment_list = pre_segments
                                        roads[i].add_seg(node=True, x=x, y=y, all_other_roads=roads)
                                        roads.append(Road(screen, post_segments))
                                        roads[-1].segment_list.insert(0, Segment(x, y, screen, roads[-1].color, _node=True))
                                        break

                            # Now we are on a new road (add a node at start)
                            roads.append(Road(screen, []))
                            roads[-1].add_seg(node=True, x=x, y=y, all_other_roads=roads)
                            break
                        else:
                            continue
                    if intersected:
                        break
            if not intersected:
                # nothing interesting, add new seg at mouse_xy
                roads[-1].add_seg(all_other_roads=roads)

        if event.type == pygame.MOUSEBUTTONUP:
            # if mouse released then we are on new road
            # make last segment of last road a node
            roads[-1].segment_list[-1].node = True
            roads.append(Road(screen, []))

    # draw all roads
    for i in range(len(roads)):
        textsurface = myfont.render(str(i), False, roads[i].color)
        length = len(roads[i].segment_list)
        if length >= 1:
            pass
            # screen.blit(textsurface, (roads[i].segment_list[round(length/2)].x, roads[i].segment_list[round(length/2)].y))
        if WIDE_ROADS:
            w = 15
        else:
            w = 1
        roads[i].draw(draw_points=DRAW_POINTS, draw_arrow=DRAW_ARROW, width=w)

    # draw node labels
    for n in nodes:
        textsurface = myfont.render(str(n.number), False, (255, 255, 255))
        screen.blit(textsurface, (n.x, n.y))
    # for i in range(len(roads)):
    #     try:
    #         textsurface = myfont.render(str(edges[i].weight), False, (255, 255, 255))
    #         screen.blit(textsurface, (roads[i].segment_list[round(length/2)].x, roads[i].segment_list[round(length/2)].y))
    #     except:
    #         pass

    pygame.display.flip()

pygame.quit()
