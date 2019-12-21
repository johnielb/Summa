## Johniel Bocacao
## 25 October 2017
## Summa
## by Flow Computing
## Version 4.0

# Random used to get rand ints for board and solutions
# Time used to calculate how long user takes -> score
# Colorsys used to convert HSV to RGB
# Json used to store and read dict
# OrderedDict used to order dict based on highest to lowest score
import random, time, colorsys, json
from tkinter import *
from collections import OrderedDict


class menuButton():
    """ Class for buttons that belong in menu, has variables for drawing coordinates,
    limit coordinates, image, text and leading screen"""

    def __init__(self, x, y, text, image, scr=0):
        # Top left coords
        self.x1 = x
        self.y1 = y
        # Bottom right coords for click limit
        self.xlim = x + 380
        self.ylim = y + 120
        # Bottom right coords for rectangle
        self.x2 = x + 120
        self.y2 = self.ylim
        # Path to icon
        self.imagePath = "data/" + image
        # Try get image
        try:
            # Tkinter image
            self.image = PhotoImage(file=self.imagePath)
        # If path doesn't exist then leave blank
        except TclError:
            self.image = PhotoImage()
            self.image.blank()
        # Button text
        self.text = text
        # Which screen button leads to
        self.scr = scr

        # Draw button
        rect = canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                       outline=fg, width=2)
        text = canvas.create_text(self.x1 + 165, self.y1 + 55, text=text, anchor=W,
                                  fill=fg, font=(body, 54))
        img = canvas.create_image(self.x1 + 60, self.y1 + 60, image=self.image)

    def click(self):
        if scr > 0:
            newScreen(self.scr)


class numberButton():
    """ Class for buttons that make up the game board, has variables necessary
    for drawing button and storing its current state on the board """

    def __init__(self, x, y, row, col, num, tru, sol):
        # Top left coords
        self.x1 = x
        self.y1 = y
        # Bottom right coords for rectangle
        self.x2 = x + 50
        self.y2 = y + 50
        # Bottom right coords for click limit
        self.xlim = self.x2
        self.ylim = self.y2
        # Where button is on array
        self.row = row
        self.col = col
        # Number button contains
        self.num = num
        # Whether button is part of solution
        self.tru = tru
        # num * tru
        self.sol = sol
        # Whether button is currently on
        self.on = False
        # Whether button has been locked by a hint
        self.hinted = False

        # Draw button
        self.circ = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, outline=fg, width=1)
        text = canvas.create_text(self.x1 + 25, self.y1 + 25, text=self.num, fill=fg, font=(body, 20))

    # Called when gameClick determines an object has been clicked
    def click(self):
        # If not locked
        if not self.hinted:
            # Swap False <-> True and adjust border likewise
            if not self.on:
                canvas.itemconfig(self.circ, width=2)
                self.on = True
            elif self.on:
                canvas.itemconfig(self.circ, width=1)
                self.on = False
            # Update total buttons
            totalButtons[self.row][0].click(self.col)
            totalButtons[self.col][1].click(self.row)

    # Called when getHint() chooses a button to lock
    def lock(self):
        # Lock it in
        self.hinted = True
        # Keep button on
        self.on = True
        # Adjust appearance
        canvas.itemconfig(self.circ, width=3)
        canvas.itemconfig(self.circ, outline="#ff5d59")
        # Update total buttons
        totalButtons[self.row][0].click(self.col, True)
        totalButtons[self.col][1].click(self.row)


