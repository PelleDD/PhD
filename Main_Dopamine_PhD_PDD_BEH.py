"""
Made by Pelle De Deckere, October 2023
Last revision: October 2023

I'm not a professional coder! Hello world
Street Code

Contact details:
https://pure.au.dk/portal/en/persons/pelle-de-deckere(ba57d59a-a1d5-438b-a8e4-33f9c5ad7e17).html
https://www.linkedin.com/in/pelle-de-deckere/
https://twitter.com/DeckerePelle
https://github.com/PelleDD


$$$**********################# IMPORTANT NOTES #############################******$$$
NEEDS TO BE RUN FROM PSYCHOPY STANDALONE APP 
 - not from any other python editor or terminal
 - tested inside PsychoPy Coder/Runner 2023.2.2

TO RUN:  
Make a file something like this, remember tp check some functions need to run before others for settings etc:

from Main_Dopamine_PhD_PDD_BEH import run_gui_path, data_file_plumm, run_plumm_exp, data_file_chord, make_list_chord, run_chord_exp #this is from the mothership

# Next, run the GUI setup and path preparation
run_gui_path()

# Create the dataFile_plumm object by calling the data_file function to save plumm data
data_file_plumm()


Run this code in the psychopy coder and click run, after one run the file will also show up in the runner

In case of library installation (midi etc) it is possible you have to run it twice before it works

###---CONTENT---###
This Main PsychoPy file containis functions for following paradigms:

- Plumm Paradigm 
- Chord Paradigm
- Spontaneous tapping task
- Synchronization continuation

###---Directory Organisation---###
- Main map
    - This file
    - Your file you run things from
       Use like this: from Main_Dopamine_PhD_PDD_BEH import run_gui_path, data_file_plumm, run_plumm_exp, data_file_chord, make_list_chord, run_chord_exp() 
    - stimuli_plumm
        - wav files
        - CSV files with stim name list under stim_name
    - stimuli_chord
        - wav files
        - csv files with stim names and mask names
    - stimuli_sync_tap
    - subject_data_pdd #gets created if not there, you can change this name

"""

#check these imports as well for each def when using certain functions seperatly
#imports
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
import random
import subprocess
import pkg_resources
import csv
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import queue

'''
some explenation on external imports for me to remember

custom imports get installed in your standalone version of psychopy go to app show contents 
Recources/lib/pyhtonX/... (mac); folder called site packages has the added libraries

from psychopy site
Adding a .pth file
An alternative is to add a file into the site-packages folder of your application. This file should be pure text and have the extension .pth to indicate to Python that it adds to the path.
On win32 the site-packages folder will be something like C:/Program Files/PsychoPy2/lib/site-packages
On macOS you need to right-click the application icon, select Show Package Contents and then navigate down to Contents/Resources/lib/pythonX.X. Put your .pth file here, next to the various libraries.
The advantage of this method is that you dont need to do the import psychopy step. The downside is that when you update PsychoPy to a new major release youll need to repeat this step (patch updates wont affect it though).


mido pushes also something into the bin folder of your psychopy (in case of deleting)
'''

#BECAUSE OF THIS THE SCRIPT HAS TO RUN ONCE FIRST, ON THE SECOND RUN EXTERNAL IMPORTS WORK#
#importing external stuff needed for midi controls, mido needs rtmidi
#define the required library versions
required_versions = {
    "mido": "1.3.0",
    "python-rtmidi": "1.5.6",
}

# Function to check and install libraries with specific versions
def check_and_install_library(library_name, required_version):
    try:
        import_module = __import__(library_name)
        installed_version = pkg_resources.get_distribution(library_name).version

        if installed_version == required_version:
            print(f"Found {library_name} version {installed_version}")
        else:
            print(f"Found {library_name} version {installed_version}, but version {required_version} is required.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{library_name}=={required_version}"])

    except ImportError:
        print(f"{library_name} not found. Installing {library_name} version {required_version}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{library_name}=={required_version}"])

# Check and install mido
#check_and_install_library("mido", required_versions["mido"])

# Check and install python-rtmidi
#check_and_install_library("python-rtmidi", required_versions["python-rtmidi"])

#import these external libraries
import mido
import rtmidi

#look what you have, MIDI gear
def find_midi_ports():
  print(f"Input ports: {mido.get_input_names()}")
  print(f"Output ports: {mido.get_output_names()}") 

#find_midi_ports()

"""
imports done, gear checked
"""


"""
This stuff has to run for the functions to functionnn 

It will create a GUI for you to fill in at the start
Create paths to everywhere we need to be, keys, ... globalize legalize
"""

