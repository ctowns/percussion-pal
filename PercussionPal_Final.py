import tkinter as tk
from tkinter import *
from tkinter import font as tkFont
import RPi.GPIO as GPIO
#from PIL import ImageTk, Image
import time
import queue
import threading
import pygame
import copy
from PercussionPalPatterns import *
from random import *

pygame.mixer.init(frequency=44100, channels = 1, size = -8, buffer = 256)
#pygame.mixer.music.load("Metronome_Click.wav")
g_Metronome = pygame.mixer.Sound("Metronome_Click.wav")

#TODO: Create 'beatmaps' arrays of the patterns to be used for detecting hits

g_Pattern = 'B1'
g_Repeats = 1
g_Tempo = 100
g_Beat = 'Get ready!'
g_LastTime = 0.0

g_LastNote = ['']
g_NextNote = ['']
g_TotalNotes = 0
g_CorrectNotes = 0
g_TimeThreshold = 1 / (g_Tempo / 60) / 4  #TODO: this needs to be calibrated
g_Accuracy = 0.0
g_Streak = 1
g_CurrentStreak = 1
g_Playback = False
g_Training = False
g_Intensity = 'medium'

g_CurrentHits=['']

in_pins = [5, 6, 13, 19, 26, 16, 20, 21]
#output pins
#4 - kick
#17 - snare
#18 - hi-hat
#27 - crash
#22 - ride
#23 - floor tom
#24 - left tom
#25 - right tom                                                                                                                                                                                                                                     tom
out_pins = [4, 17, 18, 27, 22, 23, 24, 25]

pattern1Notes = [['kick', 'hi-hat'], ['hi-hat'], ['snare', 'hi-hat'], ['hi-hat']]
pattern1Lengths = ['eigth',         'eigth',    'eigth',                'eigth']

pattern2Notes = [['kick', 'hi-hat'], ['hi-hat'], ['snare', 'hi-hat'], ['hi-hat'], ['hi-hat'], ['kick', 'hi-hat'], ['snare', 'hi-hat'], ['hi-hat']]
pattern2Lengths = ['eigth',         'eigth',    'eigth',                'eigth',    'eight',    'eight',            'eigth',            'eigth']

            #1                                                      #2                                                   
pattern2 = [(['kick', 'hi-hat'], 'eigth'), (['hi-hat'], 'eigth'), (['snare', 'hi-hat'], 'eigth'), (['hi-hat'], 'eigth'), 
            (['hi-hat'], 'eigth'), (['kick', 'hi-hat'], 'eigth'), (['snare', 'hi-hat'], 'eigth'), (['hi-hat'], 'eigth')]

            #1                                                      #2
#pattern3 = [(['kick', 'crash'], 'eigth'), (['hi-hat'], 'eigth'), (['snare', 'hi-hat'], 'eigth'), (['hi-hat'], 'eigth'), 
#            (['hi-hat'], 'eigth'), (['kick', 'hi-hat'], 'eigth'), (['snare', 'hi-hat'], 'eigth'), (['hi-hat'], 'eigth')]
#            

def flash(note_type, drum_pieces):
    global g_TotalNotes, g_LastTime, g_LastNote, g_Tempo, g_Playback
    if(g_Playback==True):
        print(drum_pieces)
        note_len = get_note_length(note_type, g_Tempo)
        default_flash_len = 60 / g_Tempo / 3;
        #turn on all relevent drum pieces
        for drum_piece in drum_pieces:
            out_pin = get_pin(drum_piece);
            GPIO.output(out_pin, GPIO.HIGH)
        #sleep for flash length
        g_LastTime = time.time()
        g_LastNote = drum_pieces
        #g_TotalNotes += len(drum_pieces) #TODO:Fix this for countoff
        time.sleep(default_flash_len);
        #turn off all pieces
        for drum_piece in drum_pieces:
            out_pin = get_pin(drum_piece);
            GPIO.output(out_pin, GPIO.LOW)
        #sleep for note length
        time.sleep(note_len - default_flash_len)



##############################GPIO###########################
def flash_ex(note_type, drum_pieces):
    global g_TotalNotes, g_LastTime, g_Streak, g_CurrentStreak, g_LastNote, g_Tempo, g_Playback, g_CorrectNotes, g_CurrentHits
    if(g_Playback==True):
        print(drum_pieces)
        note_len = get_note_length(note_type, g_Tempo)
        if(note_type == 'sixteenth'):
            default_flash_len = 60 / g_Tempo / 5
        else: #longer than a sixteenth note
            default_flash_len = 60 / g_Tempo / 3
        #turn on all relevent drum pieces
        for drum_piece in drum_pieces:
            out_pin = get_pin(drum_piece)
            GPIO.output(out_pin, GPIO.HIGH)
        g_LastTime = time.time()
        g_LastNote = copy.deepcopy(drum_pieces)
        g_TotalNotes += len(drum_pieces)
        #sleep for flash length
        time.sleep(default_flash_len)
        #turn off all pieces
        for drum_piece in drum_pieces:
            out_pin = get_pin(drum_piece)
            GPIO.output(out_pin, GPIO.LOW)

        #check for correct hits
        print(g_CurrentHits)
        for x in g_CurrentHits:
            if(x in g_LastNote):
                g_LastNote.remove(x)
                g_CorrectNotes += 1


        print('missed ' + str(g_LastNote))
        if(g_LastNote == []):
            g_CurrentStreak += 1
        else:
            if(g_CurrentStreak > g_Streak):
                g_Streak = g_CurrentStreak
            g_CurrentStreak = 0
        #clear correct notes now, that way the early hits for the next note are
        #recorded and can be cheked in the next loop
        #g_CurrentHits = []
        #sleep for note length
        time.sleep(note_len - default_flash_len)
        g_CurrentHits = []

        #to adjust this sleep to account for a threshold:
