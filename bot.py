'''
Created on Apr 18, 2020

@author: AJ Persaud
'''

import pyautogui
import time
import pytesseract
from math import sqrt, degrees, atan2
import os
import logging

#logging.basicConfig(filename=f'C:/Users/ajp47/Desktop/combatLogs/cb{time.strftime("%m%d%y.%H%M", time.localtime())}.txt',level=logging.INFO)
logging.info("Log created")
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True

#EDIT THIS Directory if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Time limit of program in seconds
TIMELIMIT = 28800
# EDIT BELOW AREA!!!!
# WANTEDGAGS: Each cell represents a gag type. The value of the cell is how many gags allowed to be had at once.
#                        COL
WANTEDGAGS =[#   Lvl 0  1  2  3  4  5  6
                    [0, 0, 0, 0, 0, 0, 0], #toonup 0
                    [0, 0, 0, 0, 0, 0, 0], #trap   1
                    [0, 0, 0, 0, 0, 0, 0], #lure   2
                    [0, 5, 5, 0, 0, 0, 0], #sound  3    ROW
                    [0, 0, 5, 5, 0, 0, 0], #throw  4
                    [0, 0, 5, 5, 0, 0, 0], #squirt 5
                    [0, 0, 0, 0, 0, 0, 0], #drop   6
            ]

PRIORITYLIST = [(3,2), (4,3), (5,3), (3,1), (4,2), (5,2), (4,1), (5,1)] 
# Tuples are (row, col) coordinates of the above table^
#
#STOP EDITING

# gag image paths
gp = [[(f'images/gags/{i}{j}.png', f'images/gags/{i}{j}o.png') for j in range(7)] for i in range(7)]
gpb = [[(f'images/gags/{i}{j}b.png', f'images/gags/{i}{j}ob.png') for j in range(7)] for i in range(7)]

gagList = []
gagListB = []
for pair in PRIORITYLIST:
    gagList.append(gp[pair[0]][pair[1]])
    gagListB.insert(0, gpb[pair[0]][pair[1]])

# coordinates. (x, y, and EXTRA)
# EXTRA determines if the Toon should move further than the x,y point,
# like when going through doors or portals.
gagShopEntrance = (-80, -91, 1)
gagShopExit = (0, 0, 0)
loopyEntrance = (-143, 7.5, 3)
backToPlayground = (-80, 100, 4)
homeDoor = (-56, -51, 5)
bank = (6.5, -20.2, 6)
loopyCircuit = [(-110, 90, 0), (-110, 50, 0), (-240, 50, 0), (-250, -15, 0), (-265, -30, 0), (-345, -35, 0), (-345, 115, 0), (-335, 115, 0), (-335, -25, 0), \
                (-265, -30, 0), (-250, -15, 0), (-250, 60, 0), (-120, 60, 0), (-120, 100, 0)]
TTCcentral = (-25, 10, 0)
fullCircuit  = [TTCcentral] + [loopyEntrance] + loopyCircuit*2

# waits for presence of some image. returns coords if found
def waitFor(image='images/book.png', regions = (1762, 902, 167, 150), length = 30, checkcombat=0):
    logging.info(f"Waiting for {image}")
    pyautogui.moveTo(360, 40)
    flag = None
    start = time.time()
    while not flag and time.time() - start < length:
        handleCrash()
        clickX()
        flag = checkBook(image, regions)
        if checkcombat:
            combatLoop()
    if flag:
        return flag
    else:
        logging.info(f"WaitFor failed")
        return None
# Returns coordinates of image if image is onscreen. Returns None if not.
# Default checks for the book image. Typically means that you are not in combat
def checkBook(image = 'images/book.png', regions = (1762, 902, 167, 150)):
    return pyautogui.locateCenterOnScreen(image, confidence = 0.8, region=regions)
# chooses gags and clicks arrows. Exits loop when out of combat.
def combatLoop(): 
    inCombat = False 
    if checkBook('images/pass.png', (1340, 560, 100, 100)):
        inCombat = True
        logging.info("entered combatLoop")
    while inCombat:
        #logging.info("trying to throw gags")
        handleCrash()
        waitFor('images/pass.png', (1340, 560, 100, 100), 10, 0)
        clickGag()
        clickArrow()
        # check if the Book is onscreen, means not in combat
        #logging.info("trying to find book")
        if checkBook():
            logging.info("Exited Combat Loop")
            inCombat = False 
            time.sleep(2) 
#clicks on gags in order of PRIORITYLIST. Attempts to pick gags that will reward XP
def clickGag():
    for pair in gagList:
        for gag in pair:
            butt = pyautogui.locateCenterOnScreen(gag, confidence = 0.99, region=(375, 250, 1125, 500))
            if butt: 
                pyautogui.click(butt)
                logging.info("Threw " + gag)
                return
    # if none are available
    for pair in gagListB:
        for gag in pair:
            butt = pyautogui.locateCenterOnScreen(gag, confidence = 0.99, region=(375, 250, 1125, 500))
            if butt: 
                pyautogui.click(butt)
                logging.info("Threw " + gag)
                return
