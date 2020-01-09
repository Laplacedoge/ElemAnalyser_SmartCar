import ElemImage
import ElemAnalyser
import ElemChannel
import threading


import os
import time

SWPISREADY = True

lock = threading.Lock()     # 创建线程互斥锁

channel = ElemChannel.ElemChannel()
analyser = ElemAnalyser.ElemAnalyser(pixr=5)  # 创建分析器对象

thread_transmit = threading.Thread(target=channel.ForceListen, args=(lock,))
thread_refresh = threading.Thread(target=analyser.imrefresh, args=(lock, 500))


thread_transmit.start()
thread_refresh.start()

thread_transmit.join()
thread_refresh.join()