import cv2
import numpy as np

def image_display(text,image):
    cv2.imshow(text, image)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    return
def image_edges(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #greyscale
    img_gb = cv2.GaussianBlur(img_gray, (5, 5), 0)
    edges = cv2.Canny(img_gb, 100 , 200)
    return edges

#===================================


def image_find_patterns(img,edges):
    ###variable initialization
    draw_img = img.copy()#display all found patterns output
    draw_save = img.copy()
    pattern_list = []
    found = []

    ###found all the contours in the image
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ##go thought every contours and search any hierarchy larger than or equal to 5
    #在轮廓列表中找到任何嵌套层数大约5的轮廓
    hierarchy = hierarchy[0]

    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:        #if a hierarchy is found, count up
            k = hierarchy[k][2]
            c = c + 1
        if c >= 5:
            found.append(i)                  #找到的轮廓

    ###build the rect
    #标记画出所有符合条件的轮廓  pattern_list: 包含所有符合条件轮廓box顶点坐标的list
    a = []
    for i in found:
        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(draw_img, [box], 0, (0, 255, 0), 2)
        for b in contours[i]:
            a.append(b)
    image_display('Position Indicator', draw_img)
    a = np.array(a)

    rect = cv2.minAreaRect(a)
    box = cv2.boxPoints(rect)
    box = np.array(box)

    #patter found
    draw_img = img.copy()
    cv2.polylines(draw_img, np.int32([box]), True, (0, 255, 0), 1)
    image_display('QR code found', draw_img)


    box = np.int32(box)
    crop_img = draw_save[box[1][0]:box[3][0],box[1][1]:box[3][1]]
    image_display('Pattern for Decoding', crop_img)

    return crop_img

def main(filename,savename):
    ###variable initialization
    b = []

    ###pre image process
    img = cv2.imread(filename)                    #load image
    edge = image_edges(img)                         #binarize and find edges

    ###find contours and
    qrImagege = image_find_patterns(img,edge)
    cv2.imwrite(savename,qrImagege)


