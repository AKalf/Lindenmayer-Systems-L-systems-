import sys
import json
import math

## Classes and functions for translating json input to drawing instructions for pen
class GrammarContainer(object): #container for json data
    def __init__ (self, inputFile):
        with open(inputFile) as json_file:  
            data = json.load(json_file)
            self.axiom = data["axiom"]
            print ("axiom: " + self.axiom)
            self.leftAngle = data["left_angle"]
            print ("left angle: " +  str(self.leftAngle))
            self.rightAngle =  data["right_angle"]
            print ("right angle: " + str(self.rightAngle))
            self.stepLength = data["step_length"]
            print ("step length: " +  str(self.stepLength))
            self.repetion =  data["order"]
            print ("order: " +  str(self.repetion))
            self.startingAngle =  data["start_angle"]
            print ("starting angle: " +  str(self.startingAngle))
            self.rules = {}
            for rule in data["rules"]:
                self.rules.update({rule : data["rules"][rule]})
            print("Rules: ")
            for x in self.rules:
                print(x + ": " + self.rules[x])
class MyPen(object): 
    def __init__ (self):
        self.xPos = 0
        self.Ypos = 0
def CreateLSystem (grammarContainer):
    startingString = grammarContainer.axiom
    endingString = ""
    for x in range(0, grammarContainer.repetion):
        endingString = processString(grammarContainer, startingString)
        #print("ending: " + endingString)
        startingString = endingString
    return endingString
def processString(grammarContainer, stringToProcess): #for each char of string apply rules
    newString = ""
    for char in stringToProcess:
        newString = newString + ApplyRules(grammarContainer, char)
    #print("New string: " + newString)
    return newString
def ApplyRules(grammarContainer, char): #checks if there is rule for char and returns the transformed char
    newString = ""
    for rule in grammarContainer.rules:
        if rule == char:
            #print (rule + " " + char)
            newString = grammarContainer.rules[rule]
            #print("transforming: " + char + " to: " + newString)
            return newString
        else:
            newString = char
    return newString
def TranslateStringToInstructions(myPen, grammarRules, finalString): #translate the string produced from grammar to algorithmic steps
    angle = grammarRules.startingAngle
    savedIndexes = [[],[],[]]
    init = False
    results = []
    for char in finalString:
        if char == "F" or char == "G":
            if init == False:        
                multi = math.cos(math.radians(angle))
                newX = grammarRules.stepLength * multi + myPen.xPos
                myPen.xPos = round(newX, 2)
                multi = math.sin(math.radians(angle))
                newY = grammarRules.stepLength * multi + myPen.Ypos
                myPen.Ypos = round(newY, 2)
                #print("(0, 0), (" + str(myPen.xPos) + ", " + str(myPen.Ypos) + ")")
                results.append("(0, 0), (" + str(myPen.xPos) + ", " + str(myPen.Ypos) + ")")
                init = True
            else:
                previousX = myPen.xPos
                multi = math.cos(math.radians(angle))
                newX = grammarRules.stepLength * multi + myPen.xPos
                myPen.xPos = round(newX, 2)
                previousY = myPen.Ypos
                multi = math.sin(math.radians(angle))
                newY = grammarRules.stepLength * multi + myPen.Ypos
                myPen.Ypos = round(newY, 2)
                #print("(" + str(previousX) + ", " + str(previousY) + "), (" + str(myPen.xPos) + ", " + str(myPen.Ypos) + ")")
                results.append("(" + str(previousX) + ", " + str(previousY) + "), (" + str(myPen.xPos) + ", " + str(myPen.Ypos) + ")")
        elif char == "+":
            angle += grammarRules.leftAngle
        elif char == "-":
            angle -= grammarRules.rightAngle
        elif char == "[":
                savedIndexes[0].append(myPen.xPos)
                #print ("Saved X: " + str(savedIndexes[0][-1]))
                savedIndexes[1].append(myPen.Ypos)
                #print("Saved Y: " + str (savedIndexes[1][-1]))
                savedIndexes[2].append(angle)
        elif char == "]":
                myPen.xPos = savedIndexes[0].pop()
                myPen.Ypos = savedIndexes[1].pop()
                #print("Retrieved coords: X: " + str(myPen.xPos) + ", Y: " + str(myPen.Ypos))
                angle = savedIndexes[2].pop()
    return results