def run_gui_path():
    #version psychopy
    global psy_version
    psy_version = __version__

    #tell me everything you encounter
    logging.console.setLevel(logging.DEBUG) #tell me everything you encounter

    #get directory name of file, give path to this directory
    global my_path
    my_path = os.path.abspath(os.path.dirname(__file__))

    #change working directory to given path of this file
    os.chdir(my_path)

    #Create folder in the map this file is, for all subject output data if there is not one already
    global data_dir
    data_dir = os.path.join(my_path, 'subject_data_pdd') #change this for your own projects
    os.makedirs(data_dir, exist_ok=True)

    #Get the path to the current working directory
    global cwd
    cwd = os.getcwd()

    #Construct the path to the stimuli folder inside the project folder
    global stimuli_plumm_path
    stimuli_plumm_path = os.path.join(cwd, "stimuli_plumm")
    global stimuli_chord_path
    stimuli_chord_path = os.path.join(cwd, "stimuli_chord")
    global stimuli_path_sync_tap
    stimuli_path_sync_tap = os.path.join(cwd, "stimuli_sync_tap")

    #Set default settings, dictionary
    global settings
    settings = {
                'subject': '0',  # Subject code use for loading/saving data
                'gender': ['male', 'female'],
                'age': '',
                'session': '1', #session 
                'run_type_plumm': ['training','exp','off'], #run type for plumm paradigm or turn off
                'run_type_chord': ['training','exp', 'off'], #run type for chord paradigm or turn off
                'run_type_spon_tap': ['training','exp', 'off'], #run type for spontaneous tapping task 
                'run_type_sync_tap': ['training','exp', 'off'], #run type for synchronization continuation tapping task
                'run_type_dur_est': ['training','exp', 'off'], #run type for duration discrmination task
                'debug': True,  # If true, small window, print extra info
                'home_dir': my_path, #not really being used but maybe handy to see where all this stuff is running from
                'after_stim_plumm': 0, #time between end of stim and appearance of rating scale
                'rating_time_plumm': 7, # number of seconds to make rating       
                'between_stim_chord': 2, # number of seconds between two presenations of the chord stim
                'after_mask_chord': 2, #time between mask and next chord 
                'after_stim_chord': 0, #time between end of stim and appearance of rating scale
                'rating_time_chord': 7, # number of seconds to make rating
                'spon_tap_duration': 20, # amount of taps per trial for the duration of the spontaneous tapping task
                'sync_break_duration': 3, #time between the audio stim from the sync tap task       
            }

    #Push date, exp name and psychopy version into settings
    settings['date'] = data.getDateStr() # get date and time via data module
    settings['exp_name'] = 'dopamine_phd_pdd_beh' #set experiment name
    settings['version'] = psy_version #push version of psychopy used in the gui

    # Define the order in which you want the elements to appear in the GUI
    element_order = [
    'subject',
    'gender',
    'age',
    'session',
    'run_type_plumm',
    'run_type_chord',
    'run_type_spon_tap',
    'run_type_sync_tap',
    'run_type_dur_est',
    'debug',
    'home_dir',
    'after_stim_plumm',
    'rating_time_plumm',
    'between_stim_chord',
    'after_mask_chord',
    'after_stim_chord',
    'rating_time_chord',
    'spon_tap_duration', 
    'sync_break_duration', 
    ]

    #create dialog box, we put this here because we need the settingssss for stuff to direct
    info_dlg = gui.DlgFromDict(settings, title='settings', order=element_order)

    if info_dlg.OK: #if user presses OK then
        global next_settings
        next_settings = settings.copy()
    else: #user didn't press OK, i.e. cancelled
        core.quit()

    #folder name for the subject
    sub_folder_name = settings['subject'] + '_' + settings['date'] + '_' + settings['exp_name']

    #Create subject folder in the subject_data map this map is for individual output data if there is not one already
    if  settings['run_type_plumm'] in ['exp', 'training'] or \
        settings['run_type_chord'] in ['exp', 'training'] or \
        settings['run_type_spon_tap'] in ['exp', 'training'] or \
        settings['run_type_dur_disc'] in ['exp', 'training'] or \
        settings['run_type_sync_tap'] in ['exp', 'training']: #dont make a subject folder if all is off
            sub_dir = os.path.join(data_dir, sub_folder_name)
            os.makedirs(sub_dir, exist_ok=True)

            #path where data is pushed to, it joins the cwd with the map subject_data
            global data_path
            data_path = sub_dir

    #function and key to quit the experiment and save log file
    #Set relevant keys
    global kb
    kb = keyboard.Keyboard()
    global keyESC
    keyESC = 'escape' #key to quit experiment
    global keyNext
    keyNext = 'space' #key to advance

    #ESC quits the experiment
    if event.getKeys(keyList = [keyESC]): #press 'escape'
        logging.flush()
        core.quit()

    #set window size
    global win
    if settings['debug']: #if in debug mode, not full screen
            win = visual.Window(fullscr=False)
            
    else: #otherwise full screen
            win = visual.Window(monitor='testMonitor', fullscr=True)

    #make sure mouse is visible
    win.allowGUI = True                        
    win.mouseVisible = True

    #return settings, data_path

"""
MAKING OF CHORD/MASK list for Chord Paradigm

you need to run this before the run_chord_exp

unequal amount of chords and masks and random assign every chord with a mask you need this, otherwise you can run the trialhandler 
straight from the csv for one kind of stimuli or equal amount of different stimuli like this
trialList=data.importConditions(csv_list)
"""
def make_list_chord():
    if settings['run_type_chord'] == 'exp':
        csv_list = os.path.join(stimuli_chord_path, "stim_mask_list_chord_train.csv")
    else:
        csv_list = os.path.join(stimuli_chord_path, "stim_mask_list_chord_train.csv")
    # Load the stim/mask CSV file into a DataFrame, csv_list deterimned by the training or exp, THE SEP thing costed me 3 hours to figure out, check column names!!!
    df = pd.read_csv(csv_list, engine='python', encoding = 'utf-8', sep=';')

    # Extract the mask and stim column into a list
    stim_list = df['stim'].tolist()
    mask_list = df['mask'].dropna().tolist()

    # Initialize a list to store assigned masks per chord
    global assigned_masks
    assigned_masks = []

    for i in stim_list:
        global mask
        mask = random.choice(mask_list)
        assigned_masks.append(mask)

    # Add the assigned masks as a new column in the DataFrame
    df['assignedmask'] = assigned_masks

    #Construct the path to the CSV file inside the stimuli folder both for the exp and training session
    global assigned_csv_file
    if settings['run_type_chord'] == 'exp':
        #new csv file name
        assigned_csv_file =  "chord_assigned" + '_' + next_settings['subject'] + ".csv"
    else:
        assigned_csv_file =  "chord_train" + '_' + next_settings['subject'] + ".csv"

    # Save the DataFrame with the 'assignedmask' column to a new CSV file
    output_csv_path = os.path.join(data_path, assigned_csv_file)
    df.to_csv(output_csv_path, sep=';', index=False)  # Save to a new CSV file

    #make a path to the csv file for the trial handler to pull
    global csv_file_assigned
    csv_file_assigned = output_csv_path

