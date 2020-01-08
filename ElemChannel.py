import ElemImage
import numpy as np
import serial
import time
import threading

com = 'COM15'
baudrate = 115200
timeout = 5

'''
with serial.Serial(com, baudrate, timeout=timeout) as serial_wireless:
    sum = 0
    while True:
        if serial_wireless.in_waiting:
            s = serial_wireless.read(serial_wireless.in_waiting)
            sum = sum + len(s)
            print(s)
            print(len(s))
            print('<    {}  >'.format(sum))
'''

class ElemChannel:
    # --- private members ---
    __comport = 'COM15'
    __baudrate = 115200
    __timeout = 2

    # --- public members ---
    channel = 0


    def __init__(self, comport='COM15', baudrate=115200, timeout=5):
        self.__comport = comport
        self.__baudrate = baudrate
        self.__timeout = timeout
        try:
            self.channel = serial.Serial(self.__comport, self.__baudrate, timeout=self.__timeout)
        except Exception as e:
            print("[异常 : 串口 {} 打开失败]".format(self.__comport), e)
            exit()

    # 保存为16进制的swp文件, 根据图像种类的不同, 存储的结构也会不同
    def save2hex(self, imgdata, dispath=r'C:\Users\Administrator\Desktop\ElemAnalyser_SmartCar\swap\ElemImage.swp',
                 height=ElemImage.ELEMIMAGE_HEIGHT, width=ElemImage.ELEMIMAGE_WIDTH):
        # print(type(imgdata))
        # if str.lower(imgtype) == 'rgb':
        #     buf = np.frombuffer(imgdata, dtype=np.uint8)
        #     buf = np.hstack([np.array([0x01, height, width], dtype=np.uint8),
        #                      buf
        #                      ]).tostring()
        #
        # elif str.lower(imgtype) == 'gray':
        #     buf = np.frombuffer(imgdata, dtype=np.uint8)
        #     buf = np.hstack([np.array([0x02, height, width], dtype=np.uint8),
        #                      buf
        #                      ]).tostring()
        #
        # elif str.lower(imgtype) == 'bin' or str.lower(imgtype) == 'binary':
        #     pass
        buf = imgdata
        with open(dispath, 'wb') as file:
            file.write(buf)

    # 实时监听串口数据, 以一整张图为单位接收数据
    def listen(self, lock):
        height = ElemImage.ELEMIMAGE_HEIGHT
        width = ElemImage.ELEMIMAGE_WIDTH

        header = 0
        flag_firstrcv = 0   # 用于标记一次传图的第一个数据流
        flag_timer = 0      # 用于标记一次传图的开始与结束
        datasize = 0
        rcvsize = 0
        data = bytes()

        while True:
            time.sleep(1)
            bufsize = self.channel.in_waiting
            if bufsize != 0:
                beingzero = 0
                if flag_timer == 0:
                    flag_timer = 1
                    ts = time.time()

                data += self.channel.read(bufsize)
                # 现在data是当前传图数据流中的第一个分组
                if flag_firstrcv == 0:
                    flag_firstrcv = 1
                    header = data[0]

                    if header == 0x01:
                        datasize = 3 * height * width + 3
                    elif header == 0x02:
                        datasize = height * width + 3
                    elif header == 0x03:
                        datasize = height * width / 8 + 3
                    else:
                        rcvsize = 0
                        print('[ElemChannel : 图传输标志头错误, 未知的图像类型]')
                        # exit()

                rcvsize += bufsize
                # print(bufsize)
                # print('Rcvsize : {}'.format(rcvsize))
                # print('Datasize : {}'.format(datasize))

            # 如果本次传输完成
            if rcvsize != 0 and rcvsize == datasize:
                te = time.time()
                flag_timer = 0
                flag_firstrcv = 0

                print('[ElemChannel : 已接收{}图像]'.format('RGB' if header == 0x01 else ('gray' if header == 0x02 else 'binary')))
                print('[应接收数据部分 : {}]'.format(datasize))
                print('[已接收数据部分 : {}]'.format(rcvsize))
                print('[本次用时 : {}]'.format(te - ts))
                rcvsize = 0
                lock.acquire()  # 加锁
                self.save2hex(data)
                lock.release()  # 解锁
                data = bytes()



    def test(self):
        while True:
            if(self.channel.in_waiting):
                temp = self.channel.read(self.channel.in_waiting)
                print(1, '->>>', len(temp))
            else:
                print(0)
            time.sleep(0.1)

if __name__ == '__main__':
    lock = threading.Lock()
    chal = ElemChannel()
    chal.listen(lock)