def clickArrow():
    arrow = pyautogui.locateCenterOnScreen('images/arrow.png')
    if arrow:
        pyautogui.click(arrow)
        logging.info("Clicked arrow")
# used to exit fishing
def clickX():
    X = pyautogui.locateCenterOnScreen("images/X.png", confidence = 0.9, region=(1484, 935, 100, 63))
    if X: 
        pyautogui.click(X)
# goes to "next" coords based off of last coords
# theta is the angle relative to 0 degrees
#theta 2 is the angle needed to turn
# r is the distance needed to walk
#returns true if the movement was successfull
def goTo(nextC):
    logging.info("goTo")
    waitFor(checkcombat=1)
    current = ''
    tries = 0
    while not current and tries < 10:
        try:
            tries+=1
            current = readImg()
            x1, y1, h1 = current
        except:
            current=''
            turn(36)
    if not current:
        return False
    x2, y2, extra = nextC
    r = sqrt( (x2-x1)**2 + (y2-y1)**2 )
    theta = degrees( atan2(  y2-y1, x2-x1 ) ) - 90
    theta2 = (theta - h1) % 360
    if theta2 > 180:
        theta2-=360
    #logging.info("theta2 = " + str(theta2))
    turn(theta2)
    forward(r, extra)
    # checks if move was successful
    # accounts for if moved through doors
    try:
        if extra:
            return True
        current2 = readImg()
        xc, yc = current2[0], current2[1]
        return (abs(xc-x2) < 20 and abs (yc-y2) < 20)
    except:
        pass   
# Takes a screenshot of TTR debug info and finds current coords    
def readImg():
    if not waitFor(checkcombat=1):
        logging.warning('readImg could not checkBook')
        return False
    text = []
    pyautogui.hotkey('shift', 'f1')
    flag = pyautogui.locateOnScreen('images/H.png', region=(973, 232, 243, 260), confidence=0.8)

    if flag:
        img = pyautogui.screenshot(region=(977, 150, 243, 260))
        #img.save(f"C:/Users/ajp47/Desktop/Messing Around/my_image.png")
        text = pytesseract.image_to_string(img)
        text = text.split()
        #logging.info(text)
        textlist = list(filter(lambda x: "." in x, text))
        
        if len(textlist) >= 4:
            try:
                current = (float(textlist[0][1:]), float(textlist[1]), float(textlist[3]))
                logging.info("readImg found coordinates")
                return current
            except:
                logging.info("text couldn't be converted to double")
    return False
def turn(theta2):
    sec = (abs(theta2))/100
    if theta2 > 0:
        pyautogui.keyDown('left', _pause=0)
        time.sleep(sec)
        pyautogui.keyUp('left')
    else:
        pyautogui.keyDown('right', _pause=0)
        time.sleep(sec)
        pyautogui.keyUp('right')
def forward(r, extra=0):
    sec = int(r)/20
    if extra:
        sec += 2
    if sec > 2:
        pyautogui.keyDown('up', _pause=0)
        time.sleep(1)
        pyautogui.keyDown('ctrl', _pause=0)
        time.sleep(0.3)
        pyautogui.keyUp('ctrl', _pause=0)
        time.sleep(sec-1.5)
        pyautogui.keyUp('up', _pause=0)
    else:
        pyautogui.keyDown('up', _pause=0)
        time.sleep(sec)
        pyautogui.keyUp('up', _pause = 0)
def enterGame():
    waitFor('images/quitbutton.png', (1642, 938, 247,83), 60 )
    pyautogui.moveTo(925, 28)
    pyautogui.dragTo(925, 0, 1, button='left')
    pyautogui.click(925,462)
    waitFor('images/makeatoon.png', (1178, 583, 419, 327))
    time.sleep(1)
    pyautogui.click(533, 357)    
def handleCrash():
    yes = checkBook('images/yes.png', (560, 324, 790, 500))
    if yes:
        logging.info("Crashed... Handling")
        pyautogui.click(yes)
        enterGame()
        return True
    else:
        return False
def toPlayground():
    logging.info("toPlayground")
    book = waitFor(checkcombat=1)
    pyautogui.click(book)
    butt = waitFor('images/mapButt.png', (1387, 212, 71, 60))
    pyautogui.click(butt)
    TTC = waitFor('images/TTC.png', (662, 337, 775, 531))
    pyautogui.click(TTC)
    time.sleep(7)
