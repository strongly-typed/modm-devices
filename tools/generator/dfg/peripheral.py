# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Niklas Hauser
# Copyright (c)      2016, Fabian Greif
# All rights reserved.

from .device_tree import DeviceTree
from .register import Register

class Peripheral(DeviceTree):
    """ Peripheral
    Represents the names and masks of the peripherals control and data registers
    and methods for smart comparison.
    """

    def __init__(self, name):
        super().__init__(name)
        self.addSortKey(lambda r: (int(r["offset"]), int(r["size"])))

    def addRegister(self, pos, name, size):
        reg = Register(pos, name, size)
        self._addChild(-1, reg)
        return reg

    def getComparisonDict(self, other):
        pass

    def getComparisonPeripheral(self, other):
        assert isinstance(other, Peripheral)

        comparision_dict = {'common_keys': [], 'different_keys': []}

        common = Peripheral()
        if self.name == other.name:
            common.name = self.name
        self_delta = Peripheral(self.name)
        other_delta = Peripheral(other.name)

        # compare registers
        self_regs = list(self.registers)
        other_regs = list(other.registers)

        common.registers = list(set(self_regs).intersection(other_regs))
        self_delta.registers = list(set(self_regs).difference(other_regs))
        other_delta.registers = list(set(other_regs).difference(self_regs))

        comparision_dict['common'] = common
        comparision_dict['self_delta'] = self_delta
        comparision_dict['other_delta'] = other_delta

        return comparision_dict

    def isEmpty(self):
        return len(self.children) == 0

    def _ascii(self):
        s = "\n Peripheral(\n\t{'name': '" + str(self.name) + "',\n"
        s += "\t'registers': ["
        st = ""
        for reg in self.registers:
            st += str(reg)
        st = st.replace("\n", "\n\t")
        return s + st + " ]})"
