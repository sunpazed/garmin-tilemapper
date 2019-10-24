#!/usr/bin/python

from PIL import Image, ImageOps
import hashlib
import ctypes
import argparse
import math
from pathlib import Path

VERSION = '0.9.2'
DESCRIPTION = 'CIQ tilemapper {0} (c) 2017-2019 Franco Trimboli'.format(VERSION)

# globals
TILE_SIZE = 24
SCREEN_SIZE = 240
MAX_CHARS = 512

tileTable = []
hashTable = {}
charTable = []
charsToIgnore = [141]

charCurrent = 0
charOffset = 32

fontTileX = 0
fontTileY = 0

# command line defaults
debug = False
rotate = True
destinationResolution = 240
destinationFilename = 'destfont'
sourceFilename = 'souce.png'


def main():

    global tileTable
    global TILE_SIZE
    global destinationResolution
    global destinationFilename
    global debug

    args = parseArgs()

    if args.debug:
        debug = True

    # header
    print(DESCRIPTION)

    destinationResolution = abs(args.resolution)
    destinationFilename = args.output

    # Define the mode we are in, and target resolution
    print('Tile mode is {0}'.format(args.mode))
    print('Target resolution {0}x{0}'.format(destinationResolution))

    # number of chars we will use for our fontmap, 24x24 in this case
    totalCharsForTilemap = 24
    TILE_SIZE = args.tile_size

    # create a font canvas to store the processed tiles
    fontCanvas = newCanvas(TILE_SIZE*totalCharsForTilemap,TILE_SIZE*totalCharsForTilemap)

    # process input files
    filesToProcess = args.input

    if len(filesToProcess) > 1:
        print('Batch process {0} files'.format(len(filesToProcess)))

    # let's iterate through all the source files one by one
    for sourceFilename in filesToProcess:

        print('Input file to process "{0}"'.format(sourceFilename))

        # attempt to load the source image, and process it
        canvas = loadPNG(sourceFilename)

        if canvas:

            # print the details of the source image
            detailsCanvas(canvas)
            sanitiseCanvas(canvas)

            # we pre-process the canvas to prep it for processing
            canvas = preprocessCanvas(canvas)

            if args.mode == 'rotate':
                # angle function
                angleStart,angleStop,angleSteps = args.angle_begin, args.angle_end, args.angle_step
                processAngle(canvas,fontCanvas,angleStart,angleStop,angleSteps)
            else:
                # single frame function
                canvas = scaleCanvas(canvas,destinationResolution)
                processFrames(canvas,fontCanvas)

            print("\nDone")

    # have we processed any tiles, then save the destination font files
    if len(tileTable) > 0:

        filename = destinationFilename

        try:
            # save datafile, includes the JSON data for the tiles
            dataFile = generateDataFile()
            f = open(destinationFilename+'.json', 'w')
            f.write(str(dataFile))
            f.close()

            # save font description file
            fontFile = generateFontFile(destinationFilename)
            f = open(destinationFilename+'.fnt', 'w')
            f.write(str(fontFile))
            f.close()

            # save final tilemap image
            fontCanvas.save(filename+'.png', "PNG")
            print('Output saved as "{0}.fnt", "{0}.json", "{0}.png"'.format(filename))

        except Exception:
            print('ERROR: Cannot save files')

def parseArgs():

    global args
    global DESCRIPTION

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i','--input', nargs='+', required=True, help='input png file(s)')
    parser.add_argument('-o','--output', type=str, required=True, help='output file (png,fnt,json)')
    parser.add_argument("-m",'--mode', choices=['static', 'rotate'], default='static', type=str, help='\'static\' will process one or more static frames. \'rotate\' will rotate a frame')
    parser.add_argument("-r",'--resolution', default=240, type=int, help='resolution of target device')
    parser.add_argument("-d",'--debug', type=bool, nargs='?', const=True, default=False, help='turn debug mode on')
    parser.add_argument("-u",'--angle-begin', type=int, help='begin angle (rotate mode)')
    parser.add_argument("-v",'--angle-end', type=int, help='end angle (rotate mode)')
    parser.add_argument("-s",'--angle-step', type=int, help='step between angles (rotate mode)')
    parser.add_argument("-t",'--tile-size', type=int, default=24, help='tile size (experimental)')

    args = parser.parse_args()

    if (args.mode == 'rotate' and
        not (isinstance(args.angle_begin,int) and
        isinstance(args.angle_end,int) and
        isinstance(args.angle_step,int)
        )
        ):

        parser.error('The --mode (-m) argument in \'rotate\' requires the --angle-begin, --angle-end, and --angle-step arguments')

    return args

