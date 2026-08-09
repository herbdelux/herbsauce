import ttkbootstrap as tb
from tkinter import filedialog as fd
import tkinter as tk
from tkinter import ttk as ttk
import time
import threading
import numpy as np
import sys
import os
import argparse
import math
from tkinter import messagebox as mb
import webbrowser
import PIL
import sounddevice as sd
#import gc
import queue
q = queue.Queue(maxsize=48)
#Props to all the people who made the packages imported above, and the Python people, and the Thonny people!

parser = argparse.ArgumentParser(description="For Soundcard package importation")
parser.add_argument("-s", "--soundcard", action="store_true")
#parsetime = parser.parse_args()

#parser2 = argparse.ArgumentParser(description="For opening file off the bat")
parser.add_argument("filename", nargs="?", action="store")
parsetime = parser.parse_args()

fileparse = ""

if parsetime.filename is not None:
    fileparse = parsetime.filename
    print(fileparse + ": file opened off the bat")
    del sys.argv[1]
    #print(len(sys.argv))
    print("parser for file")
else:
    print("no parser for file")
 
if not parsetime.soundcard:
    print("importing sounddevice package")
    import sounddevice as sd
else:
    print("importing soundcard package")
    import soundcard as sc

#herb sauce version 1.0 created by herb delux.
# https://deluxeherbs.net/artists/herbdelux/herbdelux.html, https://herbdeluxmusic.bandcamp.com, https://github.com/herbdelux
#This program is intended to MAKE and PLAY .herb audio files. They have a 50 byte minimum header size, that is variable in length, if you add meta data.
#To make a .herb file, you must import/open a .wav file (or multiple .wav files) in the program and convert it using the .herb Creator tab.
#It supports up to 255 metadata items, each with a variable data length of up to 255 characters. 
#A .herb file is a lossless audio file that can technically contain up to 16,777,215 audio tracks.
#.herb files are encoded as PCM audio data. All integers, both signed and unsigned, are written in big endian.
#This program in particular can create 2.0 (stereo), 4.0 (quadraphonic), and 6.0 (hexaphonic) versions of .herb files,
#exported as name.2.herb, name.4.herb, or name.6.herb, to make it easy to figure out which file to select and play.
#herb sauce is intended to make it simple to create and play these .herb files, by utilizing the Sounddevice and Soundcard packages in Python.
#Most desktop PC soundcards these days support 6 to 8 assignable outputs. And most people with class-compliant recording interfaces have ones that support at least 4 channels out.
#No more messing around with LFE, RFE, CENTER, etc. Just channel 1-2, 3-4, 5-6, etc.
#For file header structure and audio frame structure: click Settings tab, then Support Me!/About, then click the header structure button
#The intended setup for most music mixed into 4.0 is dual stereo. (Go to Settings tab in herb sauce, click How to use to see a picture of a dual stereo setup)
#4.0 dual stereo is where one pair (the 1,2) is on the outside, and the other pair (the 3,4) is on the inside, setup symmetrically.

#Linux current pyinstaller command needed
#pyinstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py

#Splash may not be needed. It seems to load pretty quickly. #Splash pyinstaller args:
#--hidden-import pyi_splash --splash pics/SplashHerbSauce.png

#Windows
#pyinstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --icon HerbSauceico2.ico --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py

#Mac - creates a slow to open version that seems highly compatible with different units. use --onedir --w for .app version thats faster but less compaitable with different installs it seems
#python3 -m PyInstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --icon HerbSauceico2.icns --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py

#For strange pip/Py installations:
#--exclude-module PyQt5 --exclude-module PyQt6

#Removed splash because the program opens up pretty fast on Windows and Linux. Also, I don't think Mac supports splash.
#Use --hidden-import pyi_splash --splash image.png during pyinstaler compile for splash screen, with code below
#Apparently the following code is needed along with the above pyinstaller args, for splash screen to work properly
##try:
    ##import pyi_splash
    ##pyi_splash.update_text("Program loaded")
    ##pyi_splash.close()
    
##except:
    ##pass
    
#This seems to delete the sd variable and its associations or whatever. I don't think it undoes the actual importation.
#Therefore sounddevice and soundcard packages will still conflict if both imported, at least in Linux it seems.
#del sd

#Queue stuff
#q = Queue(maxsize=1000)
#q.put(var)
#q.get()
#q.empty(), q.full(), q.qsize()
#q.put_nowait(), q.get_nowait()

def musictime(link):
    
    #This apparently works too
    #webbrowser.open_new()

    musicdict = {
        1 : "https://herbdeluxmusic.bandcamp.com",
        2 : "https://github.com/herbdelux",
        3 : "https://deluxeherbs.net/artists/herbdelux/herbdelux.html",
        }
    
    webbrowser.open(musicdict[link])

    #Old way of doing this
    #if link ==1:
        #webbrowser.open("https://herbdeluxmusic.bandcamp.com")
    #elif link == 2:
        #webbrowser.open("https://github.com/herbdelux")

    return

def wavchoose(chooser):
    
    global filewav1
    global filewav2
    global filewav3
    global sampleratewav1
    global bitdepthwav1
    global sampleratewav2
    global bitdepthwav2
    global headsizewav1
    global file1mono
    global file2mono
    global file3mono
    global manualheader
    global quadro
    global hexa
    global wavdir
    
    #Add back in .wave files option?
    filetypes = [
            ("Wav files", "*.wav"),
            ("All files", "*")
        ]

    wavname = fd.askopenfilename(title="Open file", initialdir=wavdir, filetypes=filetypes)
    
    if wavname == "" or wavname == ():
        print("No file selected")
        return

    dirs1, filenamestrip1 = os.path.split(wavname)
    filenamesplit1 = filenamestrip1.split(".")[1]
    wavdir = dirs1
    
    #Why is this here?
    ##quadro = False
    
    #Get wav samplerate, bitdepth, and header length
    with open(wavname, "rb") as w1:
        
        dtrack = 0
                
        #Skippin them first 4 RIFF bytes
        w1.read(4)
        dtrack = dtrack + 4
        
        #Size of RIFF chunk?
        sizechunk = int.from_bytes(w1.read(4), 'little')
        print(str(sizechunk) + " sizechunk")
        dtrack = dtrack + 4
        
        #Skippin
        w1.read(4)
        dtrack = dtrack + 4
        
        #Size of format chunk
        fmttext = w1.read(4)
        dtrack = dtrack + 4
    
        if fmttext != b'fmt ':
            print("Problem with your wave file header. Attempting anyway")
            mb.showinfo(title="Error", icon='info', message="Problem with your wav file. Attempting anyway")
            
            #return
        
        else:
            pass
        
        fmtsize = int.from_bytes(w1.read(4), wavendyness, signed=False)
        dtrack = dtrack  + 4
        
        adjustfmt = fmtsize - 16
        
        print(str(fmtsize) + " fmtsize")
        
        #Audio format 1 for PCM/uncompressed
        w1.read(2)
        dtrack = dtrack + 2
        
        #Number of channels
        numchan = int.from_bytes(w1.read(2), wavendyness, signed=False)
        print("Number of channels: " + str(numchan))
        dtrack = dtrack + 2
        
        if numchan == 1:
            quadro = False
            hexa = False
            if chooser == 1:
                file1mono = True
            elif chooser == 2:
                file2mono = True
            elif chooser == 3:
                file3mono = True
        elif numchan == 4:
            quadro = True
            hexa = False
            if chooser == 1:
                file1mono = False
            elif chooser == 2:
                file2mono = False
            elif chooser == 3:
                file3mono = False
        elif numchan == 6:
            hexa = True
            quadro = False
            if chooser == 1:
                file1mono = False
            if chooser == 2:
                file2mono = False
            if chooser == 3:
                file3mono = False
        elif numchan == 2:
            quadro = False
            hexa = False
            if chooser == 1:
                file1mono = False
            elif chooser == 2:
                file2mono = False
            elif chooser == 3:
                file3mono = False
        else:
            print("Cannot import wav with more than 4 channels.")
            return
            
        #Read 4 bytes for sample rate
        sampleratewav1 = w1.read(4)
        sampleratewav1 = int.from_bytes(sampleratewav1, wavendyness, signed=False)
        print("Sample rate: " + str(sampleratewav1))
        dtrack = dtrack + 4
        
        #Skip 6 bytes for byte rate and block align
        w1.read(4)
        dtrack = dtrack + 4
        #Block align: numchannels * bits per sample / 8
        print(str(int.from_bytes(w1.read(2), 'little')) + " block align")
        dtrack = dtrack + 2
        
        #Read 2 bytes for bit depth
        bitdepthwav1 = w1.read(2)
        bitdepthwav1 = int.from_bytes(bitdepthwav1, wavendyness, signed=False)
        print("Bit depth: " + str(bitdepthwav1))
        dtrack = dtrack + 2
        if fmtsize != 16:
            w1.read(adjustfmt)
            dtrack = dtrack + adjustfmt
        else:
            pass
        
        #Print data subchunk - b'smpl' for Reason rendered wavs
        datacheck = w1.read(4)
        dtrack = dtrack + 4
        print(datacheck)
        #checknum = 4 means 44 byte header. checknum = 6 means 46 byte header
        #Trying to find the b'data' section.
        if datacheck == b'data':
            headsizewav1 = 44 + adjustfmt
            checknum = 4 + adjustfmt
        elif datacheck != b'data':
            dtracker = False
            
            while dtracker == False:
                tt = w1.read(1)
                dtrack = dtrack + 1
                if tt == b'd':
                    tt2 = w1.read(1)
                    dtrack = dtrack + 1
                    if tt2 == b'a':
                        tt3 = w1.read(1)
                        dtrack = dtrack + 1
                        if tt3 == b't':
                            tt4 = w1.read(1)
                            dtrack = dtrack + 1
                            if tt4 == b'a':
                                #dtrack = dtrack + 1
                                headsizewav1 = dtrack + 4
                                print("Header length is: " + str(headsizewav1))
                                checknum = 4
                                dtracker = True
        else:
            mb.showinfo(title="Alert", icon='info', message="Could not determine the header length of your wav file.\nAttempting to read as 44 byte header depending on fmt length")
            headsizewav1 = 44 + adjustfmt
            checknum = 4
        
        print(str(headsizewav1) + " byte header detected")
        
        if manualheader == 0:
            temphead = headsizewav1
        else:
            print("However, using custom header length of: " + str(manualheader))
            temphead = manualheader
            
        #Finish it off
        w1.read(checknum)
        #Print number of bytes in data section subchunk2 size minus complete header length
        #print(int.from_bytes(w1.read(checknum), endyness))

    if chooser == 1:
        
        labelwav11.configure(text="Selected wav file:\n" + filenamestrip1 + "\nNumber of Chan: " + str(numchan) + "\n" + str(sampleratewav1) + ", " + str(bitdepthwav1) + "bits\nHeader length: " + str(temphead) + "\n")
        filewav1 = wavname
        
    elif chooser == 2:
        
        labelwav22.configure(text="Selected wav file:\n" + filenamestrip1 + "\nNumber of Chan: " + str(numchan) + "\n" + str(sampleratewav1) + ", " + str(bitdepthwav1) + "bits\nHeader length: " + str(temphead) + "\n")
        filewav2 = wavname
    
    elif chooser == 3:
        
        labelwav32.configure(text="Selected wav file:\n" + filenamestrip1 + "\nNumber of Chan: " + str(numchan) + "\n" + str(sampleratewav1) + ", " + str(bitdepthwav1) + "bits\nHeader length: " + str(temphead) + "\n")
        filewav3 = wavname
    
    print("Quadro = " + str(quadro))
    print("Hexa = " + str(hexa))
    return

def createherb(herbname, wav1, wav2, wav3, samplerate, bitdepth, headsizewav, track, artist, album, trnum, year):
    
    global file1mono
    global file2mono
    global file3mono
    global manualheader
    global customdir1
    global cdircheck
    global quadro
    global hexa
    global endyness
    
    track = track.rstrip()
    artist = artist.rstrip()
    album = album.rstrip()
    year = year.rstrip()
    trnum = trnum.rstrip()

    metavals = [b'track', b'artis', b'album', b'year0', b'trnum']
        
    if track != "" or artist != "" or album != "" or year != "" or trnum != "":
        meta = True
        print("meta true")
        headerlength = 50 + (len(track) + 5) + (len(artist) + 5) + (len(album) + 5) + (len(str(trnum)) + 5) + (len(str(year)) + 5)
    else:
        meta = False
        print("meta false")
        headerlength = 50
        
    if manualheader != 0:
        headsizewav = manualheader
    else:
        pass
    
    herbname = herbname.rstrip()
    
    print(customdir1 + "customdir")
    if cdircheck == True:
        cdir = customdir1 + "/"
    else:
        cdir = customdir1
    
    print(str(cdir) + " cdirtime")
    
    if wav1 == "" and wav2 == "" and wav3 == "":
        print("Error. Please select 1 to 3 .wav files to create your .herb file.")
        print("They should each be the same exact size")
        return
    
    else:
        pass
              
    if wav3 != "" and wav2 !="" and wav1 != "":
        triplevar = True
        doublevar = True
    elif wav3 != "" and wav2 == "" and wav1 != "":
        triplevar = False
        doublevar = True
        wav2 = wav3
    elif wav3 != "" and wav2 != "" and wav1 == "":
        triplevar = False
        doublevar = True
        wav1 = wav3
    elif wav3 == "" and wav2 != "" and wav1 != "":
        triplevar = False
        doublevar = True
    elif wav3 != "" and wav2 == "" and wav1 == "":
        triplevar = False
        doublevar = False
        wav1 = wav3
    elif wav1 != "" and wav2 == "" and wav3 == "":
        triplevar = False
        doublevar = False
    elif wav2 != "" and wav1 == "" and wav3 == "":
        triplevar = False
        doublevar = False
        wav1 = wav2

    if doublevar == False and triplevar == False and quadro == True and hexa == False:
        numchan = 4
    elif doublevar == False and triplevar == False and quadro == False and hexa == False:
        numchan = 2
    elif doublevar == True and triplevar == False and quadro == False and hexa == False:
        numchan = 4
    elif doublevar == True and triplevar == True and quadro == False and hexa == False:
        numchan = 6
    elif doublevar == False and triplevar == False and quadro == False and hexa == True:
        numchan = 6
        print("hexa")
    else:
        print("NUMCHAN SETTING ISSUE")
         
    if quadro == True and doublevar == True:
        print("Can only convert 4 channel wav into 4 channel .herb. Not add any more wavs.")
        return
    elif hexa == True and doublevar == True:
        print("Can only convert 6 channel wav into 6 channel .herb. Not add any more wavs.")
        return
    
    if herbname == "":
        print("You did not specify a name for your .herb file.")
        print("Exporting as untitled." + str(numchan) + ".herb.")
        herbname = "untitled." + str(numchan) + ".herb"
    
    else:
        herbs = herbname.split(".")
        
        if len(herbs) == 1:
            herbname = herbname + "." + str(numchan) + ".herb"

        else:
            if herbs[1] == "herb":
                herbname = herbs[0] + "." + str(numchan) + "." + herbs[1]
        
            else:
                herbname = herbname + "." + str(numchan) + ".herb"
                
    #.herb file header structure: 50 bytes minimum with no metadata or track info. Variable header length WITH metadata
        
    bitdict = {
        "8" : 1,
        "16" : 2,
        "24" : 3
        }
    
    bitdepth = int(bitdepth)
    samplerate = int(samplerate)
    
    byz = bitdict[str(bitdepth)]
    #print(byz)
    
    stereodict = {
        "1" : 1,
        "2" : 2,
        "3" : 3,
        }
    
    ##try:
    print(str(str(cdir) + herbname))
    
    with open(str(str(cdir) + herbname), 'wb') as db, open(wav1, "rb") as w1:
        
        labelcreated2.configure(text="Creating, please wait.")
        
        #For 2 stereo tracks
        if doublevar == True:
            w2 = open(wav2, "rb")
        else:
            pass
        
        #For three stereo tracks
        if triplevar == True:
            w3 = open(wav3, "rb")
        else:
            pass
        
        bitdepth2 = int(bitdepth) / 8
        
        #Check to make sure both stereo files are the same length/size.
        #Full size of audio data
        if doublevar == False and triplevar == False:
            size1 = os.path.getsize(wav1)
            size1adjusted = math.ceil((size1 - headsizewav) / (bitdepth2 * 2))
            fullsize = size1 - headsizewav
             
        elif doublevar == True and triplevar == False:
            size1 = os.path.getsize(wav1)
            size2 = os.path.getsize(wav2)
            size1adjusted = math.ceil((size1 - headsizewav) / (bitdepth2 * 2))
            fullsize = (size1 * 2) - (headsizewav*2)
        
        elif triplevar == True and doublevar == True:
            size1 = os.path.getsize(wav1)
            size2 = os.path.getsize(wav2)
            size3 = os.path.getsize(wav3)
            size1adjusted = math.ceil((size1 - headsizewav) / (bitdepth2 * 2))
            fullsize = (size1 * 3) - (headsizewav * 3)
        else:
            pass
        
        if doublevar == True and triplevar == False:
            if size1 != size2:
                print("Error. Your two stereo wav files are of different lengths. Trying to parse anyway.")
            else:
                pass
        
        elif triplevar == True and doublevar == True:
            if size1 != size2 or size1 != size3 or size2 != size3:
                print("Error. Your stereo wav files are of different lengths. Trying to parse anyway.")
            else:
                pass
        else:
            pass

        #Write 4 bytes for b'herb'
        #herbarray = [8, 5, 18, 2]
        db.write(b'herb')
        
        #4 for b'pcmb' pulse code modulation big endian
        db.write(b'pcmb')
        
        #Header length (in bytes) as 3 byte
        db.write(headerlength.to_bytes(4, endyness, signed=False))
        
        #Random HERB notes
        #Doesn't work the way I though.
        #db.write(b'/x08')
        #db.write(b'/x05')
        #db.write(b'/x12')
        #db.write(b'/x02')
        #Works for ints in array
        ##db.write(herbarray[0].to_bytes(1, 'little', signed=False))
        ##db.write(herbarray[1].to_bytes(1, 'little', signed=False))
        ##db.write(herbarray[2].to_bytes(1, 'little', signed=False))
        ##db.write(herbarray[3].to_bytes(1, 'little', signed=False))

        #Number of stereo tracks 3 byte
        numchan = numchan.to_bytes(3, endyness, signed=False)
        db.write(numchan)
        
        #Bit depth 2 byte
        bitdepthb = bitdepth.to_bytes(2, endyness, signed=False)
        db.write(bitdepthb)

        #Samplerate 4 bytes
        samplerate = samplerate.to_bytes(4, endyness, signed=False)
        #print("Samplerate in bytes" + str(samplerate))
        db.write(samplerate)
        
        #Full size of audio frames portion which comes after b'leaf'
        db.write(fullsize.to_bytes(10, endyness, signed=False))
        
        #Adding 10 more empty bytes at the end for future additions and changes to the header system. Or because I wanted the header length to be an even 50 minimum.
        fillnum = 0
        fillnum = fillnum.to_bytes(10, endyness, signed=False)
        db.write(fillnum)
        
        if meta == True:
            nummetas2 = 5
        else:
            nummetas2 = 0
        
        #Metadata portion. The start is signified with b'tags'
        db.write(b'tags')
        db.write(nummetas2.to_bytes(1, endyness, signed=False))
        
        #See .herb file documentation PDF for more details about these tags.
        #b'trck', b'arti', b'albm', b'year', b'tnum', b'ofnm', b'comp', b'prod', b'feat', b'spos', b'mix0', b'mast', b'note', b'imag'
        #You can come up with your own, and even put it in your own order. I recommend looking at how herb sauce parses metadata in the getherbinfo() function.
        if meta == True:
            
            #4 bytes for b'trck'
            db.write(b'trck')
            tracknamelen = len(track)
            db.write(tracknamelen.to_bytes(1, endyness, signed=False))
            #m = bytes(thing, "UTF-8") -- turns it into bytestring from string
            db.write(track.encode("utf-8"))
            print(track)
            
            #Add 4 bytes for b'arti'
            db.write(b'arti')
            artistnamelen = len(artist)
            db.write(artistnamelen.to_bytes(1, endyness, signed=False))
            db.write(artist.encode("utf-8"))
            print(artist)
            
            #Add 4 bytes for b'albm'
            db.write(b'albm')
            albumnamelen = len(album)
            db.write(albumnamelen.to_bytes(1, endyness, signed=False))
            db.write(album.encode("utf-8"))
            print(album)
            
            #Add 4 bytes for b'year'
            db.write(b'year')
            yl = len(str(year))
            db.write(yl.to_bytes(1, endyness, signed=False))
            year = str(year)
            if year == "":
                pass
            else:
                print("writing yearnum")
                db.write(year.encode("utf-8"))
                ##db.write(year.to_bytes(yl, endyness, signed=False))
            print(str(len(str(year))) + " yearnumc length")
            
            #Add 4 bytes for b'tnum'
            db.write(b'tnum')
            tn = len(str(trnum))
            db.write(tn.to_bytes(1, endyness, signed=False))
            trnum = str(trnum)
            print(trnum)
            print(type(trnum))
            if trnum == "":
                pass
            else:
                print("writing trnum")
                db.write(trnum.encode("utf-8"))
                #db.write(trnum.to_bytes(tn, endyness, signed=False))
                
            print(str(len(str(trnum))) + " tracknumc length")
            
            #Audio data begins after this
            db.write(b'leaf')
            
        else:
            #Audio data begins after this
            db.write(b'leaf')
            
        #Actual data begins after lowercase herb. This signifies official end of the header, regardless of metadata
        #db.write(b'leaf')
        
        #Read/Write actual data
        #Skip header
        ##for a in range(0, headsizewav):
            ##w1.read(1)
        w1.read(headsizewav)
        
        if doublevar == True:
            #w2.read(1)
            w2.read(headsizewav)
        else:
            pass
            
        if triplevar == True:
            #w3.read(1)
            w3.read(headsizewav)
        else:
            pass
            
        for i in range(0, size1adjusted):
            
            #For having a mono wav being imported, potentially needs fixing
            if quadro == True and doublevar == False and triplevar == False and hexa == False:
                #print("qt df tf hf")
                h1 = w1.read(byz)
                h2 = w1.read(byz)
                h3 = w1.read(byz)
                h4 = w1.read(byz)
            elif hexa == True and quadro == False and doublevar == False and triplevar == False:
                #print("ht qf df tf")
                h1 = w1.read(byz)
                h2 = w1.read(byz)
                h3 = w1.read(byz)
                h4 = w1.read(byz)
                h5 = w1.read(byz)
                h6 = w1.read(byz)
                
            if file1mono == False and file2mono == False and file3mono == False and quadro == False and hexa == False:
                #print("normal")
                h1 = w1.read(byz)
                h2 = w1.read(byz)
                
                #For 4 channels
                if doublevar == True:
                    h3 = w2.read(byz)
                    h4 = w2.read(byz)
                else:
                    pass
                
                #For 6 channels
                if triplevar == True:
                    h5 = w3.read(byz)
                    h6 = w3.read(byz)
                else:
                    pass
                
            #For having a mono wav being imported, needs fixing
            elif quadro == False and hexa == False and (file1mono != False or file2mono != False or file3mono != False):
                #print("e normal")
                if file1mono == True:
                    h1 = w1.read(byz)
                    h2 = h1
                else:
                    h1 = w1.read(byz)
                    h2 = w1.read(byz)
                
                if doublevar == True:
                    if file2mono == True:
                        h3 = w2.read(byz)
                        h4 = h3
                    else:
                        h3 = w2.read(byz)
                        h4 = w2.read(byz)
                else:
                    pass
                
                #For three stereo tracks
                if triplevar == True:
                    if file3mono == True:
                        h5 = w3.read(byz)
                        h6 = h5
                    else:
                        h5 = w3.read(byz)
                        h6 = w3.read(byz)
                else:
                    pass
                
            if not h1 or not h2:
                print("Breaking, no more data to read/write (1 createherb())")
                break
            
            #Says it needs four bytes. Keeping for reference.
            #h1 = struct.unpack("<I", h1)
            #h1 = struct.pack(">I", h1)
            #h1 = h1.decode()
            
            h1 = int.from_bytes(h1, wavendyness, signed=True)
            h1 = h1.to_bytes(byz, endyness, signed=True)
            h2 = int.from_bytes(h2, wavendyness, signed=True)
            h2 = h2.to_bytes(byz, endyness, signed=True)
            
            db.write(h1)
            db.write(h2)
            
            #For two stereo tracks
            if quadro == True and doublevar == False and triplevar == False and hexa == False:
                #print("quadro write")
                h3 = int.from_bytes(h3, wavendyness, signed=True)
                h3 = h3.to_bytes(byz, endyness, signed=True)
                h4 = int.from_bytes(h4, wavendyness, signed=True)
                h4 = h4.to_bytes(byz, endyness, signed=True)
                
                db.write(h3)
                db.write(h4)
                
            elif hexa == True and quadro == False and doublevar == False and triplevar == False:
                #print("hexa write")
                h3 = int.from_bytes(h3, wavendyness, signed=True)
                h3 = h3.to_bytes(byz, endyness, signed=True)
                h4 = int.from_bytes(h4, wavendyness, signed=True)
                h4 = h4.to_bytes(byz, endyness, signed=True)
                h5 = int.from_bytes(h5, wavendyness, signed=True)
                h5 = h5.to_bytes(byz, endyness, signed=True)
                h6 = int.from_bytes(h6, wavendyness, signed=True)
                h6 = h6.to_bytes(byz, endyness, signed=True)
                
                db.write(h3)
                db.write(h4)
                db.write(h5)
                db.write(h6)
                
            else:
                pass
            
            if doublevar == True and quadro == False and hexa == False:
                #print("double write")
                h3 = int.from_bytes(h3, wavendyness, signed=True)
                h3 = h3.to_bytes(byz, endyness, signed=True)
                h4 = int.from_bytes(h4, wavendyness, signed=True)
                h4 = h4.to_bytes(byz, endyness, signed=True)
                
                db.write(h3)
                db.write(h4)
                
            else:
                pass
                
            #For three stereo tracks
            if triplevar == True and quadro == False and hexa == False:
                #print("triple write")
                h5 = int.from_bytes(h5, wavendyness, signed=True)
                h5 = h5.to_bytes(byz, endyness, signed=True)
                h6 = int.from_bytes(h6, wavendyness, signed=True)
                h6 = h6.to_bytes(byz, endyness, signed=True)
                
                db.write(h5)
                db.write(h6)
            else:
                pass
            
        w1.close()
        if doublevar == True:
            w2.close()
        else:
            pass
        if triplevar == True:
            w3.close()
        else:
            pass
        
        db.close()
    
    if (doublevar == True and triplevar == False) or (quadro == True and doublevar == False and triplevar == False):
        print("File exported as " + herbname + " with 4 channels")
    elif (doublevar == True and triplevar == True) or (hexa == True and quadro == False and doublevar == False and triplevar == False):
        print("File exported as " + herbname + " with 6 channels")
    elif doublevar == False and triplevar == False and quadro == False and hexa == False:
        print("File exported as " + herbname + " with 2 channels")
    else:
        print("Unable to determine exported as number of channels for " + herbname)
        
    labelcreated1.configure(text=".herb file exported as:\n\n" + herbname + "\n" + str(int.from_bytes(samplerate, endyness, signed=False)) + ", " + str(int.from_bytes(bitdepthb, endyness, signed=False)) + "bits\n" + "Number of channels: " + str(float(int.from_bytes(numchan, endyness, signed=False))))
    labelcreated2.configure(text="")
    
    ##except Exception as e:
        ##print("Something went wrong with creating .herb file")
        ##print(e)
    
    return

