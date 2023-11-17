"""
Made by Pelle De Deckere, October 2023

Run this at the start of the experiment

###---This file as to be in same directory as the imported module!---###

"""
#import the good stuff
import os
from os import path
import sys
import psychopy as pp
pp.useVersion('2023.2.2') #force version of psychopy everything after is based on this version
from psychopy import prefs
prefs.general['audioLib'] = ['pyo'] #this has to be imported before the sound module
from psychopy import gui, core, logging, event, visual, data, sound
sound.init(44100, buffer=128) #set audio buffers apparently this works best without cracks etc
from psychopy import __version__
from psychopy.hardware import keyboard
import pandas as pd
import time
import random
import subprocess
import pkg_resources
import csv
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import queue

#custom functions
from Main_Dopamine_PhD_PDD_BEH import run_gui_path, data_file_plumm, run_plumm_exp, tap_data_file, data_file_chord, make_list_chord, run_chord_exp, check_and_install_library, find_midi_ports, run_spon_tap, run_sync_tap #this is from the mothership

#external imports for midi
required_versions = {
    "mido": "1.3.0",
    "python-rtmidi": "1.5.6",
}

# Check and install mido
check_and_install_library("mido", required_versions["mido"])

# Check and install python-rtmidi
check_and_install_library("python-rtmidi", required_versions["python-rtmidi"])

#check for midi gear 
find_midi_ports()

# Next, run the GUI setup and path preparation
run_gui_path()

# Create the dataFile_plumm object by calling the data_file function to save plumm data
data_file_plumm()

#datafile chord
data_file_chord()

#stim and mask list, makes a personal csv for every participant
make_list_chord()

#finally, run the Plumm experiment if that's what you need and want, it will not run if off is chosen.
run_plumm_exp()

#run chord paradigm
run_chord_exp()

#data file tapping stuff
tap_data_file()

#run spon tap exp
run_spon_tap()

#run sync tap
run_sync_tap()

#i said shutdownnnnnn skrrt
core.quit()