class totalButton():
    """ Class for unclickable buttons at the end of the board's rows/columns
    that store the solution to the row/column """

    def __init__(self, order, num, pos, x, y):
        # How far down object is on grid
        self.order = order
        # Number to display
        self.num = num
        # Pos [0] = place on right; [1] = place on bottom
        self.isRow = True
        # Current sum on board
        self.sum = 0
        if pos == 1:
            self.isRow = False
        # Top left coords
        self.x1 = x
        self.y1 = y
        # Bottom right coords
        self.x2 = x + 50
        self.y2 = y + 50
        # Initiate new array for selected buttons
        self.selected = [];
        for i in range(len(arrGrid)):
            self.selected.append(0)
        self.isCorrect = False

        # Draw button
        self.circ = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, width=3)
        if self.num == 0:
            self.correct()
        else:
            self.reset()
        text = canvas.create_text(self.x1 + 25, self.y1 + 25, text=self.num, fill=fg, font=(body, 20))


    # When solution is met, adjust variables and appearance to be active
    def correct(self):
        self.isCorrect = True
        canvas.itemconfig(self.circ, outline="#2cc414")

    # When solution is not met, adjust variables and appearance to be inactive
    def reset(self):
        self.isCorrect = False
        canvas.itemconfig(self.circ, outline=fg)

    # Called after number buttons have been clicked so that this obj
    # can understand what happened
    def click(self, pos):
        if self.isRow:
            num = arrGrid[self.order][pos]
        else:
            num = arrGrid[pos][self.order]
        # flip state of selected button and adjust total accordingly
        if self.selected[pos] == 1:
            self.selected[pos] = 0
            self.sum -= num
        else:
            self.selected[pos] = 1
            self.sum += num
        # check if correct
        if self.sum == self.num:
            self.correct()
        else:
            self.reset()


def hslToRgb(hue):
    """ Converts HSV value to RGB so Tkinter can read it """
    h = (hue % 360) / 360
    r, g, b = colorsys.hsv_to_rgb(h, 0.45, 0.45)
    r = int(round(r * 255, 0))
    g = int(round(g * 255, 0))
    b = int(round(b * 255, 0))
    return "#%02x%02x%02x" % (r, g, b)


def changer(hue):
    """ Changes background colour by incrementing hue """
    bg = hslToRgb(hue)
    hue += 2
    canvas.config(background=bg)
    if scr == 1:
        for i in range(len(widgets)):
            widgets[i].config(bg=bg)
    exitButton.config(bg=bg, activebackground=bg)
    root.after(20, changer, hue)


def nameLimit(*args):
    """ Function loops to ensure that input doesn't go over char limit """
    val = tempName.get()[0:10]
    tempName.set(val)


def changeName(*args):
    """ Function error checks name (alphabetic, 15 or less) and stores
    if input is valid """
    global name
    check = tempName.get()
    if len(check) < 1 or (' ' in check) == True:
        error = "Please enter your first name."
    elif check.isalpha():
        name = check.lower()
        # Removes entry
        widgets[0].place_forget()
        newScreen(2)
        return
    else:
        # Sets and displays error
        error = "Please enter only letters."
    canvas.itemconfigure(errorTxt, text=error)
    # Clears entry
    widgets[0].delete(0, 'end')


def setDiff(choice):
    """ Function sets constants based on the user's choice in difficulty """
    # Easy
    if choice == 1:
        size = 4
        limit = 5
    # Medium
    elif choice == 2:
        size = 5
        limit = 8
    # Hard
    elif choice == 3:
        size = 6
        limit = 10
    return size, limit


def newBoard(size, limit):
    """ Function that creates new board for new game based on difficulty set """
    # Create number board with random numbers
    grid = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(random.randint(1, limit))
        grid.append(row)
    # Create accompanying truth board
    trues = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(random.randint(0, 1))
        trues.append(row)
    return grid, trues


def getHint():
    """ Get random button and reveal solution """
    global hint, hintCount
    hintCount += 1
    size = len(arrTrues)
    while True:
        # Get random coordinates
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        # Checks if there are no more hints to give out as all are set to 0
        noMoreHints = all(arrTrues[0] == i for i in arrTrues)
        # Get colour of hint button
        status = canvas.itemcget(hint, "fill")
        # If button is enabled then do etc
        if status == fg:
            if noMoreHints:
                break
            # If coordinate isn't a button that is part of solution, restart
            elif arrTrues[row][col] == 0:
                continue
            # If coordinate is part of solution, set to 0 and lock it in
            else:
                arrTrues[row][col] = 0
                widgets[row][col].lock()
                # Greys out hint
                canvas.itemconfig(hint, fill="#888888")
                # Waits 10 seconds until hint button is ungreyed
                root.after(5000, lambda: canvas.itemconfig(hint, fill=fg))
                break
        else:
            break