def openherb(prefile):
    
    global filename0
    global maindir

    #AND HERE
    labelopen0.focus()

    filetypes = [
            ("Herb files", "*.herb"),
            ("All files", "*")
        ]
    
    if prefile == "":
        
        filename001 = fd.askopenfilename(title="Open file", initialdir=maindir, filetypes=filetypes)

        if filename001 == "" or filename001 == ():
            print("No file selected")
            return
        
        else:
            filename0 = filename001
            
            dirs1, filenamestrip1 = os.path.split(filename0)
            #This only affects the 2.herb or 4.herb portion. So [1] is herb.
            filenamesplit1 = filenamestrip1.split(".")[1]
            try:
                maindir = dirs1
            except:
                pass
            labelopen1.configure(text="Selected file:\n" + filenamestrip1)
            if len(filenamestrip1) > 35:
                labelaudio2.configure(text="")
            elif len(filenamestrip1) < 36:
                labelaudio2.configure(text="\n")
    
    else:
        print("PRE FILE")
        filename0 = prefile
        labelopen1.configure(text="Selected file:\n" + prefile)
        if len(prefile) > 31:
            labelaudio2.configure(text="")
        elif len(prefile) < 32:
            labelaudio2.configure(text="\n")
            
    getherbinfo(filename0, 0)
    
    return


def getherbinfo(filename, doer):

    global headsize00
    global bitdepth00
    global samplerate00
    global numchan00
    global filename0
    global stopper
    global trackname
    global artistname
    global albumname
    global tracknum
    global yearnum
    global currentplay
    global endyness
    global metaitems
    global metalist
    
    #IT DOES SOMETHING UP HERE THOUGH. YEEEEHAWWWW.
    #labelopen0.focus()
    
    try:
        
        metadict0 = {
            b'trck' : "",
            b'arti' : "",
            b'albm' : "",
            b'year' : "",
            b'tnum' : "",
            b'ofnm' : "",
            b'comp' : "",
            b'prod' : "",
            b'feat' : "",
            b'imag' : "",
            b'spos' : "",
            b'mixx' : "",
            b'mast' : "",
            b'gear' : "",
            b'note' : ""            
            }
        
        #Ignore this for now
        #metalist0 = [[b'trck', ""],[b'arti', ""],[b'albm', ""],[b'year', ""],[b'tnum', ""],]
        
        if doer == 0:
                
            if filename == "":
                print("Please open a .herb file first.")
                return
            else:
                pass

            with open(filename, "rb") as db:
                
                #Minimum headsize, without metadata/track info, is 50 bytes. With b'tags' followed by a single byte int greater than 0, it becomes variable in size due to metadata.
                print("Opening " + str(filename))

                d12 = db.read(4)
                
                if d12 != b'herb':
                    print("Error. No b'herb'. Possibly wrong file type.")
                    print("Attempting anyway.")
                    #return

                else:
                    pass
                
                #4 for b'pcmb'
                pcmread = db.read(4)
                
                #Hopefully this now supports variable header length. 3 bytes for header length
                headsize00 = int.from_bytes(db.read(4), endyness, signed=False)
                print("Headersize is: " + str(headsize00))

                #Get number of stereo tracks
                numchan00 = int.from_bytes(db.read(3), endyness, signed=False)
                print("Number of channels: " + str(numchan00))
                
                #Get bitdepth
                bitdepth00 = int.from_bytes(db.read(2), endyness, signed=False)
                print("Bitdepth is " + str(bitdepth00))
                
                #Get samplerate
                samplerate00 = int.from_bytes(db.read(4), endyness, signed=False)
                print("Samplerate is " + str(samplerate00))         

                labelaudio6.configure(text="Sample rate: " + str(samplerate00))
                labelaudio7.configure(text="Bit depth: " + str(bitdepth00))
                labelaudio8.configure(text="Number of channels: " + str(float(numchan00)))
                labelaudio82.configure(text="Header size: " + str(headsize00) + " bytes")
                ##playnum.configure(text=str(numchan00) + "\nChannels")

                #Get full file size in bytes
                fullfilesize = int.from_bytes(db.read(10), endyness, signed=False)
        
                #Song length calculation
                bitdict = {
                    8 : 1,
                    16 : 2,
                    24 : 3
                    }
                
                tracklength = (((fullfilesize - headsize00) / bitdict[bitdepth00]) / numchan00) / samplerate00
                tracklength = round(tracklength, 0)
                tracklength = int(tracklength)
                tracklengthmin = int(tracklength / 60)
                tracklengthrem = tracklength % 60
                
                print("Track length: " + str(tracklengthmin) + " m " + str(tracklengthrem) + "s")
                labelaudiolength.configure(text="Length: " + str(tracklengthmin) + "m " + str(tracklengthrem) + "s")
                
                #Read 10 for empty future proofing bytes
                db.read(10)
                
                print(headsize00)
                
                #b'tags'
                readleaf = db.read(4)
                
                metaitems = db.read(1)
                metaitems = int.from_bytes(metaitems, endyness, signed=False)
                if metaitems == 0:
                    metalist = []
                else:
                    metalist = []
                    metalist.append(metaitems)
                labelmetaitems.configure(text="Metadata items: " + str(metaitems) + "\n")
                print(str(metaitems) + " metadata items detected")
                
                root.title("herb sauce")
                
                try:
                    if headsize00 > 50 and metaitems > 0:
                        
                        for qq in range(0, metaitems):
                            #b'trck' etc
                            mval = db.read(4)
                            #Don't use this
                            ##if trackval == b'herb':
                                ##print("breaking metadata herb found")
                                ##break
                            msize = int.from_bytes(db.read(1), endyness, signed=False)
                            mdata = db.read(msize)
                            mdata2 = mdata.decode("utf-8")
                            #print(metadict0[mval])
                            if mval in metadict0.keys():
                                metadict0[mval] = mdata2
                            #also works
                            #if mval in metadict0
                            #if metadict0.get(mval) == None
                            else:
                                pass
                            
                            metalist.append([mval, mdata2])
                            
                        
                        trackname = metadict0[b'trck']
                        artistname = metadict0[b'arti']
                        albumname = metadict0[b'albm']
                        yearnum = metadict0[b'year']
                        tracknum = metadict0[b'tnum']
                        
                        #trackname = metalist0[0][1]
                        #artistname = metalist0[1][1]
                        #albumname = metalist0[2][1]
                        #yearnum = metalist0[3][1]
                        #tracknum = metalist0[4][1]
                        
                        if trackname == "" and artistname == "":
                            pass
                        elif trackname == "" and artistname != "":
                            root.title("[no title] by " + str(artistname) + " - herb Sauce")
                        elif trackname != "" and artistname == "":
                            root.title(str(trackname) + " - herb sauce")
                        elif trackname !="" and artistname != "":
                            root.title(str(trackname) + " by " + str(artistname) + " - herb sauce")
                            
                        labelaudio9.configure(text="Track name: " + str(trackname))
                        labelaudio10.configure(text="Artist name: " + str(artistname))
                        labelaudio11.configure(text="Album name : " + str(albumname))
                        labelaudio12.configure(text="Track number: " + str(tracknum))
                        labelaudio13.configure(text="Year : " + str(yearnum) + "\n")
                        
                        lowerleaf = db.read(4)
                        if lowerleaf != b'leaf':
                            print("No b'leaf' found, trying to process anyway")
                        else:
                            print("b'leaf' found 12")
                    else:
                        trackname = ""
                        artistname = ""
                        albumname = ""
                        tracknum = ""
                        yearnum = ""
                        print("Apparently no track metadata")

                        labelaudio9.configure(text="Track name: " + str(trackname))
                        labelaudio10.configure(text="Artist name: " + str(artistname))
                        labelaudio11.configure(text="Album name : " + str(albumname))
                        labelaudio12.configure(text="Track number: " + str(tracknum))
                        labelaudio13.configure(text="Year : " + str(yearnum) + "\n\n")
                        
                        lowerleaf = db.read(4)
                        if lowerleaf != b'leaf':
                            print("no b'leaf' found, trying to process anyway")
                        else:
                            print("b'leaf' found 15")
                
                except Exception as e:
                    print("something went wrong read0")
                    print(e)
                    trackname = ""
                    artistname = ""
                    albumname = ""
                    tracknum = ""
                    yearnum = ""
                    print("Apparently no track metadata")

                    labelaudio9.configure(text="Track name: " + str(trackname))
                    labelaudio10.configure(text="Artist name: " + str(artistname))
                    labelaudio11.configure(text="Album name : " + str(albumname))
                    labelaudio13.configure(text="Year : " + str(yearnum))
                    labelaudio12.configure(text="Track number: " + str(tracknum) + "\n\n")

                    
                    lowerleaf = db.read(4)
                    if lowerleaf != b'leaf':
                        print("no b'leaf' found, trying to process anyway")
                    else:
                        print("b'leaf' found 15")
                            
                filename0 = filename
                
                db.close()
    

        
        elif doer == 1:

            if currentplay == 1:
                print("currentplay1")
                return
            else:
                pass
            
            if filename == "":
                print("Please open a .herb file first.")
                return
            else:
                pass
            
            if buffervar.get() == 1:
                #WHAT THE FUCK THIS WORKS. HAVE TO SEND ARGS IN SEPARATELY. Still blocks GUI for some reason, while buffering if I recall correctly?
                #I think I added some Tkinter update functions in some of these functions to help unfreeze the GUI.
                if len(sys.argv) > 1:
                    threading.Thread(target=doherb2sc, args=(filename0, samplerate00, bitdepth00, numchan00, headsize00,)).start()
                else:
                    threading.Thread(target=doherb2, args=(filename0, samplerate00, bitdepth00, numchan00, headsize00,)).start()
                    
                #m1.start()
                
                #Works but blocks the sup print AND the GUI.
                ##doherb2(filename0, samplerate00, bitdepth00, numchan00, headsize00)
                
                #This prints right away so why is the GUI still freezing?
                
                #Doesn't affect anything.
                #m1.join()
                
                #This doens't do anything here.
                #root.update_idletasks()
                
                #Works fine but still freezes GUI for a few moments. Doesn't work with threading.
                ##asyncio.run(doherb2(filename0, samplerate00, bitdepth00, numchan00, headsize00))
                
                #Doesnt unblock GUI. May cause infinity windows in Windows
                #m1 = mp.Process(target=doherb2(filename0, samplerate00, bitdepth00, numchan00,))
                #m1.start()
            
            else:
                #asyncio.run(doherbstream(filename0, samplerate00, bitdepth00, numchan00, headsize00))
                
                #Using Threading doesn't seem to make a difference in Linux. Live playing still works fine.
                ##threading.Thread(target=doherbstream, args=(filename0, samplerate00, bitdepth00, numchan00, headsize00,)).start()

                if len(sys.argv) > 1:
                    doherbstreamsc(filename0, samplerate00, bitdepth00, numchan00, headsize00)
                    #threading.Thread(target=doherbstreamsc, args=(filename0, samplerate00, bitdepth00, numchan00, headsize00,)).start()
                else:
                    dostream1(filename0, samplerate00, bitdepth00, numchan00, headsize00)
                    #threading.Thread(target=dostream1, args=(filename0, samplerate00, bitdepth00, numchan00, headsize00,)).start()
            
            #Keeping for reference
            #doherb2(filename0, samplerate00, bitdepth00, numchan00)
            #root.update()
            #root.update_idletasks()
            
            #m1.join()
                    
    except Exception as e:
        print("Something went wrong read1")
        print(e)
          
    return

