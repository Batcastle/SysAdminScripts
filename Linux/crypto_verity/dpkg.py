#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  dpkg.py
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
"""Check Cryptographic verity of installed packages - DPKG module"""
import os
import subprocess as subproc

_dpkg_cache = "/var/lib/dpkg/info"
if not os.path.exists(_dpkg_cache):
    print("DPKG cache directory does not exist. Cannot operate. Exiting...")
    exit(1)


def load_md5s() -> dict:
    """Load MD5 sums to memory"""
    md5_files = [f"{_dpkg_cache}/{each}" for each in os.listdir(_dpkg_cache) if "md5sums" in each]
    md5_sums = {}
    for each in md5_files:
        with open(each, "r") as file:
            contents = file.read().split("\n")
        for each1 in contents:
            line = each1.split("  ")
            if line != ['']:
                md5_sums["/" + line[1]] = line[0]
    return md5_sums


def load_conffiles() -> list:
    """Load list of conffiles into memory"""
    conf_files_files = [f"{_dpkg_cache}/{each}" for each in os.listdir(_dpkg_cache) if "conffiles" in each]
    conf_files = []
    for each in conf_files_files:
        with open(each, "r") as file:
            contents = file.read().split("\n")
        for each1 in contents:
            if each1 != '':
                conf_files.append(each1)
    return conf_files


def files_to_packages(files: list) -> list:
    """Take a list of files and provide the packages they belong to."""
    pkgs = []
    for each in files:
        pkg = subproc.check_output(["dpkg", "-S", each]).decode().split(": ")[0]
        if pkg not in pkgs:
            pkgs.append(pkg)
    return pkgs


def reinstall_pkgs(packages: list) -> bool:
    """Reinstall packages"""
    try:
        subproc.check_call(["sudo", "apt-get", "update"])
        subproc.check_call(["sudo", "apt-get", "install", "--reinstall"] + packages)
    except subproc.SubprocessError:
        return False
    return True


def has_diversion(file_path: str) -> bool:
    """Check if a file has a diversion due to another package"""
    file_name = file_path.split("/")[-1].split(".")[0]
    extension = file_path.split("/")[-1].split(".")[-1]
    path = "/".join(file_path.split("/")[:-1])
    dir_contents = os.listdir(path)
    for each in dir_contents:
        if (file_name in each) and ("orig" in each) and (extension in each):
            return True
    return False
