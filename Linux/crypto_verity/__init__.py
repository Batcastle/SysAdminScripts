#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  __init__.py
#
#  Copyright 2024 Thomas Castleman <batcastle@draugeros.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
"""Check Cryptographic verity of installed packages"""
import os

# We need to detect what package manager the system has so we can refrence that for MD5 sums
PATH = os.environ["PATH"].split(":")
pkgmgmnt = None
for each in PATH:
    try:
        if "apt" in os.listdir(each):
            pkgmgmnt = "apt"
            # apt found
            break
    except FileNotFoundError:
        # file does not exist. Skipping...
        pass

if pkgmgmnt is None:
    # No known package manager found. Exiting...
    exit(1)

if pkgmgmnt == "apt":
    import crypto_verity.dpkg as loader

del each, PATH, pkgmgmnt
del dpkg

