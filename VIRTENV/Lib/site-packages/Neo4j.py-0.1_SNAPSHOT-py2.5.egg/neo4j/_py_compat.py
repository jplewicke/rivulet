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
Module for compatibility between python versions.
"""

import sys

if sys.version_info[0] == 3:
    # Make Python 3.x look for the __metaclass__ member
    def Object(): # Don't pollute the namespace
        class Type(type):
            def __new__(meta, name, bases, body):
                metaclass = body.get('__metaclass__')
                if metaclass is None:
                    # No metaclass defined - delegate to type.__new__
                    return type.__new__(meta, name, bases, body)
                else:
                    # Remove the metaclass from the inheritance chain
                    new_bases = []
                    for base in bases:
                        if base is Object: base = object
                        new_bases.append(base)
                    bases = tuple(new_bases)
                    # Create the class as an instance of the metaclass
                    return metaclass(name, bases, body)
        Object = Type('Object', (object,), {}) # Define in local namespace
        return Object
    Object = Object()

    Set = set

    def is_string(obj):
        return isinstance(obj, str)

    def is_integer(obj):
        return isinstance(obj, int)

elif sys.version_info[0] == 2:
    Object = object

    try:
        Set = set
    except:
        from sets import Set

    try:
        _stringtype = basestring
    except:
        try:
            _stringtype = (str, unicode)
        except:
            _stringtype = str
    def is_string(obj):
        return isinstance(obj, _stringtype)

    def is_integer(obj):
        return isinstance(obj, (int, long))

else:
    raise ImportError("Unsupported Python version")