#        if(note_len - default_flash_len * 2 > 0):
#            time.sleep(note_len - (default_flash_len * 2))
#            g_CurrentHits = []
#            time.sleep(default_flash_len)
#        else:
#            g_CurrentHits = []
#            time.sleep(note_len - default_flash_len)


       #  #check for early notes
       # for x in g_CurrentHits:
       #     if(x in g_NextNote):
       #         g_NextNote.remove(x)
       #         g_CorrectNotes += 1
#    else:
#        g_TotalNotes += len(drum_pieces)



def get_pin(drum_piece):
    if drum_piece == 'kick':
        return 4
    elif drum_piece == 'snare':
        return 17
    elif drum_piece == 'hi-hat':
        return 18
    elif drum_piece == 'crash':
        return 27
    elif drum_piece == 'ride':
        return 22
    elif drum_piece == 'floor tom':
        return 23
    elif drum_piece == 'left tom':
        return 24
    elif drum_piece == 'right tom':
        return 25


def get_piece(in_pin):
    if in_pin == 5:
        return 'hi-hat' #falling edge triggered
    elif in_pin == 6:
        return 'ride'
    elif in_pin == 13:
        return 'kick' #falling edge triggered
    elif in_pin == 19:
        return 'left tom'
    elif in_pin == 26:
        return 'floor tom'
    elif in_pin == 16:
        return 'right tom'
    elif in_pin == 20:
        return 'crash'
    elif in_pin == 21:
        return 'snare'


def get_note_length(note, tempo):
    sec_per_beat = 60 / tempo
    if (note == 'whole'):
        return sec_per_beat * 4
    if(note == 'half'):
        return sec_per_beat * 2
    if(note == 'quarter'):
        return sec_per_beat
    if(note == 'eigth'):
        return sec_per_beat / 2
    if(note == 'sixteenth'):
        return sec_per_beat / 4


def configure_pins():
    global g_Tempo, out_pins, in_pins
    GPIO.setmode(GPIO.BCM)
    default_flash_len = 60.0 / g_Tempo / 4
    print('default flash: ' + str(int(default_flash_len * 1000)))
    for x in out_pins:
        GPIO.setup(x, GPIO.OUT)
        GPIO.output(x, GPIO.LOW)
    for x in in_pins:
        if(x == 6 or x == 13 or x ==5): #falling edge triggered
            GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(x, GPIO.FALLING, bouncetime= 200)#int(default_flash_len * 1000))
            GPIO.add_event_callback(x, detect_hit)
        else: #rising edge triggered
            GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(x, GPIO.RISING, bouncetime= 200)#int(default_flash_len * 1000))
            GPIO.add_event_callback(x, detect_hit)


def detect_hit(in_pin):
    global g_TotalNotes, g_CorrectNotes, g_CurrentHits
    currentTime = time.time()
    currentPiece = get_piece(in_pin)
    g_CurrentHits.append(currentPiece)
    # print('test' + str(currentPiece))
    # timeDifference = currentTime - g_LastTime
    # print ('Hit detected! ' + str(currentPiece) + ', time difference: ' + str(timeDifference))
    # if(currentPiece in g_LastNote):
    #     if (timeDifference < g_TimeThreshold):
    #         g_LastNote.remove(currentPiece) #remove the piece so it is not counted again
    #         g_CorrectNotes += 1;
    # elif(currentPiece in g_NextNote):
    #     if(timeDifference > g_TimeThreshold): #TODO: do some more math on this
    #         g_NextNote.remove(currentPiece) #remove the piece so it is not counted again
    #         g_CorrectNotes += 1






###################################################################
###########################GUI METHODS############################
##################################################################




#############################################################################
#################################GUI setup###################################
#############################################################################

###consult this: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

######################GUI funtions########################
def exitProgram():
    print("Exit button pressed")
    #GPIO.cleanup()
    if(hasattr(app, 'thread')):
        if(app.thread.is_alive()):
            global g_Playback
            g_Playback = False
            time.sleep(1)
    app.destroy()

def increaseTempo(tempo_label):
    global g_Tempo
    g_Tempo = g_Tempo + 5
    if g_Tempo > 180:
        g_Tempo = 180
    #tempo_string.set(str(tempo_int) + ' bpm')
    tempo_label['text']=str(g_Tempo)

def decreaseTempo(tempo_label):
    global g_Tempo
    g_Tempo = g_Tempo - 5
    if g_Tempo < 40:
        g_Tempo = 40
    #tempo_string.set(str(g_Tempo) + ' bpm')
    tempo_label['text'] =  str(g_Tempo)

def increaseRepeats(repeat_label):
    global g_Repeats
    g_Repeats = g_Repeats + 1
    if g_Repeats > 20:
        g_Repeats = 20
    #repeat_string.set(str(g_Repeats) + ' bpm')
    repeat_label['text']=str(g_Repeats)