def dostream1(filename, samplerate, bits1, numchan, headsize0):
    
    global stopper
    global currentplay
    global streamer
    global soundcardchanger  
    global exclusivevar2
    global devicechoice
    global endyness
    #global pauser
    global volumevar
    
    if devicechoice == False:
        devicechoice1 = sd.default.device[0]
    else:
        devicechoice1 = devicechoice
        
    if int(sd.query_devices()[devicechoice1]['max_output_channels']) < int(numchan):
        print("Youre playing a file with more channels than your current audio device supports.")
        print("Recommend to change your audio device or the program might break.")
        mb.showinfo(title="Alert", icon='info', message="Youre playing a file with more channels than your current audio device supports.\nRecommend to change your audio device or the program might break.")
    else:
        pass
    
    if currentplay == 1:
        return
    else:
        currentplay = 1
    
    streamer = 1
    stopper = 0
    
    event = threading.Event()
    
    sd.default.samplerate = samplerate
    
    #Doesn't work. Read only. default.device takes precedent. All devices and their APIs returned with query.
    #sd.default.hostapi = hostapi
    
    #sd.default.hostapi = sd.query_hostapis()[0]
    #or
    #sd.default.hostapi = 0
    
    #Randoml exclusive stuff that doesn't seem to work.
    ##if exclusivevar2 == 1:
        ##wasapiexclusive = sd.WasapiSettings(exclusive=True)
        ##sd.default.extra_settings = wasapiexclusive
    ##else:
        ##pass
    
    bitdepthb = int(bits1 / 8)
    
    bitsdict = {
        "24" : 16777214+2,
        "16" : 65534+2,
        "8" : 255+2
        }
    
    max24 = bitsdict[str(bits1)]/2

    print("max24: " + str(max24))
    
    try:
        buttonplay.configure(text="Pause playback", command=lambda: pausetime(1))
        
        bitstream = blockvariable.get()
        print("bitstream " + str(bitstream))
        
        with open(filename, 'rb') as hwave:
        
            #FOR SOME REASON THIS WAY WORKS PROPERLY, BUT USING THE PRECREATED VARIABLE DOESNT (TOO CHOPPY). WTF
        
            #Skip the header
            #Player blocksize must be bigger than number of frames I buffer using for loops each go around. What?
            for i in range(0, headsize0):
                
                hwave.read(1)
            
            print("numchan: " + str(numchan))
            #print(type(numchan))
            
            for ii in range(0, 1):             
                #For numpy .T version
                if numchan == 2:
                    templist = [[],[]]
                elif numchan == 4:
                    templist = [[],[],[],[]]
                elif numchan == 6:
                    templist = [[],[],[],[],[],[]]
                
                for iii in range(0, bitstream):
                    #Read each sample, for each channel, for each stereo track
                    h1 = hwave.read(bitdepthb)
                    h2 = hwave.read(bitdepthb)
                    if not h1 or not h2:
                        print("Breaking, no more data")
                        buttonplay.configure(text="Play .herb file", command=lambda: pausetime(0))
                        currentplay = 0
                        playlabel.configure(text="   Stopped")
                        return
                    
                    if numchan == 4 or numchan == 6:
                        #print("4")
                        h3 = hwave.read(bitdepthb)
                        h4 = hwave.read(bitdepthb)
                        if not h3 or not h4:
                            print("Breaking, no more data")
                            buttonplay.configure(text="Play .herb file", command=lambda: pausetime(0))
                            currentplay = 0
                            playlabel.configure(text="   Stopped")
                            return
                    else:
                        pass
                    
                    if numchan == 6:
                        #print("69 baby")
                        h5 = hwave.read(bitdepthb)
                        h6 = hwave.read(bitdepthb)
                        if not h5 or not h6:
                            print("Breaking, no more data")
                            buttonplay.configure(text="Play .herb file", command=lambda: pausetime(0))
                            currentplay = 0
                            playlabel.configure(text="   Stopped")
                            return
                    else:
                        pass
                
                    #Old code for reference
                    #wstruct = struct.unpack("<h", h1)
                    #numpy.append(templist, converted1, axis=1)
                    
                    #print("appending")
                    
                    #Just for reference code. Not what I wanted though.
                    #np.append(temp00,(int.from_bytes(h1, endyness, signed=True) / max24))

                    templist[0].append(int.from_bytes(h1, endyness, signed=True) / max24)
                    templist[1].append(int.from_bytes(h2, endyness, signed=True) / max24)
                    
                    if numchan == 4 or numchan == 6:
                        templist[2].append(int.from_bytes(h3, endyness, signed=True) / max24)
                        templist[3].append(int.from_bytes(h4, endyness, signed=True) / max24)
                    else:
                        pass
                    
                    if numchan == 6:
                        templist[4].append(int.from_bytes(h5, endyness, signed=True) / max24)
                        templist[5].append(int.from_bytes(h6, endyness, signed=True) / max24)
                    else:
                        pass
                
                #print(temp1 time)
                temp1 = np.array(templist, dtype=float).T
                #print("q time")
                q.put_nowait(temp1)

                if devicechoice != False:
                    dd = devicechoice
                else:
                    dd = sd.default.device[0]
                
                playlabel.configure(text="   Playing")
                
                #14, 4
                #Only use blocksize 128 for now or everything breaks
                stream1 = sd.OutputStream(samplerate=samplerate, device=dd, blocksize=bitstream, channels=numchan, callback=doherbstream00, finished_callback=event.set)
                
                with stream1:
                    while len(temp1):
                            
                        if stopper == 1:
                            print("stopping")
                            return
                        
                        #For numpy .T version
                        if numchan == 2:
                            templist = [[],[]]
                        elif numchan == 4:
                            templist = [[],[],[],[]]
                        elif numchan == 6:
                            templist = [[],[],[],[],[],[]]
                        
                        for iaia in range(0, bitstream):
                            #Read each sample, for each channel, for each stereo track
                            h1 = hwave.read(bitdepthb)
                            h2 = hwave.read(bitdepthb)
                            
                            if numchan == 4 or numchan == 6:
                                h3 = hwave.read(bitdepthb)
                                h4 = hwave.read(bitdepthb)
                            else:
                                pass
                            
                            if numchan == 6:
                                h5 = hwave.read(bitdepthb)
                                h6 = hwave.read(bitdepthb)
                        
                            else:
                                pass
                        
                            if not h1 or not h2:
                                print("Breaking, no more data")
                                buttonplay.configure(text="Play .herb file", command=lambda: pausetime(0))
                                currentplay = 0
                                playlabel.configure(text="   Stopped")
                                return

                            #wstruct = struct.unpack("<h", h1)
                            
                            #Converts to int and scales to +1 and -1
                            ##converted1 = int.from_bytes(h1, 'little', signed=True) / max24
                            ##converted2 = int.from_bytes(h2, 'little', signed=True) / max24
                            ##converted3 = int.from_bytes(h3, 'little', signed=True) / max24
                            ##converted4 = int.from_bytes(h4, 'little', signed=True) / max24
                            
                            #When not using .T
                            #templist.append([converted1, converted2])
                            #templist2.append([converted3, converted4])

                            #For when using the numpy array .T command.
                            ##templist[0].append(converted1)
                            ##templist[1].append(converted2)
                            ##templist[2].append(converted3)
                            ##templist[3].append(converted4)
                            
                            #numpy.append(templist, converted1, axis=1)
                            
                            templist[0].append((int.from_bytes(h1, endyness, signed=True) / max24) * volumevar) 
                            templist[1].append((int.from_bytes(h2, endyness, signed=True) / max24) * volumevar)
                            
                            if numchan == 4 or numchan == 6:
                                #print("a")
                                templist[2].append((int.from_bytes(h3, endyness, signed=True) / max24) * volumevar)
                                templist[3].append((int.from_bytes(h4, endyness, signed=True) / max24) * volumevar)
                            else:
                                pass
                            
                            if numchan == 6:
                                #print("b")
                                templist[4].append((int.from_bytes(h5, endyness, signed=True) / max24) * volumevar)
                                templist[5].append((int.from_bytes(h6, endyness, signed=True) / max24) * volumevar)
                            else:
                                pass
                    
                        temp1 = np.array(templist).T
                        #print("sup1")
                        q.put(temp1)
                        #print("sup2")
                    event.wait()
                    
    except Exception as e:
        print("Something went wrong.stream1")
        print(e)
        mb.showinfo(title="Error", icon='info', message="Something went wrong.")
        return
    #print("smang")
                
    return

def doherbstream00(outdata, frames, time, status):

    global pauser
    #root.update()
    #root.update_idletasks()

    #print("00")
    
    if status.output_underflow:
        print("Output underflow, increase blocksize?")
        #raise sd.CallbackAbort
    else:
        pass
    
    #assert not status
    
    try:
        data1 = q.get_nowait()
    except queue.Empty as e:
        print("Queue empty, ending")
        raise sd.CallbackAbort from e
    
    if len(data1) > len(outdata):
        outdata[:len(data1)] = data1
        outdata[len(data1):].fill(0)
        raise sd.CallbackStop
    elif pauser == True:
        outdata[:].fill(0)
    else:
        outdata[:] = data1

    #print("001")
        

