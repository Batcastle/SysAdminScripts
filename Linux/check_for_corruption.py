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
print("Loading", end="", flush=True)
import crypto_verity
import hashlib
import time
import os
import multiprocessing as multiproc
import psutil
import math
real_start = time.time()

md5sums = crypto_verity.loader.load_md5s()
print(".", end="", flush=True)
conffiles = crypto_verity.loader.load_conffiles()
print(".", end="", flush=True)

# Setup for multithreading versions
core_count = psutil.cpu_count()
#core_count = 2
if core_count > 4:
    core_count = math.ceil(core_count / 2)

# define how many files each thread should scan
work_load_size = math.ceil(len(md5sums) / core_count)
work_load = [{}]
count = 0
for each in md5sums:
    if count < work_load_size:
        work_load[-1][each] = md5sums[each]
        count+=1
    else:
        work_load.append({each: md5sums[each]})
        count = 1
        print(".", end="", flush=True)


print("Done!")


def scan(md5_list: dict, conf_list: list) -> dict:
    start = time.time()
    corrupted = []
    missing = []
    scanned = 0
    for each in md5_list:
        if each in conf_list:
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
        try:
            md5 = hashlib.md5(open(each,'rb').read()).hexdigest()
        except PermissionError:
            print(f"{each}: PERMISSION DENIED")
        if md5 == md5sums[each]:
            print(f"{each}: OK")
        else:
            print(f"{each}: CORRUPTED!!!")
            if not crypto_verity.loader.has_diversion(each):
                corrupted.append(each)
            else:
                print("Has a diversion. Ignoring...")
    end = time.time()
    return {"M": missing, "C": corrupted, "T": end-start, "S": scanned}

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
for each in work_load:
    queues.append(multiproc.Queue())
    threads.append(multiproc.Process(target=boilerplate, args=({"M": each, "C": conffiles}, queues[-1])))
    threads[-1].start()

# monitor their progress
count = len(threads)
# agregate data once complete
corrupted = []
missing = []
scan_run_time = 0
scanned = 0
while count > 0:
    for each in queues:
        if each.qsize() == 1:
            output = each.get()
            corrupted+=output["C"]
            missing+=output["M"]
            scanned+=output["S"]
            #each.task_done()
            threads[queues.index(each)].join()
            count-=1
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
    ans = input (f"Would you like for me to re-install these for you? [Y/n]: ")
    end_freeze = time.time()
    if ans.lower() in ("y", "yes", "yeah", "sure", "yep", "go ahead", "1"):
        crypto_verity.loader.reinstall_pkgs(packages_to_reinstall)
    else:
        print("Not reinstalling. Exiting...")
else:
    print("No missing or corrupted files found!")

real_end = time.time()
full_run_time = (real_end - real_start) - (end_freeze - start_freeze)
scan_run_time = end - start
print(f"""
{'=' * 25}
#    SCAN STATISTICS    #
{'=' * 25}
Scan time:       {"%.2f" % scan_run_time} seconds
Total time:      {"%.2f" % full_run_time} seconds
Files scanned:   {scanned}
Corrupted files: {len(corrupted)}
Missing files:   {len(missing)}
""")
