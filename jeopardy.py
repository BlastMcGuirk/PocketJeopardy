import epd2in7
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
import random
from os import listdir
import json

# Keep track of the buttons on the e-Paper HAT
btn1 = Button(5)
btn2 = Button(6)
btn3 = Button(13)
btn4 = Button(19)

# HAT setup
epd = epd2in7.EPD()
epd.init()
print("Clearing and loading...")
epd.Clear(0xFF)

# Gets the font in a particular size
def getFont(size):
    return ImageFont.truetype('/home/pi/Jeopardy/Korinna-Regular.ttf', size)

# Get all the common fonts for the program
fontCategory = getFont(14)
fontEpisode = getFont(12)
fontValue = getFont(12)
fontClue = getFont(16)
fontAnswer = getFont(20)

# Toggle for whether or not the answer is showing
showAnswer = False

# Display the intro screen when the program is started
def printIntro():
    HImage = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)

    draw = ImageDraw.Draw(HImage)
    fontSmall = getFont(25)
    fontBig = getFont(40)

    # Draw a title screen
    draw.text((80, 40), "THIS  IS", font = fontSmall, fill = 0)
    draw.text((10, 80), "JEOPARDY!", font = fontBig, fill = 0)

    epd.display(epd.getbuffer(HImage))

# Display the intro screen
printIntro()

# Function to get the x coordinate of text that is centered
def getCenterX(text, draw, font):
    textSize = draw.textsize(text, font = font)[0]
    return (264 - textSize) / 2

# Function to get the x coordinate of text that is right aligned
def getRightX(text, dist, draw, font):
    textSize = draw.textsize(text, font = font)[0]
    return (264 - textSize) - dist

# Function to split up a line of text in to multiple lines based on the font size
def getMultiLines(text, draw, font):
    allWords = text.split(' ')
    
    lines = []
    start = 0
    # for each word
    for i in range(len(allWords)):
        # Add the word to the line
        line = ' '.join(allWords[start : i + 1])
        if (draw.textsize(line, font = font)[0] > 260):
            # If the line is too long to be displayed, it's an error
            if (start == i):
                print("FATAL ERROR... LINE TOO LONG")
            # Otherwise, the line is everything up to the last word added
            else:
                lines.append(' '.join(allWords[start : i]))
                # Start from the next word
                start = i
    # Add the last line
    lines.append(' '.join(allWords[start:]))
    return lines

# Display a clue to the screen
def displayJeopardyClue(clue):
    HImage = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)

    draw = ImageDraw.Draw(HImage)

    categoryX = getCenterX(clue['category'], draw, fontCategory)
    valueX = getRightX('$' + str(clue['value']), 2, draw, fontValue)

    # Header
    draw.text((categoryX, 2), clue['category'] + '  ', font = fontCategory, fill = 0)
    draw.line([(0, 22), (264, 22)], fill = 0)

    # Clue
    whatToShow = clue['answer'] if showAnswer else clue['clue']
    lines = getMultiLines(whatToShow.upper(), draw, fontClue)
    for i in range(len(lines)):
        lineX = getCenterX(lines[i], draw, fontClue)
        draw.text((lineX, 22 + (i * 18)), lines[i] + '  ', font = fontClue, fill = 0)
    
    # Footer
    draw.line([(0, 162), (264, 162)], fill = 0)
    draw.text((2, 162), clue['episode'].upper() + '  ', font = fontEpisode, fill = 0)
    draw.text((valueX, 162), '$' + str(clue['value']) + '  ', font = fontValue, fill = 0)

    epd.display(epd.getbuffer(HImage))

# Function to get a random clue from the list of shows (not included in repo)
def getRandomClue():
    # Get a random show file
    allShows = [f for f in listdir('/home/pi/Jeopardy/shows')]
    show = random.choice(allShows)
    # Read in the whole file
    with open('/home/pi/Jeopardy/shows/' + show, 'r') as read_file:
        showData = json.load(read_file)
    # Get a random clue from the file
    clue = random.choice(showData)
    clue['episode'] = clue['episode'].split('-')[0]
    return clue

# Start the program with a random clue
myClue = getRandomClue()

# Function to handle pressing buttons
def handleBtnPress(btn):
    pinNum = btn.pin.number
    global myClue
    global showAnswer

    # The first button
    if (pinNum == 5):
        # Hide any answers and display a new clue
        showAnswer = False
        myClue = getRandomClue()
        displayJeopardyClue(myClue)

    # The second button
    if (pinNum == 6):
        # Show the answer to the current clue
        showAnswer = not showAnswer
        displayJeopardyClue(myClue)

# Add button presses
btn1.when_pressed = handleBtnPress
btn2.when_pressed = handleBtnPress
btn3.when_pressed = handleBtnPress
btn4.when_pressed = handleBtnPress

# Keep looping! (probably a better way to do this...)
while True:
    x = 1 + 1