def decreaseRepeats(repeat_label):
    global g_Repeats
    g_Repeats = g_Repeats - 1
    if g_Repeats < 1:
        g_Repeats = 1
    #repeat_string.set(str(repeat_int) + ' bpm')
    repeat_label['text']=str(g_Repeats)

def countOff(thread):
    global g_Beat, g_Tempo, g_Metronome
    tempo = g_Tempo
    print('Counting Off')

    g_Beat = 1
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('half', ['kick'])

    g_Beat = 2
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('half', ['kick'])

    g_Beat = 1
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('quarter', ['kick'])

    g_Beat = 2
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('quarter', ['kick'])

    g_Beat = 3
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('quarter', ['kick'])

    g_Beat = 4
    print(g_Beat)
    thread.queue.put(g_Beat)
    #pygame.mixer.music.play()
    g_Metronome.play()
    flash('quarter', ['kick'])


def setPattern(patternLabel, pattern):
    global g_Pattern
    patternLabel['text'] = pattern
    g_Pattern = pattern

#    #play sample of pattern
#    if pattern == 'B1':
#        pygame.mixer.music.load('Pattern_1.wav')


def initializeGlobals():
    global g_Pattern, g_Repeats, g_Tempo, g_Beat, g_LastTime, g_LastNote, g_TotalNotes, g_CorrectNotes, g_TimeThreshold, g_Accuracy, g_Streak
    g_Pattern = 'B1'
    g_Repeats = 1
    g_Tempo = 100
    g_Beat = 'Get ready!'
    g_LastTime = 0.0
    g_LastNote = ['']
    g_TotalNotes = 0
    g_CorrectNotes = 0
    g_TimeThreshold = 1 / (g_Tempo / 60) / 4  #TODO: this needs to be calibrated
    g_Accuracy = 0.0
    g_Streak = 1

def initializeFeedbackGlobals():
    global g_Beat, g_LastTime, g_LastNote, g_TotalNotes, g_CorrectNotes, g_TimeThreshold, g_Accuracy, g_Streak, g_CurrentStreak
    g_Beat = 'Get ready!'
    g_LastTime = 0.0
    g_LastNote = ['']
    g_TotalNotes = 0
    g_CorrectNotes = 0
    g_Accuracy = 0.0
    g_Streak = 1
    g_CurrentStreak = 0



def beginPlayback(thread):
    global g_Playback, g_Training
    print('Begin Playback')
    initializeFeedbackGlobals()
    configure_pins()
    if(g_Training == False):
        countOff(thread)
        startPattern(thread)
        g_Playback = False
        calculateFeedback()
        GPIO.cleanup()
    else: #training mode
        thread.queue.put('Watch first!')
        countOff(thread)
        startPattern(thread)
        thread.queue.put('Now you try!')
        initializeFeedbackGlobals()
        countOff(thread)
        startPattern(thread)
        g_Playback = False
        g_Training = False
        calculateFeedback()
        GPIO.cleanup()



def startPattern(thread):
    global g_Tempo, g_Repeats, g_Pattern, g_NextNote, g_Streak, g_Metronome, g_Intensity
    g_Streak = 0   
    g_Intensity = 'medium'
    print(g_Pattern)
    if g_Pattern == 'B1':
        print('Basic Pattern #1 - Repeats ' + str(g_Repeats))
        for repeat in range(0, g_Repeats * 2):
            print('###############Repeat: ' + str(repeat + 1))
            for x in range(0, len(pattern1Notes)):
                print('Beat: ' + str(x))
                if( x % 2 == 0):
                    #pygame.mixer.music.play()
                    g_Metronome.play()
                    g_Intensity = 'hard'
                else:
                    g_Intensity = 'medium'
                thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
                flash_ex(pattern1Lengths[x], pattern1Notes[x])

    elif g_Pattern == 'B2':
        print ('Basic Pattern #2')
        for repeat in range (0, g_Repeats):
            print('###############Repeat: ' + str(repeat + 1))
            for x in range(0, len(pattern2)):
                print('Beat: ' + str(x))
                if( x % 2 == 0):
                    #pygame.mixer.music.play()
                    g_Metronome.play()
                thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
                flash_ex(pattern2[x][1], pattern2[x][0])



            # print('Measure 1 - Repeat ' + str(x))
            # #1
            # pygame.mixer.music.play()
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['kick'])
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat'])
            # #2
            # pygame.mixer.music.play()
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat', 'snare'])
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat'])
            # #3
            # pygame.mixer.music.play()
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat'])
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat', 'kick'])
            # #4
            # pygame.mixer.music.play()
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat', 'snare'])
            # thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
            # flash_ex('eigth', ['hi-hat'])

    elif g_Pattern == 'I1':
        print ('Intermediate Pattern #1')
        for repeat in range (0, g_Repeats):
            print('###############Repeat: ' + str(repeat + 1))
            for x in range(0, len(pattern3)):
                print('Beat: ' + str(x))
                if( x % 2 == 0):
                    #pygame.mixer.music.play()
                    g_Metronome.play()
                thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
                flash_ex(pattern3[x][1], pattern3[x][0])

    elif g_Pattern == 'I2':
        print ('Intermediate Pattern #2')
        for repeat in range (0, g_Repeats):
            print('###############Repeat: ' + str(repeat + 1))
            for x in range(0, len(pattern4)):
                print('Beat: ' + str(x))
                if( x % 2 == 0):
                    #pygame.mixer.music.play()
                    g_Metronome.play()
                thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
                flash_ex(pattern4[x][1], pattern4[x][0])

    elif g_Pattern == 'Starlight':
        print ('Starlight')
        for repeat in range (0, g_Repeats):
            print('###############Repeat: ' + str(repeat + 1))
            for x in range(0, len(patternStarlight)):
                print('Beat: ' + str(x))
                if( x % 2 == 0):
                    #pygame.mixer.music.play()
                    g_Metronome.play()
                thread.queue.put('%s/%s' % (g_CorrectNotes, g_TotalNotes))
                flash_ex(patternStarlight[x][0], patternStarlight[x][1])

    elif g_Pattern == 'Whack':
        print ('Whack-A-Mole!')
        WhackAMole(thread.queue)

