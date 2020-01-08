import cv2
import numpy as np
import ElemImage
import time
import threading

NUM_ROWPIXEL = 60
NUM_COLPIXEL = 160


class ElemAnalyser:
    # --- private members ---
    __pixelradius = 0   # pixel radius
    __pixelsize = 0     # diameter of pixel
    __pixelborder = 0   # distance between two pixels
    __height = 0  #
    __width = 0   #
    __canvashape = 0    # shape(size) of the canvas

    __elemimage = 0

    # --- public members ---
    # plan for colors
    GRAY = [102, 102, 102]
    WHITE = [255, 255, 255]
    BLACK = np.array([0, 0, 0], dtype=np.uint8)
    BLUE = [204, 153, 102]
    BROWN = [102, 153, 204]
    ORANGE = [0, 102, 204]

    # all pixels are drawn on the canvas
    canvas = 0
    def __init__(self, pixr=5, high=NUM_ROWPIXEL, width=NUM_COLPIXEL, border=-1):
        self.__pixelradius = pixr
        self.__pixelsize = self.__pixelradius * 2 + 1
        self.__pixelborder = border
        self.__height = high
        self.__width = width

        # init for shape of the canvas
        self.__canvashape = [
            self.__height * self.__pixelsize +
            (self.__height - 1) * self.__pixelborder,
            self.__width * self.__pixelsize +
            (self.__width - 1) * self.__pixelborder
            ]
        self.__canvashape.append(3)
        self.__canvashape = np.array(self.__canvashape)
        #print(self.__canvashape)
        
        # init for canvas
        self.canvas = np.full(self.__canvashape, self.WHITE, dtype=np.uint8)
        #print(self.canvas.shape)

    def loadimg(self, path=r'C:\Users\Administrator\Desktop\ElemAnalyser_SmartCar\swap\ElemImage.swp'):
        self.__elemimage = ElemImage.ElemImage(path)

    # 测试, 将会显示所有位置的像素点, 像素点为[黑色], 背景为[白色]
    def test(self, colr=BLACK):
        
        for row in range(self.__pixelradius,
                         self.__canvashape[0],
                         self.__pixelsize + self.__pixelborder):
            for col in range(self.__pixelradius,
                             self.__canvashape[1],
                             self.__pixelsize + self.__pixelborder):
                cv2.circle(self.canvas,(col, row), self.__pixelradius, colr, -1)
        
        winname = 'ElementAnalysis for Smart Car'
        cv2.namedWindow(winname)
        print(self.canvas.shape)
        cv2.imshow(winname, self.canvas)
        cv2.waitKey(0)
        cv2.destroyWindow(winname)
    def imshow(self):

        winname = ''        # 窗口名字

        if(self.__elemimage.isRGB == True):
            for row in range(0, self.__height):
                for col in range(self.__width):
                    color = self.__elemimage.getdata()[row][col]
                    # [int(x) for x in color]
                    cv2.circle(self.canvas,
                               (
                                   self.__pixelradius + col * (self.__pixelsize + self.__pixelborder),
                                   self.__pixelradius + row * (self.__pixelsize + self.__pixelborder)
                                ),
                               self.__pixelradius, [int(x) for x in color], -1)
            winname = 'ElementAnalysis for Smart Car - RGB'
        elif(self.__elemimage.isgray == True):
            for row in range(0, self.__height):
                for col in range(self.__width):
                    color = int(self.__elemimage.getdata()[row][col])
                    cv2.circle(self.canvas,(self.__pixelradius + col * (self.__pixelsize + self.__pixelborder),
                                            self.__pixelradius + row * (self.__pixelsize + self.__pixelborder)),
                               self.__pixelradius, [color, color, color], -1)
            winname = 'ElementAnalysis for Smart Car - Gray'



        cv2.namedWindow(winname)
        cv2.imshow(winname, self.canvas)
        cv2.waitKey(0)
        cv2.destroyWindow(winname)

    # 图像刷新显示
    def imrefresh(self, lock, cycle=1000):
        times = 1
        while True:
            lock.acquire()  # 加锁
            self.loadimg()
            lock.release()  # 解锁
            winame = ''
            if self.__elemimage.isRGB:
                winame = 'Element Analyzer for Smart Car - RGB'
                for row in range(0, self.__height):
                    for col in range(self.__width):
                        color = self.__elemimage.getdata()[row][col]
                        # [int(x) for x in color]
                        cv2.circle(self.canvas,
                                   (
                                       self.__pixelradius + col * (self.__pixelsize + self.__pixelborder),
                                       self.__pixelradius + row * (self.__pixelsize + self.__pixelborder)
                                    ),
                                   self.__pixelradius, [int(x) for x in color], -1)
                cv2.imshow(winame, self.canvas)
                print('[ElemAnalyser : 图像已刷新 {}]'.format(times))
                times += 1
                cv2.waitKey(cycle)


            if self.__elemimage.isgray:
                winame = 'Element Analyzer for Smart Car - gray'
                for row in range(0, self.__height):
                    for col in range(self.__width):
                        color = int(self.__elemimage.getdata()[row][col])
                        cv2.circle(self.canvas, (self.__pixelradius + col * (self.__pixelsize + self.__pixelborder),
                                                 self.__pixelradius + row * (self.__pixelsize + self.__pixelborder)),
                                   self.__pixelradius, [color, color, color], -1)
                cv2.imshow(winame, self.canvas)
                print('[ElemAnalyser : 图像已刷新 {}]'.format(times))
                times += 1
                cv2.waitKey(cycle)
            if self.__elemimage.isbin:
                winame = 'Element Analyzer for Smart Car - binary'
                pass

    def togray(self):
        self.__elemimage.RGB2gray()


if __name__ == '__main__':
    ea = ElemAnalyser(pixr=4, high=60, width=160, border=-1)

    ElemImage.ElemImage.RGB2hex(r'C:\Users\Administrator\Desktop\ElemImage_Straight_160x60.png',
                                r'C:\Users\Administrator\Desktop\ElemImage_Straight_160x60.swp')
    ts = time.time()
    ea.loadimg(r'C:\Users\Administrator\Desktop\ElemImage_Straight_160x60.swp')
    ea.togray()
    ea.imshow()
    te = time.time()

    print('Start Time : {}'.format(ts))
    print('End   Time : {}'.format(te))
    print('Time : {}'.format(te - ts))
