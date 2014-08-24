#!/usr/bin/env python2
"""
Copyright (c) 2014, Patrick Louis <patrick at iotek do org>
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    1.  The author is informed of the use of his/her code. The author does not have to consent to the use; however he/she must be informed.
    2.  If the author wishes to know when his/her code is being used, it the duty of the author to provide a current email address at the top of his/her code, above or included in the copyright statement.
    3.  The author can opt out of being contacted, by not providing a form of contact in the copyright statement.
    4.  If any portion of the author's code is used, credit must be given.
            a. For example, if the author's code is being modified and/or redistributed in the form of a closed-source binary program, then the end user must still be made somehow aware that the author's work has contributed to that program.
            b. If the code is being modified and/or redistributed in the form of code to be compiled, then the author's name in the copyright statement is sufficient.
    5.  The following copyright statement must be included at the beginning of the code, regardless of binary form or source code form.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Except as contained in this notice, the name of a copyright holder shall not
be used in advertising or otherwise to promote the sale, use or other dealings
in this Software without prior written authorization of the copyright holder.

----

A daemon used to execute programs depending on the state of the lid and the
state of the jack (earphones)

Depends on daemon
"""
import daemon
import os
import time

"""
The time to wait between iterations in seconds
"""
SLEEP_TIME = 1

"""
The location of the lid file
usually: /proc/acpi/button/lid/*/state
"""
LID_LOCATION = "/proc/acpi/button/lid/LID0/state"

"""
The location of the jack file
usually: /proc/asound/card0/codec#0
"""
JACK_LOCATION = "/proc/asound/card0/codec#0"

"""
States

(JACK_IN  - LID_OPEN) : (IO)
(JACK_IN  - LID_CLOSE): (IC)
(JACK_OUT - LID_OPEN) : (OO)
(JACK_OUT - LID_CLOSE): (OC)
"""
STATE         = ("IO","IC","OO","OC")

"""
The commands to be executed when switching from one state to another
"""
STATE_COMMANDS= {
        "OOIO":"",
        "IOOO":"",
        "IOOC":"",
        "OCIO":"",
        "OCIC":"",
        "ICOC":"espeak 'remove jack while lid closed'",
        "ICOO":"",
        "OOIC":"",
        "IOIC":"",
        "ICIO":"",
        "OOOC":"",
        "OCOO":""
        }

"""
The current state the program is in
"""
CURRENT_STATE = ""

"""
Content of the jack file
"""
JACK_FILE     = ""

"""
Return True if the earphones are plugged in
The first time it returns False
"""
def jack_in_state():
    global JACK_FILE
    #at startup
    if JACK_FILE == "":
        JACK_FILE = open(JACK_LOCATION,'r').read()
        return False
    new_file = open(JACK_LOCATION,'r').read()

    sp1 = JACK_FILE.split("\n")
    sp2 = new_file.split("\n")
    JACK_FILE = new_file
    for i in range(len(sp2)): #loop in the new file
        if sp2[i] != sp1[i]:
            if "OUT" in sp2[i]:
                return False
            else:
                return True
    return False

"""
Return True if the lid is open
"""
def lid_open_state():
    lid = open(LID_LOCATION, 'r').read()
    if "open" in lid:
        return True
    else:
        return False

"""
Return the current state as a string
"""
def get_state():
    letter_one = ""
    letter_two = ""
    if jack_in_state():
        letter_one = "I"
    else:
        letter_one = "O"
    if lid_open_state():
        letter_two = "O"
    else:
        letter_two = "C"
    return letter_one+letter_two

"""
Will execute the command related to the state transition
"""
def execute_command(command):
    print command
    print STATE_COMMANDS[command]
    if STATE_COMMANDS[command] != "":
        os.system(STATE_COMMANDS[command])
        return
    else:
        return

"""
That's the routine that should be daemonized
"""
def main_routine():
    global CURRENT_STATE
    while True:
        time.sleep(SLEEP_TIME)
        if CURRENT_STATE == "": #at the first execution
            CURRENT_STATE = get_state()
            continue
        new_state = get_state()
        if new_state != CURRENT_STATE:
            execute_command(CURRENT_STATE+new_state)
            CURRENT_STATE = new_state


"""
Make it run ask a daemon
"""
with daemon.DaemonContext():
    main_routine()
