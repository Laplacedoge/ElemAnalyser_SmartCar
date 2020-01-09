# ElemImage类 : 用于存储智能车当前赛道的元素识别图像, 提供了读取图像功能

import numpy as np
import cv2
import time

ELEMIMAGE_HEIGHT = 60
ELEMIMAGE_WIDTH = 160

dftpath = r'C:\Users\Administrator\Desktop\ElemAnalyser_SmartCar\swap\ElemImage.swp'


class ElemImage:
    # --- private members ---
    __header = 0
    __height = 0
    __width = 0
    __data = 0

    # --- public members ---
    isRGB = False      # RGB图像标志
    isgray = False      # gray图像标志
    isbin = False      # binary图像标志

    def __init__(self, srcpath=dftpath):
        with open(srcpath, 'rb') as file:
            buf = file.read()
            print(len(buf))
            self.__header = buf[0]
            self.__height = buf[1]
            self.__width = buf[2]
            self.__data = buf[3:]
            del(buf)    # 可能我们的buf会有点儿大(^_^)!!!

            # [ElemImage标志头 __header 的各位含义] [0 : 置1时表示传过来的图是RGB图像] [7-1 : 未进行定义]
            # RGB图像的情况
            if self.__header == 0x01:
                self.isRGB = True
                self.isgray = False
                self.isbin = False

                if (len(self.__data) != self.__height * self.__width * 3):
                    print('[ElemImage : 读取swp(RGB)图像错误, 数据部分正确大小应是{}而实际读取大小是{}字节]'.
                          format(self.__height * self.__width * 3, len(self.__data)))
                    exit()

            # gray图像
            elif self.__header == 0x02:
                self.isRGB = False
                self.isgray = True
                self.isbin = False

                if (len(self.__data) != self.__height * self.__width):
                    print('[ElemImage : 读取swp(gray)图像错误, 数据部分正确大小应是{}而实际读取大小是{}字节]'.
                          format(self.__height * self.__width, len(self.__data)))
                    exit()

            # binary图像
            elif self.__header == 0x03:
                self.isRGB = False
                self.isgray = False
                self.isbin = True

                if (len(self.__data) != self.__height * self.__width / 8):
                    print('[ElemImage : 读取swp(binary)图像错误, 数据部分正确大小应是{}而实际读取大小是{}字节]'.
                          format(self.__height * self.__width / 8, len(self.__data)))
                    exit()
            else:
                print('[ElemImage : 读取swp图像头部错误, 未知的图像类型]')
                exit()
            print('[ElemImage : 成功读取swp({})图像, 数据部分读取大小是{}字节]'.
                  format('RGB' if self.isRGB else('gray' if self.isgray else 'binary'), len(self.__data)))
            if self.isRGB:
                reshapetuple = [self.__height, self.__width, 3]
            elif self.isgray:
                reshapetuple = [self.__height, self.__width]
            elif self.isbin:
                reshapetuple = [self.__height, int(self.__width / 8)]
            self.__data = np.frombuffer(self.__data, dtype=np.uint8).reshape(reshapetuple)  # __data转换成ndarray

    def getdata(self):
        return self.__data

    # 根据图片路径更新ElemImage对象
    def update(self, srcpath):
        self.__init__(srcpath=srcpath)

    # 转灰度
    def RGB2gray(self):
        tempdata = np.zeros([self.__height, self.__width])
        for row in range(0, self.__height):
            for col in range(0, self.__width):
                tempnum = round(0.11 * self.__data[row][col][0] + 0.59 * self.__data[row][col][1] + 0.3 * self.__data[row][col][2])
                if(tempnum > 255):
                    tempdata[row][col] = 255
                else:
                    tempdata[row][col] = tempnum
        self.__data = tempdata
        del tempdata
        self.isRGB = False
        self.isbin = False
        self.isgray = True

    # 以RGB显示ElemImage对象(需按下任意键退出)
    def imshow(self):
        if self.isRGB:
            reshapetuple = [self.__height, self.__width, 3]
        elif self.isgray:
            reshapetuple = [self.__height, self.__width]
        elif self.isbin:
            pass
        buf = self.__data.reshape(reshapetuple)
        winname = 'For imshow'
        cv2.namedWindow(winname)
        cv2.imshow(winname, buf)
        cv2.waitKey(0)
        cv2.destroyWindow(winname)

    # 以RGB刷新ElemImage对象
    def refresh(self):
        if self.isRGB:
            reshapetuple = [self.__height, self.__width, 3]
        elif self.isgray:
            reshapetuple = [self.__height, self.__width]
        elif self.isbin:
            pass
        buf = self.__data.reshape(reshapetuple)
        winname = 'For imshow'
        # cv2.namedWindow(winname)
        print(buf.shape)
        # cv2.destroyAllWindows()
        cv2.imshow(winname, buf)
        #time.sleep(1)
        cv2.waitKey(1000)
        # cv2.destroyWindow(winname)

    # 将RGB图片(需opencv支持的图片格式)转换成swp格式并存放(测试用)
    @staticmethod   # 静态函数
    def RGB2hex(srcpath, dispath):
        data = cv2.imread(srcpath)
        buf = np.array([0x01], dtype=np.uint8)  # __header 标志头
        buf = np.hstack([buf,
                         np.array(data.shape[0], dtype=np.uint8),   # __height 图像高度
                         np.array(data.shape[1], dtype=np.uint8),   # __width  图像宽度
                         data.reshape([data.shape[0] * data.shape[1] * data.shape[2]])  # __data 图像像素信息
                         ]).tostring()
        with open(dispath, 'wb') as file:
            file.write(buf)

    # RGB565到RGB888的转换
    @staticmethod
    def RGB565toRGB888(data, isimg=False):
        if ~isimg:
            val = data[0] * 256 + data[1]
            print(data[0])
            print(data[1])
            print(val)
            # R = (val >> 11) * 8
            # G = ((val & 0x07E0) >> 5) * 4
            # B = (val & 0x001F) * 8
            R = (val >> 11) << 3
            G = (val & 0x07E0) >> 3
            B = (val & 0x001F) << 3
            return (R, G, B)



if __name__ == '__main__':
    # ElemImage.RGB2hex(r'C:\Users\Administrator\Desktop\ElemImage_S-Bend_160x60.png',
    #                   r'C:\Users\Administrator\Desktop\ElemImage_S-Bend_160x60.swp')

    while True:
        img = ElemImage(srcpath=r'C:\Users\Administrator\Desktop\ElemImage_Straight_160x60.swp')
        img.refresh()

        time.sleep(0)

        img.update(srcpath=r'C:\Users\Administrator\Desktop\ElemImage_S-Bend_160x60.swp')
        img.refresh()

    # img = ElemImage(srcpath=dftpath)
    # img.imshow()

    # b = b'\x38\xe7'
    # print(b)
    # print(ElemImage.RGB565toRGB888(b))
