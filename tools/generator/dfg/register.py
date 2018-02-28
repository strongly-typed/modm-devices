# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Niklas Hauser
# Copyright (c)      2016, Fabian Greif
# All rights reserved.

import re
from .device_tree import DeviceTree

class Register(DeviceTree):
    """ Register
    Represents the names and masks of the registers
    and methods for smart comparison.
    """

    def __init__(self, pos, name, size):
        super().__init__(name)
        self.setAttributes("offset", pos, "size", size)
        self.addSortKey(lambda f: (int(f["offset"]), int(f["width"])))

    def addField(self, name, offset):
        self.addField(name, offset, 1)

    def addField(self, name, offset, width):
        field = self.addChild(name)
        field.setAttributes("offset", offset, "width", width)

    def maskFromRegister(self):
        mask = 0
        for f in self.children:
            mask |= (((1 << f["width"]) - 1) << f["offset"])
        return mask

    def getFieldsWithPattern(self, pattern):
        results = []
        for f in self.children:
            match = re.search(pattern, f["name"])
            if match: results.append(f);
        return results

    def isEmpty(self):
        return len(self.children) == 0

    def _ascii(self):
        s = "\n Register: " + str(self.name)
        bW = 15
        self._sortTree()
        for ii in reversed(range(self["size"])):
            s += "\n+" + ("-"*(bW - 1) + "+") * 8
            values = "\n|" + (" "*(bW - 1) + "|") * 8

            for f in self.children:
                index = f["offset"]
                if ii * 8 <= index < (ii + 1) * 8:
                    index -= ii * 8
                    values = values[:2 + bW * (7 - index)] + f.name.center(bW - 1) + values[1 + bW * ((8 - index)):]

            s = s + values + "\n+" + ("-"*(bW - 1) + "+") * 8
        return s
