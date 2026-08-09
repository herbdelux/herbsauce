
## herb sauce 1.0.

herb sauce is an attempt at a program that converts .wav files into .herb files, and also plays them through your soundcard or audio interface. While a .herb file technically supports over 16 million channels of audio due to how its header strucutre works, the program itself supports 2, 4, and 6 channel creation and playback. The initial goal though was 4.0, front facing speakers, set up symetrically so: Speaker 1 and then 3 on the left, speaker 4 and then 2 on the right. See the speakers image in the main directory to see an example (although I recommend for sonic reasons that all 4 speakers be the same make and model, or at least hopefully the same size and wattage. I'm broke so I have two different makes and models with two different sized cones, but I think it still sounds great.)

When you have an extra stereo mix bus to play with in your mix, whether digital or analog, you end up with the potential to red line less, use less limiting and compressing (and possibly less EQ and filter depending on the situation), this increases dynamic range and texture depth without compromising loundness, and may even help you not lean on things like intelligent limits as much. On top of that, instead of say 8 tracks summing into a final 2 (L and R) which gives you a fidelity ratio of up to 1:4 of the original signals; now you can send 4 tracks into one stereo bus, and 4 into the other, giving you up to a 1:2 ratio of the original signal's fidelity before summing if that makes sense. Point is, I think it sounds like the better version of the stereo version. Not to mention, you can potentially play around and do some tricks like dry/wet via the two stereo busses, or even dueling bass lines without any competition in the low end (except your kicks or whatever) allowing you to get away with more stuff that just wouldn't mix down great in the stereo realm. 

Think about it like this: at a small music venue, the guitar has a dedicated amp and speaker (and isn't going into the mixer), just like the bass. The vocals has a dedicated mixer and PA system without any other signal competition, and the drums goes through the air. When it mixes in the air before hitting your ears, as opposed to mixing in a mixer first and summing together, it just sounds way more raw and better in my opinion; way more filled with the original energy and life. So going 4.0 front facing (again, no surround stuff going on) is attempting to get closer to a small venue fidelity, even for music that was made electronically.

I honestly think the 4.0 versions of my track are way closer to what I would "want you to hear" while I was making the song. Way more texture and dynamics, without any special effect or speaker positioning gimmicks like surround. The program also works via channel 1-2, 3-4, 5-6 etc, no more LF, CF, RF stuff that's not even very standardized in my opinion. 
### To compile:

### Windows
pyinstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --icon HerbSauceico2.ico --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py

### Mac
pyinstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --icon HerbSauceico2.icns --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py

## Linux
pyinstaller -F -w --add-data "speakers_small.png:." --add-data "HerbSaucePeppers.png:." --add-data "HerbSauceico2.png:." --hidden-import ttkbootstrap --hidden-import PIL --collect-all ttkbootstrap --collect-all PIL herbsauce.py


Things I want to add:
-Playlist support
-Storing your settings for the next use of the program.

Visit https://deluxeherbs.net to listen to and/or purchase (some of it is free) 4.0 (front facing) music in .herb format from original artists including myself. 