"""
You need this to run before everything to have a data handler to push your data stuff, other functions will use the object dataFile_x
"""
def data_file_plumm(): #psychopy to save output etc
    if settings['run_type_plumm'] in ['exp', 'training']: #create this stuff when we do stuff not when off
        # create a filename with path seperated by the unique name it should get when exp
        global filename_plumm
        filename_plumm = data_path + os.sep + settings['subject'] + '_' + settings['date'] + '_' + '_' + 'plumm' + '_' + settings['exp_name']

        #An ExperimentHandler to push data into, helps with data saving during the exp
        global dataFile_plumm
        dataFile_plumm = data.ExperimentHandler(name=next_settings['exp_name'], version='1.0.0',
            extraInfo=next_settings, runtimeInfo=None,
            originPath=my_path,
            savePickle=True, saveWideText=True,
            dataFileName=filename_plumm)
        
def data_file_chord(): #datafile handler for the chord experiment
    if settings['run_type_chord'] in ['exp', 'training']: #create this stuff when we do stuff not when off
        # create a filename with path seperated by the unique name it should get when exp
        global filename_chord
        filename_chord = data_path + os.sep + settings['subject'] + '_' + settings['date'] + '_' + '_' + 'chord' + '_' + settings['exp_name']

        #An ExperimentHandler to push data into, helps with data saving during the exp
        global dataFile_chord
        dataFile_chord = data.ExperimentHandler(name=next_settings['exp_name'], version='1.0.0',
            extraInfo=next_settings, runtimeInfo=None,
            originPath=my_path,
            savePickle=True, saveWideText=True,
            dataFileName=filename_chord)
        
"""
This runs the pleasurable urge to move to music (PLUMM) paradigm:

x amount of auditory stimuli get presented 3 times (randomized per block), with a different question. Between each trial there is a break provided
- wanting to move
- pleasure
- complexity

name of stim get read out of a csv inside of a stimuli map where the wav files are located
"""

