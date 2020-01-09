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
            time.sleep(0.1)
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
                        datasize = int(height * width / 8 + 3)
                    else:
                        print('[ElemChannel : 图传输标志头错误, 未知的图像类型]')
                        exit()

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
    def ForceListen(self, lock):
        header      = 0 # 标志头(Flags Header)
        height      = 0 # 图像高度
        width       = 0 # 图像宽度
        stdsize     = 0 # 图像标准尺寸, 根据header的变化而变化(Standerd Image Size)
        rcvsize     = 0 # 当前已接收数据的字节大小(Received Image Size)
        grpsize     = 0 # 当前串口缓存区域数据字节大小(Current Data Size in Serial Buffer)

        flg_frsrcv  = 1 # 首次接收图像的第一个分组的标志位, 也可能只有这一个分组(Flag for the First Image Data Group)
        flg_imgtimer= 0 # 一次图像传输的耗时计时器标志位(Flag for the Whole Image Timer)

        databuf     = bytes() # 数据存储缓存(Buffer for Data)

        vrftime_stt = time.time()
        vrftime     = 0 # 校验时间, 保存从上一个分组接收结束到下一个分组接收开始的间隔时间(Verify Time)
        overtime    = 0.3#若单片机发送数据间隔时间(处理时间 + 延时时间)是t, 电脑读取buffer的间隔时间是s, 那么overtime必须在s~t之间
        #flg_vrftimer= 0 # 校验计时器标志位()[0 : 计时已结束, 准备下一轮计时, 1 : 计时一开始, 准备计时结束]



        while True:
            time.sleep(0.1)
            grpsize = self.channel.in_waiting   # 存储当前串口缓存中的已存在字节大小
            if grpsize > 0:
                vrftime = time.time() - vrftime_stt
                if vrftime > overtime:      # 校验计时时间大于超时时间
                    print('[已超时 vt = {}]'.format(vrftime))
                    databuf = bytes()       # 说明数据正常或者是数据异常
                    rcvsize = 0
                    flg_frsrcv = 1          # 数据异常则手动将首次接收标志扳回1

                databuf += self.channel.read(grpsize)
                rcvsize += grpsize


                print('[  标志  : {}]'.format('头部分组' if flg_frsrcv == 1 else '普通分组'))
                print('[当前分组 : {}]'.format(grpsize))
                print('[已经接收 : {}]'.format(rcvsize))
                print('[标准接收 : {}]\n'.format(stdsize))

                if flg_frsrcv == 1:
                    flg_frsrcv = 0
                    header = databuf[0]
                    height = databuf[1]
                    width  = databuf[2]

                    if header == 0x01:
                        stdsize = 3 * height * width + 3
                    elif header == 0x02:
                        stdsize = height * width + 3
                    elif header == 0x03:
                        stdsize = int(height * width / 8 + 3)
                    else:
                        print('[ElemChannel : 图传输标志头错误, 未知的图像类型]')
                vrftime_stt = time.time()

            if rcvsize == stdsize and rcvsize >= 0:
                flg_frsrcv = 1
                rcvsize = 0
                lock.acquire()
                self.save2hex(databuf)
                lock.release()
                databuf = bytes()









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
    chal.ForceListen(lock)