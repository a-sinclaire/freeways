import random
import time

import shapely
import copy
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

    def add_seg(self, node=False, x=0, y=0, all_other_roads=None):
        _x, _y = pygame.mouse.get_pos()
        if node:
            _x = x
            _y = y
        min_node_distance = 10
        for road in all_other_roads:
            for seg in road.segment_list:
                if seg.node:
                    if dist(_x, _y, seg.x, seg.y) < min_node_distance:
                        if len(self.segment_list) >= 1:
                            if seg == self.segment_list[-1]:
                                continue
                        # close enough to existing node to combine with it
                        node = True
                        _x = seg.x
                        _y = seg.y

        length = len(self.segment_list)
        if length == 0 or node:
            self.segment_list.append(Segment(_x, _y, self.screen, self.color, _node=True))
        elif dist(_x, _y, self.segment_list[-1].x, self.segment_list[-1].y) > self.min_dist:
            self.segment_list.append(Segment(_x, _y, self.screen, self.color, node))

    def draw(self, draw_points=False, width=1):
        for i in range(len(self.segment_list)):
            self.segment_list[i].color = self.color
            seg = self.segment_list[i]
            if i-1 >= 0:
                prev_seg = self.segment_list[i-1]
                pygame.draw.line(screen, self.color, (seg.x, seg.y), (prev_seg.x, prev_seg.y), width)
            if draw_points:
                self.segment_list[i].draw()


roads = [Road(screen, [])]

no_loop = False
running = True
DRAW_POINTS = True
WIDE_ROADS = False
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
            print("---")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            # show points
            DRAW_POINTS = not DRAW_POINTS
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # make roads wide
            WIDE_ROADS = not WIDE_ROADS
        if pygame.mouse.get_pressed()[0]:
            # if mouse is down add segments to current road (last road in list)
            # check if new segment will intersect any previous segments
            intersected = False
            if len(roads[-1].segment_list) >= 2:
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
                        _x, _y = pygame.mouse.get_pos()
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
                                        pre_segments = (roads[i].segment_list[0:k-1:1])
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
                if roads[-1].add_seg(all_other_roads=roads):
                    roads.append(Road(screen, []))
                    roads[-1].add_seg(node=True, all_other_roads=roads)

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
            screen.blit(textsurface, (roads[i].segment_list[round(length/2)].x, roads[i].segment_list[round(length/2)].y))
        if WIDE_ROADS:
            w = 50
        else:
            w = 1
        roads[i].draw(draw_points=DRAW_POINTS, width=w)

    pygame.display.flip()

pygame.quit()
