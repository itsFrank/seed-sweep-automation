#!/usr/bin python3
import subprocess
import os.path
import sys

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
    seed = int(sys.argv[0])

fastest_fmax = getExistingFmax()

run = True
while run:
    cleanSynth()
    synthSetup(seed)
    print("Starting with seed = {}...".format(seed), end = " ", flush=True)
    runSynth()
    fmax = getFmax()
    if fmax == -1:
        print("An error occured")
    else:
        print("Complete - FMAX = {}".format(fmax), end = " ", flush=True)
        if fmax > fastest_fmax:
            print(" - New fastest; saving results to fastest_synth", end = " ", flush=True)
            moveFastestSynth(fmax)
        print("")
    seed += 1


