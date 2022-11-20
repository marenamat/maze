#!/usr/bin/python3

from random import randrange, random, sample

import cairo

mm = 72 / 25.4

# Maze entry numbering:
#   top:     0     .. (w-1)
#   right:   w     .. (w+h-1)
#   bottom: (w+h)  .. (2w+h-1)
#   left:   (2w+h) .. (2w+2h-1)

class Maze:
    def __init__(self, w, h, maxdepth, routes=None):
        self.w = w
        self.h = h

        if routes is None:
            routes = [ [ randrange(self.w + self.h), self.w + self.h + randrange(self.w + self.h) ] ]

        self.routes = routes

        if w == h == 1:
            self.children = []
            self.split = None
            self.split_pos = None
            return

        if w > h:
            # Wide, split vertically.
            self.split_pos = int((w/3) * (1 + random()))
            if self.split_pos == 0:
                self.split_pos = 1
            split_from = self.split_pos
            split_to = 2*w + h - split_from

            joint_range = h

            a_offset = split_to - split_from - h
            b_offset = split_from

            ja_offset = split_from
            jb_offset = 2*h + 2*(w - split_from) - 1

        else:
            # High, split horizontally.
            self.split_pos = int((h/3) * (1 + random()))
            if self.split_pos == 0:
                self.split_pos = 1
            split_from = w + self.split_pos
            split_to = 3*w + 2*h - split_from

            joint_range = w

            a_offset = split_to - split_from - w
            b_offset = split_from - w

            ja_offset = split_from
            jb_offset = w - 1

        routes_a = []
        routes_b = []

        crossroutes = []

        for r in routes:
            entries_a = []
            entries_b = []
            for e in r:
                if e >= split_from and e < split_to:
                    entries_b.append(e - b_offset)
                elif e >= split_to:
                    entries_a.append(e - a_offset)
                else:
                    entries_a.append(e)

            if len(entries_a) == 0:
                routes_b.append(entries_b)
            elif len(entries_b) == 0:
                routes_a.append(entries_a)
            else:
                crossroutes.append({
                        "a": entries_a,
                        "b": entries_b,
                        })

        joints = sample(range(joint_range), len(crossroutes))
        joints.sort()

        for j, c in zip(joints, crossroutes):
            print(f"Crossroute { c } at { j }")
            c["a"].append(j + ja_offset)
            c["b"].append(jb_offset - j)
            routes_a.append(c["a"])
            routes_b.append(c["b"])

        self.split = joints

        print(f"Split at {split_from}, {split_to}")
        print(f"Routes A: { routes_a }")
        print(f"Routes B: { routes_b }")
        print(f"Crossroutes: { crossroutes }")

        if maxdepth == 0:
            self.children = []
        elif w > h:
            self.children = [
                    Maze(self.split_pos, h, maxdepth-1, routes_a),
                    Maze(w - self.split_pos, h, maxdepth-1, routes_b)
                    ]
        else:
            self.children = [
                    Maze(w, self.split_pos, maxdepth-1, routes_a),
                    Maze(w, h - self.split_pos, maxdepth-1, routes_b)
                    ]

    def entry_to_midpoint(self, pos):
        w = self.w
        h = self.h
        if pos < w:
            return (pos + 0.5, 0)
        elif pos < w+h:
            return (w, pos - w + 0.5)
        elif pos < w*2 + h:
            return (w*2+h - pos - 0.5, h)
        else:
            return (0, w*2 + h*2 - pos - 0.5)

    def draw(self, page_width=210*mm, page_height=297*mm, margin_lr=20*mm, margin_tb=25*mm):
        context = cairo.Context(cairo.PDFSurface("maze.pdf", page_width, page_height))
        context.translate(margin_lr, margin_tb)

        rw = page_width - margin_lr*2
        rh = page_height - margin_tb*2

        hbs = rw / self.w
        vbs = rh / self.h

        entries = {}
        for r in self.routes:
            for e in r:
                entries[e] = True

        print(entries)

        context.move_to(0, 0)
        pos = 0

        for _ in range(self.w):
            if pos in entries:
                context.rel_move_to(hbs, 0)
            else:
                context.rel_line_to(hbs, 0)
            pos += 1

        for _ in range(self.h):
            if pos in entries:
                context.rel_move_to(0, vbs)
            else:
                context.rel_line_to(0, vbs)
            pos += 1

        for _ in range(self.w):
            if pos in entries:
                context.rel_move_to(-hbs, 0)
            else:
                context.rel_line_to(-hbs, 0)
            pos += 1

        for _ in range(self.h):
            if pos in entries:
                context.rel_move_to(0, -vbs)
            else:
                context.rel_line_to(0, -vbs)
            pos += 1

        context.stroke()

        self.draw_split(context, hbs, vbs)

        context.show_page()

    def draw_split(self, context, hbs, vbs):
        if self.split is None:
            return

        if len(self.children) > 0:
            self.children[0].draw_split(context, hbs, vbs)

            lx = { p: True for p in self.split }

            context.save()

            if self.w > self.h:
                # vertical split
                context.translate(hbs * self.split_pos, 0)
                context.move_to(0, 0)
                for p in range(self.h):
                    if p in lx:
                        context.rel_move_to(0, vbs)
                    else:
                        context.rel_line_to(0, vbs)
            else:
                # horizontal split
                context.translate(0, vbs * self.split_pos)
                context.move_to(hbs * self.w, 0)
                for p in range(self.w):
                    if p in lx:
                        context.rel_move_to(-hbs, 0)
                    else:
                        context.rel_line_to(-hbs, 0)

            context.stroke()

            self.children[1].draw_split(context, hbs, vbs)

            context.restore()

        if len(self.children) == 0:
            for r in self.routes:
                q = list(r)

                x, y = self.entry_to_midpoint(q.pop(0))
                context.move_to(x * hbs, y * vbs)

                for p in q:
                    x, y = self.entry_to_midpoint(p)
                    context.line_to(x * hbs, y * vbs)

                context.stroke()


Maze(20, 35, -1).draw()
#Maze(12, 8, 1).draw()