def run_plumm_exp():
    if settings['run_type_plumm'] in ['exp', 'training']: #if off dont run this
        #rating instructions
        rate_inst_move = '\n\nHow much did this musical pattern make you want to move? \n\n'
        rate_inst_pleasure = '\n\nHow much pleasure did you experience listening to this musical pattern? \n\n'
        rate_inst_complexity = '\n\nHow complex do you find this musical pattern? \n\n'
        rate_inst_full = [rate_inst_move, rate_inst_pleasure, rate_inst_complexity]
        # Join the list of instructions into a single string
        rate_inst_full = ''.join(rate_inst_full)
        
        #create instructions     
        exp_inst =      ('EXPERIMENT \n\n'+
                        'Please listen closely to the following rhythms. '+ 
                        'A rhythm will be presented once in each trial. '+
                        'On every trial you will be asked to rate. '+  
                        rate_inst_full +
                        'You will use the mouse to make your ratings by clicking on the scale (1-100). '+
                        '1 = not at all / none / very weak and '+
                        '100 = very much / a lot / very strong. '+
                        'Please make your rating based on your initial impression of the rhythm without overthinking it. \n\n'+
                        'PRESS SPACE TO START.'  )

        # set instruction text parameters
        instr = visual.TextStim(win, text = exp_inst, height=.05, pos=(0, 0), wrapWidth=1.8, alignHoriz='center', alignVert='center')
        
        #welcome text
        welcome = visual.TextStim(win, text='Welcome to the experiment! \n\nPlease press space to continue.', pos=(0, 0))

        #break text
        break_text = visual.TextStim(win, text='Take a short break. Press SPACE to continue.', pos=(0, 0))
        
        #make fixation cross                          
        fixation = visual.ShapeStim(win,
                                    vertices=((0, -0.15), (0, 0.15), (0, 0),
                                            (-0.1, 0), (0.1, 0)),
                                    lineWidth=13,
                                    closeShape=False,
                                    lineColor='white')

        #End screen
        end = visual.TextStim(win, text = 
        'Thanks for participating \n\n'
        'Press space to quit the experiment \n\n')

        #create visual rating scales 
        RatingScale = visual.RatingScale(win, low = 1, high = 100, mouseOnly=True, pos=(0, -0.1),
            scale = 'not at all                                                              very much',
            markerStart = 50, showAccept = False, stretch = 2, skipKeys = None,        
            marker='circle', size=0.85, name='plumm_rating', tickMarks = [1, 25, 50, 75, 100])

        #create a sound objects this will change later through the setsound function
        sound_1 = sound.Sound('A', secs=8, stereo=True, hamming=True,
        name='sound_1') #stim are 8s
        sound_duration = sound_1.getDuration() #so we know how long it has to play
        sound_1.setVolume(1.0, log=False) #1 is the max for psychopy so volume control is controlled by os

        ####---EXPERIMENT STARTS---####
        #set clocks
        globalClock = core.Clock()  # to track the time since experiment started

        #draw instructions and flip it on the screen
        welcome.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        #draw instructions depending what has been chosen
        instr.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        #change cwd to the stimuli map otherwise it cannot trigger the files from the map
        os.chdir(stimuli_plumm_path)

        #Construct the path to the CSV file inside the stimuli folder both for the exp and training session for plumm
        if settings['run_type_plumm'] == 'exp':
            csv_list = os.path.join(stimuli_plumm_path, "stim_list_groove.csv")
        else:
            csv_list = os.path.join(stimuli_plumm_path, "stim_list_groove_train.csv")

        ###---LOOP STARTS---###
        #set up trial handler to look after randomisation of conditions etc for the actual exp
        trials = data.TrialHandler(nReps=3.0, method='random', #nreps because we want this thing to run 3 times for each question
            extraInfo=next_settings, originPath=-1,
            trialList=data.importConditions(csv_list),
            seed=None, name='trials')
        dataFile_plumm.addLoop(trials)  # add the loop to the experiment
        thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values

        for thisTrial in trials: #everything in this loop changes per trial/block
            repetition_number = trials.thisRepN  # Get the current repetition number of the trial
            trial_number = trials.thisN
            #Now you can use 'repetition_number' to modify something in your trials
            if repetition_number == 0:
                #create rating question 
                rate_inst = visual.TextStim(win, text = rate_inst_move, height=.07, pos=(0, .25))
            elif repetition_number == 1:
                #create rating question 
                rate_inst = visual.TextStim(win, text = rate_inst_pleasure, height=.07, pos=(0, .25))
            else:
                #create rating question 
                rate_inst = visual.TextStim(win, text = rate_inst_complexity, height=.07, pos=(0, .25))
            
            if (trial_number == 3 or trial_number == 6) and settings['run_type_plumm'] == 'training': #here you can put in precise breaks for certain modes
                break_text.draw()
                win.flip()
                event.waitKeys(keyList=[keyNext])

            if (trial_number == 12 or trial_number == 24) and settings['run_type_plumm'] == 'exp':
                break_text.draw()
                win.flip()
                event.waitKeys(keyList=[keyNext])       
                
            #i do not know what this does but it goes into the csv and read the headers of the lists or something, it works... 
            if thisTrial != None: #when this starts your inside the trial in this case the list of auditory stim
                    for paramName in thisTrial:
                            exec('{} = thisTrial[paramName]'.format(paramName))
                    # Extract the 'stim_name' from your CSV data
                    stim_name = thisTrial['stim_name']
                    
                    #update sound components parameters for each repeat of the loop depending on choice in gui
                    sound_1.setSound(stim_name, hamming = True)  

                    #timer for routine
                    routineTimer = core.Clock()  #to track time remaining of each routine 

                    #Prepare to start Routine, mask stim
                    routineForceEnded = False
                    #start mask
                    while routineTimer.getTime() < (sound_duration):
                        fixation.draw()
                        sound_1.play(when=win)
                        win.flip()
                        core.wait(sound_duration + settings['after_stim_plumm'])
                        if event.getKeys(keyList = [keyESC]): #press 'escape'
                            logging.flush()
                            core.quit()
                    if routineForceEnded:
                        routineTimer.reset()
                    else:
                        routineTimer.addTime(-sound_duration)
                        
                    #start rating routine (think of blocks) 
                    routineForceEnded = False

                    #reset from previous run
                    RatingScale.reset()
                    #now we start the visual part of the rating block, give x s of time to rate
                    while routineTimer.getTime() < settings['rating_time_plumm']:
                        rate_inst.draw()
                        RatingScale.draw()
                        win.flip()
                        if event.getKeys(keyList = [keyESC]): #press 'escape'
                            logging.flush()
                            core.quit()    
                    #add the data to the output file
                    trials.addData('RatingScale.response', RatingScale.getRating())
                    trials.addData('RatingScale.rt', RatingScale.getRT())
                    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
                    if routineForceEnded:
                        routineTimer.reset()
                    else:
                        routineTimer.addTime(-settings['rating_time_plumm'])

                    dataFile_plumm.nextEntry()

        ###---SAVING OUTPUT/QUIT---###
        #change working directory back to the path of the python file
        os.chdir(my_path)

        #get names of stimulus parameters, needed for the data save
        if trials.trialList in ([], [None], None):
            params = []
        else:
            params = trials.trialList[0].keys()

        if settings['run_type_plumm'] != 'training': #dont save training data
            #save data for this loop
            trials.saveAsExcel(filename_plumm + '.xlsx', sheetName='trials',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
            #csv
            dataFile_plumm.saveAsWideText(filename_plumm + '.csv', delim='auto') #because of this you need to run data_file as well before using this
        
        #clean slate, a new beginning
        logging.flush()

        #show end screen
        end.draw() 
        win.flip()
        event.waitKeys(keyList = [keyNext])         #list restricts options for key presses, waiting for space

        #close and clean
        dataFile_plumm.abort() #to prevent double save
        

"""
Chord/harmony paradigm

x amount of chords are presented twice with a break in between. Between the different chords a masking stim is presented. Every presentation of a chord is followed by likability scale rating.
"""
def run_chord_exp():
    if settings['run_type_chord'] in ['exp', 'training']: #if off dont run this
        if settings['run_type_chord'] == 'exp':
            csv_list_chord = os.path.join(stimuli_chord_path, "stim_mask_list_chord.csv")
        else:
            csv_list_chord = os.path.join(stimuli_chord_path, "stim_mask_list_chord_train.csv")
        # Load the stim/mask CSV file into a DataFrame, csv_list deterimned by the training or exp, THE SEP thing costed me 3 hours to figure out, check column names!!!
        df = pd.read_csv(csv_list_chord, engine='python', encoding = 'utf-8', sep=';')

        # Extract the mask and stim column into a list
        stim_list = df['stim'].tolist()
        mask_list = df['mask'].dropna().tolist()

        # Initialize a list to store assigned masks per chord
        #global assigned_masks
        assigned_masks = []

        for i in stim_list:
            #global mask
            mask = random.choice(mask_list)
            assigned_masks.append(mask)

        # Add the assigned masks as a new column in the DataFrame
        df['assignedmask'] = assigned_masks

        #Construct the path to the CSV file inside the stimuli folder both for the exp and training session
        #global assigned_csv_file
        if settings['run_type_chord'] == 'exp':
            #new csv file name
            assigned_csv_file =  "chord_assigned" + '_' + next_settings['subject'] + ".csv"
        else:
            assigned_csv_file =  "chord_train" + '_' + next_settings['subject'] + ".csv"

        # Save the DataFrame with the 'assignedmask' column to a new CSV file
        output_csv_path = os.path.join(data_path, assigned_csv_file)
        df.to_csv(output_csv_path, sep=';', index=False)  # Save to a new CSV file

        #make a path to the csv file for the trial handler to pull
        #global csv_file_assigned
        csv_file_assigned = output_csv_path

        # create text stimulus
        welcome = visual.TextStim(win, text='Welcome to the experiment! \n\nPlease press space to continue.', 
                                    pos=(0, 0))

        #create instructions     
        exp_inst =          'EXPERIMENT \n\n' \
                            'Please listen closely to the following chords. ' \
                            'A chord will be presented twice in each trial. ' \
                            'On every trial you will be asked to rate. ' \
                            'how much you liked that chord. ' \
                            'You will use the mouse to make your ratings by clicking on the scale (1-100). '\
                            '1 = not at all / none / very weak and '\
                            '100 = very much / a lot / very strong. '\
                            'Please make your rating based on your initial impression of the chord without overthinking it. '\
                            'Remember to listen to and rate the chord and not the random note sequence in between. \n\n'\
                            'PRESS SPACE TO START.'
                            
        #create instructions     
        pract_inst =        'PRACTICE RUN \n\n' \
                            'Please listen closely to the following chords. ' \
                            'A chord will be presented twice in each trial. ' \
                            'On every trial you will be asked to rate ' \
                            'how much you liked that chord. ' \
                            'You will use the mouse to make your ratings by clicking on the scale (1-100). '\
                            '1 = not at all / none / very weak and '\
                            '100 = very much / a lot / very strong. '\
                            'Please make your rating based on your initial impression of the chord without overthinking it. '\
                            'Remember to listen to and rate the chord and not the random note sequence in between. \n\n'\
                            'PRESS SPACE TO START.'               

        #if training run, then use training instructions 
        if settings['run_type_chord'] == 'training':
            text_inst = pract_inst #instructions            
        else: #otherwise, exp
            text_inst = exp_inst  

        # set instruction text parameters
        instr = visual.TextStim(win, text = text_inst, height=.05, pos=(0, 0), wrapWidth=1.8, alignHoriz='center', alignVert='center')
            
        #create rating question 
        rate_inst = visual.TextStim(win, text = 'How much did you like the chord?', height=.07, pos=(0, .25))

        #make fixation cross                          
        fixation = visual.ShapeStim(win,
                                        vertices=((0, -0.15), (0, 0.15), (0, 0),
                                                (-0.1, 0), (0.1, 0)),
                                        lineWidth=13,
                                        closeShape=False,
                                        lineColor='white')

        #End screen
        end = visual.TextStim(win, text = 
            'Thanks for participating \n\n'
            'Press space to quit the experiment \n\n')

        #create visual rating scales 
        RatingScale = visual.RatingScale(win, low = 1, high = 100, mouseOnly=True, pos=(0, -0.1),
                scale = 'not at all                                                              very much',
                markerStart = 50, showAccept = False, stretch = 2, skipKeys = None,        
                marker='circle', size=0.85, name='Liking', tickMarks = [1, 25, 50, 75, 100])

        #create a sound objects this will change later through the setsound function
        sound_1 = sound.Sound('A', secs=2, stereo=True, hamming=True,
            name='sound_1') #stim are 2s
        mask_1 = sound.Sound('A', secs=3, stereo=True, hamming=True,
            name='mask') #masks are 3s

        sound_duration = sound_1.getDuration() #so we know how long it has to play
        mask_duration = mask_1.getDuration()

        sound_1.setVolume(1.0, log=False) #1 is the max for psychopy so volume control is controlled by os
        mask_1.setVolume(1.0, log=False)

        ####---EXPERIMENT/TRAINING STARTS---####
        #set clocks
        globalClock_chord = core.Clock()  # to track the time since experiment started

        #draw instructions and flip it on the screen
        welcome.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        #draw instructions depending what has been chosen
        instr.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        #change cwd to the stimuli map otherwise it cannot trigger the files from the map
        os.chdir(stimuli_chord_path)

        #set up trial handler to look after randomisation of conditions etc for the actual exp
        trials_chord = data.TrialHandler(nReps=1.0, method='random', 
            extraInfo=next_settings, originPath=-1,
            trialList=data.importConditions(csv_file_assigned),
            seed=None, name='trials')
        dataFile_chord.addLoop(trials_chord)  # add the loop to the experiment
        thisTrial = trials_chord.trialList[0]  # so we can initialise stimuli with some values

        ####---EXPERIMENT---####
        #start loop sequence
        for thisTrial in trials_chord:
            #i do not know what this does but it goes into the csv and read the headers of the lists or something, it works... loopy loopy
            if thisTrial != None:
                for paramName in thisTrial:
                    exec('{} = thisTrial[paramName]'.format(paramName))
                    # Extract the 'stim_name' from your CSV data
                    stim = thisTrial['stim']
                    assignedmask = thisTrial['assignedmask']

                #update sound components parameters for each repeat of the loop depending on choice in gui
                sound_1.setSound(stim, hamming = True)  
                mask_1.setSound(assignedmask, hamming = True)

                #timer for routine
                routineTimer_chord = core.Clock()  #to track time remaining of each routine 

                #Prepare to start Routine, mask stim
                routineForceEnded = False
                #start mask
                while routineTimer_chord.getTime() < (settings['after_mask_chord'] + mask_duration):
                    fixation.draw()
                    mask_1.play(when=win)
                    win.flip()
                    core.wait(mask_duration + settings['after_mask_chord'])
                    if event.getKeys(keyList = [keyESC]): #press 'escape'
                        logging.flush()
                        core.quit()
                if routineForceEnded:
                    routineTimer_chord.reset()
                else:
                    routineTimer_chord.addTime(-mask_duration - settings['after_mask_chord'])  

                #Prepare to start Routine, sound stim
                routineForceEnded = False
                #all the components of this block
                #start the block with sound
                while routineTimer_chord.getTime() < (2*sound_duration + settings['between_stim_chord']+ settings['after_stim_chord']):
                    fixation.draw()
                    sound_1.play(when=win)
                    win.flip()
                    core.wait(sound_duration + settings['between_stim_chord'])
                    fixation.draw()
                    sound_1.play(when=win)
                    win.flip()
                    core.wait(sound_duration + settings['after_stim_chord'])
                    #core.wait(2*sound_duration + settings['between_stim'])
                    if event.getKeys(keyList = [keyESC]): #press 'escape'
                        logging.flush()
                        core.quit()

                if routineForceEnded:
                    routineTimer_chord.reset()
                else:
                    routineTimer_chord.addTime(-settings['between_stim_chord']-2*sound_duration+ settings['after_stim_chord'])  
                    
                #start rating routine (think of blocks) 
                routineForceEnded = False
                #reset from previous run
                RatingScale.reset()
                #now we start the visual part of the rating block, give x s of time to rate
                while routineTimer_chord.getTime() < settings['rating_time_chord']:
                    rate_inst.draw()
                    RatingScale.draw()
                    win.flip()
                    if event.getKeys(keyList = [keyESC]): #press 'escape'
                        logging.flush()
                        core.quit()    
                #add the data to the output file
                trials_chord.addData('RatingScale.response', RatingScale.getRating())
                trials_chord.addData('RatingScale.rt', RatingScale.getRT())
                # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
                if routineForceEnded:
                    routineTimer_chord.reset()
                else:
                    routineTimer_chord.addTime(-settings['rating_time_chord'])

                dataFile_chord.nextEntry()

        #change working directory back to the path of the python file
        os.chdir(my_path)

        #get names of stimulus parameters, needed for the data save
        if trials_chord.trialList in ([], [None], None):
            params = []
        else:
            params = trials_chord.trialList[0].keys()

        #save data only when exp is running these shouldn't be strictly necessary (should auto-save)
        if settings['run_type_chord'] == 'exp':
            trials_chord.saveAsExcel(filename_chord + '.xlsx', sheetName='trials',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            dataFile_chord.saveAsWideText(filename_chord+'.csv', delim='auto') 

        #log flush
        logging.flush()

        #show end screen
        end.draw() 
        win.flip()
        event.waitKeys(keyList = [keyNext])         #list restricts options for key presses, waiting for space

        #close and clean
        dataFile_chord.abort() #to prevent double save
        

"""
needed for tap experiments
"""

def tap_data_file():
    global tap_filename
    tap_filename = data_path + os.sep + settings['subject'] + '_' + 'tap_' + settings['date'] + '_' + settings['exp_name']

"""
Spontaneous tapping task
"""

def run_spon_tap():
    if settings['run_type_spon_tap'] in ['exp', 'training']: #if off dont run this
        
        # Create a "Thank you" message
        welcome = visual.TextStim(win, text="Thank you for participating!\n\n" \
                                    "Press space to continue" 
                                    , pos=(0, 0))

        # Create a "Thank you" message end
        end = visual.TextStim(win, text="Thank you for participating!\n\n" \
                                    "Press space to end" 
                                    , pos=(0, 0))

        #Instructions spon tap message
        instr_spon_tap = visual.TextStim(win, text= "Tap on the MIDI pad at your preferred steady tempo.\n\n" \
                                    "Press space to continue" 
                                        , pos=(0, 0))

        #make fixation cross                          
        fixation = visual.ShapeStim(win,
                                    vertices=((0, -0.15), (0, 0.15), (0, 0),
                                            (-0.1, 0), (0.1, 0)),
                                    lineWidth=13,
                                    closeShape=False,
                                    lineColor='white')
        
        
        # Create break screen
        break_text = visual.TextStim(win, text="Pause\n\n" \
                                     "Press Space to start"
                                     , pos=(0, 0))
                
        # Initialize lists to store tap data
        # Initialize variables
        num_taps = settings['spon_tap_duration']
        if settings['run_type_spon_tap'] == 'exp':
            num_runs = 3
        else:
            num_runs = 1
        taps_completed = 0 #count taps during trial
        spon_tap_data = []

        #lets try to open the gates of midi, change names wathever you are using
        midi_device_1 = 'Arturia BeatStep'
        midi_device_2 = 'APC Key 25'
        try:
            midi_input = mido.open_input(midi_device_1)
            print("Using Arturia BeatStep MIDI input.")
        except IOError:
            # If 'Arturia BeatStep' is not available, try to open 'APC Key 25'
            try:
                midi_input = mido.open_input(midi_device_2)
                print("Using APC Key 25 MIDI input.")
            except IOError:
                # If both devices are unavailable, handle the error or set a default input
                print("No suitable MIDI input found. Handle the error or set a default input.")
        
        ###---EXPERIMENT/TRAINING STARTS---####
        #set clocks
        globalClock = core.Clock()  # to track the time since experiment started

        #draw instructions and flip it on the screen
        welcome.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        #draw instructions depending what has been chosen
        instr_spon_tap.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        ###SPONTANEOUS TAPPING###
        #Participants tap x times on their own preferred pace
        #start
        # Outer loop for multiple runs
        for run in range(num_runs):
            taps_completed = 0  # Reset taps_completed for each run
            
            if run > 0: #no break screen at the first run
                # Show a break screen
                break_text.draw()
                win.flip()
                # Wait for spacebar press to start the run
                event.waitKeys(keyList=[keyNext])

            start_time = time.time()
            #while time.time() - start_time < settings['spon_tap_duration']: #you can use this if you want to use time
            while taps_completed < num_taps:
                fixation.draw()
                win.flip()
                for msg in midi_input.iter_pending():
                    if msg.type == 'note_on':
                        tap_time = (time.time() - start_time)
                        tap_velocity = msg.velocity
                        # Create a dictionary to store tap data first and settings later
                        tap_entry = {
                                'tap_timing(s)': tap_time,
                                'tap_velocity(s)': tap_velocity,
                                'audio_file': '',
                                'audio_onset_timing(s)': '',
                                'audio_close_timing(s)': '', 
                                'task': f'spontaneous_tap_run_{run + 1}' #gives the task and the run number of the trial
                            }
                        # Add settings data to the tap entry
                        tap_entry.update(settings)
                        # Append the tap entry to the list of tap data, looopy
                        spon_tap_data.append(tap_entry)

                        # Increment the taps_completed counter
                        taps_completed += 1

        # Close the MIDI input when the experiment is done
        midi_input.close()

        # Save the data this function is made for this task to save
        def save_to_csv(filename, tap_data):
            if not filename.endswith(".csv"):
                filename += ".csv" #if the filename doesnt have the extension .csv add it
            with open(filename, 'w', newline='') as csvfile:
                    csvwriter = csv.DictWriter(csvfile, fieldnames=tap_data[0].keys())

                    # Write headers
                    csvwriter.writeheader()

                    # Write tap data
                    csvwriter.writerows(tap_data)

            print(f"Data and settings saved to {filename}")

        #Call the save_to_csv function to save the collected data
        save_to_csv(tap_filename, spon_tap_data)

        # Display the "Thank you" message until space
        end.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])   # key stroke ends it all

        print("Hooray another data set")

        # Close the window and end the experiment
        