# process a single frame into tiles
def processFrames(canvas,fontCanvas):

        global TILE_SIZE

        numberOfFrames = 1

        currentFrame = 0

        tileArray = processTiles(canvas,TILE_SIZE,fontCanvas)
        tileTable.append(tileArray)

        currentFrame += 1;
        progress = '{:2.1%}'.format(currentFrame / numberOfFrames)

        print("Progress: {0}, frames: {1}, tiles: {2}".format(progress,len(tileTable),len(hashTable)), end="\r")

        if debug:
            print(tileTable)

        return

# rotate and process a multile frames into tiles
def processAngle(canvas,fontCanvas, angleStart, angleStop, angleSteps):

        global TILE_SIZE
        global destinationResolution

        numberOfFrames = len(range(angleStart, angleStop+angleSteps, angleSteps))

        print('{0} frame(s) to process '.format(numberOfFrames))

        currentFrame = 0

        for angle in range(angleStart, angleStop+angleSteps, angleSteps):
            currentCanvas = canvas.rotate(angle, Image.BILINEAR)
            currentCanvas = scaleCanvas(currentCanvas,destinationResolution)
            tileArray = processTiles(currentCanvas,TILE_SIZE,fontCanvas)
            tileTable.append(tileArray)

            currentFrame += 1;
            progress = '{:2.1%}'.format(currentFrame / numberOfFrames)

            print("Progress: {0}, frames: {1}, tiles: {2}".format(progress,len(tileTable),len(hashTable)), end="\r")

        if debug:
            print(tileTable)

        return


# display the details of the current image
def detailsCanvas(canvas):

    print('Format is {0}, resolution {1}x{2}, mode {3}'.format(canvas.format, canvas.size[0], canvas.size[1], canvas.mode))

    return

# load a png, store into a canvas
def loadPNG(filename):

    try:
        img = Image.open(filename)
        if debug:
            print('[loadPNG] loaded "{0}"'.format(filename))
        return img

    except:
        print('ERROR: Couldn\'t load "{0}" error...'.format(filename))
        return False

# crop image to smallest dimension to make it square
def preprocessCanvas(canvas):
    canvas = invertCanvas(canvas)
    return canvas

# TODO: check that the image is square, at least
def sanitiseCanvas(canvas):
    return

# scale image to destination
def scaleCanvas(canvas,newsize):
    return canvas.resize((newsize,newsize), Image.BILINEAR)

# invert the canvas as per the font spec
def invertCanvas(canvas):

    if canvas.mode == 'RGBA':
        r,g,b,a = canvas.split()
        rgb_image = Image.merge('RGB', (r,g,b))
        inverted_image = ImageOps.invert(rgb_image)
    else:
        inverted_image = ImageOps.invert(canvas)

    if debug:
        print(canvas.format, canvas.size, canvas.mode)

    return inverted_image

# send a valid tile to the font canvas
def pushToFontTiles(canvas,data,x,y):
    canvas.paste(data,(x,y))
    return

# check the tile for data, compare or store the hash
def checkTileForData(canvas):

    try:
        w = canvas.size[0]
        h = canvas.size[1]
        data = []
        hasData = 0;

        for u in range(w):
            for v in range(h):
                pixels = canvas.getpixel((u,v))
                data.append(pixels)
                hasData = hasData + sum(pixels[:3])

        # we hash the tile to check for duplicates
        if hasData:
            data_md5 = hashlib.md5(str(data).encode()).hexdigest()
            return data_md5

        else:
            return False

    except:
        return False

# fetch the next tile from the source canvas
def fetchTile(canvas,x,y):
    try:
        extents = (x*TILE_SIZE, y*TILE_SIZE, (x*TILE_SIZE)+TILE_SIZE, (y*TILE_SIZE)+TILE_SIZE)
        tile = canvas.crop(extents)
        return tile
    except:
        print('Problem fetching a tile...')
        return False

# TODO: check if tile already exists
def checkHashArray():
    return

# generate the .fnt file
def generateFontFile(filename):

    global hashTable
    global TILE_SIZE

    hashList = []

    for item in hashTable.values():
        hashList.append(item)

    sortedHash = sorted(hashList, key=lambda k: k['char'])

    lines = 'info face={0} size={1} bold=0 italic=0 charset=ascii unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0 outline=0\ncommon lineHeight={2} base={3} scaleW=256 scaleH=256 pages=1 packed=0\npage id=0 file="{4}.png"\nchars count={5}\n'.format(Path(filename).name,TILE_SIZE,TILE_SIZE,TILE_SIZE,Path(filename).name,len(sortedHash))

    for item in sortedHash:
        lines = lines + 'char id={0} x={1} y={2} width={3} height={4} xoffset=0 yoffset=0 xadvance={5} page=0 chnl=15\n'.format(str(item['char']),str(item['xc']*TILE_SIZE),str(item['yc']*TILE_SIZE),str(TILE_SIZE),str(TILE_SIZE),str(TILE_SIZE))

    return lines