def doherb2(filename, samplerate, bits1, numchan, headsize0):

    global stopper
    global channelset
    global channelset3
    global channelset1
    global currentplay
    global asiovar
    global chanmapper2
    global streamer
    global soundcardchanger
    global exclusivevar2
    global devicechoice
    global endyness
    global volumevar
    
    streamer = 2
    
    if devicechoice == False:
        devicechoice1 = sd.default.device[0]
    else:
        devicechoice1 = devicechoice
        
    if int(sd.query_devices()[devicechoice1]['max_output_channels']) < int(numchan):
        print("Youre playing a file with more channels than your current audio device supports.")
        print("Recommend to change your audio device or the program might break.")
        mb.showinfo(title="Alert", icon='info', message="Youre playing a file with more channels than your current audio device supports.\nRecommend to change your audio device or the program might break.")
    else:
        pass
    
    #root.update()
    #root.update_idletasks()
    
    if currentplay == 1:
        return
    else:
        pass
    
    currentplay = 1

    #Doesn't work. Read only. default.device takes precedent. All devices and their APIs returned with query.
    #sd.default.hostapi = hostapi
    
    if exclusivevar2 == 1:
        wasapiexclusive = sd.WasapiSettings(exclusive=True)
        sd.default.extra_settings = wasapiexclusive
    else:
        pass
    
    playlabel.configure(text="   Buffering")
    
    bitdepthb = int(bits1 / 8)
    
    bitsdict = {
        "24" : 16777214+2,
        "16" : 65534+2,
        "8" : 255+2
        }
    
    max24 = bitsdict[str(bits1)]/2
    print(max24)
    
    try:
        #Using a variable makes it a lot slower. Use "with" as seen below.
        #herbwave = open('wavetest.wav', 'rb')
        
        size1 = os.path.getsize(filename)
        
        if numchan == 2:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 2))       
        elif numchan == 4:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 4))
        elif numchan == 6:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 6))
            
        if sys.platform == "linux":
            #Linux
            #channelmap = ["left", "right", "center", "lfe"]
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                #For 7.1 motherboard card
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")

        elif sys.platform == "win32":
            #Win
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")
        
        else:
            #Mac?
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")
        
        
        sd.default.samplerate = samplerate
        #sd.default.device = 4
        if devicechoice != False:
            sd.default.device = devicechoice
        else:
            sd.default.device = sd.default.device[0]

        channelmapsd = []
        
        for bb in range(0,len(channelmap)):
            channelmapsd.append(channelmap[bb] + 1)
        print(channelmapsd)
        
        with open(filename, 'rb') as hwave:
            
            #FOR SOME REASON THIS WAY WORKS PROPERLY, BUT USING THE PRECREATED VARIABLE DOESNT (TOO CHOPPY). WTF. SEE doherbstream()
            #, default_speaker.player(samplerate=samplerate, blocksize=64, channels=[2,3]) as sp2:
        
            #Skip the header
            for i in range(0, headsize0):
                
                hwave.read(1)

            #For numpy .T version
            if numchan == 2:
                templist = [[],[]]
            elif numchan == 4:
                templist = [[],[],[],[]]
            elif numchan == 6:
                templist = [[], [], [], [],[],[]]
        
            tt = [[0,0], [0,0], [0,0], [0,0]]
            tt1 = np.array(tt).T
            #ds.play(tt1)
            
            for aa in range(0, blocksize):

                for ii in range(0, 4096):
                            
                    #Read each sample, for each channel, for each stereo track
                    h1 = hwave.read(bitdepthb)
                    h2 = hwave.read(bitdepthb)
                    
                    if numchan == 4 or numchan == 6:
                        h3 = hwave.read(bitdepthb)
                        h4 = hwave.read(bitdepthb)
                    else:
                        pass
                    
                    if numchan == 6:
                        h5 = hwave.read(bitdepthb)
                        h6 = hwave.read(bitdepthb)
                    else:
                        pass
                    
                    if not h1 or not h2:
                        print("Breaking, no more data")
                        print("Playing")
                        
                        playlabel.configure(text="   Playing")
                        
                        temp1 = np.array(templist).T
                        
                        if sys.platform == "win32" or sys.platform == "osx":
                            #sd.play(temp1, extra_settings=specialout)
                            if chanmapper2 == True:
                                print("with mapping")
                                sd.play(temp1, mapping=channelmapsd)
                            else:
                                print("no mapping")
                                sd.play(temp1)
                            #Should I bring this back or remove it?
                            sd.wait()
                        else:
                            #default_speaker.play(temp1, samplerate=samplerate, channels=channelmap)
                            #Doesnt work in quadraphonic mode, no mapping allowed for Linux?
                            if chanmapper2 == True:
                                print("with mapping")
                                sd.play(temp1, mapping=channelmapsd)
                            else:
                                print("no mapping")
                                sd.play(temp1)
                            #Should I bring this back or remove it?
                            sd.wait()
                                
                        currentplay = 0
                        playlabel.configure(text="   Stopped")
                        print("Stopped")
                        return

                    #wstruct = struct.unpack("<h", h1)
                        
                    #Converts to int and scales to +1 and -1
                    ##converted1 = int.from_bytes(h1, 'little', signed=True) / max24
                    ##converted2 = int.from_bytes(h2, 'little', signed=True) / max24
                    ##converted3 = int.from_bytes(h3, 'little', signed=True) / max24
                    ##converted4 = int.from_bytes(h4, 'little', signed=True) / max24
                        
                    #When not using .T
                    #templist.append([converted1, converted2])
                    #templist2.append([converted3, converted4])

                    #For when using the numpy array .T command.
                    ##templist[0].append(converted1)
                    ##templist[1].append(converted2)
                    ##templist[2].append(converted3)
                    ##templist[3].append(converted4)
                        
                    #numpy.append(templist, converted1, axis=1)
                        
                    templist[0].append((int.from_bytes(h1, endyness, signed=True) / max24) * volumevar)
                    templist[1].append((int.from_bytes(h2, endyness, signed=True) / max24) * volumevar)
                    
                    if numchan == 4 or numchan == 6:
                        templist[2].append((int.from_bytes(h3, endyness, signed=True) / max24) * volumevar)
                        templist[3].append((int.from_bytes(h4, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                    
                    if numchan == 6:
                        templist[4].append((int.from_bytes(h5, endyness, signed=True) / max24) * volumevar)
                        templist[5].append((int.from_bytes(h6, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                    
                    #This allows root GUI to keep working, but song never buffers.
                    #root.update_idletasks()
                    
                #WHAT THE FUUUUUCK. HOW DOES THIS SOLVE THE FUCKING PROBLEM? WHAT THE FUCK.
                #This makes it so the GUI doesn't freeze while pre-buffering the song.
                #ds.play(tt1)
                updateherb2()
                
            #See notes above for when .T will be useful here. Decided to go against it, since no issues occuring yet.
            #Yet I used it.
            temp1 = np.array(templist).T
            
            print("Playing")
            
            #This is a bad idea in Windows. Seems to open up a new window or something.
            #mp2 = mp.Process(target=default_speaker.play(temp1, samplerate=samplerate00, channels=channelmap))
            #mp2.start()
            
            #This works in Windows and Linux.
            #mp3 = threading.Thread(target=default_speaker.play(temp1, samplerate=samplerate, channels=channelmap))
            #mp3.start()
            
            playlabel.configure(text="   Playing")
            
            if sys.platform == "win32":
                #sd.play(temp1, extra_settings=specialout)
                if chanmapper2 == True:
                    print("with mapping")
                    #Cant have channels=num arg passed, it causes an error.
                    sd.play(temp1, mapping=channelmapsd)
                else:
                    print("no mapping")
                    sd.play(temp1)
                sd.wait()
            else:
                #default_speaker.play(temp1, samplerate=samplerate, channels=channelmap)
                #Doesnt work in quadraphonic mode, no mapping allowed for Linux?

                if chanmapper2 == True:
                    print("with mapping")
                    sd.play(temp1, mapping=channelmapsd)
                else:
                    print("no mapping")
                    sd.play(temp1)
                sd.wait()

        playlabel.configure(text="   Stopped")
        print("Playback finished")
            
        hwave.close()
        
        currentplay = 0
    
    except Exception as e:
        print("Something went wrong.")
        print(e)
        mb.showinfo(title="Error", icon='info', message="Something went wrong.")
    
    return

def doherbstreamsc(filename, samplerate, bits1, numchan, headsize0):

    global stopper
    global channelset
    global channelset3
    global channelset1
    global currentplay
    global buffersettingval
    global pauser
    global endyness
    global volumevar
    
    #root.update()
    #root.update_idletasks()

    stopper = 0
    
    if currentplay == 1:
        return
    else:
        pass
    
    currentplay = 1
    
    bitdepthb = int(bits1 / 8)
    
    bitsdict = {
        "24" : 16777214+2,
        "16" : 65534+2,
        "8" : 255+2
        }
    
    max24 = bitsdict[str(bits1)]/2
    print(max24)
    
    try:
        buttonplay.configure(text="Pause playback", command=lambda: pausetime(1))
        
        #Using a variable makes it a lot slower. Use "with" as seen below.
        #herbwave = open('wavetest.wav', 'rb')
        
        if devicechoice != False:
            default_speaker = sc.all_speakers()[devicechoice]
        else:
            default_speaker = sc.default_speaker()
            
        #print(sc.channel_name_map())
        
        #spp = default_speaker.player(samplerate=samplerate, blocksize=64, channels=channelset)
        
        size1 = os.path.getsize(filename)
        
        if numchan == 2:
            sizeadjusted = math.ceil((size1 - headsize0) / (bitdepthb * 2)) 
        elif numchan == 4:
            sizeadjusted = math.ceil((size1 - headsize0) / (bitdepthb * 4))
        elif numchan == 6:
            sizeadjusted = math.ceil((size1 - headsize0) / (bitdepthb * 6))
            
        if sys.platform == "linux":
            #Linux
            #channelmap = ["left", "right", "center", "lfe"]
            if numchan == 2:
                #For 2.0 channels
                channelmap = channelset1
                blocksize2 = 8192
                buffsize1 = 32768
                blocksize3 = 4096
                #65536
            elif numchan == 4:
                #For 4.0 channels
                channelmap = channelset
                blocksize2 = 8192
                buffsize1 = 65536
                blocksize3 = 16384
                #65536
            elif numchan == 6:
                #For 6.0 channels
                channelmap = channelset3
                blocksize2 = 12000
                buffsize1 = 93312
                blocksize3 = 8192
                #93312
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Streaming playback")

        elif sys.platform == "win32":
            #Win
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 8192
                buffsize1 = 32768
                blocksize3 = 4096
                #65536
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 8192
                buffsize1 = 65536
                blocksize3 = 4096
                #65536
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 12000
                buffsize1 = 93312
                blocksize3 = 8192
                #93312
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Streaming playback")
        
        else:
            #Mac?
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 512
                buffsize1 = 32768
                blocksize3 = 256
                #65536
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 512
                buffsize1 = 65536
                blocksize3 = 256
                #65536
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 512
                buffsize1 = 93312
                blocksize3 = 256
                #93312
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Streaming playback")
        
        #print(blocksize2)
        #print(buffsize1)
        
        playlabel.configure(text="   Playing")
        
        print(channelmap)
        
        with open(filename, 'rb') as hwave, default_speaker.player(samplerate=samplerate, blocksize=blocksize2, channels=channelmap) as ds:
            
            #FOR SOME REASON THIS WAY WORKS PROPERLY, BUT USING THE PRECREATED VARIABLE DOESNT (TOO CHOPPY). WTF
        
            #Skip the header
            #Player blocksize must be bigger than number of frames I buffer using for loops each go around. What?
            for i in range(0, headsize0):
                
                hwave.read(1)
            
            print(numchan)
            for ii in range(0, sizeadjusted):
                
                while pauser == True:
                    time.sleep(0.25)
                    
                if stopper == 1:
                    playlabel.configure(text="   Stopped")
                    currentplay = 0
                    return
                else:
                    pass
                
                #For numpy .T version
                if numchan == 2:
                    templist = [[],[]]
                elif numchan == 4:
                    templist = [[],[],[],[]]
                elif numchan == 6:
                    templist = [[],[],[],[],[],[]]
                
                for iii in range(0, blocksize3):
                    #Read each sample, for each channel, for each stereo track
                    h1 = hwave.read(bitdepthb)
                    h2 = hwave.read(bitdepthb)
                    
                    if numchan == 4 or numchan == 6:
                        #print("yy1")
                        h3 = hwave.read(bitdepthb)
                        h4 = hwave.read(bitdepthb)
                    else:
                        pass
                    
                    if numchan == 6:
                        #print("mangy1")
                        h5 = hwave.read(bitdepthb)
                        h6 = hwave.read(bitdepthb)
                    else:
                        pass
                
                    if not h1 or not h2:
                        print("Breaking, no more data")
                        buttonplay.configure(text="Play .herb file", command=lambda: pausetime(0))
                        currentplay = 0
                        playlabel.configure(text="   Stopped")
                        return

                    #wstruct = struct.unpack("<h", h1)
                    
                    #Converts to int and scales to +1 and -1
                    ##converted1 = int.from_bytes(h1, 'little', signed=True) / max24
                    ##converted2 = int.from_bytes(h2, 'little', signed=True) / max24
                    ##converted3 = int.from_bytes(h3, 'little', signed=True) / max24
                    ##converted4 = int.from_bytes(h4, 'little', signed=True) / max24
                    
                    #When not using .T
                    #templist.append([converted1, converted2])
                    #templist2.append([converted3, converted4])

                    #For when using the numpy array .T command.
                    ##templist[0].append(converted1)
                    ##templist[1].append(converted2)
                    ##templist[2].append(converted3)
                    ##templist[3].append(converted4)
                    
                    #numpy.append(templist, converted1, axis=1)
                    
                    templist[0].append((int.from_bytes(h1, endyness, signed=True) / max24) * volumevar)
                    templist[1].append((int.from_bytes(h2, endyness, signed=True) / max24) * volumevar)
                    
                    if numchan == 4 or numchan == 6:
                        templist[2].append((int.from_bytes(h3, endyness, signed=True) / max24) * volumevar)
                        templist[3].append((int.from_bytes(h4, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                    
                    if numchan == 6:
                        templist[4].append((int.from_bytes(h5, endyness, signed=True) / max24) * volumevar)
                        templist[5].append((int.from_bytes(h6, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                    
                #See notes above for when .T will be useful here. Decided to go against it, since no issues occuring yet.
                #Yet I used it once again. I like how I set up the arrays leading up to .T so I have no plans to change it.
                temp1 = np.array(templist).T

                #This works
                #ds.play(temp1)
                
                #This works in Linux. Still choppy in Windows. Want to test asyncio
                #threading.Thread(target=ds.play(temp1)).start()
                #Works fine in Linux too
                ds.play(temp1)
                currentplay = 0
                #Throws error
                #await ds.play(temp1)
                #asyncio.run(ds.play(temp1))
                #task1 = asyncio.create_task(ds.play(temp1))

                #Doesn't work. Causes problems. If I run it in a separate thread it works, but it all plays at once.
                #threading.Thread(target=ds.play, args=(temp1,))
                
                #This causes infinity windows to pop up in win32. Disabling for now.
                ##mp3 = mp.Process(target=ds.play, args=(temp1,))
                ##mp3.start()
                                
        print("Playback finished")
        playlabel.configure(text="   Stopped")
        
        #Close this above, too?
        hwave.close()
        
        currentplay = 0
    
    except Exception as e:
        print("Something went wrong.")
        print(e)
        mb.showinfo(title="Error", icon='info', message="Something went wrong.")
        
    return

def doherb2sc(filename, samplerate, bits1, numchan, headsize0):

    global stopper
    global channelset
    global channelset3
    global channelset1
    global currentplay
    global devicechoice
    global endyness
    global volumevar
    
    #root.update()
    #root.update_idletasks()
    
    if currentplay == 1:
        return
    else:
        pass
    
    currentplay = 1

    stopper = 0
    
    playlabel.configure(text="   Buffering")
    
    bitdepthb = int(bits1 / 8)
    
    bitsdict = {
        "24" : 16777214+2,
        "16" : 65534+2,
        "8" : 255+2
        }
    
    max24 = bitsdict[str(bits1)]/2
    print(max24)
    
    try:
        #Using a variable makes it a lot slower. Use "with" as seen below.
        #herbwave = open('wavetest.wav', 'rb')
        
        if devicechoice != False:
            default_speaker = sc.all_speakers()[devicechoice]
        else:
            default_speaker = sc.default_speaker()
        #print(sc.channel_name_map())
        
        #spp = default_speaker.player(samplerate=samplerate, blocksize=64, channels=channelset)
        
        size1 = os.path.getsize(filename)
        
        if numchan == 2:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 2))       
        elif numchan == 4:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 4))
        elif numchan == 6:
            sizeadjusted = math.ceil((size1 - 14) / (bitdepthb * 6))
            
        if sys.platform == "linux":
            #Linux
            #channelmap = ["left", "right", "center", "lfe"]
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                #For 7.1 motherboard card
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")

        elif sys.platform == "win32":
            #Win
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")
        
        else:
            #Mac?
            if numchan == 2:
                channelmap = channelset1
                blocksize2 = 128
            elif numchan == 4:
                channelmap = channelset
                blocksize2 = 128
            elif numchan == 6:
                channelmap = channelset3
                blocksize2 = 216
            blocksize = sizeadjusted + 6
            bsize1 = 1
            print("System platform: " + str(sys.platform))
            print("Buffering entire song before playback")
            
        with open(filename, 'rb') as hwave:
            
            #FOR SOME REASON THIS WAY WORKS PROPERLY, BUT USING THE PRECREATED VARIABLE DOESNT (TOO CHOPPY). WTF. SEE doherbstream()
            #, default_speaker.player(samplerate=samplerate, blocksize=64, channels=[2,3]) as sp2:
        
            #Skip the header
            for i in range(0, headsize0):
                
                hwave.read(1)

            #For numpy .T version
            if numchan == 2:
                templist = [[],[]]
            elif numchan == 4:
                templist = [[],[],[],[]]
            elif numchan == 6:
                templist = [[], [], [], [],[],[]]
        
            tt = [[0,0], [0,0], [0,0], [0,0]]
            tt1 = np.array(tt).T
            #ds.play(tt1)
            
            for aa in range(0, blocksize):

                for ii in range(0, 4096):
                            
                    #Read each sample, for each channel, for each stereo track
                    h1 = hwave.read(bitdepthb)
                    h2 = hwave.read(bitdepthb)
                    
                    if numchan == 4 or numchan == 6:
                        h3 = hwave.read(bitdepthb)
                        h4 = hwave.read(bitdepthb)
                    else:
                        pass
                    
                    if numchan == 6:
                        h5 = hwave.read(bitdepthb)
                        h6 = hwave.read(bitdepthb)
                    else:
                        pass
                    
                    if not h1 or not h2:
                        print("Breaking, no more data")
                        print("Playing")
                        playlabel.configure(text="   Playing")
                        temp1 = np.array(templist).T
                        default_speaker.play(temp1, samplerate=samplerate, channels=channelmap)
                        currentplay = 0
                        playlabel.configure(text="   Stopped")
                        print("Stopped")
                        return

                    #wstruct = struct.unpack("<h", h1)
                        
                    #Converts to int and scales to +1 and -1
                    ##converted1 = int.from_bytes(h1, 'little', signed=True) / max24
                    ##converted2 = int.from_bytes(h2, 'little', signed=True) / max24
                    ##converted3 = int.from_bytes(h3, 'little', signed=True) / max24
                    ##converted4 = int.from_bytes(h4, 'little', signed=True) / max24
                        
                    #When not using .T
                    #templist.append([converted1, converted2])
                    #templist2.append([converted3, converted4])

                    #For when using the numpy array .T command.
                    ##templist[0].append(converted1)
                    ##templist[1].append(converted2)
                    ##templist[2].append(converted3)
                    ##templist[3].append(converted4)
                        
                    #numpy.append(templist, converted1, axis=1)
                        
                    templist[0].append((int.from_bytes(h1, endyness, signed=True) / max24) * volumevar)
                    templist[1].append((int.from_bytes(h2, endyness, signed=True) / max24) * volumevar)
                    
                    if numchan == 4 or numchan == 6:
                        templist[2].append((int.from_bytes(h3, endyness, signed=True) / max24) * volumevar)
                        templist[3].append((int.from_bytes(h4, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                    
                    if numchan == 6:
                        templist[4].append((int.from_bytes(h5, endyness, signed=True) / max24) * volumevar)
                        templist[5].append((int.from_bytes(h6, endyness, signed=True) / max24) * volumevar)
                    else:
                        pass
                
                #This allows root GUI to keep working, but song never buffers.
                #root.update_idletasks()
                updateherb2()
                                
                #WHAT THE FUUUUUCK. HOW DOES THIS SOLVE THE FUCKING PROBLEM? WHAT THE FUCK.
                #This makes it so the GUI doesn't freeze while pre-buffering the song.
                #ds.play(tt1)
                
            #See notes above for when .T will be useful here. Decided to go against it, since no issues occuring yet.
            temp1 = np.array(templist).T
                
            print("Playing")
            #This is a bad idea in Windows. Seems to open up a new window or something.
            #mp2 = mp.Process(target=default_speaker.play(temp1, samplerate=samplerate00, channels=channelmap))
            #mp2.start()
            
            #This works in Windows and Linux.
            #mp3 = threading.Thread(target=default_speaker.play(temp1, samplerate=samplerate, channels=channelmap))
            #mp3.start()
            
            playlabel.configure(text="   Playing")
            #This seems to work too, without issue, at least in Linux.
            default_speaker.play(temp1, samplerate=samplerate, channels=channelmap)
            
        playlabel.configure(text="   Stopped")
        print("Playback finished")
            
        hwave.close()
        
        currentplay = 0
    
    except:
        print("Something went wrong.")
        mb.showinfo(title="Error", icon='info', message="Something went wrong.")
    
    return

def updateherb2():
    
    #This function allows the GUI to unfreeze while still pre-buffering an entire song.
    #a = 1
    
    root.update_idletasks()
    
    return True

def pausetime(num):

    global pauser
    
    if num == 1:
        pauser = True
        playlabel.configure(text="   Paused")
        buttonplay.configure(text="Resume playback", command=lambda: pausetime(0))
    if num == 0:
        pauser = False
        playlabel.configure(text="   Playing")
        buttonplay.configure(text="Pause playback", command=lambda: pausetime(1))
    return

def testaudio(num, num2):

    global devicechoice
    global channelset
    global channelset3
    global channelset1
    global channelsetsd
    global channelset3sd
    global channelset1sd
    global chanmapper2
    
    print(str(chanmapper2) + "sup")
    print(channelset)
    print(channelsetsd)
    channelsd = []
    channelsc = []
    
    if len(sys.argv) == 1:
        packnum = 1
    else:
        packnum = 2
            
    if num2 == 0:
        print("channel test")
            
        try:
            if num == 0:
                if num == 0:
                    buttontest.configure(text="Stop audio test", command=lambda: threading.Thread(target=testaudio, args=(1,0,)).start())
                    if len(sys.argv) > 1:
                        mb.showinfo(title="Info", icon='info', message="You should first hear high tone out of " + str(channelset[0]+1) + "-" + str(channelset[1]+1) + " ONLY (stereo pair #1) for about 4 seconds, and then a low tone out of " + str(channelset[2]+1) + "-" + str(channelset[3]+1) + " ONLY (stereo pair #2) for about 4 seconds.\n\nIf you don't hear it properly, activate custom channel\nmapping and modify the 4.0 settings; or uncheck Soundcard package mode. Make sure to hit 'Save settings' after making a change.\n\nPress OK to continue")
                    else:
                        mb.showinfo(title="Info", icon='info', message="You should first hear high tone out of " + str(channelsetsd[0]) + "-" + str(channelsetsd[1]) + " ONLY (stereo pair #1) for about 4 seconds, and then a low tone out of " + str(channelsetsd[2]) + "-" + str(channelsetsd[3]) + " ONLY (stereo pair #2) for about 4 seconds.\n\nIf you don't hear it properly, activate custom channel\nmapping and modify the 4.0 settings; or check Soundcard package mode. Make sure to hit 'Save settings' after making a change.\n\nPress OK to continue")
                
                #buttontest.configure(text="Stop audio test", command=lambda: testaudio(1))
                time.sleep(1)
                t0 = [[],[],[],[]]
                samplerate = 44100
                t = np.linspace(0, 8, samplerate*8)
                y = np.sin(1000 * (2 * np.pi) * t) * 0.5
                y2 = np.sin(120 * (2 * np.pi) * t) * 0.5
                for i in range(0, int(len(y)/2)):
                    t0[0].append(y[i])
                    t0[1].append(y[i])
                
                for ia in range(0, int(len(y)/2)):
                    t0[0].append(0)
                    t0[1].append(0)
                    
                for ii in range(0, int(len(y2)/2)):
                    t0[2].append(0)
                    t0[3].append(0)
                    
                for iia in range(0, int(len(y2)/2)):
                    t0[2].append(y2[iia])
                    t0[3].append(y2[iia])
                
                
                temp01 = np.array(t0).T
                print("starting test audio")
                if packnum == 1:
                    sd.default.samplerate = samplerate
                    if devicechoice != False:
                        print("custom device " + str(devicechoice))
                        #print(sd.query_devices()[devicechoice])
                        sd.default.device = devicechoice
                    else:
                        print("no custom device")
                        sd.default.device = sd.default.device[0]
                    if chanmapper2 == True:
                        print(chanmapper2)
                        threading.Thread(target=sd.play(temp01, mapping=channelsetsd)).start()
                    else:
                        print(chanmapper2)
                        threading.Thread(target=sd.play(temp01)).start()
                    sd.wait()
                else:
                    if devicechoice != False:
                        default_speaker2 = sc.all_speakers()[devicechoice]
                    else:
                        default_speaker2 = sc.default_speaker()
                    threading.Thread(target=default_speaker2.play(temp01, samplerate=samplerate, channels=channelset)).start()
                    
                buttontest.configure(text="Test 4.0 audio", command=lambda: threading.Thread(target=testaudio, args=(0,0,)).start())
                print("Donezo with test audio")
            else:
                buttontest.configure(text="Test 4.0 audio", command=lambda: threading.Thread(target=testaudio, args=(0,0,)).start())
                if packnum == 1:
                    sd.stop()
                else:
                    pass
        except Exception as e:
            print("Something went wrong. Try a different audio device perhaps.")
            print(e)
            buttontest.configure(text="Test 4.0 audio", command=lambda: threading.Thread(target=testaudio, args=(0,0,)).start())
    
    #Test levels
    elif num2 == 1:
        try:
            if num == 0:
                buttontest2.configure(text="Stop audio test", command=lambda: threading.Thread(target=testaudio, args=(1,1,)).start())

                if len(sys.argv) > 1:
                    mb.showinfo(title="Info", icon='info', message="You should first hear high tone out of channel " + str(channelset[0]+1) + " only, followed by the tone out of channel " + str(channelset[1]+1) + " only; followed by channel " + str(channelset[2]+1) + " only, followed by channel " + str(channelset[3]+1) + " only. Make sure all the levels on your speaker pairs sound equal.\n\n If you are missing any channels, go to the Settings tab and adjust the custom channel mapping, or uncheck using the Soundcard package. Make sure to click Save settings.\n\nClick OK to continue.")
                else:
                    mb.showinfo(title="Info", icon='info', message="You should first hear high tone out of channel " + str(channelset[0]+1) + " only, followed by the tone out of channel " + str(channelset[1]+1) + " only; followed by channel " + str(channelset[2]+1) + " only, followed by channel " + str(channelset[3]+1) + " only. Make sure all the levels on your speaker pairs sound equal.\n\n If you are missing any channels, go to the Settings tab and adjust the custom channel mapping, or uncheck using the Soundcard package. Make sure to click Save settings.\n\nClick OK to continue.")
                
                #num2 = 2
                print("level test")
                
                time.sleep(1)
                t0 = [[],[],[],[]]
                samplerate = 44100
                t = np.linspace(0, 8, samplerate*8)
                y = np.sin(1000 * (2 * np.pi) * t) * 0.5
                y2 = np.sin(120 * (2 * np.pi) * t) * 0.5

                for i in range(0, 50100):
                    t0[0].append(y[i])
                    t0[1].append(0)
                    t0[2].append(0)
                    t0[3].append(0)
                                              
                
                for b in range(0, 3800):
                    t0[0].append(0)
                    t0[1].append(0)
                    t0[2].append(0)
                    t0[3].append(0)
                    
                for ii in range(0, 50100):
                    t0[0].append(0)
                    t0[1].append(y[ii])
                    t0[2].append(0)
                    t0[3].append(0)

                for bb in range(0, 3800):
                    t0[0].append(0)
                    t0[1].append(0)
                    t0[2].append(0)
                    t0[3].append(0)
                    
                for iii in range(0, 50100):
                    t0[0].append(0)
                    t0[1].append(0)
                    t0[2].append(y[iii])
                    t0[3].append(0)

                for bbb in range(0, 3800):
                    t0[0].append(0)
                    t0[1].append(0)
                    t0[2].append(0)
                    t0[3].append(0)
                    
                for iiii in range(0, 50100):
                    t0[0].append(0)
                    t0[1].append(0)
                    t0[2].append(0)
                    t0[3].append(y[iiii])
                                 
                temp01 = np.array(t0).T
                
                if packnum == 1:
                    sd.default.samplerate = samplerate
                    if devicechoice != False:
                        print("custom device " + str(devicechoice))
                        #print(sd.query_devices()[devicechoice])
                        sd.default.device = devicechoice
                    else:
                        print("no custom device")
                        sd.default.device = sd.default.device[0]
                    if chanmapper2 == True:
                        print(chanmapper2)
                        threading.Thread(target=sd.play(temp01, mapping=channelsetsd)).start()
                    else:
                        print(chanmapper2)
                        threading.Thread(target=sd.play(temp01)).start()
                    sd.wait()
                else:
                    if devicechoice != False:
                        default_speaker2 = sc.all_speakers()[devicechoice]
                    else:
                        default_speaker2 = sc.default_speaker()
                    threading.Thread(target=default_speaker2.play(temp01, samplerate=samplerate, channels=channelset)).start()
                
                buttontest2.configure(text="Test 4.0 Levels", command=lambda: threading.Thread(target=testaudio, args=(0,1,)).start())
         
            else:
                buttontest2.configure(text="Test 4.0 Levels", command=lambda: threading.Thread(target=testaudio, args=(0,1,)).start())
                if packnum == 1:
                    sd.stop()
                else:
                    pass
                
        except Exception as e:
            print("Something went wrong. Try a different audio device perhaps.")
            print(e)       
            
    return

def changedir():
    
    global customdir
    global cdircheck
    
    customdir = fd.askdirectory(title="Select directory", initialdir='.')
    
    labeldirbutton.configure(text="Custom .herb output directory: \n" + str(customdir) + "")
    
    cdircheck = True
    
    return

def channelchange(selection, selection3, selection1, customheader, bufferset):
    
    global channelset
    global channelset3
    global channelset1
    global channelsetsd
    global channelset3sd
    global channelset1sd
    global manualheader
    global buffersettingval
    global customdir
    global customdir1
    global chanmapper
    global chanmapper2
    global soundcardchanger
    global exclusivevar2
    global devicechoice
    
    #hostapi = int(hostapi1.get()[0]) - 1
    
    if exclusivevar.get() == 1:
        exclusivevar2 = 1
        print("Exclusive mode on for WASAPI.")
    else:
        exclusivevar2 = 0
        print("Exclusive mode off for WASAPI.")
        
    if chanmapper.get() == 1:
        chanmapper2 = True
        print("Custom channel mappings active")
    else:
        chanmapper2 = False
        print("Custom channel mappings inactive")
        
    buffersettingval = 0
    #buffersettingval = bufferset
    
    if buffersettingval == 0:
        print("Tracks will pre-buffer before playing. It takes more time but has no chance of choppiness.")
    else:
        print("Tracks will buffer live while playing. It plays almost right away but may chop depending on your computer's system or soundcard.")
    
    customheader = customheader.rstrip()
    
    if customheader == "":
        manualheader = 0
    else:
        try:
            manualheader = int(customheader)
            print(manualheader)
        except:
            manualheader = 0
            print("Problem with your manual wav file header size. Not setting manual header")

    
    channeldict = {
        "[1,2,3,4]" : [0,1,2,3],
        "[1,2,5,6]" : [0,1,4,5],
        "[1,2,7,8]" : [0,1,6,7],
        "[3,4,5,6]" : [2,3,4,5],
        "[3,4,7,8]" : [2,3,6,7]
        }

    channeldict3 = {
        "[1,2,3,4,5,6]" : [0,1,2,3,4,5],
        "[1,2,3,4,7,8]" : [0,1,2,3,6,7],
        "[1,2,5,6,7,8]" : [0,1,4,5,6,7],
        "[3,4,5,6,7,8]" : [2,3,4,5,6,7],
        "[5,6,7,8,9,10]" : [4,5,6,7,8,9]
        }
    
    channeldict1 = {
        "[1,2]" : [0,1],
        "[3,4]" : [2,3],
        "[5,6]" : [4,5],
        "[7,8]" : [6,7]
        }
 
    channelset = channeldict[selection]
    channelset3 = channeldict3[selection3]
    channelset1 = channeldict1[selection1]

    channeldictsd = {
        "[1,2,3,4]" : [1,2,3,4],
        "[1,2,5,6]" : [1,2,5,6],
        "[1,2,7,8]" : [1,2,7,8],
        "[3,4,5,6]" : [3,4,5,6],
        "[3,4,7,8]" : [3,4,7,8]
        }

    channeldict3sd = {
        "[1,2,3,4,5,6]" : [1,2,3,4,5,6],
        "[1,2,3,4,7,8]" : [1,2,3,4,7,8],
        "[1,2,5,6,7,8]" : [1,2,5,6,7,8],
        "[3,4,5,6,7,8]" : [3,4,5,6,7,8],
        "[5,6,7,8,9,10]" : [5,6,7,8,9,10]
        }
    
    channeldict1sd = {
        "[1,2]" : [1,2],
        "[3,4]" : [3,4],
        "[5,6]" : [5,6],
        "[7,8]" : [7,8]
        }
    
    channelsetsd = channeldictsd[selection]
    channelset3sd = channeldict3sd[selection3]
    channelset1sd = channeldict1sd[selection1]
 
    if customdir != "" or customdir != ():
        customdir1 = customdir
    else:
        pass
    
    print("Settings saved. Output channels set to:\n" + str(channelset1) + " for (2.0 channels)\n" + str(channelset) + " (for 4.0 channels)\n" + str(channelset3) + " (for 6.0 channels)\n" + "Custom .herb output path: \n" + str(customdir1))
    
    if manualheader == 0:
        pass
    else:
        print("Manual wav file header length for importation (creator tab): " + str(manualheader))
    
    print(soundcardvar.get())
    if soundcardvar.get() == 0 and len(sys.argv) == 1:
        print("Doing nothing for sound package. Still using Sounddevice.")
        pass
    elif soundcardvar.get() == 0 and len(sys.argv) > 1:
        print("restarting with sounddevice package")
        print(sys.executable)
        print(sys.argv)
        del sys.argv[1]
        #sys.argv.append("--soundcard")
        time.sleep(1.5)
        if "py" in sys.executable:
            #For Python version
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            #For compiled version. Works but not properly in Windows.
            os.execv(sys.executable, sys.argv)
            #This doesnt work properly. Sticking with OG version that breaks in Windows.
            #os.system(str(str(sys.executable) + " --soundcard"))
            #sys.exit()
    elif soundcardvar.get() == 1 and len(sys.argv) > 1:
        print("Doing nothing for sound package. Still using Soundcard.")
        pass
    else:
        print("restarting with soundcard package")
        print(sys.executable)
        print(sys.argv)
        sys.argv.append("--soundcard")
        time.sleep(1.5)
        if "py" in sys.executable:
            #For Python version
            os.execv(sys.executable, [sys.executable] + sys.argv)
            #This doesnt work yet
            #os.system(str(str(sys.executable) + " --soundcard"))
            sys.exit()
        else:
            #For compiled version. Works, but not properly in Windows.
            os.execv(sys.executable, sys.argv)
            #This doesnt work properly. Sticking with version that has Windows problems.
            #os.system(str(str(sys.executable) + " --soundcard"))
            #sys.exit()

    if devicechoice == False:
        print("Doing nothing with device")
    elif devicechoice != False and len(sys.argv) == 1:
        #sd
        sd.default.device = devicechoice
        print("Choosing" + str(devicechoice) + " as audio device")
    elif devicechoice != False and len(sys.argv) > 1:
        print("Choosing" + str(devicechoice) + " as audio device") 

    if len(sys.argv) > 1 and devicechoice == False:
        devicessc2 = "Sound card in use:\n" + str(sc.default_speaker())
        labelsoundcard.configure(text=devicessc2)
    elif len(sys.argv) > 1 and devicechoice != False:
        devicessc2 = "Sound card in use:\n" + str(sc.all_speakers()[devicechoice])
        labelsoundcard.configure(text=devicessc2)
    elif len(sys.argv) == 1 and devicechoice == False:
        devicessd = sd.default.device[0]
        ddd2 = "Sound card in use:\n" + sd.query_devices()[devicessd]['name'] + ", Max output channels: " + str(sd.query_devices()[devicessd]['max_output_channels'])
        labelsoundcard.configure(text=ddd2)
    elif len(sys.argv) == 1 and devicechoice != False:
        #devicessd = sd.query_devices()[devicechoice]
        ddd2 = "Sound card in use:\n" + sd.query_devices()[devicechoice]['name'] + ", Max output channels: " + str(sd.query_devices()[devicechoice]['max_output_channels'])
        labelsoundcard.configure(text=ddd2)
        
    labelsaved.configure(text="  Settings updated")
    
    return

def tabchangefocus(event):
    
    #This function ended up solving nothing. Keeping for now but not being used.
    
    #root.focus()
    pass

def delux():
    
    global deluxvar
    
    if deluxvar == 0:
        deluxvar = 1
        styler.theme_use("tokyo-night-dark")
        styler.configure('TButton', background="#292a32")
        root.configure(background="black")
        styler.configure('TFrame', background="black", foreground="black", bordercolor="black", borderwidth=0, highlightbackground="black", highlightthickness=0)
        styler.map('TFrame')
        styler.configure('TLabel', background="black", foreground="white")
        #styler.configure('TButton', background="blue", foreground="white")
        styler.configure('TEntry', background="blue", foreground="black")
        #tabmargins=0, lightcolor="black", darkfcolor="black"
        styler.configure('TNotebook', background="black", foreground="black", bordercolor="#292532")
        #This negates the border completely regardless of defining a color above.
        styler.map('TNotebook', bordercolor="black")
        #This does nothing it seems.
        #styler.map('TNotebook')
        #The padding = has to be a dimension. 0.03i (or 0.06i) as a string. wtf. c=centimeter, i=inches, m=millimeters, p=printers points about 1/72"
        styler.configure('TNotebook.Tab', background="black", foreground="pink", bordercolor="black", padding="0.03i")
        styler.map('TNotebook.Tab', background=[("selected", "pink")], foreground=[("active", "grey"), ("selected", "black")])
        #styler.configure('TNotebook.Separator', borderwidth=0, highlightthickness=0, bordercolor="black", background="black", foreground="black")
        styler.configure('TCheckbutton', background="black", foreground="white", highlightcolor="blue", indicatorbackground="black", indicatorforeground="white")
        styler.configure('Roundtoggle.Toolbutton', background="black", foreground="white")
        bufferbox.configure(bg="black", fg="white", activebackground="#303030", activeforeground="white", highlightthickness=0, selectcolor='black')
        checksoundcard.configure(bg="black", fg="white", activebackground="#303030", activeforeground="white", highlightthickness=0, selectcolor='black')
        #checkchanmap.configure(bg="black", fg="white", activebackground="#303030", activeforeground="white", highlightthickness=0, selectcolor='black')
        #styler.configure('TButton', background="#277fbc")
        #herbimagelabel.config(bg="black")
        planetimagelabel.configure(bg="black")
        checkchanmap.configure(background="black", foreground="white", activebackground="#303030", activeforeground="white", highlightthickness=0, selectcolor='black')
    elif deluxvar == 1:
        deluxvar = 0
        styler.theme_use("tokyo-night-light")
        styler.configure('TButton', background="#dddddd")
        styler.map('TNotebook', bordercolor="white")
        root.configure(background="white")
        styler.configure('TFrame', background="white", foreground="black", bordercolor="black", borderwidth=0, highlightbackground="black", highlightthickness=0)
        styler.map('TFrame')
        styler.configure('TLabel', background="white", foreground="black")
        styler.configure('TEntry', background="white", foreground="black")
        #tabmargins=0, lightcolor="black", darkcolor="black"
        styler.configure('TNotebook', background="white", foreground="black", bordercolor="#c5c5c5")
        styler.map('TNotebook')
        styler.configure('TNotebook.Tab', background="white", foreground="black", bordercolor="white", padding="0.03i")
        styler.map('TNotebook.Tab', background=[("selected", "pink")], foreground=[("active", "black"), ("selected", "black")])
        #styler.configure('TNotebook.Separator', borderwidth=0, highlightthickness=0, bordercolor="black", background="black", foreground="black")
        styler.configure('TCheckbutton', background="white", foreground="black")
        styler.configure('Roundtoggle.Toolbutton', background="white", foreground="black")   
        bufferbox.configure(bg="white", fg="black", activebackground="#E1E1E1", activeforeground="black", highlightthickness=0, selectcolor='white')
        checksoundcard.configure(bg="white", fg="black", activebackground="#E1E1E1", activeforeground="black", highlightthickness=0, selectcolor='white')
        #herbimagelabel.config(bg="white")
        planetimagelabel.configure(bg="white")
        checkchanmap.configure(background="white", foreground="black", activebackground="#E1E1E1", activeforeground="black", highlightthickness=0, selectcolor='white')
    return

def supporttime():
    
    global deluxvar
    
    root4 = tk.Toplevel(root)

    #With no geometry call, it appears in the middle of the screen in linux.
    #root2.geometry("320x320-180+200")
    root4.title("Support me! / About")
    root4.geometry("+480+200")
    
    if deluxvar == 1:
        root4.config(bg="black")
    else:
        root4.config(bg="white")
    
    try:   
        currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        rp4 = "HerbSauceico2.png"
        rp44 = "HerbSauceico3.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp4 = sys._MEIPASS
            print("mei")
        except Exception as e:
            bp4 = os.path.abspath(".")
            print("no mei")
            #print(e)
            
        filecheck4 = os.path.join(bp4, rp4)
        icon4 = tk.PhotoImage(file=filecheck4)
        root4.iconphoto(False, icon4)
    except:
        pass
    
    frame1root4 = ttk.Frame(root4)
    frame1root4.grid(column=0, row=0, sticky="nsew")
    
    aboutlabel00 = ttk.Label(frame1root4, anchor="center", text="How to Support!", font=('arial', 16, 'bold'))
    aboutlabel00.grid(column=0, row=1, padx=12, pady=12)
    
    #aboutlabel001 = ttk.Label(frame1root4, anchor="center", text="")
    #aboutlabel001.grid(column=0, row=2, padx=12)
    
    ##aboutlabel01 = ttk.Label(frame1root4, anchor="center", text="Send your donation via PayPal to:")
    ##aboutlabel01.grid(column=0, row=3, padx=12)
    
    ##aboutblank01 = ttk.Label(frame1root4, anchor="center", text="herb@deluxeherbs.net\n")
    ##aboutblank01.grid(column=0, row=4, padx=12)
    ##aboutblank01.config(foreground="#277fbc")
    
    aboutlabel02 = ttk.Label(frame1root4, anchor="center", text="Support my music, or my software via these links:")
    aboutlabel02.grid(column=0, row=5, padx=12)
    
    aboutlabel20 = ttk.Label(frame1root4, anchor="center", cursor="hand2", text="Stereo music:  https://herbdeluxmusic.bandcamp.com")
    aboutlabel20.grid(column=0, row=7, padx=12)
    aboutlabel20.config(foreground="#277fbc")

    aboutlabel20.bind("<Button-1>", lambda e: musictime(1))

    aboutlabel22 = ttk.Label(frame1root4, anchor="center", cursor="hand2", text="4.0 (.herb) music:  https://deluxeherbs.net/artists/herbdelux/herbdelux.html")
    aboutlabel22.grid(column=0, row=6, padx=12)
    aboutlabel22.config(foreground="#277fbc")
    
    aboutlabel22.bind("<Button-1>", lambda e: musictime(3))

    aboutlabel21 = ttk.Label(frame1root4, anchor="center", cursor="hand2", text="Open source software:  https://github.com/herbdelux")
    aboutlabel21.grid(column=0, row=9, padx=12)
    aboutlabel21.config(foreground="#277fbc")
    
    aboutlabel21.bind("<Button-1>", lambda e: musictime(2))
    
    aboutlabel03 = ttk.Label(frame1root4, text="")
    aboutlabel03.grid(column=0, row=10, padx=12)

    herbimagelabel = ttk.Label(frame1root4, text="herb sauce\n", font=("Arial", 16))
    herbimagelabel.grid(column=0, row=11, sticky="n")

    aboutlabel04 = ttk.Label(frame1root4, text="About herb sauce:", font=('bold'))
    aboutlabel04.grid(column=0, row=12, padx=12)
    
    aboutlabel05 = ttk.Label(frame1root4, wraplength=480, text="Version 1.0 of herb sauce was created by herb delux. It is a free player and creator program for .herb files, which are lossless uncompressed audio files which can store up to 16,777,215 channels of audio. This program allows you to play and create them in 2 (stereo), 4 (quadraphonic), and 6 (hexaphonic) versions.\n")
    aboutlabel05.grid(column=0, row=14, padx=12)
    
    aboutlabel06 = ttk.Label(frame1root4, wraplength=480, text="License:\nThe program herb sauce and the .herb lossless audio file format are released into the world,with the intention of being free and open source. Hopefully they are used for good purposes and not bad ones.")
    aboutlabel06.grid(column=0, row=15, padx=12)

    aboutlabel07 = ttk.Label(frame1root4, wraplength=480, text="For further information regarding the licenses of the packages I import in my code, please check with their respective documentation, licenses, or developers. The herb sauce pepper plate logo I put into the public domain for the sake of not gatekeeping anything in this program.")
    aboutlabel07.grid(column=0, row=16, padx=12)
   
   
    #aboutlabel06 = ttk.Label(frame1root4, wraplength=480, text="All header items written as byte strings, or integers (big endian, unsigned). All metadata items written as byte strings, integers (big endian, unsigned), or strings encoded from utf-8. Audio samples per channel are integers stored in n number of bytes (n=bit depth/8) as integers (big endian, signed).\n")
    #aboutlabel06.grid(column=0, row=14, padx=12)
    
    ##try:
        ##currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        ##rp = "HerbSauceLogo2.png"
        ##try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            ##bp = sys._MEIPASS
            ##print("herbimage mei")
        ##except Exception as e:
            ##bp = os.path.abspath(".")
            ##print("herbimage no mei")
            #print(e)
            
        ##filecheck = os.path.join(bp, rp)
        ##herbimage = tk.PhotoImage(file=filecheck)
        ##herbimagelabel = tk.Label(frame1root4, image=herbimage)
        ##if deluxvar == 1:
            ##herbimagelabel.config(bg="black", borderwidth=0)
        ##else:
            ##herbimagelabel.config(bg="white", borderwidth=0)
        ##herbimagelabel.image = herbimage
        ##print("herb image")
    ##except Exception as e:
        ##print("no image")
        ##print(e)
        ##herbimagelabel = ttk.Label(frame1root4, text="      Herb Sauce  \n\n\n\n\n", font=("Arial", 12))

    herbblank1 = ttk.Label(frame1root4, text="")
    herbblank1.grid(column=0, row=18, sticky="nsew")

    headerbutton = ttk.Button(frame1root4, style="Outline.TButton", text="View Header structure info", command=lambda: headertime())
    headerbutton.grid(column=0, row=19, padx=12)

    donateblank = ttk.Label(frame1root4, text="")
    donateblank.grid(column=0, row=20, padx=12)

    donateclose = ttk.Button(frame1root4, style="Outline.TButton", text="Close window", command=lambda: root4.destroy())
    donateclose.grid(column=0, row=21, padx=12)
    
    aboutlabel06 = ttk.Label(frame1root4, text="")
    aboutlabel06.grid(column=0, row=22, padx=12)
    
    return

def headertime():

    global deluxvar
    
    rootheader = tk.Toplevel()
    rootheader.geometry("+350+200")
    rootheader.title("herb Sauce")

    if deluxvar == 1:
        rootheader.config(bg="black")
    else:
        rootheader.config(bg="white")
    
    try:   
        currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        rp6 = "HerbSauceico2.png"
        rp66 = "HerbSauceico3.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp6 = sys._MEIPASS
            print("mei")
        except Exception as e:
            bp6 = os.path.abspath(".")
            print("no mei")
            #print(e)
            
        filecheck6 = os.path.join(bp6, rp6)
        icon6 = tk.PhotoImage(file=filecheck6)
        rootheader.iconphoto(False, icon6)
    except:
        pass
    
    headerframe1 = ttk.Frame(rootheader)
    headerframe1.grid(column=0, row=0, sticky="nsew")
    
    headertitle = ttk.Label(rootheader, text=".herb File Header Structure\n")
    headertitle.grid(column=0, row=0, padx=12, pady=12)
    
    head1 = ttk.Label(rootheader, text="Header info written as: bytestrings, unsigned integers in big endian, or UTF-8 encoded\ninto a bytestring (for metadata info sections).\nMinimum header length is 50 bytes with no metadata (track info). With metadata the header length is variable.\n")
    head1.grid(column=0, row=2, padx=12)
    
    head2 = ttk.Label(rootheader, text="4 bytes: bytestring b'herb'\n4 bytes: bytestring b'pcmb' (represents PCM big endian)")
    head2.grid(column=0, row=4, padx=12)

    head3 = ttk.Label(rootheader, text="4 bytes: header length (integer, big endian, unsigned)\n 3 bytes: number of channels (integer, big endian, unsigned)\n2 bytes: bit depth (integer, big endian, unsigned)\n4 bytes: sample rate (integer, big endian, unsigned)")
    head3.grid(column=0, row=6, padx=12)

    head4 = ttk.Label(rootheader, text="10 bytes: full size of audio frames/data portion of the file in bytes (no header) (integer, big endian, unsigned)\n10 bytes: blank 0's because. Or maybe for future proofing (integer, big endian, unsigned)")
    head4.grid(column=0, row=8, padx=12)

    head5 = ttk.Label(rootheader, text="4 bytes: bytestring b'tags' (beginning of potential metadata items)\n1 byte: number of metadata items (integer, big endian, unsigned)")
    head5.grid(column=0, row=10, padx=12)

    head6 = ttk.Label(rootheader, text="IF THERE IS NO METADATA (TRACK INFO):", font=('bold'))
    head6.grid(column=0, row=12, padx=12)

    head7 = ttk.Label(rootheader, text="4 bytes: bytestring b'leaf' (audio frames come next)")
    head7.grid(column=0, row=14, padx=12)

    head62 = ttk.Label(rootheader, text="IF THERE IS METADATA (TRACK INFO):", font=('bold'))
    head62.grid(column=0, row=16, padx=12)

    head8 = ttk.Label(rootheader, text="4 bytes: bytestring representing metadata section (example: b'trck', b'albm', etc)\n1 byte: length of this particular metadata section (integer, big endian, unsigned)\nx bytes: the data forn this metadata section (x = the integer from the 1 byte prior,\ntext is encoded from UTF-8 into bytestring)")
    head8.grid(column=0, row=18, padx=12)

    head9 = ttk.Label(rootheader, text="When there's no more metadata sections: 4 bytes: bytestring b'leaf' (audio frames come next)\n\n")
    head9.grid(column=0, row=20, padx=12)
    
    head10 = ttk.Label(rootheader, text="Audio frames are written as integers, big endian, signed. Frames follow this format for a 4 channel file:\n1st sample channel 1, 1st sample channel2, 1st sample channel 3, 1st sample channel 4,\n2nd sample channel 1, 2nd sample channel 2, 2nd sample channel 3, 2nd sample channel 4, and so on\n")
    head10.grid(column=0, row=22, padx=12)
    
    headclose = ttk.Button(rootheader, style="Outline.TButton", text="Close window", command=lambda: rootheader.destroy())
    headclose.grid(column=0, row=24, padx=12)
    
    closeblank = ttk.Label(rootheader, text="")
    closeblank.grid(column=0, row=26, padx=12)
    
    return

def howtouse():
    
    global deluxvar
    
    root3 = tk.Toplevel(root)
    root3.title("How To Use")
    
    #With no geometry call, it appears in the middle of the screen in linux.
    root3.geometry("+380+50")
    
    if deluxvar == 1:
        root3.config(bg="black")
    else:
        root3.config(bg="white")
        
    try:
        currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        rp3 = "HerbSauceico2.png"
        rp33 = "HerbSauceico3.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp3 = sys._MEIPASS
        except Exception as e:
            bp3 = os.path.abspath(".")
            #print(e)
            
        filecheck3 = os.path.join(bp3, rp3)

        icon3 = tk.PhotoImage(file=filecheck3)
        root3.iconphoto(False, icon3)
        #For having different size icons
        #icon2 = tk.PhotoImage(file='icon/.png')
        #root.iconphoto(False, icon1, icon2)

    except:
        pass

    #root3.resizable(width=True, height=True)
    ##canv = tk.Canvas(root3, width=600, height=860)
    ##canv.grid(column=0, row=0)

    ##canv.config(bg="black")
    
    #root3.grid_columnconfigure(0, weight=1, uniform=1)
    #root3.grid_rowconfigure(1, weight=1, uniform=1)

    #root3.grid_columnconfigure(1, weight=0, uniform=1)
    #root3.grid_rowconfigure(1, weight=1)
    
    frame1root3 = ttk.Frame(root3, padding=20)
    frame1root3.grid(column=0, row=0, sticky="nsew")
    
    #canv.create_window((0, 0), window=frame1root3, anchor="center")
    
    #frame1root3.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
    
    #scrollbar1 = tk.Scrollbar(root3, orient="vertical", command=canv.yview)
    #canv["yscrollcommand"] = scrollbar1.set
    #scrollbar1.grid(column=1, row=0, sticky="nsew")

    #scrollbar2 = tk.Scrollbar(root3, orient="horizontal", command=canv.xview)
    #canv["xscrollcommand"] = scrollbar2.set
    #scrollbar2.grid(column=0, row=1, sticky="nsew")
    
    aboutlabel1 = ttk.Label(frame1root3, text="  About herb Sauce  ", font=("bold"), anchor="center")
    ##aboutlabel1.grid(column=0, row=0, pady=10)

    #aboutblank1 = ttk.Label(frame1root2, text=" ")
    #aboutblank1.grid(column=0, row=2, sticky="nsew")

    aboutlabel2 = ttk.Label(frame1root3, anchor="center", text="herb Sauce version 1.0 was created by Herb Delux\n                  See Donate button for more info!\n")
    ##aboutlabel2.grid(column=0, row=4, padx=12)
    aboutlabel2.config(foreground="#277fbc")
    
    #aboutblank2 = ttk.Label(frame1root3, text=" ")
    #aboutblank2.grid(column=0, row=8, sticky="nsew")
    
    aboutlabel3 = ttk.Label(frame1root3, anchor="center", text="herb Sauce is a player/creator software for .herb audio files.\n")
    ##aboutlabel3.grid(column=0, row=10, padx=10)
    aboutlabel3.config(foreground="#277fbc")
    
    aboutlabel4 = ttk.Label(frame1root3, anchor="center", wraplength=420, text=".herb files are lossless unncompressed audio files that contain 1 to 3 stereo tracks (2.0, 4.0, or 6.0 audio) of audio data embedded into one file (the filetype itself supports up to 255 channels of audio).\n")
    ##aboutlabel4.grid(column=0, row=12, padx=10)
    aboutlabel4.config(foreground="#277fbc")
    
    ##aboutlabel4 = ttk.Label(frame1root3, anchor="center", wraplength=420, text="Version 1.0\n")
    ##aboutlabel4.grid(column=0, row=16, padx=10)
    
    titlehow = ttk.Label(frame1root3, anchor="center", text="How To Use", font=('arial', 16, 'bold'))
    titlehow.grid(column=0, row=16, sticky="nsew")

    try:
        currentdirspeaker = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        #rp0 = "HerbSaucePlanet.png"
        rp00speaker = "speakers_small.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp0speaker = sys._MEIPASS
            print("speakers mei")
        except Exception as e:
            bp0speaker = os.path.abspath(".")
            print("speakers no mei")
            #print(e)
            
        #filecheck0 = os.path.join(bp0, rp0)
        filecheck00speaker = os.path.join(bp0speaker, rp00speaker)
        #planetimage0 = tk.PhotoImage(file=filecheck0)
        speakerlabel00 = tk.PhotoImage(file=filecheck00speaker)
        speakerlabel = tk.Label(frame1root3, image=speakerlabel00)
        speakerlabel.image = speakerlabel00
        #if deluxvar == 1:
        speakerlabel.config(bg="black", borderwidth=0)
        #else:
            #planetimagelabel.config(bg="white", borderwidth=0)
        #planetimagelabel.image = planetimage
        print("speakers image")
        #planetimagelabel.bind("<Button-1>", lambda v: [imageincrease(), planetimagelabel.configure(image=planetimage0) if imagecounter%2 != 0 else planetimagelabel.configure(image=planetimage00)])
        
    except Exception as e:
        print("no image speakers")
        print(e)
        speakerlabel = tk.Label(frame1root3, text="Speakers Pics", font=("Arial", 12))
    
    speakerlabel.grid(column=0, row=18)
    
    steplabel1 = ttk.Label(frame1root3, text="For Windows, Mac, and Linux:", font=('bold'))
    steplabel1.grid(column=0, row=20, sticky="nsew")
    #steplabel1.config(foreground="#277fbc")
    
    steplabel11 = ttk.Label(frame1root3, wraplength=500, text="1. Connect 4 speakers (2 pairs) to your sound card or audio interface. The picture above has two different branded pairs of speakers. While its recommended to use the same make and model, or at least same size speaker for both pairs, it's not a requirement. This picture shows how they should be set up. 1 pair on the outside connected to output channels 1 and 2, and 1 pair on the inside connected to output channels 3 and 4.\n")
    steplabel11.grid(column=0, row=22, sticky="nsew")
    steplabel11.config(foreground="#277fbc")
    
    steplabel12 = ttk.Label(frame1root3, wraplength=500, text="2. If you have an internal soundcard, open your audio drivers and set it to 4.0 or quadraphonic mode (if available). Note, you never have to change that setting again because normal stereo programs and web browsers will still play audio through your 1-2 speakers. If you have an external audio interface, make sure it's set to as your default sound card.\n")
    steplabel12.grid(column=0, row=23, sticky="nsew")
    steplabel12.config(foreground="#277fbc")

    steplabel13 = ttk.Label(frame1root3, wraplength=500, text="3. Run herb Sauce. If you see less than 4 (if you're trying to listen to 4 channel audio) outputs listed in the bottom right corner of the .herb Player tab, go over to the Settings tab and click 'Change audio device' and try to select one with more outputs. Make sure to click 'Save settings'. You can use the Test 4.0 button on the Settings tab to make sure everything is set up properly.\n")
    steplabel13.grid(column=0, row=24, sticky="nsew")
    steplabel13.config(foreground="#277fbc")
    
    steplabel2 = ttk.Label(frame1root3, text="4. Go to the Player tab, click Open .herb file, click Play .herb file.\n")
    steplabel2.grid(column=0, row=26, sticky="nsew")
    steplabel2.config(foreground="#277fbc")
    
    steplabel21 = ttk.Label(frame1root3, wraplength=500, text="Note: If you have audio problems try a) enabling pre-buffer mode, or changing the blocksize. It will take longer to load the song however. You can also try using Soundcard package mode. Read the instructional PDF for more info.")
    steplabel21.grid(column=0, row=28, sticky="nsew")
    steplabel21.config(foreground="#277fbc")

    steplabel22 = ttk.Label(frame1root3, wraplength=500, text="Linux users: Sounddevice mode (the default mode) seems to utilize ALSA, while Soundcard mode (in the Settings tab) seems to utilize PulseAudio.\n")
    steplabel22.grid(column=0, row=29, sticky="nsew")
    steplabel22.config(foreground="#277fbc")
    
    
    bindingbutton = ttk.Button(frame1root3, text="Show key bindings", command=lambda: mb.showinfo(title='Key bindings', icon='info', message='Key bindings:\n\nControl-o:  Open .herb file\nControl-p:  Play .herb file\nControl-s:  Stop playback\nSpacebar:  Press/click selected item or button\nTAB:  Change selected item\nCtrl+TAB: Change notebook tab'))  
    bindingbutton.grid(column=0, row=52, padx=12, sticky="w")
    
    ##bindinglabel1 = ttk.Label(frame1root3, text="Key bindings:")
    ##bindinglabel1.grid(column=0, row=30, sticky="nsew")
    
    ##bindinglabel2 = ttk.Label(frame1root3, text="Control-o:   Open .herb file\nControl-p:   Play .herb file\nControl-s:   Stop playback\nSpacebar: Press/click selected item or button\nTAB: Change selected item")
    ##bindinglabel2.grid(column=0, row=32, sticky="nsew")
    ##bindinglabel2.config(foreground="#277fbc")
    
    ##endlabelroot3 = ttk.Label(frame1root3, anchor="center", text=" ")
    ##endlabelroot3.grid(column=0, row=50, sticky="nsew")
    
    howclose = ttk.Button(frame1root3, style="Outline.TButton", text="Close window", command=lambda: root3.destroy())
    howclose.grid(column=0, row=52, padx=12, sticky="e")
    #Doesn't work on buttons for some reason
    #howclose.configure(background="black")
    
    return

def showmetainfo(filename, metadata):
    
    global deluxvar
    global metaitems
    global metalist
    
    if filename == "":
        print("no file open. no metadata to display")
        mb.showinfo(title="Error", icon='info', message="No .herb file opened. No metadata to display.")     
        return
    elif metaitems == 0:
        print("no metadata items found.")
        mb.showinfo(title="Error", icon='info', message="No metadata items found in this file.")
        return
    else:
        root5 = tk.Toplevel(root)
        
        root5.geometry("+320+300")
    
        try:
            currentdir = str(os.getcwd())
            #This is for single file pyinstaller with included data.
            ##filecheck = imagefind("Planet-text5.png")
            ##This is for local stored file. The OG way.
            rp5 = "HerbSauceico2.png"
            rp55 = "HerbSauceico3.png"
            try:
                #Apparently this doesn't work at all. The os.path.abspath thing below does though.
                bp5 = sys._MEIPASS
            except Exception as e:
                bp5 = os.path.abspath(".")
                #print(e)
                
            filecheck5 = os.path.join(bp5, rp5)
            icon5 = tk.PhotoImage(file=filecheck5)
            root5.iconphoto(False, icon5)
        except:
            print("no root5 icon")
    
        framemeta = ttk.Frame(root5, padding=10)
        framemeta.grid(column=0, row=0, sticky="nsew")
        
        labelmetainfo0 = ttk.Label(framemeta, text="All metadata found:", font=('arial', 16))
        labelmetainfo0.grid(column=0, row=1, sticky="nsew")
        
        textmeta0 = tk.Text(root5, relief="ridge", width=50, height=16, font=("Arial", 18, "bold"))
        textmeta0.grid(column=0, row=2, sticky="nsew")

        scrollbarmeta = tk.Scrollbar(root5, command=textmeta0.yview)
        textmeta0["yscrollcommand"] = scrollbarmeta.set
        scrollbarmeta.grid(column=1, row=2, sticky="nsew")

        if deluxvar == 1:
            root5.config(bg="black")
            textmeta0.config(bg="black", fg="white", insertbackground="pink")
        else:
            root5.config(bg="white")
            textmeta0.config(bg="white", fg="black", insertbackground="black")
            
        for i in range(0, metalist[0]):
            #ttk.Label(framemeta, text=str(metalist[1+i][0])).grid(column=0, row=2+i)
            textmeta0.insert(tk.END, str(metalist[1+i][0])+"\n")
            textmeta0.insert(tk.END, "\t"+str(metalist[1+i][1])+"\n")
    
    return

def choosedevice():
    
    global deluxvar
    #global bgvar
    #global fgvar
    global devicechoice
    
    root4 = tk.Toplevel()
    root4.protocol("WM_DELETE_WINDOW", root4.destroy)

    try:
        currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        rp6 = "HerbSauceico2.png"
        rp62 = "HerbSauceico3.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp6 = sys._MEIPASS
        except Exception as e:
            bp6 = os.path.abspath(".")
            #print(e)
            
        filecheck6 = os.path.join(bp6, rp6)
        icon6 = tk.PhotoImage(file=filecheck6)
        root4.iconphoto(False, icon6)
    except:
        print("no root6 icon")
    
    if len(sys.argv) == 1:
        #sd
        sdq = sd.query_devices()
        
        print(sdq)
        print(len(sdq))
        print(sdq[1]['name'])
        print(str(sdq[1]['max_output_channels']))
        
        dlist = []
        
        for i in range(0, len(sdq)):
            dlist.append(str(i + 1) + ". " + str(sdq[i]['name']) + ", Max output channels: " + str(sdq[i]['max_output_channels']))
            
        devicelist1 = tk.Variable(value=dlist)
        #Doesn't work properly
        #devicelist1.set(dlist[0])

        labelchoose0 = ttk.Label(root4, anchor="center", font=('arial', 12, 'bold'), text="\nChoose your audio device:\n")
        labelchoose0.grid(column=1, row=0, sticky="nsew")
        
        #selectmode="MULTIPLE"
        lbox1 = tk.Listbox(root4, selectmode="SINGLE", height=16, width=80, listvariable=devicelist1)
        ##lbox1.select_set(0)
        
        if deluxvar == 1:
            lbox1.config(bg="black", fg="white")
            root4.configure(bg="black")
            labelchoose0.config(foreground="pink")
        else:
            lbox1.config(bg="white", fg="black")
            root4.configure(bg="white")
        lbox1.grid(column=1, row=2, sticky="ns")
        
        scrollbar1 = tk.Scrollbar(root4, command=lbox1.yview)
        lbox1["yscrollcommand"] = scrollbar1.set
        scrollbar1.grid(column=2, row=2, sticky="nsew")
        
        buttonchoosed0 = ttk.Button(root4, text="Submit", command=lambda: [devicesubmit(lbox1.get(lbox1.curselection())) if lbox1.curselection() else print("Please select"), root4.destroy()])
        buttonchoosed0.grid(column=1, row=4, sticky="nsew")
        
    elif len(sys.argv) > 1:
        allspeakers = sc.all_speakers()
        
        dlist = []
        
        for i in range(0, len(allspeakers)):
            dlist.append(str(i + 1) + ". " + str(allspeakers[i]))
            
        devicelist1 = tk.Variable(value=dlist)
        
        labelchoose0 = ttk.Label(root4, anchor="center", font=('arial', 12, 'bold'), text="\nChoose your audio device:\n")
        labelchoose0.grid(column=1, row=0, sticky="nsew")
        
        #selectmode="MULTIPLE"
        lbox1 = tk.Listbox(root4, selectmode="SINGLE", height=16, width=80, listvariable=devicelist1)
        ##lbox1.select_set(0)
        
        if deluxvar == 1:
            lbox1.config(bg="black", fg="white")
            root4.configure(bg="black")
            labelchoose0.configure(foreground="pink")
        else:
            lbox1.config(bg="white", fg="black")
            root4.configure(bg="white")
        lbox1.grid(column=1, row=2, sticky="ns")
        
        scrollbar1 = tk.Scrollbar(root4,  command=lbox1.yview)
        lbox1["yscrollcommand"] = scrollbar1.set
        scrollbar1.grid(column=2, row=2, sticky="nsew")
        
        buttonchoosed0 = ttk.Button(root4, text="Submit", command=lambda: [devicesubmit(lbox1.get(lbox1.curselection())) if lbox1.curselection() else print("Please select"), root4.destroy()])
        buttonchoosed0.grid(column=1, row=4, sticky="nsew")
        
        #root4.bind("<Return>", lambda: [devicesubmit(lbox1.get(lbox1.curselection())) if lbox1.curselection() else print("Please select"), root4.destroy()])
        #Doesnt work
        #root4.bind("<Left>", print(lbox1.curselection()))
        #root4.bind("w", lambda: print(lbox1.curselection()))
        
    else:
        print("Couldnt determine audio device package. Went wrong.")
        return

    return

def devicesubmit(choice):

    global devicechoice
    
    try:
        if choice[1] == ".":
            devicechoice = int(choice[0]) - 1
        else:
            devicechoice = int(str(choice[0]) + str(choice[1])) -1
    except:
        devicechoice = int(choice[0]) - 1
        
    print("device choice " + str(devicechoice))
    
#    if len(sys.argv) == 1:
#        sd.default.device = devicechoice
#    else:
#        df1 = sc.all_speakers()[devicechoice]
    
    if len(sys.argv) > 1:
        devicessc2 = "Sound card in use:\n" + str(sc.all_speakers()[devicechoice])
        labelsoundcard.configure(text=devicessc2)
        chanlabel3.configure(wraplength=120, text=str(sc.all_speakers()[devicechoice]))
    else:
        print("11")
        #sdq1 = sd.query_devices()
        devicessd = devicechoice
        ddd2 = "Sound card in use:\n" + sd.query_devices()[devicessd]['name'] + ", Max output channels: " + str(sd.query_devices()[devicessd]['max_output_channels'])
        labelsoundcard.configure(text=ddd2)
        if sd.query_devices()[devicessd]['max_output_channels'] < 1:
            chanlabel3.configure(foreground="red", wraplength=120, text=str(sd.query_devices()[devicessd]['max_output_channels']) + "\n(Click 'Change audio device' in Settings tab, or check Soundcard pkg)")
        else:
            if deluxvar == 1:
                chanlabel3.configure(wraplength=120, foreground="white", text=sd.query_devices()[devicessd]['max_output_channels'])
            else:
                chanlabel3.configure(wraplength=120, foreground="black", text=sd.query_devices()[devicessd]['max_output_channels'])
    return

def limitentry(inputtext):
    
    charstring = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'()$#!?,@&=%^_ "
    
    for i in range(0, len(inputtext)):
        if inputtext[i] not in charstring:
            return False
        else:
            pass
    
    #For max character limit
    #if len(inputtext) > 16:
        #return False
    #else:
        #pass
    
    return True

def limitoverride(inputtext2):
    
    charstring2 = "0123456789"
    
    for i in range(0, len(inputtext2)):
        if inputtext2[i] not in charstring2:
            return False
        else:
            pass
    
    return True

def limitoverride2(inputtext3):
    
    charstring2 = "0123456789 abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-=_+/,.;:"
    
    for i in range(0, len(inputtext3)):
        if inputtext3[i] not in charstring2:
            return False
        else:
            pass
    
    return True

def addtrackinfo():
    
    global tracknamec
    global artistnamec
    global albumnamec
    global yearnumc
    global tracknumc
    
    root2 = tk.Toplevel()
    root2.title("Add track info")
    root2.geometry("+600+200")
    
    try:
        currentdir = str(os.getcwd())
        #This is for single file pyinstaller with included data.
        ##filecheck = imagefind("Planet-text5.png")
        ##This is for local stored file. The OG way.
        rp2 = "HerbSauceico2.png"
        rp22 = "HerbSauceico3.png"
        try:
            #Apparently this doesn't work at all. The os.path.abspath thing below does though.
            bp2 = sys._MEIPASS
        except Exception as e:
            bp2 = os.path.abspath(".")
            #print(e)
            
        filecheck2 = os.path.join(bp2, rp2)
        icon2 = tk.PhotoImage(file=filecheck2)
        root2.iconphoto(False, icon2)
        
    except:
        pass
    
    frametop1 = ttk.Frame(root2, padding=30)
    frametop1.grid(column=0, row=0, sticky="nsew")

    labelmeta = ttk.Label(frametop1, text="Track info (optional)", font=("bold"))
    labelmeta.grid(column=0, row=0, sticky="nsew")

    labeltrack = ttk.Label(frametop1, text="Track name:")
    labeltrack.grid(column=0, row=1, sticky="nsew")

    entrytrack = ttk.Entry(frametop1, width=36, validate="key", validatecommand=(vc, "%P"))
    entrytrack.grid(column=0, row=2, sticky="nsew")

    if tracknamec != "":
        #entrytrack.delete("0.0", "end")
        entrytrack.insert(0, tracknamec)
        
    labelartist = ttk.Label(frametop1, text="\nArtist name:")
    labelartist.grid(column=0, row=3, sticky="nsew")

    entryartist = ttk.Entry(frametop1, width=36, validate="key", validatecommand=(vc, "%P"))
    entryartist.grid(column=0, row=4, sticky="nsew")

    if artistnamec != "":
        #entrytrack.delete("0.0", "end")
        entryartist.insert(0, artistnamec)
        
    labelalbum = ttk.Label(frametop1, text="\nAlbum name:")
    labelalbum.grid(column=0, row=5, sticky="nsew")

    entryalbum = ttk.Entry(frametop1, width=36, validate="key", validatecommand=(vc, "%P"))
    entryalbum.grid(column=0, row=8, sticky="nsew")

    if albumnamec != "":
        #entrytrack.delete("0.0", "end")
        entryalbum.insert(0, albumnamec)
        
    labeltracknum = ttk.Label(frametop1, text="\nTrack number:")
    labeltracknum.grid(column=0, row=10, sticky="nsew")
    
    entrytracknum = ttk.Entry(frametop1, validate="key", validatecommand=(vc3, "%P"))
    entrytracknum.grid(column=0, row=12, sticky="w")

    if tracknumc != "":
        #entrytrack.delete("0.0", "end")
        entrytracknum.insert(0, tracknumc)
        
    labelyear = ttk.Label(frametop1, text="\nYear released:")
    labelyear.grid(column=0, row=14, sticky="nsew")
    
    entryyear = ttk.Entry(frametop1, validate="key", validatecommand=(vc2, "%P"))
    entryyear.grid(column=0, row=16, sticky="w")

    if yearnumc != "":
        #entrytrack.delete("0.0", "end")
        entryyear.insert(0, yearnumc)
        
    labelinfo1 = ttk.Label(frametop1, text=" ")
    labelinfo1.grid(column=0, row=17, sticky="nsew")
    
    buttonaddinfo = ttk.Button(frametop1, text="Submit track info", command=lambda: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])
    buttonaddinfo.grid(column=0, row=18, sticky="nsew")
    
    entrytrack.bind("<Return>", lambda e: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])
    entryartist.bind("<Return>", lambda e: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])
    entryalbum.bind("<Return>", lambda e: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])
    entrytracknum.bind("<Return>", lambda e: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])
    entryyear.bind("<Return>", lambda e: [submittrackinfo(entrytrack.get(), entryartist.get(), entryalbum.get(), entrytracknum.get(), entryyear.get()), root2.destroy()])

    entrytrack.focus()
    
    return

def submittrackinfo(track1, artist1, album1, tracknum1, year1):
    
    global tracknamec
    global artistnamec
    global albumnamec
    global tracknumc
    global yearnumc
    
    track1.rstrip()
    artist1.rstrip()
    album1.rstrip()
    tracknum1.rstrip()
    year1.rstrip()
    
    tracknamec = track1
    artistnamec = artist1
    albumnamec = album1
    tracknumc = tracknum1
    yearnumc = year1
    
    labelinfoadded.configure(text="Track info saved")
    
    return

def endherb(samplerate):
    
    global stopper
    global currentplay
    global streamer
    global pauser
    
    #AND HERE
    labelopen0.focus()
    
    pauser = False
    buttonplay.configure(text="Play .herb file", command=lambda: threading.Thread(target=getherbinfo, args=(filename0, 1,)).start())
    #event.wait()
    
    stopper = 1
    currentplay = 0
    
    if streamer == 2 and len(sys.argv) == 1:
        try:
            sd.stop()
            streamer = 0
        except:
            print("couldnt stop pre-buffered playback")
    else:
        pass
    
    #This causes an error or exception for some reason. Leaving this out for now.
    ##q.queue.clear()
    for ii in range(0, len(q.queue)):
        q.get()
        
    temp00 = [[0.0,0.0], [0.0,0.0]]
    temp0 = np.array(temp00)
    
    #None of this works when using OutputStream to stop sound.
    #sd.stop()
    #sd.default.device = sd.default.device[0]
    #sd.default.samplerate = 44100
    #sd.play(temp0)
    #sd.wait()
    
    #gc.collect()
    #df2 = sc.default_speaker()
    
    #Doesnt work. Nor does df2.play(m2, samplerate=samplerate)
    #with df2.player(samplerate=samplerate) as ds:
        #m = [[0,0],[0,0],[0,0],[0,0]]
        #m2 = np.array(m)
        #ds.play(m2)
    
    print("Ended " + str(sys.platform) + " playback")
    playlabel.configure(text="   Stopped")
    return

def volumechange(volamount):
    
    global volumevar
    
    #print(volumeshift.get())
    
    #volumevar = float(volumevar0.get())
    voldict = {
        "100%" : 1.0,
        "80%" : 0.8,
        "60%" : 0.6,
        "40%" : 0.4,
        "20%" : 0.2,
        "0%" : 0.0
        }
    
    volumevar = voldict[volamount]
    print(volumevar)
    
    #volumevar = volumeshift.get()

    
    return

def closing():
    
    global mangy
    global stopper
    
    mangy = 1
    stopper = 1
    
    print("Quitting. Current pid: " + str(os.getpid()))
    
    #os.kill(pid, signal)
    #For termination
    #os.kill(os.getpid(), signal.SIGTERM)
    
    root.quit()
    root.destroy()
    
    #THIS WORKS TO STOP AUDIO PLAYING WHEN YOU CLOSE THE PROGRAM
    try:
        os._exit(os.EX_OK)
    except:
        print("Attempted to end processes, but something went wrong")
    
    #This is probably not needed. Leaving it in anyway
    sys.exit()

    #quit and exit cannot be used in production code according to the internet
    #quit()
    #exit()
    
    
#themename = 'superhero'
root = tk.Tk()
#root = tb.App()

##root = ttk.Window()
if sys.platform == "win32":
    root.geometry("-350-150")
    #On windows this opens the window locked in with the right of the taskbar, but it bleeds behind the task bar.
    #root.geometry("-0-0")
elif sys.platform == "linux":
    root.geometry("-200-150")
    #In Linux this opens the window locked in with the bottom right of taskbar, with no bleed into the task bar.
    #root.geometry("-0-0")
else:
    #On Mac using one of the geometry calls above, the program bleeds into the right side of the screen a lot.
    root.geometry("-460+150")
    
#root.geometry("620x680-100+100")
root.title("herb sauce")

#Transparent window
#root.attributes('-alpha', 0.5)

#Window size
##xx = root.winfo_rootx()
##yy = root.winfo_rooty()
#Screen size
#width2 = root.winfo_screenwidth()
#height2 = root.winfo_screenheight()
#Unknown?
##wwidth = root.winfo_width
##hheight = root.winfo_height
#from PIL import ImageGrab
#img = ImageGrab.grab()
#print(img.size)

#root.resizable(width=False, height=False)

#This makes a frameless window but it's always on top
#root.overrideredirect(True)

#Full screen but with taskbar instance
#root.wm_attributes('-fullscreen', 'true')

#This removes frames, but still isn't always on top, but no taskbar instance. Only for X11 Linux.
#root.wm_attributes('-type', 'splash')

root.resizable(True, True)


#This makes that column take up whole frame
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#Grid.rowconfigure(root, 0, weight=1)
#Grid.columnconfigure(root, 0, weight=1)

root.protocol("WM_DELETE_WINDOW", closing)

#Works in Linux, and apparently Windows too.
try:
    currentdirico = str(os.getcwd())
    #This is for single file pyinstaller with included data.
    ##filecheck = imagefind("Planet-text5.png")
    ##This is for local stored file. The OG way.
    #Peppers
    rpico = "HerbSauceico2.png"
    #Planet
    rpico2 = "HerbSauceico3.png"
    try:
        #Apparently this doesn't work at all. The os.path.abspath thing below does though.
        bpico = sys._MEIPASS
    except Exception as e:
        bpico = os.path.abspath(".")
        #print(e)
        
    filecheckico = os.path.join(bpico, rpico)
    iconico = tk.PhotoImage(file=filecheckico)
    root.iconphoto(False, iconico)
    
except:
    pass


##frame1 = ttk.Frame(root, padding=10)
##frame1.grid(column=0, row=0, sticky="nsew")

##frame2 = ttk.Frame(root, padding=10)
##frame2.grid(column=0, row=1, sticky="nsew")

#padding=10
tabs1 = ttk.Notebook(root, padding=6)

#PC Performance tab
frametab1 = ttk.Frame(tabs1, padding=10)

#frametab2 = ttk.Frame(tabs1, padding=10)
frametab3 = ttk.Frame(tabs1, padding=15)
frametab4 = ttk.Frame(tabs1, padding=10)
frametab5 = ttk.Frame(tabs1, padding=10)

frametab3.grid_rowconfigure(0, weight=1)
frametab3.grid_columnconfigure(0, weight=1)
##frametab3.grid_rowconfigure(1, weight=1)
##frametab3.grid_columnconfigure(1, weight=0)
frametab3.grid_rowconfigure(2, weight=0)
frametab3.grid_columnconfigure(2, weight=1)
#frametab3.grid_rowconfigure(3, weight=0)
#frametab3.grid_columnconfigure(3, weight=1)

frametab4.grid_rowconfigure(0, weight=1)
frametab4.grid_columnconfigure(0, weight=1)
frametab4.grid_rowconfigure(1, weight=1)
frametab4.grid_columnconfigure(1, weight=0)
frametab4.grid_rowconfigure(2, weight=1)
frametab4.grid_columnconfigure(2, weight=1)
#frametab4.grid_rowconfigure(3, weight=1)
#frametab4.grid_columnconfigure(3, weight=1)

frametab5.grid_rowconfigure(0, weight=1)
frametab5.grid_columnconfigure(0, weight=1)
frametab5.grid_rowconfigure(1, weight=1)
frametab5.grid_columnconfigure(1, weight=0)
frametab5.grid_rowconfigure(2, weight=1)
frametab5.grid_columnconfigure(2, weight=1)
#frametab5.grid_rowconfigure(3, weight=1)
#frametab5.grid_columnconfigure(3, weight=1)

frametab41 = ttk.Frame(frametab4, padding=10)
frametab42 = ttk.Frame(frametab4, padding=10)

frametab51 = ttk.Frame(frametab5, padding=10)
frametab52 = ttk.Frame(frametab5, padding=10)
frametab53 = ttk.Frame(frametab5, padding=10)

frametab31 = ttk.Frame(frametab3, padding=6)
frametab32 = ttk.Frame(frametab3, padding=6)

tabs1.grid_rowconfigure(0, weight=0)
tabs1.grid_columnconfigure(0, weight=0)
tabs1.grid_rowconfigure(1, weight=0)
tabs1.grid_columnconfigure(1, weight=0)
tabs1.grid_rowconfigure(2, weight=0)
tabs1.grid_columnconfigure(2, weight=0)
##frametab53.rowconfigure(1,weight=1)
##frametab53.columnconfigure(1, weight=1)

#Not needed?
##frametab1.grid(column=0, row=0, sticky="nsew")

styler = tb.Style()
#styler=ttk.Style()
#sandstone-light/dark, united, pulse, minty, vapor, everforest, tokyo-night, one, dracula, grubbox, catppuccin, solarized, nord, pydata, bootstrap
#To be depricated, but looks cool with gray.
#I CANT BELIEVE I HAVE TO RE DO THIS SHIT AT THE LAST SECOND. TTKBOOTSTRAP BE UPDATING THEIR SHIT MAN.
#LOOKS SICK, COOL GREY
##styler.theme_use("solarized-dark")
##LOOKS SICK, MORE GREY
##styler.theme_use("bootstrap-dark")
#ALSO SICK AS FUCK
##styler.theme_use("tokyo-night-dark")

#style.configure('TNotebook')
#bordercolor="green" -- for .configure

root.configure(background="white")
styler.configure('TFrame', background="white", foreground="black", bordercolor="black", borderwidth=0, highlightbackground="black", highlightthickness=0)
styler.map('TFrame')
styler.configure('TLabel', background="white", foreground="black")
styler.configure('TEntry', background="white", foreground="black")
#tabmargins=0, lightcolor="black", darkcolor="black"
styler.configure('TNotebook', background="white", foreground="black", bordercolor="#c5c5c5")
styler.map('TNotebook')
styler.configure('TNotebook.Tab', background="white", foreground="black", bordercolor="black", padding=10)
styler.map('TNotebook.Tab', background=[("selected", "pink")], foreground=[("active", "black"), ("selected", "black")])
#styler.configure('TNotebook.Separator', borderwidth=0, highlightthickness=0, bordercolor="black", background="black", foreground="black")
styler.configure('TCheckbutton', background="white", foreground="black")
styler.configure('Roundtoggle.Toolbutton', background="white", foreground="black")

#font=("monospace", 11)
if sys.platform == "linux":
    styler.configure('TNotebook.Tab', font=(None, 11))
else:
    styler.configure('TNotebook.Tab', font=(None, 10))

#styler1 = ttk.Style(tabs1)
#styler1.configure('TNotebook.Tab', bordercolor="green")

#padding = 10 adds padding to actual frame, not tab
#tabs1.add(frametab2, text="Networking")
#image =  can be used to add icon? Must use PhotoImage first.
#underline = marks a single character. 0 = first character, 1 = second, etc.
tabs1.add(frametab3, text=" .herb Player ")
tabs1.add(frametab4, text=" .herb Creator ")
tabs1.add(frametab5, text="  Settings  ")
#tabs1.add(frametab1, text="PC Performance")
#tabs1.tab(frametab3, state="disabled") or state="normal"
#tabs1.hide(frametab3) .forget(frametab3)
#so that ctrl+tab or ctrl+shift+tab can be used for traversal
tabs1.enable_traversal()

tabs1.grid(column=0, row=0, sticky="nsew")

frametab41.grid(column=0, row=0, sticky="nsew")
frametab42.grid(column=2, row=0, sticky="nsew")

frametab51.grid(column=0, row=0, sticky="nsew")
frametab52.grid(column=2, row=0, sticky="nsew")

frametab53.grid(column=0, row=1, columnspan=50, rowspan=50, sticky="nsew")

frametab31.grid(column=0, row=0, sticky="nsew")
sepplay = ttk.Separator(frametab3, orient=tk.VERTICAL)
sepplay.grid(column=1, row=0, rowspan=50, padx=12, pady=10, sticky="nsew")
frametab32.grid(column=2, row=0, rowspan=50, columnspan=50, sticky="nsew")

#frametab5.columnconfigure(0,weight=1)

#Makes a small window with no notebook, only frametab1
##rametab1.grid(column=0, row=0, rowspan=10, columnspan=10)

#frametab1.columnconfigure(0, weight=0)
#frametab1.rowconfigure(0, weight=0)

sepsettings = ttk.Separator(frametab5, orient=tk.VERTICAL)
sepsettings.grid(column=1, row=0, sticky="nsew")

sepcreator = ttk.Separator(frametab4, orient=tk.VERTICAL)
#rowspan = 20
sepcreator.grid(column=1, row=0, sticky="nsew")

#Global variables
mangy = 0
stopper = 0
deluxvar = 0
endyness = "big"
wavendyness = "little"

#For Player tab
filename0 = ""
filenamegetinfo = ""
bitdepth00 = 0
samplerate00 = 0
numchan00 = 0
currentplay = 0
headsize00 = 0
trackname = ""
artistname = ""
albumname = ""
tracknum = ""
yearnum = ""
pauser = False
fullbuff = []
asiovar = False
streamer = 0
metaitems = 0
metalist = []
maindir = "."
volumevar = 1.0

#For Creator tab
exportedherb = ""
filewav1 = ""
filewav2 = ""
filewav3 = ""
file1mono = False
file2mono = False
file3mono = False
sampleratewav1 = 0
bitdepthwav1 = 0
sampleratewav2 = 0
bitdepthwav2 = 0
headsizewav1 = 46
#monotest = False
tracknamec = ""
artistnamec = ""
albumnamec = ""
yearnumc = ""
tracknumc = ""
quadro = False
hexa = False
cdircheck = False
wavdir = "."

#For Settings tab
channelset = [0,1,2,3]
channelset3 = [0,1,2,3,4,5]
channelset1 = [0,1]
channelsetsd = [1,2,3,4]
channelset3sd = [1,2,3,4,5,6]
channelset1sd = [1,2]
manualheader = 0
buffersettingval = 0
customdir = ""
customdir1 = ""
soundcardchanger = 0
exclusivevar2 = 0
devicechoice = False

#tk vars
buffervar = tk.IntVar(root)
buffersetting = tk.IntVar(root)
variablechannel = tk.StringVar(root)
variablechannel3 = tk.StringVar(root)
variablechannel1 = tk.StringVar(root)
chanmapper = tk.IntVar(root)
chanmapper2 = False
soundcardvar = tk.IntVar(root)
exclusivevar = tk.IntVar(root)
#Scale object doesnt seem to care about the volumevar0 intcar
#volumevar0 = tk.IntVar
varvolume = tk.StringVar(root)
listvolumes = ["", "100%", "80%", "60%", "40%", "20%", "0%"]
varvolume.set(listvolumes[1])
blockvariable = tk.IntVar(root)
bitstreamarray = [0, 64, 128, 256, 512, 1024]
blockvariable.set(bitstreamarray[3])

#Begin the generation of visual items.

#Frametab3

labelopen0 = ttk.Label(frametab31, anchor="center", text=".herb Player\n", font=("bold"))
labelopen0.grid(column=0, row=1, sticky="n")


#Adding  takefocus=0 to the Button makes it so that it doesn't auto focus. However, it also can't focus at all even with TAB key.
buttonopen = ttk.Button(frametab31, text="Open .herb file", padding=5, command=lambda: openherb(""))
buttonopen.grid(column=0, row=2, sticky="nsew")

##labelaudio1 = ttk.Label(frametab3, text="")
##labelaudio1.grid(column=0, row=1, sticky="nsew")

labelopen1 = ttk.Label(frametab31, text="Selected file:\n", wraplength=220)
labelopen1.grid(column=0, row=3, sticky="nsew")

labelaudio2 = ttk.Label(frametab31, text="\n", wraplength=220)
labelaudio2.grid(column=0, row=4, sticky="nsew")

#buttonaudio = ttk.Button(frametab3, text="Audio", command=lambda: threading.Thread(target=doaudio, daemon=True).start())
buttonplay = ttk.Button(frametab31, text="Play .herb file", padding=5, command=lambda: threading.Thread(target=getherbinfo, args=(filename0, 1,)).start())
buttonplay.grid(column=0, row=5, sticky="nsew")
#buttonplay.bind("<Button-1>", lambda e: threading.Thread(target=getherbinfo(filename0)).start())

labelaudio3 = ttk.Label(frametab31, text="")
labelaudio3.grid(column=0, row=6, sticky="nsew")

##tbstyle1 = tb.Style()
##tbstyle1.configure("info.Squaretoggle.Toolbutton", background="black", foreground="white")

bufferbox = tk.Checkbutton(frametab31, cursor="hand2", text="Pre-Buffer entire song before playback    ", variable=buffervar, onvalue=1, offvalue=0)
bufferbox.configure(bg="black", fg="white", activebackground="#303030", activeforeground="white", highlightthickness=0, selectcolor='black')
bufferbox.grid(column=0, row=7, sticky="w")

#This led to nothing.
#bufferbox.bind("<<NotebookTabChanged>>", tabchangefocus)

#bufferbox.focus()
##if len(sys.argv) == 1:
    #SD
    #print("sup sys.argv == 1")
    ##pass
##else:
    #SC
    #print("sup sys.argv NOT 1")
    ##if sys.platform != "linux":
        ##bufferbox.select()
    ##else:
        ##pass

#buffervar = tk.IntVar(root, 1)
    
#For ttk.Checkbutton. This Doesn't change buffervar value though.
#If you change buffervar value, it makes this a weird slash rather than a check mark in the checkbox.
#bufferbox.state(["selected"])

###print(buffervar.get())

labelaudio33 = ttk.Label(frametab31, text="")
labelaudio33.grid(column=0, row=8, sticky="nsew")

buttonstop = ttk.Button(frametab31, text="Stop playback", padding=5, command=lambda: threading.Thread(target=endherb, args=(samplerate00,)).start())
buttonstop.grid(column=0, row=9, sticky="nsew")

labelaudio4 = ttk.Label(frametab31, text="")
labelaudio4.grid(column=0, row=10, sticky="nsew")

#command=volumechange,variable=volumevar0,
#volumeshift = ttk.Scale(frametab31, from_=0.0, to_=1.0, style="Horizontal.TScale", orient='horizontal')
#volumeshift.grid(column=0, row=11)

#volumeshift.bind("<B1-Motion>", volumechange)
#volumeshiftshift.bind("<ButtonRelease>", lambda v: checktxt(variable1.get(), variable2.get(), str(smallbox.get("0.0", "end")), variable4.get()))

##labelaudio5 = ttk.Label(frametab3, text="System platform: " + str(sys.platform))
##labelaudio5.grid(column=0, row=12, sticky="nsew")

labelaudio8 = ttk.Label(frametab31, text="Number of channels: " + str(numchan00 * 2), font=('bold'))
labelaudio8.grid(column=0, row=12, sticky="nsew")

labelaudio6 = ttk.Label(frametab31, text="Sample rate: " + str(samplerate00))
labelaudio6.grid(column=0, row=13, sticky="nsew")

labelaudio7 = ttk.Label(frametab31, text="Bit depth: " + str(bitdepth00))
labelaudio7.grid(column=0, row=15, sticky="nsew")

labelaudio82 = ttk.Label(frametab31, text="Header size:")
labelaudio82.grid(column=0, row=17, sticky="nsew")

labelmetaitems = ttk.Label(frametab31, cursor="hand2", text="Metadata items: \n")
labelmetaitems.grid(column=0, row=18, sticky="nsew")

labelmetaitems.bind("<Button-1>", lambda v: showmetainfo(filename0, metalist))

labelaudiolength = ttk.Label(frametab31, text="Length: ", wraplength=220)
labelaudiolength.grid(column=0, row=19, sticky="nsew")

labelaudio9 = ttk.Label(frametab31, text="Track name: " + str(trackname), wraplength=220)
labelaudio9.grid(column=0, row=20, sticky="nsew")

labelaudio10 = ttk.Label(frametab31, text="Artist name: " + str(artistname), wraplength=220)
labelaudio10.grid(column=0, row=21, sticky="nsew")

labelaudio11 = ttk.Label(frametab31, text="Album name: " + str(albumname), wraplength=220)
labelaudio11.grid(column=0, row=22, sticky="nsew")

labelaudio12 = ttk.Label(frametab31, text="Track number: ", wraplength=220)
labelaudio12.grid(column=0, row=23, sticky="nsew")

labelaudio13 = ttk.Label(frametab31, text="Year: " + "\n\n", wraplength=220)
labelaudio13.grid(column=0, row=24, sticky="nsew")


#Frametab4

labelcreate1 = ttk.Label(frametab41, text="   Input up to 3 wav files   ", font=("bold"))
labelcreate1.grid(column=0, row=0, sticky="nsew")

labelarrow = ttk.Label(frametab41, text="    ------>\n")
labelarrow.grid(column=0, row=1, sticky="e")

buttonopenwav1 = ttk.Button(frametab41, text="Open .wav file 1", padding=6, command=lambda: threading.Thread(target=wavchoose, args=(1,)).start())
buttonopenwav1.grid(column=0, row=2, sticky="nsew", ipadx=10)

##labelwav1 = ttk.Label(frametab41, text="")
##labelwav1.grid(column=0, row=1, sticky="nsew")

labelwav11 = ttk.Label(frametab41, text=filewav1 + "\n\n\n\n", wraplength=160)
labelwav11.grid(column=0, row=3, sticky="nsew")

buttonopenwav2 = ttk.Button(frametab41, text="Open .wav file 2", padding=6, command=lambda: threading.Thread(target=wavchoose, args=(2,)).start())
buttonopenwav2.grid(column=0, row=4, sticky="nsew")

##labelwav22b = ttk.Label(frametab41, text="")
##labelwav22b.grid(column=0, row=4, sticky="nsew")

labelwav22 = ttk.Label(frametab41, text=filewav2 + "\n\n\n\n", wraplength=160)
labelwav22.grid(column=0, row=5, sticky="nsew")

buttonopenwav2 = ttk.Button(frametab41, text="Open .wav file 3", padding=6, command=lambda: threading.Thread(target=wavchoose, args=(3,)).start())
buttonopenwav2.grid(column=0, row=7, sticky="nsew")

##labelwav32b = ttk.Label(frametab41, text="")
##labelwav32b.grid(column=0, row=8, sticky="nsew")

vc = root.register(limitentry)

labelwav32 = ttk.Label(frametab41, text=filewav3 + "\n\n\n\n", wraplength=160)
labelwav32.grid(column=0, row=9, sticky="nsew")

##labelinfo0 = ttk.Label(frametab42, text="Add track info (optional)")
##labelinfo0.grid(column=0, row=7, sticky="nsew")

labelmetatop = ttk.Label(frametab42, text="Create .herb file\n", font=("bold"))
labelmetatop.grid(column=0, row=7, sticky="nsew")

buttonmeta = ttk.Button(frametab42, text="Add track info (optional)", padding=6, command=addtrackinfo)
buttonmeta.grid(column=0, row=8, sticky="nsew")

labelinfoadded = ttk.Label(frametab42, text=" ")
labelinfoadded.grid(column=0, row=9, sticky="nsew")

labelentryname = ttk.Label(frametab42, text="\nChoose a file name for your .herb file,     \nminus the extension")
labelentryname.grid(column=0, row=10, sticky="nsew")

#show="." for passwords.
entryherb = ttk.Entry(frametab42, validate="key", validatecommand=(vc, "%P"))
entryherb.grid(column=0, row=11, sticky="nsew")

labelwav33 = ttk.Label(frametab42, text="")
labelwav33.grid(column=0, row=12, sticky="nsew")

buttoncreate = ttk.Button(frametab42, text="Create .herb file", padding=6, command=lambda: threading.Thread(target=createherb, args=(str(entryherb.get()), filewav1, filewav2, filewav3, sampleratewav1, bitdepthwav1, headsizewav1, tracknamec, artistnamec, albumnamec, tracknumc, yearnumc,)).start())
buttoncreate.grid(column=0, row=13, sticky="nsew")

##labelwav4 = ttk.Label(frametab42, text="")
##labelwav4.grid(column=0, row=15, sticky="nsew")

labelcreated1 = ttk.Label(frametab42, text=".herb file exported as:\n", font=('bold'), wraplength=220)
labelcreated1.grid(column=0, row=16, sticky="nsew")

labelcreated2 = ttk.Label(frametab42, text="")
labelcreated2.grid(column=0, row=18, sticky="w")

#Frametab5
#OG list
#channellist = ["","[0,1,2,3]","[0,1,4,5]","[0,1,6,7]","[2,3,4,5]"]
#User friendly list
channellist = ["","[1,2,3,4]","[1,2,5,6]","[1,2,7,8]","[3,4,5,6]"]
channellist3 = ["","[1,2,3,4,5,6]","[1,2,3,4,7,8]","[1,2,5,6,7,8]","[3,4,5,6,7,8]"]
channellist1 = ["", "[1,2]","[3,4]","[5,6]","[7,8]"]
variablechannel.set(channellist[1])
variablechannel3.set(channellist3[1])
variablechannel1.set(channellist1[1])

#width=19
buttonhow = ttk.Button(frametab51, text="Change audio device", command=lambda: choosedevice())
buttonhow.grid(column=0, row=0)

labelblocksize = ttk.Label(frametab51, text="\nBlocksize (default 256)")
labelblocksize.grid(column=0, row=2)

menublocksize = ttk.OptionMenu(frametab51, blockvariable, *bitstreamarray)
menublocksize.grid(column=0, row=3)

labelsubmit = ttk.Label(frametab51, text="")
labelsubmit.grid(column=0, row=4, sticky="nsew")

labelframe50 = ttk.Label(frametab51, anchor="center", text="Output channels\n", font=('bold'))
labelframe50.grid(column=0, row=5, sticky="nsew")

#style="Roundtoggle.Toolbutton"
#checkchanmap = ttk.Checkbutton(frametab51, cursor="hand2", variable=chanmapper, onvalue=1, offvalue=0, text="Custom channel mapping\n(for pre-buffer mode or\nSoundcard package mode)")
checkchanmap = tk.Checkbutton(frametab51, cursor="hand2", variable=chanmapper, onvalue=1, offvalue=0, text="Custom channel mapping\n(for pre-buffer mode or\nSoundcard pkg mode)")
checkchanmap.grid(column=0, row=6, sticky="nsew")

labelchanmap = ttk.Label(frametab51, text=" ")
labelchanmap.grid(column=0, row=8, sticky="nsew")

labelframe501 = ttk.Label(frametab51, text="For 2.0 channels:")
labelframe501.grid(column=0, row=9, sticky="nsew")

option0 = ttk.OptionMenu(frametab51, variablechannel1, *channellist1)
#option1.config(highlightthickness=0)
#option1["menu"].config(bg=bgvar, fg=fgvar, activebackground=bgvar, activeforeground=fgvar)
#option1["borderwidth"] = 0
#option1["hightlightbackground"] = 0
option0.grid(column=0, row=10, sticky="nsew")

labelframe502 = ttk.Label(frametab51, text=" ")
labelframe502.grid(column=0, row=11, sticky="nsew")

labelframe51 = ttk.Label(frametab51, text="For 4.0 channels:")
labelframe51.grid(column=0, row=12, sticky="nsew")

option1 = ttk.OptionMenu(frametab51, variablechannel, *channellist)
#option1.config(highlightthickness=0)
#option1["menu"].config(bg=bgvar, fg=fgvar, activebackground=bgvar, activeforeground=fgvar)
#option1["borderwidth"] = 0
#option1["hightlightbackground"] = 0
option1.grid(column=0, row=13, sticky="nsew")

labelframe52 = ttk.Label(frametab51, text="Default: [1, 2, 3, 4]\n")
labelframe52.grid(column=0, row=14, sticky="nsew")

labelframe522 = ttk.Label(frametab51, text="For 6.0 channels:")
labelframe522.grid(column=0, row=15, sticky="nsew")

option3 = ttk.OptionMenu(frametab51, variablechannel3, *channellist3)
#option1.config(highlightthickness=0)
#option1["menu"].config(bg=bgvar, fg=fgvar, activebackground=bgvar, activeforeground=fgvar)
#option1["borderwidth"] = 0
#option1["hightlightbackground"] = 0
option3.grid(column=0, row=16, sticky="nsew")

labeloption = ttk.Label(frametab51, text="Default: [1,2,3,4,5,6]")
labeloption.grid(column=0, row=17, sticky="nsew")

##buffersetting2 = ttk.Checkbutton(frametab52, cursor="hand2", text="Use multiprocessing for\nnon-buffered playing", variable=buffersetting, onvalue=1, offvalue=0)
##buffersetting2.grid(column=0, row=2, sticky="w")
#For tk.Checkbutton
#buffersetting2.select()
#For ttk.Checkbutton
##buffersetting2.state(["selected"])

#labelframe53 = ttk.Label(frametab52, text=" ")
#labelframe53.grid(column=0, row=13, sticky="nsew")

vc2 = root.register(limitoverride)
vc3 = root.register(limitoverride2)

labeloverride = ttk.Label(frametab52, text="Manual .wav header length override:")
labeloverride.grid(column=0, row=14, sticky="w")

entryoverride = ttk.Entry(frametab52, validate="key", validatecommand=(vc2, "%P"))
entryoverride.grid(column=0, row=15, sticky="e")

labelentrybyte = ttk.Label(frametab52, text="Bytes:")
labelentrybyte.grid(column=0, row=15, sticky="w")

labelentrybyte = ttk.Label(frametab52, text=" ")
labelentrybyte.grid(column=0, row=16, sticky="nsew")

buttondir = ttk.Button(frametab52, text="Select custom .herb output directory", command=changedir)
buttondir.grid(column=0, row=17, sticky="w")

labeldelux0 = ttk.Label(frametab52, text=" ")
labeldelux0.grid(column=0, row=18, sticky="w")

checksoundcard = tk.Checkbutton(frametab52, cursor="hand2", variable=soundcardvar, onvalue=1, offvalue=0, text="Enable Soundcard pkg,\n disable Sounddevice pkg\n[Meant for Linux/Pulseaudio,\nprogram will restart]")
checksoundcard.grid(column=0, row=19, sticky="nsew")


if len(sys.argv) > 1:
    #checksoundcard.state(["selected"])
    checksoundcard.select()
else:
    pass


labeldelux01 = ttk.Label(frametab52, text=" ")
labeldelux01.grid(column=0, row=20, sticky="w")

#Keeping for reference.
##if sys.platform == "win32":
    ##checkexclusive = ttk.Checkbutton(frametab52, variable=exclusivevar, onvalue=1, offvalue=0, text="Exclusive mode\n(Windows only,\nSounddevice package only) )")
    ##checkexclusive.grid(column=0, row=21, sticky="w")
    
    ##labelexclusive = ttk.Label(frametab52, text=" ")
    ##labelexclusive.grid(column=0, row=22, sticky="w")
##else:
    ##pass


#if len(sys.argv) == 1:
    #apilist = [""]
    
    #for ac in range(0, len(sd.query_hostapis())):
        #apilist.append(str(ac+1) + ". " + str(sd.query_hostapis()[ac]['name']))
        
    #hostapi1.set(apilist[1])
    
    #labelapi0 = ttk.Label(frametab52, text="Host API:")
    #labelapi0.grid(column=0, row=23, sticky="w")
    
    ##optionapi = ttk.OptionMenu(frametab52, hostapi1, *apilist)
    ##optionapi.grid(column=0, row=24, sticky="w")
    
    #labelapi = ttk.Label(frametab52, text="")
    #labelapi.grid(column=0, row=25, sticky="w")   
#else:
    #pass

buttondelux = ttk.Button(frametab52, text="Delux mode on/off", width=18, command=lambda: delux())
buttondelux.grid(column=0, row=26, sticky="w")

labeldelux0 = ttk.Label(frametab52, text=" ")
labeldelux0.grid(column=0, row=27, sticky="w")

buttonhow = ttk.Button(frametab52, text="How To Use", width=18, command=lambda: howtouse())
buttonhow.grid(column=0, row=28, sticky="w")

labeldelux = ttk.Label(frametab52, text=" ")
labeldelux.grid(column=0, row=29, sticky="w")

buttonabout = ttk.Button(frametab52, style="Outline.TButton", text="Support me! / About", width=18, command=lambda: supporttime())
buttonabout.grid(column=0, row=30, sticky="w")

labeldelux = ttk.Label(frametab52, text="")
labeldelux.grid(column=0, row=31, sticky="w")

testframe = ttk.Frame(frametab52)
testframe.grid(column=0, row=32, sticky="nsew")

testtext = ttk.Label(testframe, text="Soundcard and speaker testing:")
testtext.grid(column=0, row=0, sticky="nsew", columnspan=50)

#width=18
buttontest = ttk.Button(testframe, text="Test 4.0 Channels", command=lambda: threading.Thread(target=testaudio, args=(0,0,)).start())
buttontest.grid(column=0, row=1, padx=0)

buttontest2 = ttk.Button(testframe, text="Test 4.0 Levels", command=lambda: threading.Thread(target=testaudio, args=(0,1,)).start())
buttontest2.grid(column=1, row=1, padx=2)

labeldelux2 = ttk.Label(frametab52, text="\n")
labeldelux2.grid(column=0, row=34, sticky="w")
#labelbutton0 = ttk.Label(frametab53, text=" ")
#labelbutton0.grid(column=0, row=29, sticky="nsew")

#Default.Tbutton, Outline.Tbutton, Ghost.TButton, Link.Tbutton?
#info, primary, secondary, success, warning, danger, light, dark
#bg, fg, selectbg, selectfg, border, inputbg, inputgb, active
buttonsubmitchannel = ttk.Button(frametab52, style="primary.TButton", text="         Save settings         ", command=lambda: channelchange(variablechannel.get(), variablechannel3.get(), variablechannel1.get(), entryoverride.get(), buffersetting.get()))
buttonsubmitchannel.grid(column=0, row=35, sticky="n")

#These 3 lines don't seem to do anything. So I just left the 1.
styler1 = tb.Style()
#styler1.configure("Outline.TButton", background="#3b5ea2", foreground="pink")
#styler1.configure("primary.TButton", background="pink")
#styler1.configure("Roundtoggle.Toolbutton", background="black", foreground="white")
  
labelsaved = ttk.Label(frametab52, text=" ")
labelsaved.grid(column=0, row=36, sticky="n")


if len(sys.argv) > 1:
    devicessc = "Sound card in use:\n" + str(sc.default_speaker())
    labelsoundcard = ttk.Label(frametab53,wraplength=450, text=devicessc)
    labelsoundcard.grid(column=0, row=31, sticky="w")
else:
    devicessd = sd.default.device[0]
    ddd = "Sound card in use:\n" + sd.query_devices()[devicessd]['name'] + ", Max output channels: " + str(sd.query_devices()[devicessd]['max_output_channels'])
    labelsoundcard = ttk.Label(frametab53, wraplength=450, text=ddd)
    labelsoundcard.grid(column=0, row=31, sticky="w")


labeldirbutton = ttk.Label(frametab53, text=" ")
labeldirbutton.grid(column=0, row=33, columnspan=50, sticky="w")

playblank0 = ttk.Label(frametab32, text="")
#playblank0.grid(column=0, row=0, sticky="nsew")

imagecounter = 0

try:
    currentdir0 = str(os.getcwd())
    #This is for single file pyinstaller with included data.
    ##filecheck = imagefind("Planet-text5.png")
    ##This is for local stored file. The OG way.
    #rp0 = "HerbSaucePlanet.png"
    rp00 = "HerbSaucePeppers.png"
    try:
        #Apparently this doesn't work at all. The os.path.abspath thing below does though.
        bp0 = sys._MEIPASS
        print("planet mei")
    except Exception as e:
        bp0 = os.path.abspath(".")
        print("planet no mei")
        #print(e)
        
    #filecheck0 = os.path.join(bp0, rp0)
    filecheck00 = os.path.join(bp0, rp00)
    #planetimage0 = tk.PhotoImage(file=filecheck0)
    planetimage00 = tk.PhotoImage(file=filecheck00)
    planetimagelabel = tk.Label(frametab32, image=planetimage00)
    #if deluxvar == 1:
    planetimagelabel.config(bg="black", borderwidth=0)
    #else:
        #planetimagelabel.config(bg="white", borderwidth=0)
    #planetimagelabel.image = planetimage
    print("herb image main")
    #On click change image. Keeping for reference.
    #planetimagelabel.bind("<Button-1>", lambda v: [imageincrease(), planetimagelabel.configure(image=planetimage0) if imagecounter%2 != 0 else planetimagelabel.configure(image=planetimage00)])
    
except Exception as e:
    print("no image main")
    print(e)
    planetimagelabel = tk.Label(frametab32, text="      herb sauce  \n\n\n", font=("Arial", 12))

#padx=10
planetimagelabel.grid(column=0, row=1)

def imageincrease():
    
    global imagecounter
    
    imagecounter = imagecounter + 1
    
    return

playnum = ttk.Label(frametab32, text="", font=('arial', 12))
playnum.grid(column=0, row=2, sticky="nsew")

playblank = ttk.Label(frametab32, text="\n\n\n")
playblank.grid(column=0, row=3, sticky="nsew")

playlabel = ttk.Label(frametab32, text="   Stopped")
playlabel.grid(column=0, row=4, sticky="nsew")

playlabel2 = ttk.Label(frametab32, font=(14), text="")
playlabel2.grid(column=0, row=5)

vollabel = ttk.Label(frametab32, text="\n\n\n\n\n\nVolume:")
vollabel.grid(column=0, row=6)

volumemenu = ttk.OptionMenu(frametab32, varvolume, *listvolumes, command=lambda v: volumechange(varvolume.get()))
volumemenu.grid(column=0, row=7)

blankchan = ttk.Label(frametab32, text="\n\n\n\n")
blankchan.grid(column=0, row=8, sticky="nsew")

chanlabel = ttk.Label(frametab32, text="Audio device")
chanlabel.grid(column=0, row=10, sticky="nsew")

chanlabel2 = ttk.Label(frametab32, text="max outputs: ")
chanlabel2.grid(column=0, row=12, sticky="nsew")

smanger = False

#Look for an audio device available with 4 (followed by 2) outputs minimum. Sometimes it picks the wrong one, or a virtual device that doesn't output audio.
if len(sys.argv) == 1:
    #If Win or Mac
    if sys.platform != "linux":
        d00 = sd.default.device[0]
        
        og = sd.query_devices()
        ogarray = []
        
        #If current audio device is already acceptable
        if og[d00]['max_output_channels'] >= 4:
            print("passing initial change of audio device")
            pass
        #Otherwise
        else:
            #Look for 4 channel or more audio device
            for qr in range(0, len(og)):
                if int(og[qr]['max_output_channels']) >= 4:
                    print("4 output device found. setting new audio device")
                    smanger = True
                    sd.default.device = qr
                    ddd = "Sound card in use:\n" + og[qr]['name'] + ", Max output channels: " + str(og[qr]['max_output_channels'])
 
                    labelsoundcard.config(text=ddd)
                    break
                else:
                    ogarray.append([qr, int(og[qr]['max_output_channels'])])
                    
            #Look for 2 channel or more audio device
            for qrr in range(0, len(og)):
                if smanger == True:
                    break
                if int(og[qrr]['max_output_channels']) >= 2:
                    print("2 output device found. setting new audio device")
                    sd.default.device = qrr
                    ddd = "Sound card in use:\n" + og[qrr]['name'] + ", Max output channels: " + str(og[qrr]['max_output_channels'])
 
                    labelsoundcard.config(text=ddd)
                    break
                else:
                    pass
    #If Linux
    else:
        pass
    
    d0 = sd.default.device[0]
    if sd.query_devices()[d0]['max_output_channels'] < 1:
        chanlabel3 = ttk.Label(frametab32, wraplength=120, foreground="red", text=str(sd.query_devices()[d0]['max_output_channels']) + "\n(Click 'Change audio device' in Settings tab, or check Use Soundcard package)")
    else:
        chanlabel3 = ttk.Label(frametab32, wraplength=120, text=sd.query_devices()[d0]['max_output_channels'])
    chanlabel3.grid(column=0, row=15, sticky="nsew")
elif len(sys.argv) > 1:
    chanlabel3 = ttk.Label(frametab32, wraplength=120, text=str(sc.default_speaker()))
    chanlabel3.grid(column=0, row=15, sticky="nsew")
    
ff = ""

wwidth = root.winfo_width
hheight = root.winfo_height

#GLOBAL
tabber = 0

def switchtab():
    global tabber
    
    #Focus on next tab. Or not.
    
    return
    
root.bind("<Control-o>", lambda v: openherb())
root.bind("<Control-p>", lambda v: threading.Thread(target=getherbinfo, args=(filename0, 1,)).start())
root.bind("<Control-s>", lambda v: threading.Thread(target=endherb, args=(samplerate00,)).start())
#root.bind("<Control-Tab>", lambda v: switchtab())

delux()

#Prefile parsing via arg loading or whatever
if fileparse != "":
    openherb(fileparse)
else:
    pass


#Doesn't seem to do anything. Sike. I moved it down here and now it does seem to do something.
#Double sike. It doesn't actually do anything it seems.
#labelopen0.focus()

#If no mainloop() here, but update()'s used, apparently it refreshes the program fine, but has UI problems.
root.mainloop()

#root.quit()

#Random shit
#def keyhandla(event):
    #print(event.char, event.keysym, event.keycode, event.x, event.y)
#root.bind("<Key>", keyhandla)
#root.bind("z", thing)
#root.bind("za1", lambda x: print("you pressed z then a then 1"))
#"<FocusIn>", "<FocusOut>"
#For entering and exiting frame: "<Enter>",  "<Exit>"

#Write HERB
#bb = bytearray(b'H')
#bbb = 'H'
#print(bb.hex())
#print(bb.decode())
#print(bb)
#bytes(bb).decode()       
#cc = "HERB"
#print(cc.encode('utf-8'))
