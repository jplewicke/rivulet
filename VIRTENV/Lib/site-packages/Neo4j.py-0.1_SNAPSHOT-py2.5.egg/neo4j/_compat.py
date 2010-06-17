# -*- coding: utf-8 -*-

# Copyright (c) 2008-2010 "Neo Technology,"
#     Network Engine for Objects in Lund AB [http://neotechnology.com]
# 
# This file is part of Neo4j.py.
# 
# Neo4j.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Python version compatibility.

 This module contains compatibility code for working on both Python 2.x
 and Python 3.x.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

import sys

if sys.version_info >= (3,0):
    def is_string(obj):
        return isinstance(obj, str)
    def is_integer(obj):
        return isinstance(obj, int)
    def is_number(obj):
        return isinstance(obj, (int, float))
    raise ImportError("Py3k support not implemented.")
else:
    Object = object
    try:
        assert issubclass(unicode, basestring)
    except:
        try:
            assert len((str, unicode)) == 2
        except:
            def is_string(obj):
                return isinstance(obj, str)
        else:
            def is_string(obj):
                return isinstance(obj, (str, unicode))
    else:
        def is_string(obj):
            return isinstance(obj, basestring)
    def is_integer(obj):
        return isinstance(obj, (int, long))
    def is_number(obj):
        return isinstance(obj, (int, long, float))