## classes and functions used to create grammar from coordinates
class Edge(object): # a line between two points
    def __init__ (self, x1, y1, x2, y2):
        self.startX = x1 
        self.startY = y1
        self.endX = x2
        self.endY = y2
        self.isVertical = False
        if y1 != y2:
            self.isVertical = True
        self.isMarkOnRight = None
class GridBlock(object): # a grid block is defined from 4 edges
    def __init__ (self):
        self.edges = []
        edge = Edge(0,0,0,0)
        self.edges.append(edge)
        self.edges.append(edge)
        self.edges.append(edge)
        self.edges.append(edge)
        self.marked = False # if an edge points to this block
def FindMax(coords): #finds the max X and Y from the input coordinates
    maxX = 0
    maxY = 0
    for x in coords[0]:
        if x > maxX:
            maxX = x
    for y in coords[1]:
        if y > maxY:
            maxY = y
    r = [[],[]]
    r[0].append(int(maxX))
    r[1].append(int(maxY))
    return r
def FindDist(x1, y1, x2, y2): #find the distance (therefore step-length) between two points
    result = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
    return result
def CreateEdges(edgeLength, coords): #creates edges from input coordinates
    verticalEdges = []
    horizontalEdges = []
    maxX = FindMax(coords)[0][0]
    maxY = FindMax(coords)[1][0]
    for x in range(0, maxX,int(edgeLength)):
        for y in range(0, maxY,int(edgeLength)):
            newEdge = Edge(x, y, x, y+edgeLength)
            verticalEdges.append(newEdge)
            newEdge = Edge(x, y, x+edgeLength, y)
            horizontalEdges.append(newEdge)
    grid = [horizontalEdges, verticalEdges]
    return grid
def CreateGrid(edgeLength, coords): #create blocks and assign corresponding edges to them
    grid = CreateEdges(edgeLength, coords)
    verticalEdges = grid[1]
    horizontalEdges = grid[0]
    blocks = []
    for numOfBlocks in range(len(verticalEdges)):
        newBlock = GridBlock()
        blocks.append(newBlock)
    for index in range(len(blocks)-1):
        blocks[index].edges[0] = horizontalEdges[index]
        blocks[index].edges[3] = verticalEdges[index]
    for index in range(len(blocks)-1,0,-1):
        blocks[index].edges[1] = verticalEdges[index]
        blocks[index].edges[2] = horizontalEdges[index]
    return blocks
def FindEdge(x1, y1, x2, y2, grid): #find an edge from the grid. Program breakes here
    for edge in grid[0]:
        if edge.startX == x1 and edge.startY == y1 and edge.endX == x2 and edge.endY == y2:
            return edge
    for edge in grid[1]:
        if edge.startX == x1 and edge.startY == y1 and edge.endX == x2 and edge.endY == y2:
            return edge
    print("--------------ERROR---------")
    print("COULD NOT FIND EDGE")
    print("############################")
    return None
def FindBlocksOfEdge(edge, blocks): # returns the blocks this edge belongs to
    results = []
    for block in blocks:
        for blockEdge in block.edges:
            if edge == blockEdge:
                results.append(block)
    return results
def MyOpenFile(path): # Function that opens a file at location "path" and returns the text specified. If locating the file fails, user is asked to try again 

    try: # if file at location "path" opened sucessfully 
        with open(path, "r") as graphFile:			
            # take all the lines from the file and save them to the "text" var
            text = graphFile.readlines()
            graphFile.close()
            return text   
    except FileNotFoundError: # if file at location "path" fails to open
        print("file could not be opened")
        print("Write the full path of the file that contains the graph")
        path = input("") #save new path inserted from user
        return MyOpenFile(path, text) # try again to open file	
def CreateCoordsFromText (text): #translate the input coordinates from strings to intigers
    coordsList = [[],[]]
    for line in text:
        line = line.replace(' ', '')
        line = line.replace('(', '')
        line = line.replace(')', ',')
        coords = line.split(',')
        x1 = float(coords[0])
        y1 = float(coords[1])
        x2 = float(coords[2])
        y2 = float(coords[3])
        coordsList[0].append(x1)
        coordsList[1].append(y1)
        coordsList[0].append(x2)
        coordsList[1].append(y2)
    return coordsList
def FindPath(edgeLength, coords): #search all grid edges and store the ones defined by the input coordinates
    grid = CreateEdges(edgeLength, coords)
    verticalEdges = grid[1]
    horizontalEdges = grid[0]
    pathEdges = []
    for pathEdge in range(len(coords[0])-1):
        edge = FindEdge(coords[0][pathEdge], coords[1][pathEdge], coords[0][pathEdge+1], coords[1][pathEdge+1], grid)
        if edge is not None:
            pathEdges.append(edge)
    return pathEdges
