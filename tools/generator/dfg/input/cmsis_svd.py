# -*- coding: utf-8 -*-
# Copyright (c) 2018, Niklas Hauser
# All rights reserved.

import re
import logging
from libpath import Path

LOGGER = logging.getLogger('dfg.input.cmsis.svd')

class CmsisSvd:
    """
    Reading one CMSIS SVD file
    """
    PATH = Path(__file__).parents[2] / "cmsis_svd" / data /

    @staticmethod
    def get_svd(filename, replace = []):
        replacers = replace + CmsisHeader.REPLACE
        try:
            with open(filename, "r", errors="replace") as headerFile:
                content = headerFile.read()
                for r in replacers:
                    content = re.sub(r[0], r[1], content, flags=(re.DOTALL | re.MULTILINE))
                # print(content)
                return CppHeaderParser.CppHeader(content, "string")
        except CppHeaderParser.CppParseError as e:
            LOGGER.error("Unable to parse '{}': {}".format(filename, str(e)))
            return None