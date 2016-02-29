# Ethan Massey 2/28/2016
#
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <emassey2@wisc.edu> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# If you are ever in Madison, send me a pm or shoot me an email!
# ----------------------------------------------------------------------------
#
#
# WARNING! This code was initially written while real, more important code was 
# compiling, and really came together during two late night, beer fueled, coding
# sessions. There are mistakes, the code tends to be on the ugly side, and I
# can't guarantee bug free operation. Good luck!
#
# PS if you are using this over ssh use sudo otherwise python will complain

import sys
import pygame
import time
import RPi.GPIO as GPIO
import operator

#linux specific for getting a single char from the command line
# now that we aren't taking keyboard input it doesn't matter but w/e
import tty
import termios

NUM_PAGES = 2
NUM_CH = 12
# Rows are in, cols are out, then there is page...(it's in too)
PAGE_BTN = 8
ROW1 = 10
ROW2 = 11
ROW3 = 12
COL1 = 21
COL2 = 22
COL3 = 16
COL4 = 18

ROWS = [ROW1, ROW2, ROW3]
COLS = [COL1, COL2, COL3, COL4]

PREV_STATE = [[0 for x in range(len(COLS))] for x in range(len(ROWS))]
SOUND_DIR = 'rick/'

def main(argv):

    chStack = []
    chDict = {'a': ['AIDS',                                            'alright_morty_time_to_make_our_move'], \
              'b': ['allahu_akbar',                                    'and_thats_the_way_the_news_goes'], \
              'c': ['god_damn_it_morty_i_ask_you_to_do_one_thing',     'cover_me'], \
              'd': ['hahaha_yeah',                                     'follow_my_lead'], \
              'e': ['i_had_to_make_a_bomb_morty',                      'i_dont_like_being_told_where_to_go_and_what_to_do'], \
              'f': ['lick_lick_lick_my_balls',                         'i_dont_know_what_you_mean_by_that'], \
              'g': ['looks_like_weve_merely_prolonged_the_inevitable', 'okay_yeah_fine'], \
              'h': ['thats_right_morty',                               'sure_why_not_i_dunno'], \
              'i': ['uh_huh_yeah_i_dont_care',                         'youre_our_boy_dog_dont_even_trip'], \
              'j': ['were_gonna_9_11_it',                              'youre_frustrating_me'], \
              'k': ['what_are_you_nuts',                               'wonderful_you_win_can_we_go_home_now'], \
              'l': ['wubba_lubba_dub_dub_1',                           'whatre_you_trying_to_say_about_morty']};


    initIO()
    initScanningMatrix()
    pygame.init()
    pygame.mixer.set_num_channels(NUM_CH)
    for chNum in range(0, NUM_CH):
        ch = pygame.mixer.Channel(chNum)
        ch.set_endevent(chNum)
        chStack.append(ch)
    pageState = False


    running = True
    page = 0
    printWavs(chDict, page)
    while running:

        for event in pygame.event.get():
            chStack.append(pygame.mixer.Channel(event.type))

        # do some crappy edge detection
        if (GPIO.input(PAGE_BTN) == False):
            if not pageState:
                pageState = True
                page = page + 1
                if page >= NUM_PAGES:
                    page = 0
                printWavs(chDict, page)
        else:
            pageState = False


        # see what buttons are currently being pressed
        stack = scanMatrix()
        for c in stack:
            if (c in chDict.keys()):
                chDict[c][page]
                if not chStack:
                    print "We need to wait"
                else:
                    chStack.pop().play(pygame.mixer.Sound(SOUND_DIR + '/' + chDict[c][page] + '.wav'))
                    print c
                    
        #printState()
        time.sleep(.05)


def initIO():
    pygame.mixer.init(44100, -16, 1, 1024)
    GPIO.setmode(GPIO.BOARD)
    
    # config inputs (rows and page_btn)
    GPIO.setup(PAGE_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for row in ROWS:
        GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # config outputs (cols)
    for col in COLS:
        GPIO.setup(col, GPIO.OUT)
        GPIO.output(col, GPIO.HIGH)
    

def initScanningMatrix():
    
    global PREV_STATE
    for row in range(len(ROWS)):
        for col in range(len(COLS)):
            PREV_STATE[row][col] = False

def printState():
    global PREV_STATE
    for row in range(len(ROWS)):
        for col in range(len(COLS)):
            if PREV_STATE[row][col]:
                print "row:" + str(row) + "col:" + str(col) + "[1]"
            else:
                print "row:" + str(row) + "col:" + str(col) + "[0]"
        print "\n"
            
def getSingleChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return [ch]

def scanMatrix():
    global PREV_STATE
    activeBtns = []
    
    for col in range(len(COLS)):
        GPIO.output(COLS[col], GPIO.LOW)

        for row in range(len(ROWS)):
            if (GPIO.input(ROWS[row]) == False):
                if not PREV_STATE[row][col]:
                    PREV_STATE[row][col] = True
                    activeBtns.append(chr((col * len(ROWS) + row) + ord('a')))
            else:
                PREV_STATE[row][col] = False

        GPIO.output(COLS[col], GPIO.HIGH)

    return activeBtns

def printWavs(chDict, page):
    #hard code, because fuck it
    print '\n\n\n\n\n\n******************************************************'
    print 'Page: ' + str(page) + '\n'
    print 'l' + ' - ' +  chDict['l'][page]
    print 'k' + ' - ' +  chDict['k'][page]
    print 'j' + ' - ' +  chDict['j'][page] + '\n'
    print 'i' + ' - ' +  chDict['i'][page]
    print 'h' + ' - ' +  chDict['h'][page]
    print 'g' + ' - ' +  chDict['g'][page] + '\n'
    print 'f' + ' - ' +  chDict['f'][page]
    print 'e' + ' - ' +  chDict['e'][page]
    print 'd' + ' - ' +  chDict['d'][page] + '\n'
    print 'c' + ' - ' +  chDict['c'][page]
    print 'b' + ' - ' +  chDict['b'][page]
    print 'a' + ' - ' +  chDict['a'][page] + '\n'

if __name__ == "__main__":
    main(sys.argv[1:])
