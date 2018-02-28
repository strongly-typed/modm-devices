#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Niklas Hauser
# Copyright (c)      2016, Fabian Greif
# All rights reserved.

import os
import logging
import argparse
from collections import defaultdict
from pathlib import Path

import dfg.logger

from dfg.stm32.stm_device_tree import STMDeviceTree
from dfg.stm32.stm_identifier import STMIdentifier
from dfg.stm32.stm_header import STMHeader
from dfg.output.device_memmap import DeviceMemmapWriter
from dfg.register import Register
from dfg.peripheral import Peripheral
from dfg.device_tree import DeviceTree

from py2neo import authenticate, Graph, Node, Relationship

LOGGER = logging.getLogger("dfg.stm.memmap")


arg = argparse.ArgumentParser(description="Device File Memory Maps")
arg.add_argument("--log-level", default="WARNING", nargs="?", choices=["ERROR", "WARNING", "INFO", "DEBUG", "DISABLED"], help="Choose the output log level")
arg.add_argument("filter", nargs = "*", help="Only consider devices starting with this string")
args = arg.parse_args()

dfg.logger.configure_logger(args.log_level)
output = Path(os.path.realpath(__file__)).parents[2] / "memory" / "stm32"

deviceNames = []
for f in args.filter:
    deviceNames.extend(STMDeviceTree.getDevicesFromPrefix(f))
deviceNames = sorted(list(set(deviceNames)))


# authenticate("localhost:7474", "neo4j", "memmap")

# graph = Graph()
# graph.delete_all()

typelist = defaultdict(list)
for deviceName in deviceNames:
    did = STMIdentifier.from_string(deviceName.lower())
    # print("Parsing", did.string)
    # ndid = Node("Device", string=did.string, **did.properties)
    # graph.create(ndid)

    LOGGER.info("Parsing memory map for {}".format(did.string))
    header = STMHeader(did)
    pmap, types = header.get_memory_map()

    for typedef, registers in types.items():
        device = DeviceTree("memmap")
        device.addId(did)
        peripheral = Peripheral(typedef)
        device._addChild(-1, peripheral)
        # nperi = Node("Peripheral", name=typedef)
        # graph.create(Relationship(ndid, "MEMMAP", nperi))
        for reg in registers:
            peripheral.addRegister(reg[0], reg[2], reg[1])
            # nreg = Node("Register", position=reg[0], name=reg[2], size=reg[1])
            # graph.create(Relationship(ndid, "MEMMAP", nreg))
            # graph.create(Relationship(nperi, "REGISTER", nreg))
            # for p, (n, w, _, _, _) in reg[3].items():
            #     nfield = Node("Field", offset=p, name=n, width=w)
            #     graph.create(Relationship(ndid, "MEMMAP", nfield))
            #     graph.create(Relationship(nreg, "FIELD", nfield))
        device._sortTree()
        typelist[typedef].append(device)


def is_similar_peri(lperi, rperi):
    get_regs = lambda peri: {c["offset"]: c.name for c in peri.children}
    lregs = get_regs(lperi)
    rregs = get_regs(rperi)
    for offset, name in lregs.items():
        if offset in rregs and rregs.pop(offset) != name:
            return False
    for offset, name in rregs.items():
        if offset in lregs and lregs.pop(offset) != name:
            return False

    # print(lperi.name, lregs)
    # print(rperi.name, rregs)
    return True

def is_similar(group, rmap):
    for gmap in group:
        # print(gmap.ids)
        if is_similar_peri(gmap.children[0], rmap.children[0]):
            return True

    return False

mergelists = defaultdict(list)
for name, maps in typelist.items():
    for rmap in maps:
        for group in mergelists[name]:
            if is_similar(group, rmap):
                # print("Merging", rmap.ids)
                group.append(rmap)
                break;
        else:
            # print("New Group", rmap.ids)
            mergelists[name].append([rmap])

for name, groups in mergelists.items():
    devs = []
    counter = 0
    for group in groups:
        result = group[0]
        for d in group[1:]:
            result.merge(d)
        result.children[0].setAttribute("id", "stm32-{}".format(counter))
        result._sortTree()
        devs.append(result)
        counter += 1

    result = devs[0]
    for d in devs[1:]:
        result.merge(d)
    result._sortTree()

    DeviceMemmapWriter.write(result, output, lambda ids: name.replace("_TypeDef", "").lower())
    print(result.toString())