"""
synchronization continuation tapping task under construction
"""

def run_sync_tap():
    if settings['run_type_sync_tap'] in ['exp', 'training']:
        #Instructions sync tap message
        instr_sync_tap = visual.TextStim(win, text= "Tap on the MIDI pad with the beat of the track after the count in.\n\n" \
                                   "Press space to start" 
                                    , pos=(0, 0))
        
        # Create a "Thank you" message end  
        end = visual.TextStim(win, text="Thank you for participating!\n\n" \
                                   "Press space to end" 
                                   , pos=(0, 0))
        
        #make fixation cross                          
        fixation = visual.ShapeStim(win,
                                vertices=((0, -0.15), (0, 0.15), (0, 0),
                                        (-0.1, 0), (0.1, 0)),
                                lineWidth=13,
                                closeShape=False,
                                lineColor='white')
        # Create a "Thank you" message
        welcome = visual.TextStim(win, text="Thank you for participating!\n\n" \
                                   "Press space to continue" 
                                   , pos=(0, 0))
        
        #draw instructions depending what has been chosen
        welcome.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])
        
        sync_tap_data = []

        try:
            midi_input = mido.open_input('Arturia BeatStep')
            print("Using Arturia BeatStep MIDI input.")
        except IOError:
        # If 'Arturia BeatStep' is not available, try to open 'APC Key 25'
            try:
                midi_input = mido.open_input('APC Key 25')
                print("Using APC Key 25 MIDI input.")
            except IOError:
            # If both devices are unavailable, handle the error or set a default input
                print("No suitable MIDI input found. Handle the error or set a default input.")


        #change cwd to the stimuli map otherwise it cannot trigger the files from the map
        os.chdir(stimuli_path_sync_tap)

        #Read audio file names/tap along stimuli from the CSV file
        audio_files = []
        if settings['run_type_sync_tap'] == 'exp':
            audio_files_df = pd.read_csv('stim_list_tap.csv', sep=';')
            audio_files = audio_files_df['sync_stim_name'].tolist()
        else:
            audio_files_df = pd.read_csv('stim_list_tap_train.csv', sep=';')
            audio_files = audio_files_df['sync_stim_name'].tolist()


        #Shuffle the audio files for random order of stimuli presentation
        random.shuffle(audio_files)

        # Create a list to preload audio files
        preloaded_audio = []
        audio_file_names = []

        # Preload all audio files as objects and their names and get full duration
        #create empty variable to fill
        total_duration_sync_audio = 0

        for audio_file in audio_files:
            preloaded_audio.append(sound.Sound(audio_file)) #store sound object
            audio_file_names.append(audio_file)  # Store the file name
            audio = sound.Sound(audio_file) #get the full duration of all audio files
            total_duration_sync_audio += audio.getDuration()

        # Add sync_break_duration seconds between each audio file
        total_duration_sync_audio += (len(audio_files) - 1) * settings['sync_break_duration'] #fill the empty variable

        #Function to trigger an audio file for sync trial
        def trigger_audio(audio):
            # Play the audio file
            audio.play()
            print(f"Playing audio file: {audio}")
            core.wait(audio.getDuration())
            audio.stop()

            #Set the flag to signal the audio playback thread to stop
            #global audio_thread_running
            #audio_thread_running = False

        #Create a thread to play audiofor sync trial
        def audio_thread(audio_file, audio_onset_time):
            global audio_close_time #make it global so the tap thread can access it
            audio_duration = audio_file.getDuration()
            audio_close_time = audio_onset_time + audio_duration
            trigger_audio(audio_file)


            #while time.time() < audio_close_time:
            #    pass #keep this active until fully played the file

            #global tap_thread_running
            #tap_thread_running = False
            #print("audio/tap thread completed")

        # Create a queue for communication between threads midi and midi calcultations
        tap_queue = queue.Queue()

        #Create a thread for tap event recording
        def tap_sync_thread():
            global start_tap_time
            start_tap_time = time.time()
            while tap_thread_running:
                for msg in midi_input.iter_pending():
                    if msg.type == 'note_on':
                        #time stamp of when the tap happend it freaks out here cannot process it fast enough if there al calculations here
                        tap_time = time.time() #+ start_tap_time #processing slow bs going on here because runs perfect wathever you want here when not in a function..
                        tap_velocity = msg.velocity
                        
                        # Create a dictionary to store tap data
                        sync_tap_entry = {
                            'tap_timing(s)': tap_time, 
                            'tap_velocity(s)': tap_velocity,
                            'audio_file': audio_file_name,
                            'audio_onset_timing(s)': audio_onset_time,
                            'audio_close_timing(s)': audio_close_time,
                            'task': 'sync_tap'
                        }
                        
                        # Add settings data to the single tap entry
                        sync_tap_entry.update(settings)
                        
                        # Append the tap entry to the list of full tap data
                        #sync_tap_data.append(sync_tap_entry)

                        # Put the tap entry in the queue
                        tap_queue.put(sync_tap_entry)

        
        # Function to modify 'tap_timing(s)' values in existing entries
        def modify_tap_timings():
            while tap_thread_running:
                try:
                    # Get a tap entry from the queue
                    sync_tap_entry = tap_queue.get(timeout=1)  # Adjust the timeout as needed

                    # Modify 'tap_timing(s)' value by subtracting start_tap_time
                    sync_tap_entry['tap_timing(s)'] -= start_tap_time

                    # Append the modified tap entry to the list of full tap data
                    sync_tap_data.append(sync_tap_entry)
                except queue.Empty:
                    pass  # Continue the loop if the queue is empty


        #draw instructions depending what has been chosen
        instr_sync_tap.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])     #list restricts options for key presses, waiting for space

        ###start of the trial###
        #clock for the sync trial
        start_sync_time = time.time()

        #clock main
        while time.time() - start_sync_time < total_duration_sync_audio:
            
        #Check if there are more audio files to process it goes through the whole list
            if preloaded_audio:
                fixation.draw()
                win.flip()
                # Trigger audio file and record onset time
                audio_file = preloaded_audio.pop(0)  # Take the first audio file in the list and erase it from the list
                audio_file_name = audio_file_names.pop(0) #we need the name as well
                audio_onset_time = time.time() - start_sync_time  # Calculate onset time once for the trial

                #Start audio playback thread
                audio_playback_thread = threading.Thread(target=audio_thread, args=(audio_file, audio_onset_time))
                audio_playback_thread.start()

                #Reset the flag to ensure tap thread runs
                tap_thread_running = True

                #Start tap event recording thread, also start the thread that does the calculations
                tap_recording_thread = threading.Thread(target=tap_sync_thread)
                modify_thread = threading.Thread(target=modify_tap_timings)
                tap_recording_thread.start()
                modify_thread.start()
                
                #Wait for audio playback thread to complete
                audio_playback_thread.join()

                # Stop tap recording thread after audio playback completes
                tap_thread_running = False
                tap_recording_thread.join()

            #a break before the next audio file
            time.sleep(settings['sync_break_duration'])

        #change working directory back to the path of the python file to save correctly
        os.chdir(my_path)

        #i made this for individual task maybe not nice but just to be sure data from seperate tasks is handled seperatly
        def append_to_csv_sync(filename, tap_data):
            if not tap_data:
                print("No data to append.")
                return
            if not filename.endswith(".csv"):
                filename += ".csv" #if the filename doesnt have the extension .csv add it
            with open(filename, 'a', newline='') as csvfile: #a means append
                csvwriter = csv.DictWriter(csvfile,  fieldnames=tap_data[0].keys())

                # If the file is empty, write the headers
                if csvfile.tell() == 0:
                    csvwriter.writeheader()

                # Write tap data without writing headers again
                csvwriter.writerows(tap_data)

        # Call the append_to_csv function to append the collected data to the existing CSV file

        append_to_csv_sync(tap_filename, sync_tap_data)

        print(f"Data appended to {tap_filename}")

        #Close the MIDI input when the experiment is done
        midi_input.close()

        # Display the "Thank you" message until space
        end.draw()

        #close thread!!!
        tap_thread_running = False
        tap_recording_thread.join()
        modify_thread.join()
        
        win.flip()
        event.waitKeys(keyList = [keyNext])   # key stroke ends it all

        print("Hooray another data set")

