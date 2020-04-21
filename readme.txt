Before running bot.py, you need to:
1. pip install pyautogui
2. pip install pytesseract
3. Go to https://github.com/UB-Mannheim/tesseract/wiki
	and download appropriate pytesseract windows installer.
4. Edit constants such as TIMELIMIT, WANTEDGAGS, PRIORITYLIST
5. ToonTown must be put in Windowed Mode. Screen should be maximized.

This bot works by controlling mouse and keyboard input, not TTR itself.
You probably won't be able to multitask while bot is running.

Pixel coordinates are given as per pyautogui format: (left, top, length, height)

If bot handles a crash, it selects the character slot on the top left when logging back in.
If you need to change the character slot, edit enterGame()'s final pyautogui.click() arguments.
Change the pixel input to fit the appropriate chracter slot.

Some of my gag images are orange and do not match yours. 
If you want combat to work properly, you will need to screenshot the images of your gags and replace them in images/gags.
Sorry lol.

TOON/CHARACTER MUST BE VISIBLE STANDING BEFORE STARTING BOT.PY