# generate the .json file
def generateDataFile():

    global tileTable
    global TILE_SIZE

    groupData = []

    for group in tileTable:
        groupList = []
        for tile in group:
            packed = packData(tile['x'],tile['y'],tile['char'])
            groupList.append(packed)
        groupData.append(groupList)

    if debug:
        print(groupData)

    return groupData

# data in the json file is an array of signed 32-bit integers,
# and each integer is bit-packed as follows;
# 0b00000000000000000000111111111111 = font char, 12-bits
# 0b00000000001111111111000000000000 = x pos, 10-bits
# 0b11111111110000000000000000000000 = y pos, 10-bits
def packData(x,y,char):

    global TILE_SIZE

    dx = x*TILE_SIZE
    dy = y*TILE_SIZE

    ymask = 0xFFC00000
    xmask = 0x003FF000
    charmask = 0x00000FFF

    u = (char&charmask)|((dx<<12)&xmask)|((dy<<22)&ymask)

    return ctypes.c_int32(u).value

# create a new canvas, default colour is grey
def newCanvas(w,h):
    canvas = Image.new('RGB', (w, h), color = (128,128,128))
    return canvas

# process the current canvas, given the current tileSize, and send to destination fontCanvas
def processTiles(canvas,tileSize,fontCanvas):

    global charCurrent
    global hashTable
    global fontTileX
    global fontTileY
    global TILE_SIZE
    global MAX_CHARS

    canvasWidth = canvas.size[0]
    canvasHeight = canvas.size[1]

    uTiles = math.ceil(canvasWidth / tileSize)
    vTiles = math.ceil(canvasHeight / tileSize)

    tileArray = []

    try:

        # let's iterate across the canvas in the x, then y dimension
        for y in range(vTiles):
            for x in range(uTiles):

                # fetch a tile, and generate its hash
                currentTile = fetchTile(canvas,x,y)
                hashOfTile = checkTileForData(currentTile)

                # do we have a valid hash? great, then we have data
                if hashOfTile:
                    if debug:
                        print('[processTiles] got tile data at x:{0} y:{1} with hash:{2}'.format(x,y,hashOfTile))

                    thisChar = 0

                    # does this hash exist in the global hash table? then we have a duplicate
                    if hashOfTile in hashTable:
                        if debug:
                            print('[processTiles] collision with existing hash:{0}'.format(hashOfTile))

                        thisChar = hashTable[hashOfTile]['char']
                        thisTile = {'x':x, 'y':y, 'hash':hashOfTile, 'char':thisChar, 'xc':fontTileX, 'yc':fontTileY}
                        tileArray.append(thisTile)

                    # if not, looks like this is a new tile, so store it
                    else:
                        if debug:
                            print('[processTiles] appended hash:{0}'.format(hashOfTile))

                        # increment tile y pos, and start again
                        if (((fontTileX*TILE_SIZE)) >= fontCanvas.size[0]):
                            fontTileX = 0
                            fontTileY += 1

                        thisChar = charOffset+charCurrent
                        thisTile = {'x':x, 'y':y, 'hash':hashOfTile, 'char':thisChar, 'xc':fontTileX, 'yc':fontTileY}
                        tileArray.append(thisTile)

                        hashTable[hashOfTile] = { 'xc':fontTileX, 'yc':fontTileY, 'char':thisChar}

                        # let's push this tile to the destination fontCanvas
                        pushToFontTiles(fontCanvas,currentTile,fontTileX*TILE_SIZE,fontTileY*TILE_SIZE)

                        # increment the font char, and tile
                        charCurrent += 1
                        fontTileX += 1

                        # is this font char in the array of chars to ignore? then skip
                        while charCurrent in charsToIgnore:
                            charCurrent += 1


                # have we exceeded the maximum char size? if so, we quit
                if charCurrent > (MAX_CHARS):
                    print('ERROR: number of tiles have exceeded maximum size ({0}). Try breaking your files up, or use a larger tile size.'.format(MAX_CHARS))
                    quit()


        return tileArray

    except Exception as e:
        print('ERROR: {0}'.format(e))
        return False

main()
