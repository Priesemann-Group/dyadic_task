import shapely
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import Point

import pyglet
from pyglet.text import Label

class Lasso:
    def __init__(self, targets):
        self.last_pos = None
        self.intersection_found = False
        self.points = []
        self.lines_pyglet = []
        self.lines_shapely = []
        self.targets = targets
        
        self.last_drag_pos = None #Fixes multiple same positions problem
        self.catch_count = 0


    def draw(self):
        Label(f'Ants catched: {self.catch_count}',
                font_name='Arial',
                font_size=20,x=0,y=0,
                color=(0, 0, 0, 255)).draw()
        for l in self.lines_pyglet:
            l.draw()


    def add_line(self,x,y):
        self.points.append((x,y))
        if self.last_pos:
            #for calculations with the line
            line = LineString([self.last_pos, (x,y)])
            #there is alwas an intersection to the line before
            for i,l in enumerate(self.lines_shapely[:-1]):
                if l.intersects(line):
                    intersection = l.intersection(line)
                    
                    print(f'intersection: {intersection}')

                    if type(intersection)==Point:
                        x,y = intersection.x, intersection.y
                    elif type(intersection)==LineString:
                        x,y=intersection.coords[0]
                    else:
                        raise TypeError('unhandled intersection type')

                    self.collapse(i, (x, y))

                    line = LineString([self.last_pos, (x,y)])

                    self.intersection_found = True
                    break
            if not self.intersection_found:
                self.lines_shapely.append(line)
                #for drawing the line
                line = pyglet.shapes.Line(*self.last_pos,x,y,width=4,color=(0,255,0))
                self.lines_pyglet.append(line)
            else:
                self.last_pos = None
                self.intersection_found = False

        self.last_pos=(x,y)


    def collapse(self, strt_indx=None, intersection=None):

        if intersection:
            catch = Polygon([intersection] + self.points[strt_indx:] + [intersection])
            idx_to_del = []
            for ant in list(self.targets):
                if catch.contains(Point(ant.coords())):
                    self.catch_count+=ant.size
                    self.targets.remove(ant)
        else:
            self.last_pos = None
        
        self.intersection_found = False #TODO clear this
        self.points = []
        self.lines_pyglet = []
        self.lines_shapely = []


    def consume(self, pos):
        
        if not self.intersection_found and pos != self.last_drag_pos:
            self.add_line(*pos)

        self.last_drag_pos = pos

