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
import hashlib
import time
import os
import multiprocessing as multiproc
import math
import psutil
import crypto_verity
print("Loading", end="", flush=True)
real_start = time.time()

md5sums = crypto_verity.loader.load_md5s()
print(".", end="", flush=True)
conffiles = crypto_verity.loader.load_conffiles()
print(".", end="", flush=True)

# Setup for multithreading versions
CORE_COUNT = psutil.cpu_count()
#core_count = 2
if CORE_COUNT > 4:
    CORE_COUNT = math.ceil(CORE_COUNT / 2)

# define how many files each thread should scan
WORK_LOAD_SIZE = math.ceil(len(md5sums) / CORE_COUNT)
WORK_LOAD = [{}]
COUNT = 0
for each in md5sums.items():
    if COUNT < WORK_LOAD_SIZE:
        WORK_LOAD[-1][each[0]] = each[1]
        COUNT+=1
    else:
        WORK_LOAD.append({each[0]: each[1]})
        COUNT = 1
        print(".", end="", flush=True)


print("Done!")


def scan(md5_list: dict, conf_list: list) -> dict:
    """Perform file system scan"""
    local_corrupted = []
    local_missing = []
    local_scanned = 0
    for local_each in md5_list:
        if local_each in conf_list:
            print(f"{local_each}: SKIPPING!!!")
            continue
        local_scanned+=1
        if not os.path.exists(local_each):
            print(f"{local_each}: MISSING!!!")
            if local_each[:14] == "/usr/share/man":
                print("File is man page. Not concerned...")
                continue
            if ("translations" in local_each) or ("locale" in local_each):
                print("File is translation/locale file. Not concerned...")
                continue
            if "help" in local_each:
                print("File is likely help documentation. No concerned...")
                continue
            local_missing.append(local_each)
            continue
        try:
            with open(local_each,'rb') as file:
                md5 = hashlib.md5(file.read()).hexdigest()
        except PermissionError:
            print(f"{local_each}: PERMISSION DENIED")
        if md5 == md5sums[local_each]:
            print(f"{local_each}: OK")
        else:
            print(f"{local_each}: CORRUPTED!!!")
            if not crypto_verity.loader.has_diversion(local_each):
                local_corrupted.append(local_each)
            else:
                print("Has a diversion. Ignoring...")
    return {"M": local_missing, "C": local_corrupted, "S": local_scanned}

time.sleep (0.25)
print("Scanning...")
time.sleep (0.25)
start = time.time()
# Boiler plate code to make scan() work correctly.
# Single threaded version
#results = scan(md5sums, conffiles)
#missing = results["M"]
#corrupted = results["C"]
#scan_run_time = results["T"]
#scanned = results["S"]


# Multi-threaded version
def boilerplate(workload, queue):
    """Boilerplate code for multithreaded scan"""
    results = scan(workload["M"], workload["C"])
    queue.put(results)
    queue.close()
    queue.join_thread()

# set up threads
queues = []
threads = []
for each in WORK_LOAD:
    queues.append(multiproc.Queue())
    threads.append(multiproc.Process(target=boilerplate,
                                     args=({"M": each,
                                            "C": conffiles},
                                     queues[-1])))
    threads[-1].start()

# monitor their progress
COUNT = len(threads)
# agregate data once complete
corrupted = []
missing = []
SCANNED = 0
while COUNT > 0:
    for each in queues:
        if each.qsize() == 1:
            output = each.get()
            corrupted+=output["C"]
            missing+=output["M"]
            SCANNED+=output["S"]
            #each.task_done()
            threads[queues.index(each)].join()
            COUNT-=1
    time.sleep(0.01)

end = time.time()
print("\nScan Complete!")

if (len(missing) + len(corrupted)) > 0:
    packages_to_reinstall = crypto_verity.loader.files_to_packages(missing + corrupted)
    for each in missing + corrupted:
        print(each)
    print("\nIt appears you have missing or corrupt files.")
    print(f"To fix them, you need to re-install these packages:\n{' '.join(packages_to_reinstall)}")
    start_freeze = time.time()
    ans = input ("Would you like for me to re-install these for you? [Y/n]: ")
    end_freeze = time.time()
    if ans.lower() in ("y", "yes", "yeah", "sure", "yep", "go ahead", "1"):
        crypto_verity.loader.reinstall_pkgs(packages_to_reinstall)
    else:
        print("Not reinstalling. Exiting...")
else:
    print("No missing or corrupted files found!")

real_end = time.time()
full_run_time = (real_end - real_start) - (end_freeze - start_freeze)
SCAN_RUN_TIME = end - start
print(f"""
{'=' * 25}
#    SCAN STATISTICS    #
{'=' * 25}
Scan time:       {SCAN_RUN_TIME:.2f} seconds
Total time:      {full_run_time:.2f} seconds
Files scanned:   {SCANNED}
Corrupted files: {len(corrupted)}
Missing files:   {len(missing)}
""")