def menuClick(event):
    """ Function called when the user clicks in a menu screen """
    # Tells program which widget was last clicked    
    global clicked
    # Checks if the next button was clicked, separated from rest of code
    # as the for loop didn't like the Entry widget
    if scr == 1:
        if 300 <= event.x <= 400 and 480 <= event.y <= 520:
            changeName()
    else:
        # Checks if the widget in loop has been clicked
        for i in range(len(widgets)):
            try:
                # Check that the widget is a menu button,
                # there are widgets, and that the click is within the limit
                if (len(widgets) > 0 and widgets[i].x1 <= event.x <= widgets[i].xlim
                        and widgets[i].y1 <= event.y <= widgets[i].ylim):
                    clicked = widgets[i]
                    clicked.click()
            # Catch error in case the for loop hasn't updated its step range
            except IndexError:
                return
        # Checks if canvas text has been clicked
        # In main menu...
        if scr == 2:
            # Back to name screen
            if 100 <= event.x <= 380 and 620 <= event.y <= 680:
                newScreen(1)
        # In difficulty screen or high scores...
        if scr == 3 or scr == 8:
            # Back to main menu
            if 100 <= event.x <= 380 and 620 <= event.y <= 680:
                newScreen(2)


def gameClick(event):
    """ Function called when user clicks screen in game """
    # Tells program which widget was last clicked    
    global clicked
    # Checks if the widget in loop has been clicked
    for r in range(len(widgets)):
        for c in range(len(widgets)):
            w = widgets[r][c]
            if w.x1 <= event.x <= w.xlim and w.y1 <= event.y <= w.ylim:
                clicked = w
                clicked.click()
    # Checks if hint button has been clicked
    if 100 <= event.x <= 380 and 570 <= event.y <= 630:
        getHint()


def loopCorrect(array):
    """ Loops to click random buttons on tutorial screen
    Loops to check if answer is found in game """
    if scr == 4:
        # Get random button and click it to demonstrate
        row = random.randint(0, 1)
        col = random.randint(0, 2)
        array[row][col].click()
        # Repeat after 1 second
        root.after(1000, loopCorrect, array)
    elif scr == 6:
        # Check what values each total button has currently
        rowCheck = set(array[i][0].isCorrect for i in range(len(array)))
        colCheck = set(array[i][1].isCorrect for i in range(len(array)))
        # If the only values in each set are True, then game is beaten
        if rowCheck == {True} and colCheck == {True}:
            root.after(500, newScreen, 7)
        # Else recursion back around
        else:
            root.after(50, loopCorrect, array)


def scoring(time):
    # Size of grid = difficulty
    size = len(arrGrid)
    ''' Add: score for difficulty
     Base: maximum points for time
     Con: constant to adjust scalar in linear equation
     Div: controls gradient in linear equation '''
    # Easy
    if size == 4:
        add = 200
        base = 200
        con = 1.2
        div = 50
    # Medium
    elif size == 5:
        add = 400
        base = 300
        con = 4 / 3
        div = 60
    # Hard
    elif size == 6:
        add = 600
        base = 400
        con = 2
        div = 70
    hintDelta = hintCount * 50
    # Models a decreasing linear equation
    score = round((base * ((time * -1) / div) + con) + add, 0) - hintDelta
    # Prevents negative scores from appearing
    if score < 5:
        score = 5
    checkHighScores(score)
    return str(score).strip(".0")


def checkHighScores(score):
    """ Check if the user's score belongs in the top 10 """
    # Get high scores sorted in dict
    highScores = getHighScores()
    # Get lowest score in top 10
    minimum = list(highScores.items())[9]
    # If user already exists in high scores
    if name in highScores:
        # If new score exceeds current stored score,
        # store new score
        if score > highScores.get(name):
            highScores[name] = int(score)
        else:
            return
    else:
        # If new score exceeds 10th score,
        # store new score
        if score > minimum[1]:
            highScores.popitem()
            highScores[name] = int(score)
        else:
            return
    try:
        with open('data/hs.json', 'w') as hsFile:
            hsFile.write(json.dumps(highScores))
    # If file doesn't exist, return False
    except EnvironmentError:
        return


