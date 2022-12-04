#!/usr/bin/python3

from contextlib import contextmanager

import random
import cairo

mm = 72 / 25.4

# Maze entry numbering:
#   top:     0     .. (w-1)
#   right:   w     .. (w+h-1)
#   bottom: (w+h)  .. (2w+h-1)
#   left:   (2w+h) .. (2w+2h-1)

class Maze:
    def __init__(self, w, h, seed):
        self.w = w
        self.h = h

        stored = random.getstate()
        random.seed(seed)

        edges = \
                [ ((x, y), (x+1, y)) for x in range(w-1) for y in range(h) ] + \
                [ ((x, y), (x, y+1)) for x in range(w) for y in range(h-1) ]

        offset = random.randrange(int((w+h) / 2))
        self.entries = [ random.randrange(int((w+h) / 2)) + offset for _ in range(2) ]

        random.shuffle(edges)
        random.setstate(stored)
    
        blocks = { (x, y): [ (x, y) ] for y in range(h) for x in range(w) }
        to_join = len(blocks)

#        print(f"To join: {to_join}")

        self.edgelist = []
        for e in edges:
            a = blocks[e[0]]
            b = blocks[e[1]]

#            print(f"Blocks are {a} and {b}")

            if a is b:
                self.edgelist.append(e)
                continue

            if len(b) < len(a):
                a, b = b, a

            for w in b:
                blocks[w] = a

            a += b
            to_join -= 1
#            print(f"Joined at {e}")

#        print(blocks)

page_width  = 210*mm
page_height = 297*mm
margin_lr   =  20*mm
margin_tb   =  25*mm

context = cairo.Context(cairo.PDFSurface("maze.pdf", page_width, page_height))
context.translate(margin_lr, margin_tb)
context.set_line_cap(cairo.LINE_CAP_ROUND)
context.set_line_width(1)

rw = page_width - margin_lr*2
rh = page_height - margin_tb*2

def draw(maze):
    hbs = rw / maze.w
    vbs = rh / maze.h

    for e in maze.edgelist:
        context.move_to(hbs *  e[1][0]   , vbs *  e[1][1]     )
        context.line_to(hbs * (e[0][0]+1), vbs * (e[0][1] + 1))
        context.stroke()

    if maze.entries[0] >= maze.w:
        context.move_to(0,0)
        context.line_to(rw,0)
        context.line_to(rw,(maze.entries[0]-maze.w)*vbs)
        context.rel_move_to(0,vbs)
        context.line_to(rw,rh)
        context.stroke()
    else:
        context.move_to(0,0)
        context.line_to(maze.entries[0]*hbs,0)
        context.rel_move_to(hbs,0)
        context.line_to(rw,0)
        context.line_to(rw,rh)
        context.stroke()

    if maze.entries[1] >= maze.w:
        context.move_to(rw,rh)
        context.line_to(0,rh)
        context.rel_line_to(0,(maze.w - maze.entries[1])*vbs)
        context.rel_move_to(0,-vbs)
        context.line_to(0,0)
        context.stroke()
    else:
        context.move_to(rw,rh)
        context.rel_line_to(-maze.entries[1] * hbs, 0)
        context.rel_move_to(-hbs, 0)
        context.line_to(0,rh)
        context.line_to(0,0)
        context.stroke()

    context.show_page()

for seed in range(50):
    draw(Maze(35,50,seed))
