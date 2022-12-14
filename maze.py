#!/usr/bin/python3

from contextlib import contextmanager

import random
import cairo
import math

# Maze entry numbering:
#   top:     0     .. (w-1)
#   right:   w     .. (w+h-1)
#   bottom: (w+h)  .. (2w+h-1)
#   left:   (2w+h) .. (2w+2h-1)

class Maze:
    def __init__(self, w, h, seed):
        self.w = w
        self.h = h
        self.seed = seed

        stored = random.getstate()
        random.seed(seed)

        edges = \
                [ ((x, y), (x+1, y)) for x in range(w-1) for y in range(h) ] + \
                [ ((x, y), (x, y+1)) for x in range(w) for y in range(h-1) ]

        random.shuffle(edges)
        random.setstate(stored)
    
        blocks = { (x, y): [ (x, y) ] for y in range(h) for x in range(w) }
        to_join = len(blocks)

        self.walls = {}
        self.edges = {}

        for e in edges:
            a = blocks[e[0]]
            b = blocks[e[1]]

            if a is b:
                self.walls[e] = True
                continue

            if len(b) < len(a):
                a, b = b, a

            for cell in b:
                blocks[cell] = a

            a += b
            to_join -= 1
            self.edges[e] = True

        d = self.distances((0,0))
        for p in sorted(d, key=lambda x: d[x], reverse=True):
            if p[0] != 0 and p[0] != w-1 and p[1] != 0 and p[1] != h-1:
                continue
            
            ea = p
            break
        
        d = self.distances(ea)
        for p in sorted(d, key=lambda x: d[x], reverse=True):
            if p[0] != 0 and p[0] != w-1 and p[1] != 0 and p[1] != h-1:
                continue
            
            eb = p
            break

        dd = self.distances(eb)
        self.complexity = (
                sum([ x**2 for x in dd.values()]) +
                sum([ x**2 for x in d.values() ])
                )**0.5 / (w*h)
        
        print(f"Generated: {w}x{h}, seed={seed}, cpx={self.complexity:.4f}, plen={dd[ea]}|{d[eb]}, entries {ea} {eb}")
        self.entries = [ ea, eb ]

    def distances(self, start):
        finished = {}
        unfinished = [ start ]
        d = { start: 0 }

        while len(unfinished):
            p = unfinished.pop()
            for n in (
                    (p[0]-1, p[1]),
                    (p[0]+1, p[1]),
                    (p[0], p[1]-1),
                    (p[0], p[1]+1)
                    ):
                if n in finished:
                    continue
                if (p,n) in self.edges or (n,p) in self.edges:
                    d[n] = d[p] + 1
                    unfinished.append(n)
            finished[p] = True

        if len(d) == self.h * self.w:
            return d
        else:
            raise Exception(d)



class PDF:
    mm = 72 / 25.4
    def __init__(self, file_name="maze.pdf", page_width=210*mm, page_height=297*mm, margin_lr=20*mm, margin_tb=30*mm, show_arrows=False):
        self.surface = cairo.PDFSurface(file_name, page_width, page_height)
        self.context = cairo.Context(self.surface)
        self.context.translate(margin_lr, margin_tb)
        self.context.set_line_cap(cairo.LINE_CAP_ROUND)
        self.context.set_line_width(1)

        self.rw = page_width - margin_lr*2
        self.rh = page_height - margin_tb*2

        self.show_arrows = show_arrows

    def draw(self, maze):
        if type(maze) is list:
            for m in maze:
                self.draw(m)
            return

        hbs = self.rw / maze.w
        vbs = self.rh / maze.h

        for e in maze.walls:
            self.context.move_to(hbs *  e[1][0]   , vbs *  e[1][1]     )
            self.context.line_to(hbs * (e[0][0]+1), vbs * (e[0][1] + 1))
            self.context.stroke()

        self.context.move_to(0,0)
        self.context.line_to(self.rw,0)
        self.context.line_to(self.rw,self.rh)
        self.context.line_to(0,self.rh)
        self.context.close_path()
        self.context.stroke()

        entry_width = 0.6
        arrowlen = 1.5
        arrowwidth = 0.2

        bottomleftpoint = False
        topleftpoint = False
        bottompoint_x = None

        for e in maze.entries:
            arrowfrom = None
            self.context.save()
            self.context.set_source_rgba(1,1,1,1)
            self.context.set_line_width(2)
            if e[0] == 0:
                self.context.move_to(0, ((e[1]+(1-entry_width)/2)*vbs))
                self.context.rel_line_to(0, vbs*entry_width)
                arrowfrom = (-arrowlen, e[1])
            elif e[0] == maze.w-1:
                self.context.move_to(self.rw, (e[1] + (1-entry_width)/2)*vbs)
                self.context.rel_line_to(0, vbs*entry_width)
                arrowfrom = (maze.w-1+arrowlen, e[1])
            elif e[1] == 0:
                self.context.move_to((e[0] + (1-entry_width)/2)*hbs, 0)
                self.context.rel_line_to(hbs*entry_width, 0)
                arrowfrom = (e[0], -arrowlen)
                if e[0]*2 < maze.w:
                    topleftpoint = True
            elif e[1] == maze.h-1:
                self.context.move_to((e[0] + (1-entry_width)/2)*hbs, self.rh)
                self.context.rel_line_to(hbs*entry_width, 0)
                arrowfrom = (e[0], maze.h-1+arrowlen)
                if e[0]*2 < maze.w:
                    bottomleftpoint = True
                    bottompoint_x = e[0]
            else:
                raise Exception(e)

            self.context.stroke()
            self.context.restore()

            if self.show_arrows:
                self.context.move_to((arrowfrom[0]+0.5)*hbs, (arrowfrom[1]+0.5)*vbs)
                self.context.line_to((e[0]+0.5)*hbs, (e[1]+0.5)*vbs)
                self.context.stroke()

                self.context.move_to((e[0]+0.5)*hbs, (e[1]+0.5)*vbs)
                self.context.rel_line_to(
                        (arrowfrom[0]-e[0])*0.5*hbs + (arrowfrom[1]-e[1])*arrowwidth*0.5*hbs,
                        (arrowfrom[1]-e[1])*0.5*vbs + (arrowfrom[0]-e[0])*arrowwidth*0.5*vbs
                        )
                self.context.rel_line_to(
                        -(arrowfrom[1]-e[1])*arrowwidth*hbs,
                        -(arrowfrom[0]-e[0])*arrowwidth*vbs
                        )
                self.context.close_path()
                self.context.fill()

            self.context.save()
            self.context.translate((arrowfrom[0]+0.5)*hbs, (arrowfrom[1]+0.5)*vbs)
            self.context.scale(hbs, vbs)
            self.context.arc(0,0,0.4,0,math.atan2(1,1)*8)
            self.context.close_path()
            self.context.fill()
            self.context.restore()

        if bottomleftpoint:
            if topleftpoint:
                self.context.move_to((bottompoint_x + 3) * hbs, self.rh + 4.5*self.mm)
            else:
                self.context.move_to(0, -2*self.mm)
        else:
            self.context.move_to(0, self.rh + 4.5*self.mm)

        self.context.show_text(f"{maze.w} | {maze.h} | {maze.seed} | complexity: {maze.complexity:.4f}")
        self.context.show_page()

if __name__ == "__main__":
    PDF().draw([Maze(35,50,seed) for seed in range(50)])
#    PDF().draw([Maze(15,21,1)])
