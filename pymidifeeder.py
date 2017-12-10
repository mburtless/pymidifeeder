#!/usr/bin/env python
import sys
import os
import pyvjoy
import pygame
import pygame.midi
from pygame.locals import *
# display a list of MIDI devices connected to the computer

def init_pygame():
    """Inits the pygame processes, returns pygame get and post handlers
    """
    pygame.init()
    pygame.fastevent.init() #does fastevent even help? Who knows

    event_get = pygame.fastevent.get
    event_post = pygame.fastevent.post

    pygame.midi.init()
    return event_get, event_post

def init_vjoy():
    vjdevice = pyvjoy.VJoyDevice(1)
    vjdevice.reset()
    vjdevice.reset_buttons()
    return vjdevice

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def print_device_info():
    for i in range( pygame.midi.get_count() ):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r
        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"
        print ("%2i: interface: %s, name: %s, opened: %s %s" %
               (i, interf, name, opened, in_out))

def midi_noteon_handler(pygame_midi_event, vjdevice):
    #define events to convert
    #event.status reflects note_down (144) vs note_up (128)
    #event.data1 reflects pad pressed
    #event.dats2 reflects velocity

    #to do, prompt user to calibrate max and min and replace 36/43 below
    remapped_val = remap(pygame_midi_event.data1, 36, 43, 1, 8)


    print("You pressed button %s" % str(remapped_val))
    vjdevice.set_button(int(remapped_val),1)

def midi_noteoff_handler(pygame_midi_event, vjdevice):

    #to do, prompt user to calibrate max and min and replace 36/43 below
    remapped_val = remap(pygame_midi_event.data1, 36, 43, 1, 8)

    print("You released button %s" % str(remapped_val))
    vjdevice.set_button(int(remapped_val),0)

def pygame_event_handler(pygame_events):
    """Handles events provided by the pygame event getter
    Return quit, keydown or some debug info about a midi event"""
    for e in pygame_events:
        if e.type in [QUIT]:
            return "quit"
        if e.type in [KEYDOWN]:
            return "keydown"
        if e.type in [pygame.midi.MIDIIN]:
            # print information to console
            return_string = "Timestamp: " + str(e.timestamp) + "ms, Channel: " + str(e.data1) + ", Value: " + str(e.data2)
            return return_string

def event_loop(vjdevice, midi_device, event_get, event_post):
    """Main loop that listens for events and sends to handlers
    Takes vjoy device, midi device and pygame event get and post handlers as args"""

    print ("Logging started:")

    while True:
        pygame_event = pygame_event_handler(event_get())
        if pygame_event == "quit":
            #Add some graceful shutdown logic
            break
        elif pygame_event == "keydown":
            #Add some graceful shutdown logic
            break
        elif pygame_event:
            print (pygame_event)

        # if there are new data from the MIDI controller
        if midi_device.poll():
            midi_events = midi_device.read(10)
            pygame_midi_events = pygame.midi.midis2events(midi_events, midi_device.device_id)
            for pygame_midi_event in pygame_midi_events:
                #print(pygame_midi_event.__dict__)
                #event_post( pygame_midi_event )
                if pygame_midi_event.status == 144:
                    print('note %s on' % pygame_midi_event.data1)
                    midi_noteon_handler(pygame_midi_event, vjdevice)
                elif pygame_midi_event.status == 128:
                    print('note %s off' % pygame_midi_event.data1)
                    midi_noteoff_handler(pygame_midi_event, vjdevice)
#def main
def main():
    event_get, event_post = init_pygame()
    vjdevice = init_vjoy()

    print ("Available MIDI devices:")
    print_device_info()
    # Change this to override use of default input device
    device_id = None
    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id
    print ("Using input_id: %s" % input_id)
    midi_device = pygame.midi.Input(input_id)
    event_loop(vjdevice, midi_device, event_get, event_post)

if __name__ == '__main__':
    main()