def getHighScores():
    """ Load json in folder and return it as a dict file """
    try:
        with open('data/hs.json') as hsFile:
            # Load JSON as dict and sort by highest score (desc)
            highScores = OrderedDict(sorted(json.load(hsFile).items(),
                                            key=lambda x: x[1], reverse=True))
            return highScores
    # If file doesn't exist, return empty array
    except EnvironmentError:
        return []


def newScreen(s):
    """ Function to call when screen needs to be erased and replaced
    [0] Splash screen
    [1] Name screen
    [2] Main menu
    [3] Difficulty
    [4] How to play
    [5] Loading
    [6] Game board
    [7] Finished
    [8] High scores """
    # Clear canvas and widgets
    canvas.delete(ALL)
    del widgets[:]
    # Allows other functions to know what screen is currently shown
    global scr
    scr = s
    if scr == 0:
        # Title text
        header = canvas.create_text(240, 315, text="summa", fill=fg,
                                    font=(heading, 90))
        sub = canvas.create_text(240, 400, text="by flow computing",
                                 fill=fg, font=(body, 37))
        # Waits 1 second before displaying next screen
        root.after(1000, newScreen, 1)
    elif scr == 1:
        # tempName is sent to nameLimit(), changeName()
        # errorTxt is sent to changeName() error checking
        global tempName, errorTxt
        tempName = StringVar()
        # Title text
        header = canvas.create_text(240, 100, text="hello!", fill=fg,
                                    font=(heading, 48))
        sub = canvas.create_text(240, 200, text="and you are?",
                                 fill=fg, font=(body, 28))
        # Sets and places entry, stores in array
        entry = Entry(root, textvariable=tempName, bg=bg,
                      fg=fg, borderwidth=0, font=(body, 20))
        entry.place(x=80, y=350, width=320, height=50)
        entry.bind("<Return>", changeName)
        widgets.append(entry)  # [0]
        tempName.trace("w", nameLimit)
        entryBorder = canvas.create_line(80, 400, 400, 400, fill=fg)
        # Sets and places button
        back = canvas.create_text(350, 500, text="next >", fill=fg,
                                  font=(body, 27))
        # Sets and places error
        errorTxt = canvas.create_text(80, 420, anchor=NW, fill="#ffaaaa", text="", font=(body, 20))
        # Binds left button click to menuClick event handler
        canvas.bind("<Button-1>", menuClick)
    elif scr == 2:
        global arrGrid, arrTrues, name, totalButtons
        # Initialise so that there is only 1 global declaration
        arrGrid, arrTrues, totalButtons = [], [], []
        # Title text
        header = canvas.create_text(240, 60, text="summa", fill=fg,
                                    font=(heading, 48))
        sub = canvas.create_text(240, 110, text="welcome " + name + "!", fill=fg,
                                 font=(body, 24))
        # Menu button to difficulty
        play = menuButton(50, 160, "play", "play.gif", 3)
        # Store in array[0]
        widgets.append(play)
        # Menu button to how to section
        howto = menuButton(50, 310, "how to", "howto.gif", 4)
        # Store in array[1]
        widgets.append(howto)
        # Menu button to high scores
        score = menuButton(50, 460, "scores", "scores.gif", 8)
        # Store in array[2]
        widgets.append(score)
        # Button to change name 
        back = canvas.create_text(240, 650, text="< change name", fill=fg,
                                  font=(body, 27))
    elif scr == 3:
        # Unbinds button enabled for name entry
        canvas.unbind("<Return>")
        header = canvas.create_text(240, 80, text="how difficult?", fill=fg,
                                    font=(heading, 44))
        # Menu button for easy 
        easy = menuButton(50, 160, "easy", "easy.gif", 5)
        # Store in array[0]
        widgets.append(easy)
        # Menu button for medium
        med = menuButton(50, 310, "med", "med.gif", 5)
        # Store in array[1]
        widgets.append(med)
        # Menu button for hard
        hard = menuButton(50, 460, "hard", "hard.gif", 5)
        # Store in array[2]
        widgets.append(hard)
        # Button to main menu
        back = canvas.create_text(240, 650, text="< back", fill=fg,
                                  font=(body, 27))
    elif scr == 4:
        header = canvas.create_text(240, 80, text="how to play", fill=fg,
                                    font=(heading, 44))
        # Menu button to difficulty
        sub = canvas.create_text(240, 175,
                                 text='Light up numbers on the grid\nso that they add up to the numbers\nnext to that '
                                      'row or column',
                                 fill=fg, justify=CENTER, font=(body, 18))
        # Preset the arrays
        arrGrid = [[3, 1, 2], [2, 4, 3], [3, 2, 1]]
        arrTrues = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
        arrSols = [[3, 1, 0], [2, 0, 3], [0, 2, 1]]
        arrTotals = [[4, 5], [5, 3], [3, 4]]
        # Adjust margins for a 3x3 grid
        incr = 70
        yVal = 250 - incr
        # Trial board distinct from widgets so board can't be clicked
        trialBoard = []
        for row in range(3):
            # Increment coordinates
            xVal = 110 - incr
            yVal += incr
            tempRow = []
            for cell in range(3):
                xVal += incr
                num, tru, sol = arrGrid[row][cell], arrTrues[row][cell], arrSols[row][cell]
                # Append button to temporary row
                tempRow.append(numberButton(xVal, yVal, row, cell, num, tru, sol))
            # Store temporary row
            trialBoard.append(tempRow)
        # Display total buttons for rows
        totalButtons = []
        # Reset coordinates
        yVal = 250 - incr
        xVal = 110 - incr
        for total in range(3):
            xVal += incr
            yVal += incr
            # Make total button for nth row
            rowButton = totalButton(total, arrTotals[total][0], 0, 320, yVal)
            # Figure out total of column
            colTotal = []
            for i in range(3):
                colTotal.append(arrTrues[i][total])
            # Make total button for nth column
            colButton = totalButton(total, arrTotals[total][1], 1, xVal, 460)
            # Append to arrays, dimensions: [n][0 - row / 1 - col]
            totalButtons.append([rowButton, colButton])
        play = menuButton(80, 550, "play", "play.gif", 3)
        # Store in array[0]
        widgets.append(play)
        # Set bottom row to set a clear example for user
        trialBoard[2][1].click()
        trialBoard[2][2].click()
        # Continuously check random buttons
        loopCorrect(trialBoard)
    elif scr == 5:
        global hintCount
        # Rebind left button click to gameClick event handler
        canvas.bind("<Button-1>", gameClick)
        # Sets text
        header = canvas.create_text(240, 360, text="let's play", fill=fg,
                                    font=(heading, 44))
        # Sets the grid size and limit based on what the user clicked
        if clicked.text == "easy":
            s, l = setDiff(1)
            arrGrid, arrTrues = newBoard(s, l)
        elif clicked.text == "med":
            s, l = setDiff(2)
            arrGrid, arrTrues = newBoard(s, l)
        elif clicked.text == "hard":
            s, l = setDiff(3)
            arrGrid, arrTrues = newBoard(s, l)
        # Reset hint count
        hintCount = 0
        # Waits 1 second before displaying next screen
        root.after(1000, newScreen, 6)
    elif scr == 6:
        global hint, startTime
        header = canvas.create_text(240, 80, text="summa", fill=fg,
                                    font=(heading, 48))
        # Hint button
        hint = canvas.create_text(240, 600, text="stuck?", fill=fg,
                                  font=(body, 27))
        # Stores numbers that are part of solution
        arrSols = []
        # Proxy for difficulty
        size = len(arrGrid)
        # Set margin increments
        # Easy
        if size == 4:
            incr = 82
        # Medium
        elif size == 5:
            incr = 66
        # Hard
        elif size == 6:
            incr = 55
        # Define 0th term
        yVal = 150 - incr
        # Display number buttons
        for row in range(size):
            # Temporary row for arrSols
            solRow = []
            # Temporary row for widgets
            widgetRow = []
            xVal = 50 - incr
            yVal += incr
            for cell in range(size):
                xVal += incr
                # Prepare values for adding into number buttons
                num, tru, sol = arrGrid[row][cell], arrTrues[row][cell], arrGrid[row][cell] * arrTrues[row][cell]
                # Add to respective temporary rows
                solRow.append(sol)
                widgetRow.append(numberButton(xVal, yVal, row, cell, num, tru, sol))
            # Add to respective arrays
            arrSols.append(solRow)
            widgets.append(widgetRow)
        # Calculate totals for side buttons
        arrTotals = []
        for row in range(size):
            # Reset counters
            totalRow = 0
            totalCol = 0
            for val in range(size):
                # Sum up solutions
                totalRow += arrSols[row][val]
                totalCol += arrSols[val][row]
            # Store in array, dimensions: [n][0 - row / 1 - col]
            arrTotals.append([totalRow, totalCol])
        # Reset 0th terms
        xVal = 50 - incr
        yVal = 150 - incr
        # Display total buttons for rows
        totalButtons = []
        for total in range(size):
            xVal += incr
            yVal += incr
            # Make total button for nth row
            rowButton = totalButton(total, arrTotals[total][0], 0, 380, yVal)
            # Make total button for nth column
            colButton = totalButton(total, arrTotals[total][1], 1, xVal, 480)
            # Append to arrays, dimensions: [n][0 - row / 1 - col]
            totalButtons.append([rowButton, colButton])
        # Get time user began playing
        startTime = time.time()
        # Loop to check the buttons add up
        loopCorrect(totalButtons)
    elif scr == 7:
        congrats = ["Congratulations!", "Well done!", "Good job!", "Wow!", "Amazing!"]
        congratsString = congrats[random.randint(0, len(congrats) - 1)]
        # Get total seconds user spent playing
        totalTime = time.time() - startTime
        # Convert score to string and remove leading zero
        score = str(scoring(totalTime))
        # Add score to congratulating text
        scoreString = "You scored " + score + " points!"
        header = canvas.create_text(240, 350, text=congratsString, fill=fg,
                                    font=(heading, 42))
        sub = canvas.create_text(240, 410, text=scoreString,
                                 fill=fg, font=(body, 30))
        # Rebind menu click event handler
        canvas.bind("<Button-1>", menuClick)
        # Back to menu
        root.after(5000, newScreen, 2)
    elif scr == 8:
        header = canvas.create_text(240, 80, text="high scores", fill=fg,
                                    font=(heading, 42))
        # Get high scores
        highScores = getHighScores()
        if highScores:
            # Set counter
            i = 1
            # Display high scores on GUI
            for uName, score in highScores.items():
                # Increments as new rows are added
                y = 115 + (45 * i)
                # Write rank, name and score
                canvas.create_text(70, y, text=i, fill=fg,
                                   anchor=E, font=(body, 24))
                canvas.create_text(100, y, text=uName, fill=fg,
                                   anchor=W, font=(body, 24))
                canvas.create_text(370, y, text=score, fill=fg,
                                   anchor=W, font=(body, 24))
                # Step the counter
                i += 1
        # If file is missing
        else:
            canvas.create_text(240, 360, text="High scores missing :(",
                               fill=fg, font=(body, 32))
        back = canvas.create_text(240, 650, text="< back", fill=fg,
                                  font=(body, 27))


def init():
    # Initialise GUI
    global root, canvas, widgets, exitButton
    # Set thematic constants
    global bg, fg, body, heading
    fg = "#ffffff"
    bg = "#%02x%02x%02x" % (41, 46, 74)
    body = "Franklin Gothic Book"
    heading = "Franklin Gothic Demi"
    # Array for all widgets in view, popped when not in view
    widgets = []
    root = Tk()
    root.title("Summa by Flow Computing")
    # Locks window size
    root.resizable(width=False, height=False)
    # Canvas 100% window
    canvas = Canvas(root, width=480, height=720, bg=bg)
    canvas.pack()
    # Create exit button
    exitButton = Button(root, text="X", command=root.destroy, bg=bg,
                        activebackground=bg, activeforeground=fg, fg=fg,
                        relief=FLAT, font=(heading, 20))
    exitButton.place(x=430, y=20, width=30, height=30)
    # Splash screen
    newScreen(0)
    # Start colour changer
    changer(0)
    root.mainloop()


init()
