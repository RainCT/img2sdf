#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tool to parse a black-and-white image and generate a SDF file
# with walls from it.
#
# Copyright (c) 2013 PAL Robotics SL.
#               By Siegfried Gevatter <siegfried.gevatter@pal-robotics.com>
#               Contributors: Enrique Fernández
#           (c) 2014 Siegfried-A. Gevatter <siegfried@gevatter.omc>
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
import numpy

import sdf

def expand(horizontal, size, sx, sy):
    """
    Greedily looks for a solid rectangle starting at the given position.

    Args:
      horizontal: 2-d array, each cell indicates how many adjacent cells
                  towards the right are true (counting the cell itself).
      size:       (w, h)-tuple indicating the size of the image (and arrays).
      sx, sy:     cell to evaluate.

    Returns:
      A (width, height)-tuple for the rectangle starting at the given
      position, or None.
    """

    (w, h) = size

    width = horizontal[sy, sx]
    if not width:
        return None

    height = 1
    for y in range(sy + 1, h):
        if horizontal[y, sx] >= width:
            height += 1
        else:
            break

    return (width, height)

def extract_walls(image):
    (w, h) = image.size

    # Note: we convert to 'L' because of a bug in PIL/numpy with image mode '1'.
    # An alternative workaround would be:
    #   horizontal = numpy.reshape(image.getdata(), (h, w)).astype(dtype=int, copy=False)
    horizontal = numpy.array(image.convert('L'), dtype=int)
    for y in range(h):
        horizontal[y, w - 1] = bool(horizontal[y, w - 1])
        for x in range(w - 2, -1, -1):
            horizontal[y, x] = horizontal[y, x + 1] + 1 if horizontal[y, x] else 0

    for y in range(h):
        x = 0
        while x < w:
            r = expand(horizontal, image.size, x, y)
            if r:
                yield [x, y, r[0], r[1]]
                x += r[0]

                # Mark the region in the array, so it won't be selected again.
                horizontal[y : y + r[1], x : x + r[0]] = 0
            else:
                x += 1

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