def toBank():
    book = waitFor()  
    pyautogui.click(book)
    #butt = waitFor('images/mapButt.png', (1387, 212, 65, 60) )  
    #pyautogui.click(butt)
    home = waitFor('images/goHome.png', (937, 750, 188, 125))
    pyautogui.click(home)
    time.sleep(10)
    turn(345)
    forward(20)
    time.sleep(7)
    forward(10)
    goTo(bank)
    okButt = waitFor('images/ok.png', (1000, 500, 93, 300))
    for i in range(50):
        time.sleep(0.25)
        pyautogui.click(968, 594, _pause=0)
    pyautogui.click(okButt)
    toPlayground()
    return True
def gagStop():
    logging.info("gagStop")
    waitFor()
    success = False
    start = time.time()
    while not success and time.time()-start < 40:
        handleCrash()
        success = goTo(TTCcentral)
    if success:
        goTo(gagShopEntrance)
        time.sleep(10)
        pyautogui.keyDown('up')
        time.sleep(0.5)
        flag = None
        start = time.time()
        while not flag and time.time()-start <30:
            flag = checkBook('images/shop.png', (830, 80, 230, 100))
            turn(80)
            turn(-80)
        pyautogui.keyUp('up') 
        if flag:
            takeInventory()       
            butt = waitFor('images/doneShopping.png', (1310, 530, 210, 90))
            pyautogui.click(butt)
    toPlayground()
    return True
def takeInventory():
    #creates empty inventory matrix
    inventory = [[0 for i in range(7)] for i in range(7)]
    gagNums = [ 
              ['images/nums/0blue.png', 'images/nums/0orange.png'],
              ['images/nums/1blue.png', 'images/nums/1orange.png'],
              ['images/nums/2blue.png', 'images/nums/2orange.png'], 
              ['images/nums/3blue.png', 'images/nums/3orange.png'],
              ['images/nums/4blue.png', 'images/nums/4orange.png'],
              ['images/nums/5blue.png', 'images/nums/5orange.png', 'images/nums/5black.png'],
              ['images/nums/6blue.png', 'images/nums/6orange.png'],
              ['images/nums/7blue.png', 'images/nums/7orange.png'],
              ['images/nums/8blue.png', 'images/nums/8orange.png'],
              ['images/nums/9blue.png', 'images/nums/9orange.png'],
              ['images/nums/10black.png'],
              ]  
    #fills inventory matrix not working?? 
    for i in range(len(gagNums)):
        for j in range(len(gagNums[i])):
            coordsList = pyautogui.locateAllOnScreen(gagNums[i][j], confidence=0.9)
            for coord in coordsList:
                col = (coord[0]-800)//75
                row = (coord[1]-285)//50
                inventory[row][col] = i
    #if allowed > inventory, take some gags
    for row in range(len(inventory)):
        for col in range(len(inventory[0])):
            needed = WANTEDGAGS[row][col] - inventory[row][col]
            if needed > 0:
                for k in range(needed):
                    time.sleep(0.25)
                    pyautogui.click((col*75+800, row*50+285), _pause=0)
def walkingLoop():
    waitFor(checkcombat=1)
    tries = 0
    counter = 0
    while (counter < len(fullCircuit)) and (tries < 12):
        if handleCrash():
            return True
        tries+=1
        logging.info(f"Tries: {tries}")
        logging.info(f"attempting point {counter}, {fullCircuit[counter]}")
        success = goTo(fullCircuit[counter])
        if waitFor() and success:
            logging.info("Success")
            counter += 1
            tries = 0
        else:
            logging.info("Failed, trying again")
    toPlayground()
    #returns true if loop was complete
    return counter >= len(fullCircuit)
#the full, self sufficient bot loop.
#must begin in playground
def fullLoop():
    count = 0
    start = time.time()
    toPlayground()
    while count < 6 and start-time.time() < 1800:
        if count == 0:
            logging.info("BANK BEGIN")
            toBank()
            logging.info("BANK TERMINATED")        
        elif count == 1:
            logging.info("GAG STOP BEGIN")
            gagStop()
            logging.info("GAG STOP TERMINATED")
        elif count == 2:
            logging.info("WALKLOOP BEGIN")
            walkingLoop()
            logging.info("WALKLOOP TERMINATED")
        elif count == 3:
            logging.info("GAG STOP BEGIN")
            gagStop()
            logging.info("GAG STOP TERMINATED")
        elif count == 4:
            logging.info("WALKLOOP BEGIN")
            walkingLoop()
            logging.info("WALKLOOP TERMINATED")
        elif count == 5:
            logging.info("HEALING BEGIN")    
            for i in range(2):
                handleCrash()
                time.sleep(150)
                turn(180)
            logging.info("HEALING TERMINATED")
        count += 1

print("Hello, starting in 5 seconds")
time.sleep(5)
print("Running")
starttime = time.time()
for i in range(100):
    fullLoop()
    if time.time()-starttime > TIMELIMIT:
        break

