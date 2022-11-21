#!/usr/bin/python3

from random import randrange, random, sample, choice, seed

import cairo

mm = 72 / 25.4

seed(4)

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

        self.split_pos = None

        if w == h == 1:
            self.children = []
            self.split = None
            return
        
        while self.split_pos is None:
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

                a_rc = min(h, self.split_pos)
                b_rc = min(h, w - self.split_pos)

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

                a_rc = min(w, self.split_pos)
                b_rc = min(w, h - self.split_pos)

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

            if len(routes_a) > a_rc or len(routes_b) > b_rc:
                print(f"Split at { self.split_pos } failed: { len(routes_a) } > { a_rc } or { len(routes_b) } > { b_rc }")
                print(w, h, routes_a, routes_b)
                self.split_pos = None
                continue

        crossroutes.sort(key=lambda c: split_from - min(c["a"]) + ((w*2 + h*2) if split_from < min(c["a"]) else 0))
        print(f"Sorted crossroutes: { crossroutes }")

#        print(f"sample of range { joint_range } of { len(crossroutes) }")
        joints = sample(range(joint_range), len(crossroutes))
        joints.sort()

        jma = {}
        jmb = {}

        for j, c in zip(joints, crossroutes):
#            print(f"Crossroute { c } at { j }")
            c["a"].append(j + ja_offset)
            c["b"].append(jb_offset - j)
            routes_a.append(c["a"])
            routes_b.append(c["b"])
            jma[j] = c["a"]
            jmb[j] = c["b"]

        self.split = joints

#        while len(joints) + 1 < joint_range * 0.6:
        nj = []
        if w > 3 and h > 3 and len(joints) + 1 < joint_range * 0.6:
            f = -1
            for j in joints:
                d = j-f
                if f < 1:
                    d -= 2
                if d > 3 and j+2 < joint_range \
                        and random() > 0.4 \
                        and len(routes_a) < a_rc \
                        and len(routes_b) < b_rc \
                        :
                    # Get 2 new points
#                    print(f"sample of {d}")
                    n = sample(range(1, d), 2)
                    n.sort()

                    nj.append(j-n[0])
                    nj.append(j-n[1])

                    # Find the appropriate routes on both sides
                    ra = jma[j]
                    rb = jmb[j]

                    # Move one to the new point and create two loops
                    if random() > 0.5:
                        # Move RA
                        print(f"move ra from {j} to {j - n[1]}")
                        ra.remove(j + ja_offset)
                        ra.append(j + ja_offset - n[1])
                        jma[j - n[1]] = ra

                        # Create loop in B
                        print(f"B loop from {j - n[0]} to {j - n[1]}")
                        nrb = [ jb_offset - j + n[1], jb_offset - j + n[0] ]
                        jmb[j - n[1]] = nrb
                        jmb[j - n[0]] = nrb

                        # Create loop in A
                        print(f"A loop from {j - n[0]} to {j}")
                        nra = [ j + ja_offset - n[0], j + ja_offset ]
                        jma[j - n[0]] = nra
                        jma[j] = nra

                    else:
                        # Move RB
                        print(f"move rb from {j} to {j - n[1]}")
                        rb.remove(jb_offset - j)
                        rb.append(jb_offset - j + n[1])
                        jmb[j - n[1]] = rb

                        # Create loop in A
                        print(f"A loop from {j - n[0]} to {j - n[1]}")
                        nra = [ j + ja_offset - n[1], j + ja_offset - n[0] ]
                        jma[j - n[1]] = nra
                        jma[j - n[0]] = nra

                        # Create loop in B
                        print(f"B loop from {j - n[0]} to {j}")
                        nrb = [ jb_offset - j + n[0], jb_offset - j ]
                        jmb[j - n[0]] = nrb
                        jmb[j] = nrb
                    routes_a.append(nra)
                    routes_b.append(nrb)
                f = j

        joints += nj

        print(f"Split ({w}x{h}) at {split_from}, {split_to}")
        print(f"Routes before: { routes }")
        print(f"Routes A: { routes_a }")
        print(f"Routes B: { routes_b }")
#       print(f"Crossroutes A: { jma }")
#       print(f"Crossroutes B: { jmb }")

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
        if len(self.children) > 0 and self.split is not None:
            self.children[0].draw_split(context, hbs, vbs)

            context.save()

            if self.w > self.h:
                # vertical split
                context.translate(hbs * self.split_pos, 0)

                context.save()
                context.set_source_rgba(1, 0, 0, 0.3)
                context.set_line_width(3 * self.h)
                context.move_to(0, 0)
                context.line_to(0, vbs * self.h)
                context.stroke()
                context.restore()

                context.move_to(0, 0)
                for p in range(self.h):
                    if p in self.split:
                        context.rel_move_to(0, vbs)
                    else:
                        context.rel_line_to(0, vbs)
                context.stroke()
            else:
                # horizontal split
                context.translate(0, vbs * self.split_pos)

                context.save()
                context.set_source_rgba(1, 0, 0, 0.3)
                context.set_line_width(3 * self.w)
                context.move_to(0, 0)
                context.line_to(hbs * self.w, 0)
                context.stroke()
                context.restore()

                context.move_to(hbs * self.w, 0)
                for p in range(self.w):
                    if p in self.split:
                        context.rel_move_to(-hbs, 0)
                    else:
                        context.rel_line_to(-hbs, 0)
                context.stroke()


            self.children[1].draw_split(context, hbs, vbs)

            context.restore()

        if len(self.children) == 0:
            mx = self.w / 2
            my = self.h / 2

            for r in self.routes:
                q = list(r)

                x, y = self.entry_to_midpoint(q.pop(0))
                context.move_to(x * hbs, y * vbs)

                for p in q:
                    c1x = (x + mx) * hbs / 2
                    c1y = (y + my) * vbs / 2
                    x, y = self.entry_to_midpoint(p)
                    c2x = (x + mx) * hbs / 2
                    c2y = (y + my) * vbs / 2
                    context.curve_to(c1x, c1y, c2x, c2y, x * hbs, y * vbs)

                context.stroke()


Maze(20, 35, -1).draw()
#Maze(12, 8, 1).draw()