def WhackAMole(queue):
    global g_CurrentHits, g_CorrectNotes, g_TotalNotes, g_Streak, g_Repeats
    pieces = ['kick', 'snare', 'hi-hat', 'ride', 'crash', 'left tom', 'right tom', 'floor tom']
    totalTime = 0
    g_CurrentHits = []
    while(totalTime < 10 * g_Repeats): #20 seconds
        #get a random drum piece
        drum_piece = pieces[randint(0, 7)]

        #turn it on
        out_pin = get_pin(drum_piece)
        GPIO.output(out_pin, GPIO.HIGH)

        timeBefore = time.time()
        time.sleep(0.05)
        #wait for the piece to be hit
        while(not (drum_piece in g_CurrentHits) and (time.time() - timeBefore) < 10 ):
            print(g_CurrentHits)
            print(totalTime)

        # piece has been hit, turn the piece off
        GPIO.output(out_pin, GPIO.LOW)
        
        g_CurrentHits = []

        #count the hit
        g_CorrectNotes += 1
        g_TotalNotes += 1
        g_Streak += 1
        queue.put('%s', g_Streak)
        timeAfter = time.time()
        totalTime += (timeAfter - timeBefore)
    


def calculateFeedback():
    global g_Accuracy, g_Streak, g_Score, g_CurrentStreak
    if(g_CurrentStreak > g_Streak):
        g_Streak = g_CurrentStreak
    g_Accuracy = g_CorrectNotes / g_TotalNotes
    print('Correct notes, total notes, accuracy')
    print(g_CorrectNotes, g_TotalNotes, g_Accuracy)



