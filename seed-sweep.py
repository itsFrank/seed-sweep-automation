#!/usr/bin python3
import subprocess
import os.path
import sys
from datetime import datetime

FNULL = open(os.devnull, 'w')

def synthSetup(seed):
    cmd = ['make', 'synthsetup-seed', 'SEED={}'.format(seed)]
    subprocess.Popen(cmd, stdout=FNULL, stderr=subprocess.STDOUT).wait()

def runSynth():
    # cmd = ['cp', '/home/obrienfr/work/traversal_fpga/synth_fmax_opt_sssp/build/output_files/user_clock_freq.txt', "./synth/build/output_files/"]
    # subprocess.Popen(cmd, stdout=FNULL, stderr=subprocess.STDOUT).wait()
    cmd = ['/home/obrienfr/intel/misc/run.sh']
    with open('synth/build.log', "w+") as outfile:
        subprocess.Popen(cmd, cwd="synth", stdout=outfile).wait()

def getFmax():
    if not os.path.isfile('synth/build/output_files/user_clock_freq.txt'):
        return -1
    line = subprocess.check_output(['tail', '-1', "synth/build/output_files/user_clock_freq.txt"]).decode(sys.stdout.encoding)
    spl = line.split(":")
    return int(spl[1])

def moveFastestSynth(fmax):
    cmd = ['rm', '-rf', 'fastest_synth']
    subprocess.Popen(cmd, stdout=FNULL, stderr=subprocess.STDOUT).wait()
    cmd = ['mv', 'synth', 'fastest_synth']
    subprocess.Popen(cmd, stdout=FNULL, stderr=subprocess.STDOUT).wait()
    f = open("fastest_synth/fmax.txt","w+")
    f.write("{}".format(fmax))
    f.close()

def cleanSynth():
    cmd = ['rm', '-rf', 'synth']
    subprocess.Popen(cmd, stdout=FNULL, stderr=subprocess.STDOUT).wait()

def getExistingFmax():
    if not os.path.isdir('fastest_synth'):
        return -1
    return int(subprocess.check_output(['cat', 'fastest_synth/fmax.txt']).decode(sys.stdout.encoding))

# Can provide a start-seed to restart the process after a previous run
seed = 1
if len(sys.argv) > 1:
    seed = int(sys.argv[1])

fastest_fmax = getExistingFmax()

run = True
append_write = 'w+'
if os.path.exists("seed_sweep.log"):
    append_write = 'a' # append if already exists
f = open("seed_sweep.log", append_write)
if (append_write == "a"):
    f.write("\n")
f.write("Starting new seed-sweeping loop - Beginning with seed = {}...\n".format(seed))
while run:
    cleanSynth()
    synthSetup(seed)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f.write("[ {} ]: Starting with seed = {}...\n".format(dt_string, seed))
    f.flush()
    runSynth()
    fmax = getFmax()
    if fmax == -1:
        f.write("\tAn error occured")
        f.flush()
    else:
        f.write("\tComplete - FMAX = {}".format(fmax))
        f.flush()
        if fmax > fastest_fmax:
            fastest_fmax = fmax
            f.write("\tNew fastest; saving results to fastest_synth")
            f.flush()
            moveFastestSynth(fmax)
        f.write("\n")
        f.flush()
    seed += 1


