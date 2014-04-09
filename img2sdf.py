#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tool to parse a black-and-white image and generate a SDF file
# with walls from it.
#
# Copyright (c) 2013 PAL Robotics SL.
# By Siegfried Gevatter <siegfried.gevatter@pal-robotics.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import Image
import argparse

import sdf

def expand(data, size, sx, sy, clear_data=True):
    (w, h) = size

    width = 0
    (x, y) = (sx, sy)
    while x < w-1 and data[x,y]:
        width += 1
        x += 1

    height = 1
    (x, y) = (sx, sy + 1)
    while y < h-1:
        ok = True
        for x in range(sx, sx + width):
            if not data[x,y]:
                ok = False
                break
        if ok:
            height += 1
            y += 1
        else:
            break

    if clear_data:
        for x in range(sx, sx + width):
            for y in range(sy, sy + height):
                data[x, y] = 0

    if width:
        return (width, height)
    return None

def extract_walls(image):
    (w, h) = image.size
    pix = image.load()
    for y in range(h):
        for x in range(w):
            r = expand(pix, image.size, x, y)
            if r:
                yield [x, y, r[0], r[1]]

def load_image(filename):
    im = Image.open(filename)
    return im.convert('1').point(lambda i: bool(i == 0))

def process_image(filename, scale, height, model_name):
    image = load_image(filename)

    world = sdf.World(model_name)
    for (x, y, w, h) in extract_walls(image):
        pose = sdf.Pose((x + w / 2.0) * scale, -(y + h / 2.0) * scale, height / 2.0, 0.0)
        wall = sdf.Wall(pose, length=w * scale, width=h * scale, height=height)
        world.add_wall(wall)

    return sdf.to_string(world)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', metavar='IMAGE',
                        help='image to generate a world from.')
    parser.add_argument('scale', metavar='SCALE', type=float,
                        help='multiplier to convert from pixels to meters.')
    parser.add_argument('--height', default=1.0, type=float,
                        help='wall height.')
    parser.add_argument('--name', default='UnnamedWallsFromImage',
                        help='name to give the model (in the XML files).')
    args = parser.parse_args()

    print process_image(args.image, args.scale, args.height, args.name)

if __name__ == '__main__':
    main()