class MainApp(tk.Tk):

    def spawnthread(self):
        self.thread = ThreadedClient(self.queue)
        self.thread.start()
        self.periodiccall()

    def periodiccall(self):
        self.checkqueue()
        if self.thread.is_alive():
            self.after(50, self.periodiccall)

    def checkqueue(self):
        global g_Beat
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                g_Beat = msg
                self.frames["PlaybackPage"].updateParams() #inefficient, just change gBeat
            except Queue.Empty:
                pass

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkFont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        patternVar = StringVar()
        patternVar.set("test")

        self.queue = queue.Queue()
        self.frames = {}
        for F in (StartPage, MainMenuPage, TempoPage, ReadyPage, PlaybackPage, FeedbackPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "MainMenuPage" or page_name == "TempoPage" or page_name == "ReadyPage" or page_name == "PlaybackPage" or page_name == "FeedbackPage":
            frame.updateParams()
        if page_name == "PlaybackPage":
            global g_Playback
            g_Playback = True
            self.spawnthread()
        if page_name == "TempoPage":
            pygame.mixer.music.stop()

    def playback_pressed(self):
        global g_Playback
        if(g_Playback == True):
            g_Playback = False
        else:
            g_Playback = True
            self.spawnthread()




class ThreadedClient(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self._stop_event = threading.Event()

    def run(self):
        self.queue.put('Get ready!')
        time.sleep(1)
        beginPlayback(self)
        msg = 'Done!'
        self.queue.put(msg)


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            # image = Image.open("C:\\Users\\ctown\\Downloads")
            # background_image = ImageTk.PhotoImage(image)
            # background_label = tk.Label(win, image=background_image)
            # background_label.image=background_image;

            myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

            background_label = tk.Label(self, background='light blue')
            background_label.pack(fill="both", expand="no")
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            #create title
            #Replace this with a logo
            title=tk.Label(self, text='The Percussion Pal! [insert image]', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'black', fg='green')
            title.grid(row=1, column=3, columnspan='4', sticky = 'nsew')
            exitButton = tk.Button(self, text='Exit', font=myFont, command=exitProgram)
            exitButton.grid(row=0, column=9, sticky = 'nsew')

            startButton=tk.Button(self, text='Let\'s Rock!', font=myFont, command=lambda: controller.show_frame("MainMenuPage"), bg = 'Green', fg='black')
            startButton.grid(row=3, column=4, columnspan=2, sticky = 'nsew')


            #Make each row/column fill the space evenly
            for x in range(10):
                tk.Grid.columnconfigure(self, x, weight=1)
            for y in range(6):
                tk.Grid.rowconfigure(self, y, weight=1)

class MainMenuPage(tk.Frame):
    def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            #image = Image.open("/home/pi/Desktop/drum_background.png")
            #image = Image.open("/home/pi/Desktop/drum_background.png")
            #background_image = ImageTk.PhotoImage(image)
            #background_label = tk.Label(win, image=background_image)
            #background_label.image=background_image;

            myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

            background_label = tk.Label(self, background='white')
            background_label.pack(fill="both", expand="no")
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            #create title
            #Replace this with a logo
            title=tk.Label(self, text='The Percussion Pal!', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='green')
            title.grid(row=1, column=3, columnspan='4', sticky = 'nsew')
            restartButton = tk.Button(self, text='Restart', font=myFont, command= lambda: controller.show_frame("StartPage"), fg='white', bg='orange')
            restartButton.grid(row=0, column=0, sticky = 'nsew')

            #create all pattern labels and buttons
            beginnerLabel=tk.Label(self, text='Beginner:', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='green')
            beginnerLabel.grid(row=2, column=1, sticky = 'nsew')
            b_pattern1Button = tk.Button(self, text='Pattern #B1', font=myFont, command =lambda: setPattern(self.currentPatternLabel, 'B1'), fg='black', bg='light gray')
            b_pattern1Button.grid(row=2, column=3, sticky = 'nsew')
            b_pattern2Button = tk.Button(self, text='Pattern #B2', font=myFont, command =lambda: setPattern(self.currentPatternLabel, 'B2'), fg='black', bg='light gray')
            b_pattern2Button.grid(row=2, column=4, sticky = 'nsew')
            intermediateLabel=tk.Label(self, text='Intermediate:', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='yellow')
            intermediateLabel.grid(row=3, column=1, sticky = 'nsew')
            i_pattern1Button = tk.Button(self, text='Pattern #I1', font=myFont, command =lambda: setPattern(self.currentPatternLabel, 'I1'), fg='black', bg='light gray')
            i_pattern1Button.grid(row=3, column=3, sticky = 'nsew')
            i_pattern2Button = tk.Button(self, text='Pattern #I2', font=myFont, command =lambda: setPattern(self.currentPatternLabel, 'I2'), fg='black', bg='light gray')
            i_pattern2Button.grid(row=3, column=4, sticky = 'nsew')
            advancedLabel=tk.Label(self, text='ADVANCED:', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='red')
            advancedLabel.grid(row=4, column=1, sticky = 'nsew')
            a_pattern1Button = tk.Button(self, text='Starlight', font=myFont, command =lambda: setPattern(self.currentPatternLabel, 'Starlight'), fg='black', bg='light gray')
            a_pattern1Button.grid(row=4, column=3, sticky = 'nsew')
            a_pattern2Button = tk.Button(self, text='Whack-A-Mole!', font=tkFont.Font(family = 'Helvetica', size = 12, weight = 'bold'), command =lambda: setPattern(self.currentPatternLabel, 'Whack'), fg='black', bg='light gray')
            a_pattern2Button.grid(row=4, column=4, sticky = 'nsew')


            confirmButton=tk.Button(self, text='Confirm', font=myFont, command=lambda: controller.show_frame("TempoPage"), bg = 'Green', fg='white')
            confirmButton.grid(row=3, column=8, columnspan='2', sticky = 'nsew')
            patternTextLabel =tk.Label(self, text='Current Pattern:', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='Black')
            patternTextLabel.grid(row=1, column=8, sticky = 'nsew')
            self.currentPatternLabel =tk.Label(self, text='B1', font=tkFont.Font(family = 'Times New Roman',
                size = 15, weight = 'bold'), bg = 'white', fg='Black')
            self.currentPatternLabel.grid(row=2, column=8, sticky = 'nsew')


            #Make each row/column fill the space evenly
            for x in range(10):
                tk.Grid.columnconfigure(self, x, weight=1)
            for y in range(6):
                tk.Grid.rowconfigure(self, y, weight=1)

    def updateParams(self):
        #https://stackoverflow.com/questions/33646605/how-to-access-variables-from-different-classes-in-tkinter
        #see above link for better way to share data, avoiding globals
        global g_Pattern
        self.currentPatternLabel['text']=str(g_Pattern)


class TempoPage(tk.Frame):
    def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            #image = Image.open("/home/pi/Desktop/drum_background.png")
            #image = Image.open("/home/pi/Desktop/drum_background.png")
            #background_image = ImageTk.PhotoImage(image)
            #background_label = tk.Label(win, image=background_image)
            #background_label.image=background_image;

            myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

            background_label = tk.Label(self, background='white')
            background_label.pack(fill="both", expand="no")
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            #create title
            #Replace this with a logo
            title=tk.Label(self, text='The Percussion Pal!', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='green')
            title.grid(row=1, column=3, columnspan='4', sticky = 'nsew')
            instructionLabel = tk.Label(self, text='Please select a tempo:', font=tkFont.Font(family = 'Times New Roman',
                size = 12, weight = 'bold'), bg = 'white', fg='green')
            instructionLabel.grid(row=2, column=4, columnspan='2', sticky = 'nsew')
            restartButton = tk.Button(self, text='Back', font=myFont, command= lambda: controller.show_frame("MainMenuPage"), fg='white', bg='orange')
            restartButton.grid(row=0, column=0, sticky = 'nsew')
            exitButton = tk.Button(self, text='Exit', font=myFont, command= lambda: controller.show_frame("StartPage"), fg='white', bg='light gray')
            exitButton.grid(row=5, column=0, sticky = 'nsew')

            #create tempo and repeat labels and buttons
            tempoIncreaseButton=tk.Button(self, text='Tempo +', font=myFont, command=lambda: increaseTempo(self.tempoLabel), height=1,width=8, bg="green")
            tempoIncreaseButton.grid(row=3, column=6, sticky='nsew')
            tempoDecreaseButton=tk.Button(self, text='Tempo -', font=myFont, command=lambda: decreaseTempo(self.tempoLabel), height=1,width=8, bg="red")
            tempoDecreaseButton.grid(row=3, column=3, sticky='nsew')
            tempoTextLabel=tk.Label(self, text='Tempo:', font=tkFont.Font(family = '',
                size = 18, weight = 'bold'), bg = 'white', fg='black')
            tempoTextLabel.grid(row=3, column=4, sticky = 'nsew')
            self.tempoLabel=tk.Label(self, text='100', font=myFont, bg = 'white', fg='black', width = 3)
            self.tempoLabel.grid(row=3, column=5, sticky='ew')

            repeatIncreaseButton=tk.Button(self, text='Repeats +', font=myFont, command=lambda: increaseRepeats(self.repeatLabel), height=1,width=8, bg="green")
            repeatIncreaseButton.grid(row=4, column=6, sticky='nsew')
            repeatDecreaseButton=tk.Button(self, text='Repeats -', font=myFont, command=lambda: decreaseRepeats(self.repeatLabel), height=1,width=8, bg="red")
            repeatDecreaseButton.grid(row=4, column=3, sticky='nsew')
            repeatTextLabel=tk.Label(self, text='Repeats:', font=tkFont.Font(family = '',
                size = 18, weight = 'bold'), bg = 'white', fg='black')
            repeatTextLabel.grid(row=4, column=4, sticky = 'nsew')
            self.repeatLabel=tk.Label(self, text='1', font=myFont, bg = 'white', fg='black', width = 3)
            self.repeatLabel.grid(row=4, column=5, sticky='ew')


            confirmButton=tk.Button(self, text='Confirm', font=myFont, command=lambda: controller.show_frame("ReadyPage"), bg = 'Green', fg='white')
            confirmButton.grid(row=3, column=8, columnspan='2', sticky = 'nsew')
            patternTextLabel =tk.Label(self, text='Current Pattern:', font=tkFont.Font(family = 'Times New Roman',
                size = 18, weight = 'bold'), bg = 'white', fg='Black')
            patternTextLabel.grid(row=1, column=8, sticky = 'nsew')
            self.currentPatternLabel =tk.Label(self, text='B1', font=tkFont.Font(family = 'Times New Roman',
                size = 15, weight = 'bold'), bg = 'white', fg='Black')
            self.currentPatternLabel.grid(row=2, column=8, sticky = 'nsew')



            #Make each row/column fill the space evenly
            for x in range(10):
                tk.Grid.columnconfigure(self, x, weight=1)
            for y in range(6):
                tk.Grid.rowconfigure(self, y, weight=1)

    def updateParams(self):
        global g_Pattern, g_Tempo, g_Repeats
        self.currentPatternLabel['text']=str(g_Pattern)
        self.tempoLabel['text']=str(g_Tempo)
        self.repeatLabel['text']=str(g_Repeats)

class ReadyPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

        background_label = tk.Label(self, background='white')
        background_label.pack(fill="both", expand="no")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #create title
        title=tk.Label(self, text='Press start when you are ready to ROCK!!!', font=myFont, bg = 'black', fg='green')
        title.grid(row=2, column=4, columnspan=4, sticky = 'nsew')
        exitButton = tk.Button(self, text='Exit', font=myFont, command=exitProgram, height=2, width=6)
        exitButton.grid(row=0, column=9)


        patternTextLabel =tk.Label(self, text='Current Pattern:', font=myFont, bg = 'white', fg='Black')
        patternTextLabel.grid(row=3, column=4, sticky = 'nsew')
        self.currentPatternLabel =tk.Label(self, text='B1', font=tkFont.Font(family = 'Times New Roman',
            size = 15, weight = 'bold'), bg = 'white', fg='Black')
        self.currentPatternLabel.grid(row=3, column=5, sticky = 'nsew')

        tempoTextLabel=tk.Label(self, text='Tempo:', font=myFont, bg = 'white', fg='black')
        tempoTextLabel.grid(row=4, column=4, sticky = 'nsew')
        self.tempoLabel=tk.Label(self, text='100', font=myFont, bg = 'white', fg='black', width = 3)
        self.tempoLabel.grid(row=4, column=5, sticky='ew')

        repeatTextLabel=tk.Label(self, text='Repeats:', font=myFont, bg = 'white', fg='black')
        repeatTextLabel.grid(row=5, column=4, sticky = 'nsew')
        self.repeatLabel=tk.Label(self, text='1', font=myFont, bg = 'white', fg='black', width = 3)
        self.repeatLabel.grid(row=5, column=5, sticky='ew')

        restartButton = tk.Button(self, text='Restart', font=myFont, command= lambda: controller.show_frame("MainMenuPage"), fg='white', bg='orange')
        restartButton.grid(row=0, column=0, sticky = 'nsew')

        readyButton=tk.Button(self, text='Start!', font=myFont, command=lambda: controller.show_frame("PlaybackPage"), height=3,width=8, bg="green")
        readyButton.grid(row=6, column=4, columnspan=2, rowspan=2, stick='nsew')
        trainingButton=tk.Button(self, text='Training!', font=myFont, command=lambda: self.trainingPressed(), height=3,width=8, bg="green")
        trainingButton.grid(row=6, column=7, columnspan=2, rowspan=2, stick='nsew')


        #Make each row/column fill the space evenly
        #TODO: Fix this for all (swap 10 and 6, as below)
        for x in range(10):
            tk.Grid.columnconfigure(self, x, weight=1)
        for y in range(6):
            tk.Grid.rowconfigure(self, y, weight=1)

    def trainingPressed(self):
        global g_Training
        g_Training = True
        self.controller.show_frame("PlaybackPage")

    def updateParams(self):
        global g_Pattern, g_Tempo, g_Repeats
        self.currentPatternLabel['text']=str(g_Pattern)
        self.tempoLabel['text']=str(g_Tempo)
        self.repeatLabel['text']=str(g_Repeats)

class PlaybackPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

        background_label = tk.Label(self, background='white')
        background_label.pack(fill="both", expand="no")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #create title
        title=tk.Label(self, text='Keep on rocking! You\'re doing great!', font=myFont, bg = 'black', fg='green')
        title.grid(row=0, column=1, columnspan=7, sticky = 'nsew')
        exitButton = tk.Button(self, text='Exit', font=myFont, command=exitProgram, height=2, width=6)
        exitButton.grid(row=0, column=9, stick='nsew')


        patternTextLabel =tk.Label(self, text='Current Pattern:', font=myFont, bg = 'white', fg='Black')
        patternTextLabel.grid(row=1, column=2, sticky = 'nsew')
        self.currentPatternLabel =tk.Label(self, text='B1', font=tkFont.Font(family = 'Helvetica',
            size = 12, weight = 'bold'), bg = 'white', fg='Black')
        self.currentPatternLabel.grid(row=1, column=3, sticky = 'nsew')

        tempoTextLabel=tk.Label(self, text='Tempo:', font=myFont, bg = 'white', fg='black')
        tempoTextLabel.grid(row=1, column=4, sticky = 'nsew')
        self.tempoLabel=tk.Label(self, text='100', font=myFont, bg = 'white', fg='black', width = 3)
        self.tempoLabel.grid(row=1, column=5, sticky='ew')

        repeatTextLabel=tk.Label(self, text='Repeats:', font=myFont, bg = 'white', fg='black')
        repeatTextLabel.grid(row=1, column=6, sticky = 'nsew')
        self.repeatLabel=tk.Label(self, text='1', font=myFont, bg = 'white', fg='black', width = 3)
        self.repeatLabel.grid(row=1, column=7, sticky='ew')

        restartButton = tk.Button(self, text='Restart', font=myFont, command= lambda: self.restartPressed(), fg='white', bg='orange')
        restartButton.grid(row=0, column=0, sticky = 'nsew')

        playbackButton = tk.Button(self, text='Play/Pause', font=tkFont.Font(family = 'Helvetica',
            size = 12, weight = 'bold'), command= lambda: controller.playback_pressed(), fg='white', bg='Green')
        playbackButton.grid(row=4, column=9, sticky = 'nsew')

        feedbackButton = tk.Button(self, text='See Feedback', font=tkFont.Font(family = 'Helvetica',
            size = 12, weight = 'bold'), command= lambda: controller.show_frame("FeedbackPage"), fg='white', bg='light green')
        feedbackButton.grid(row=5, column=9, sticky = 'nsew')


        
        self.beatBox=tk.Label(self, text='Get ready!', font=tkFont.Font(family = 'Helvetica',
            size = 36, weight = 'bold'), bg = 'White', fg='Black')
        self.beatBox.grid(row=3, column=1, columnspan=7, sticky = 'nsew')
        self.intensityBox=tk.Label(self, text='Intensity', font=tkFont.Font(family = 'Helvetica',
            size = 36, weight = 'bold'), bg = 'White', fg='Black')
        self.intensityBox.grid(row=4, column=1, columnspan=7, sticky = 'nsew')





        #Make each row/column fill the space evenly
        for x in range(6):
            tk.Grid.columnconfigure(self, x, weight=1)
        for y in range(10):
            tk.Grid.rowconfigure(self, y, weight=1)

    def restartPressed(self):
        global g_Playback
        g_Playback = False
        self.controller.show_frame("MainMenuPage")

    def updateParams(self):
        global g_Pattern, g_Tempo, g_Repeats, g_Beat, g_Intensity
        self.currentPatternLabel['text']=str(g_Pattern)
        self.tempoLabel['text']=str(g_Tempo)
        self.repeatLabel['text']=str(g_Repeats) 
        self.beatBox['text']=str(g_Beat)
        self.intensityBox['text']=str(g_Intensity)

class FeedbackPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        myFont = tkFont.Font(family = 'Helvetica', size = 18, weight = 'bold')

        background_label = tk.Label(self, background='white')
        background_label.pack(fill="both", expand="no")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #create title
        title=tk.Label(self, text='Feedback: ', font=myFont, bg = 'black', fg='green')
        title.grid(row=0, column=1, columnspan=7, sticky = 'nsew')
        exitButton = tk.Button(self, text='Exit', font=myFont, command=exitProgram, height=2, width=6)
        exitButton.grid(row=0, column=9, stick='nsew')


        patternTextLabel =tk.Label(self, text='Current Pattern:', font=myFont, bg = 'white', fg='Black')
        patternTextLabel.grid(row=1, column=2, sticky = 'nsew')
        self.currentPatternLabel =tk.Label(self, text='B1', font=tkFont.Font(family = 'Helvetica',
            size = 12, weight = 'bold'), bg = 'white', fg='Black')
        self.currentPatternLabel.grid(row=1, column=3, sticky = 'nsew')

        tempoTextLabel=tk.Label(self, text='Tempo:', font=myFont, bg = 'white', fg='black')
        tempoTextLabel.grid(row=1, column=4, sticky = 'nsew')
        self.tempoLabel=tk.Label(self, text='100', font=myFont, bg = 'white', fg='black', width = 3)
        self.tempoLabel.grid(row=1, column=5, sticky='ew')

        repeatTextLabel=tk.Label(self, text='Repeats:', font=myFont, bg = 'white', fg='black')
        repeatTextLabel.grid(row=1, column=6, sticky = 'nsew')
        self.repeatLabel=tk.Label(self, text='1', font=myFont, bg = 'white', fg='black', width = 3)
        self.repeatLabel.grid(row=1, column=7, sticky='ew')

        restartButton = tk.Button(self, text='Restart', font=myFont, command= lambda: controller.show_frame("MainMenuPage"), fg='white', bg='orange')
        restartButton.grid(row=0, column=0, sticky = 'nsew')

        accuracyTextLabel=tk.Label(self, text='Accuracy (%):', font=tkFont.Font(family = 'Helvetica',
            size = 18, weight = 'bold'), bg = 'White', fg='Black')
        accuracyTextLabel.grid(row=3, column=4, sticky = 'nsew')
        self.accuracyLabel=tk.Label(self, text='85%', font=tkFont.Font(family = 'Helvetica',
            size = 18, weight = 'bold'), bg = 'White', fg='Black')
        self.accuracyLabel.grid(row=3, column=5, sticky = 'nsew')

        streakTextLabel=tk.Label(self, text='Longest Streak:', font=tkFont.Font(family = 'Helvetica',
            size = 18, weight = 'bold'), bg = 'White', fg='Black')
        streakTextLabel.grid(row=4, column=4, sticky = 'nsew')
        self.streakLabel=tk.Label(self, text='16', font=tkFont.Font(family = 'Helvetica',
            size = 18, weight = 'bold'), bg = 'White', fg='Black')
        self.streakLabel.grid(row=4, column=5, sticky = 'nsew')

        scoreTextLabel=tk.Label(self, text='Score:', font=tkFont.Font(family = 'Helvetica',
            size = 18, weight = 'bold'), bg = 'White', fg='Black')
        scoreTextLabel.grid(row=5, column=4, sticky = 'nsew')
        self.scoreLabel=tk.Label(self, text='A+', font=tkFont.Font(family = 'Helvetica',
            size = 11, weight = 'bold'), bg = 'White', fg='Black')
        self.scoreLabel.grid(row=5, column=5, sticky = 'nsew')





        #Make each row/column fill the space evenly
        for x in range(6):
            tk.Grid.columnconfigure(self, x, weight=1)
        for y in range(10):
            tk.Grid.rowconfigure(self, y, weight=1)


    def updateParams(self):
        global g_Pattern, g_TotalNotes, g_Tempo, g_Repeats, g_Accuracy, g_Streak
        print(g_Streak, g_TotalNotes, ((g_Streak + 1) * 1.0 / (g_TotalNotes * 5)) * 100)
        score = g_Accuracy * 100 +  (g_Streak * 1.0 / (g_TotalNotes * 5) * 100)

        #TODO: Check this grade calculation

        grade = int(g_Accuracy * 10000 +  ((g_Streak + 1) * 1.0 / g_TotalNotes) * 1000 + g_Streak)

        # if(score >= 97):
        #     grade = 'DRUM GOD'
        # elif(score >= 90):
        #     grade = 'Rockstar!'
        # elif(score >= 80):
        #     grade = 'Semi-Pro'
        # elif(score >= 70):
        #     grade = 'Getting There!'
        # elif(score >= 60):
        #     grade = 'First Gig'
        # else:
        #     grade = 'Rookie'

        self.currentPatternLabel['text']=str(g_Pattern)
        self.tempoLabel['text']=str(g_Tempo)
        self.repeatLabel['text']=str(g_Repeats)
        self.accuracyLabel['text']=str(int(g_Accuracy * 100))
        self.streakLabel['text']=str(g_Streak)
        self.scoreLabel['text']= str(grade)




##############BEGIN MAIN CODE###########################
if __name__ == "__main__":
    app = MainApp()
    app.geometry('800x480')
    app.mainloop()

#BEGIN MAIN GUI LOOP
tk.mainloop()