"""
duration discrimination task under construction
"""

def run_dur_est():
    if settings['run_type_dur_est'] in ['training' or 'exp']:    
        #make fixation cross                          
        fixation = visual.ShapeStim(win,
                                vertices=((0, -0.15), (0, 0.15), (0, 0),
                                        (-0.1, 0), (0.1, 0)),
                                lineWidth=13,
                                closeShape=False,
                                lineColor='white')
        # Create a "Thank you" message
        welcome = visual.TextStim(win, text="Thank you for participating!\n\n" \
                                   "Press space to continue" 
                                   , pos=(0, 0))
        
        # Display instructions
        instructions = visual.TextStim(win, text='Tap the space bar once when you think a minute has elapsed.\nPress spacebar to start.',
                                   color='white')
        
        thank_you_message = visual.TextStim(win, text='Thank you for participating!', color='white')
        
        dur_est_data = []

        #draw instructions depending what has been chosen
        welcome.draw()
        win.flip()
        event.waitKeys(keyList = [keyNext])

        instructions.draw()
        win.flip()
        event.waitKeys(keyList=[keyNext])

        # Start recording response time
        start_time = time.time()

        # Display fixation cross until the subject taps the MIDI pad
        fixation.draw()
        win.flip()
        event.waitKeys(keyList=[keyNext])

        # Record response time when the subject taps the MIDI pad
        response_time = time.time() - start_time

        # Create a dictionary to store tap data
        dur_est_entry = {
                            'tap_timing(s)': response_time, 
                            'tap_velocity(s)': "",
                            'audio_file': "",
                            'audio_onset_timing(s)': "",
                            'audio_close_timing(s)': "",
                            'task': 'dur_disc'
                        }
                        
        # Add settings data to the single tap entry
        dur_est_entry.update(settings)

        # Append the tap entry to the list of tap data, looopy
        dur_est_data.append(dur_est_entry)

        # Display thank you message
        thank_you_message.draw()
        win.flip()
        event.waitKeys(keyList=[keyNext])
        
        #i made this for individual task maybe not nice but just to be sure data from seperate tasks is handled seperatly
        def append_to_csv_sync(filename, tap_data):
            if not tap_data:
                print("No data to append.")
                return
            if not filename.endswith(".csv"):
                filename += ".csv" #if the filename doesnt have the extension .csv add it
            with open(filename, 'a', newline='') as csvfile: #a means append
                csvwriter = csv.DictWriter(csvfile,  fieldnames=tap_data[0].keys())

                # If the file is empty, write the headers
                if csvfile.tell() == 0:
                    csvwriter.writeheader()

                # Write tap data without writing headers again
                csvwriter.writerows(tap_data)

        # Call the append_to_csv function to append the collected data to the existing CSV file

        append_to_csv_sync(tap_filename, dur_est_data)

        print(f"Data appended to {tap_filename}")
        