def MarkEdges (pathEdges, coords, blocks): #proccess edges of the path and marks if they point to the left or right block. Steps: Find all edges at the boarders of the grid and mark them. Check if there are other path-edges on the block that has been marked. Force-point the edge to the block from the other side.
    maxX = FindMax(coords)[0]
    maxY = FindMax(coords)[1]
    for edge in pathEdges:
        if edge.isVertical == True:
            if edge.startX == 0 and edge.endX == 0:
                edge.isMarkOnRight = True
                edgeBlock = FindBlocksOfEdge(edge, blocks)
                edgeBlock[0].marked = True
                MarkNeighbours(pathEdges, edge, edgeBlock[0], blocks)
            elif edge.startX == maxX and edge.endX == maxX:
                edge.isMarkOnRight = False
                edgeBlock = FindBlocksOfEdge(edge, blocks)
                edgeBlock[0].marked = True
                MarkNeighbours(pathEdges, edge, edgeBlock[0], blocks)
        else:
            if edge.startY == 0 and edge.endY == 0:
                edge.isMarkOnRight = False
                edgeBlock = FindBlocksOfEdge(edge, blocks)
                edgeBlock[0].marked = True
                MarkNeighbours(pathEdges, edge, edgeBlock[0], blocks)
            elif edge.startY == maxY and edge.endY == maxY:
                edge.isMarkOnRight = True
                edgeBlock = FindBlocksOfEdge(edge, blocks)
                edgeBlock[0].marked = True
                MarkNeighbours(pathEdges, edge, edgeBlock[0], blocks)
def MarkNeighbours(pathEdges, currentEdge, edgeBlock, blocks):
    for otherPathEdge in pathEdges:
        for blockEdge in edgeBlock.edges:
            if otherPathEdge == blockEdge and blockEdge is not currentEdge:
                blockEdgesBlocks = FindBlocksOfEdge(blockEdge, blocks)
                for block in blockEdgesBlocks:
                    if block is not edgeBlock:
                        block.marked = True
                        MarkNeighbours(pathEdges, blockEdge, block, blocks)

mParam = False
dParam = False
inputFile = ""
outPutFile = "" 
print ("Arguments: " + str(len(sys.argv)))
for arg in sys.argv:
    print(str(arg))
if (len(sys.argv) == 2):                ## 1 Argument
    inputFile = sys.argv[1]
elif (len(sys.argv) == 3):              ## 2 Arguments
    if sys.argv[1] == "-m":
        mParam = True
        inputFile = sys.argv[2]
    elif sys.argv[1] == "-d":
        dParam = True
        inputFile = sys.argv[2]
    else:
        inputFile = sys.argv[1]
        outPutFile = sys.argv[2]
elif (len(sys.argv) == 4):              ## 3 Arguments
    if sys.argv[1] == "-m":
        mParam = True
        if sys.argv[2] == "-d":
            dParam = True
            inputFile = sys.argv[3]
        else:
             inputFile = sys.argv[2]
             outPutFile = sys.argv[3]
    elif sys.argv[1] == "-d":
        dParam = True
        inputFile = sys.argv[2]
        outPutFile = sys.argv[3]
elif (len(sys.argv) == 5):              ## 4 Arguments
    mParam = True
    dParam = True
    inputFile = sys.argv[3]
    outPutFile = sys.argv[4]
else:
    print("Write the full path of the input file")
    path = input("")
    print("you typed: "+ path)
if dParam == True: 
    grammarRules = GrammarContainer(inputFile)
    myPen = MyPen()
    finalString = (CreateLSystem(grammarRules))
    print("final string: " + finalString)
    results = TranslateStringToInstructions(myPen, grammarRules, finalString)
    if mParam == True:
        for x in results:
            print(x)
    if outPutFile is not "":
        file = open(outPutFile, "w") 
        for x in results:
            file.write(x + '\n') 
        file.close() 
else:
    text = MyOpenFile(inputFile)
    coords = CreateCoordsFromText(text)
    stepLength = FindDist(coords[0][0], coords[1][0], coords[0][1], coords[1][1])
    blocks = CreateGrid(int(stepLength), coords)
    path = FindPath(int(stepLength), coords)
    MarkEdges(path, coords, blocks)
    for edge in path:
        if edge.isMarkOnRight == True:
            print("R ")
        elif edge.isMarkOnRight == False:
            print("L ")
