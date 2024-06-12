#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  check_for_corruption.py
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
print("Loading...", end="", flush=True)
import crypto_verity
import hashlib
import time
import os

md5sums = crypto_verity.loader.load_md5s()
conffiles = crypto_verity.loader.load_conffiles()
print("Done!")

time.sleep (0.25)
print("Scanning...")
time.sleep (0.25)
start = time.time()
corrupted = []
missing = []
scanned = 0
for each in md5sums:
    if each in conffiles:
        print(f"{each}: SKIPPING!!!")
        continue
    scanned+=1
    if not os.path.exists(each):
        print(f"{each}: MISSING!!!")
        if each[:14] == "/usr/share/man":
            print("File is man page. Not concerned...")
            continue
        elif ("translations" in each) or ("locale" in each):
            print("File is translation/locale file. Not concerned...")
            continue
        elif ("help" in each):
            print("File is likely help documentation. No concerned...")
            continue
        missing.append(each)
        continue
    md5 = hashlib.md5(open(each,'rb').read()).hexdigest()
    if md5 == md5sums[each]:
        print(f"{each}: OK")
    else:
        print(f"{each}: CORRUPTED!!!")
        if not crypto_verity.loader.has_diversion(each):
            corrupted.append(each)
        else:
            print("Has a diversion. Ignoring...")
end = time.time()
print("Scan Complete!")

if (len(missing) + len(corrupted)) > 0:
    packages_to_reinstall = crypto_verity.loader.files_to_packages(missing + corrupted)
    for each in missing + corrupted:
        print(each)
    print("\nIt appears you have missing or corrupt files.")
    print(f"To fix them, you need to re-install these packages:\n{' '.join(packages_to_reinstall)}")
    ans = input (f"Would you like for me to re-install these for you? [Y/n]: ")
    if ans.lower() in ("y", "yes", "yeah", "sure", "yep", "go ahead", "1"):
        crypto_verity.loader.reinstall_pkgs(packages_to_reinstall)
    else:
        print("Not reinstalling. Exiting...")
else:
    print("No missing or corrupted files found!")

real_end = time.time()
print(f"""
{'=' * 25}
#    SCAN STATISTICS    #
{'=' * 25}
Scan time:       {end-start} seconds
Total time:      {real_end-start} seconds
Files scanned:   {scanned}
Corrupted files: {len(corrupted)}
Missing files:   {len(missing)}
""")
