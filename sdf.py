#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Module to create SDF files with rectangular walls.
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

import lxml.etree as xml

class UniqueId(object):

    __last_uid = -1

    @classmethod
    def get_uid(cls):
        cls.__last_uid += 1
        return cls.__last_uid

class Pose(object):

    def __init__(self, x, y, z=0, r=0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r

    def xml(self):
        node = xml.Element('pose')
        node.text = '%.5f %.5f %.5f 0 0 %.5f' % (self.x, self.y, self.z, self.r)
        return node

class Size(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def xml(self):
        node = xml.Element('size')
        node.text = '%.5f %.5f %.5f' % (self.x, self.y, self.z)
        return node

class Material(object):

    def __init__(self, material_name, material_uri='file://media/materials/scripts/gazebo.material'):
        self.material_name = material_name
        self.material_uri = material_uri

    def xml(self):
        node = xml.Element('material')
        script = xml.SubElement(node, 'script')
        xml.SubElement(script, 'uri').text = self.material_uri
        xml.SubElement(script, 'name').text = self.material_name
        return node

class Geometry(object):

    def __init__(self, size):
        self.size = size

    def xml(self):
        node = xml.Element('geometry')
        box = xml.SubElement(node, 'box')
        box.append(self.size.xml())
        return node

class Wall(UniqueId):

    def __init__(self, pose, length, width, height):
        self.uid = self.get_uid()
        self.pose = pose
        self.length = length
        self.width = width
        self.height = height

    def xml(self):
        link = xml.Element('link')
        link.set('name', 'Wall_%d' % self.uid)

        geometry = Geometry(Size(self.length, self.width, self.height))

        # Collision Model
        collision = xml.SubElement(link, 'collision')
        collision.set('name', 'Wall_%d_Collision' % self.uid)
        collision.append(geometry.xml())
        collision.append(self.pose.xml())

        # Visual Model
        visual = xml.SubElement(link, 'visual')
        visual.set('name', 'Wall_%d_Visual' % self.uid)
        visual.append(geometry.xml())
        visual.append(Material('Gazebo/Grey').xml())
        visual.append(self.pose.xml())

        return link

class World(object):

    def __init__(self, model_name):
        self.model_name = model_name
        self.walls = []

    def add_wall(self, wall):
        self.walls.append(wall)

    def xml(self):
        root = xml.Element('sdf', version='1.4')

        model = xml.SubElement(root, 'model')
        model.set('name', self.model_name)
        xml.SubElement(model, 'static').text = '1'

        for wall in self.walls:
            model.append(wall.xml())

        return root

def to_string(inst, pretty_print=True):
    tree = inst.xml()
    pre = ''
    if tree.tag == 'sdf':
        pre = '<?xml version="1.0" ?>\n'
    return pre + xml.tostring(inst.xml(), pretty_print=pretty_print)

if __name__ == '__main__':
    world = World('ExampleWorld')
    world.add_wall(Wall(Pose(0, 0, 0, 0), 5, 1, 2.5))
    print to_string(world)
