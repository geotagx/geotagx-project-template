# -*- coding: utf-8 -*-
#
# This module is part of the GeoTag-X project build tool.
# It contains miscellaneous helper functions.
#
# Author: Jeremy Othieno (j.othieno@gmail.com)
#
# Copyright (c) 2016-2017 UNITAR/UNOSAT
#
# The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from geotagx_validator.helper import check_arg_type

def get_formatted_configuration_set(path, enable_logging=False):
    """Returns a set of formatted configurations for the GeoTag-X project
    located at the specified path.

    Args:
        path (str): A path to a directory containing a GeoTag-X project.
        enable_logging (bool): If set to True, the function will log most of its operations.

    Returns:
        dict|None: A dictionary containing a set of formatted configurations if the specified
            path contains a valid GeoTag-X project, None otherwise.

    Raises:
        TypeError: If the path argument is not a string or enable_logging is not a boolean.
        IOError: If the specified path is inaccessible or not a directory, or if a required
            configuration in the directory at the specified path is inaccessible.
    """
    check_arg_type(get_formatted_configuration_set, "path", path, basestring)
    check_arg_type(get_formatted_configuration_set, "enable_logging", enable_logging, bool)

    from geotagx_validator.helper import deserialize_configuration_set
    from geotagx_formatter.core import format_configuration_set

    return format_configuration_set(deserialize_configuration_set(path), enable_logging)


def serialize_configuration_set(configuration_set, path, overwrite=False, compress=False):
    raise NotImplementedError
