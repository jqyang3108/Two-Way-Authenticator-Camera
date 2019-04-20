import cv2, numpy
from PIL import Image

def printMatrix(matrix, type,name):

    if sum(matrix[int(len(matrix)/2)]) < 255:
        a = numpy.multiply(matrix, 255)
    else:
        a = matrix
    for row in a:
        print(row)
    gen = numpy.array(a, dtype=numpy.uint8)
    cv2.imshow(name, gen)
    cv2.waitKey(2000)
    cv2.destroyWindow(name)

def trim_white_space(matrix):

    isUsefulRow = False
    trimmedMatrix = []
    startPoint, endPoint = 0, 0
    for row in matrix:
        if isUsefulRow:
            if len(trimmedMatrix) == endPoint - startPoint:
                break
            trimmedMatrix += [row[startPoint: endPoint]]
        elif not rowIsWhiteSpace(row):
            isUsefulRow = True
            startPoint, endPoint = extract_end_points(row)
    matrix = trimmedMatrix

    return matrix
def rowIsWhiteSpace(row):
    for i in row:
        if i != 255:
            return False
    return True
def extract_end_points(firstRow):
    wastedSpace = 0
    for num in firstRow:
        if num == 255:
            wastedSpace += 1
        else:
            break
    lastBlackIndex, count = wastedSpace, wastedSpace
    for num in firstRow[wastedSpace:]:
        if num == 0:
            lastBlackIndex = count
        count += 1
    return (wastedSpace, lastBlackIndex)


def scale_matrix(matrix):
    ratio = find_ratio(matrix)
    scaledMatrix = []
    yCount = 0
    for row in matrix:
        if yCount % ratio == 0:
            xCount = 0
            newRow = []
            for value in row:
                if xCount % ratio == 0:
                    newRow += [value]
                xCount += 1
            scaledMatrix += [newRow]
        yCount += 1
    return scaledMatrix


def find_ratio(matrix):
    for row in matrix:
        scale = 0
        for num in row:
            scale += 1
            if num == 255:
                return scale // 7
    raise Exception("This image is not binary!")
#==========demask


def extractMaskPattern(matrix):
    maskPattern = matrix[8][2:5]
    #print('self.matrix in extract is', matrix)

    power = 1
    total = 0
    for i in maskPattern:
        if i == 0:
            total += power
        power <<= 1
    maskMatrix = []
    j = 0
    for row in matrix:
        i = 0
        newRow = []
        for val in matrix[j]:
            # print(i)
            if extractMaskNumberBoolean(total, i, j):
                newRow += [0]
            else:
                newRow += [1]
            i += 1
        j += 1
        maskMatrix += [newRow]
    #print('maskMatrix is ',maskMatrix)
    return maskMatrix

def extractMaskNumberBoolean(number, j, i):

        if number == 0:
            return (i * j) % 2 + (i * j) % 3 == 0
        elif number == 1:
            return i % 2 == 0
        elif number == 2:
            return ((i * j) % 3 + i + j) % 2 == 0
        elif number == 3:
            return (i + j) % 3 == 0
        elif number == 4:
            return (i / 2 + j / 3) % 2 == 0
        elif number == 5:
            return (i + j) % 2 == 0
        elif number == 6:
            return ((i * j) % 3 + i * j) % 2 == 0
        elif number == 7:
            return j % 3 == 0
        else:
            raise Exception("Unknown Mask Pattern")
def demask(matrix,mask):
    demaskedMatrix = []
    y = 0

    while y < len(matrix):
        row = []
        x = 0
        while x < len(matrix[0]):
            modifyValue = matrix[y][x]
            if (modifyValue == 255):
                modifyValue = 1
            row += [(~modifyValue + 2 ^ ~mask[y][x] + 2)]
            x += 1
        demaskedMatrix += [row]
        y += 1
    return demaskedMatrix

#decode


def decode(scaledMatrix,version,demaskedPattern):

    zig_zag_traversal = traverse_matrix(version,scaledMatrix,demaskedPattern)
    word = ""
    length = decode_bits(zig_zag_traversal, 4)

    #print('length', length)
    bytes = 8
    for i in range(int(length)):
        a = decode_bits(zig_zag_traversal, 12 + i * bytes)
        word += chr(int(a))
    return word

def traverse_matrix(version,scaled,demaskedPattern):
    traversal = []
    x, y, direction = len(scaled) - 1, len(scaled) - 1, -1
    #print(x,y,direction)
    #print(out_of_bounds(scaled,x, y),in_fixed_area(version,scaled,x, y))
    while True:
        if out_of_bounds(scaled,x, y):
            direction, y, x = -direction, y - 2, x - direction
        if not in_fixed_area(version,scaled,x, y):
            traversal += [demaskedPattern[x][y]]
        if y < 8:
            break
        elif y % 2 != 0:
            x, y = x + direction, y + 1
        else:
            y -= 1
    #print(traversal)
    return traversal

def decode_bits(traversal, start, number_of_bits=8):
    factor = 2 << (number_of_bits - 2)
    character = 0
    for i in traversal[start:start + number_of_bits]:
        character += i * factor
        if factor == 1:
            return character
        factor /= 2


def out_of_bounds(matrix,x, y):

    if x > len(matrix) - 1 or y > len(matrix) - 1:
        return True
    elif x < 0 or y < 0:
        return True
    elif x < 9 and (y < 9 or y >= len(matrix) - 8):
        return True
    elif x < 9 and y >= len(matrix) - 8:
        return True
    else:
        return False
def in_fixed_area(version,demaskedMatrix, x, y):
    within_orientation_markers = 0
    if version > 1:
        within_orientation_markers = x in range(len(demaskedMatrix) - 10 + 1, len(demaskedMatrix) - 5 + 1) and y in range(len(demaskedMatrix) - 10 + 1, len(demaskedMatrix) - 5 + 1)

    if within_orientation_markers:
        return True
    elif x == 6 or y == 6:
        return True


def main(filename):
    rawMatrix = numpy.asarray(Image.open(filename).convert('L')).tolist()
    matrix = trim_white_space(rawMatrix)
    printMatrix(rawMatrix, 'binary', 'Original QR Code')

    #printMatrix(matrix)
    scaleMatrix = scale_matrix(matrix)
    version = ((len(scaleMatrix) - 21) // 4) + 1
    #print('scale is ',scaleMatrix)
    printMatrix(scaleMatrix, 'binary', 'Scaled Image')

    #print mask pattern
    maskPattern = extractMaskPattern(scaleMatrix)
    #print('mask is',maskPattern)
    printMatrix(maskPattern,'binary','Mask Pattern')

    #print demasked pattern
    demaskedMatrix = demask(scaleMatrix,maskPattern)
    printMatrix(demaskedMatrix, 'binary', 'Demasked Pattern')

    #start decode
    print('============================================\n','Result: ',decode(scaleMatrix,version,demaskedMatrix),'\n============================================')

