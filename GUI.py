#import time
import socket
#from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import cv2, numpy, time, csv, sys
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
#Set server ip address, port, buffer capacity


class MyApp(ttk.Frame):
    
    '''ボタンやキャンバスの設定、表示'''
    def __init__(self, root, controler):  

        root.geometry('1275x765')
        root.title("GUI_for_gaze input")

        self.recive_data = bytes()
        self.lock = threading.Lock()
        
        ###フレーム作成###
        ttk.Frame.__init__(self, root, width=1275, height=765, padding=10)

        ###背景画像用のキャンバス###
        self.cvs = tk.Canvas(self,width=1275,height=765)
        self.cvs.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

        ###シンボル作成###
        #前進シンボル
        img_forward = Image.open('forward_3d.png')
        img_forward = img_forward.resize((200, 100))
        img_forward = ImageTk.PhotoImage(img_forward)
        #停止シンボル
        img_stop = Image.open('stop_3d.png')
        img_stop = img_stop.resize((200, 200))
        img_stop = ImageTk.PhotoImage(img_stop)
        #cw旋回シンボル
        img_cw = Image.open('cw_3d.png')
        img_cw = img_cw.resize((150, 200))
        img_cw = ImageTk.PhotoImage(img_cw)
        #ccwシンボル
        img_ccw = Image.open('ccw_3d.png')
        img_ccw = img_ccw.resize((150, 200))
        img_ccw = ImageTk.PhotoImage(img_ccw)
        ######

        ###ボタン設置###
        #前進ボタン
        button_forward = tk.Button(
            self,
            image=img_forward,
            command=self.forward
        )
        self.img_forward = img_forward
        #button_forward['bg'] = root['bg']
        #貼り付け
        button_forward.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )
        #停止ボタン
        button_stop = tk.Button(
            self,
            image=img_stop,
            command=self.stop
        )
        self.img_stop = img_stop
        #貼り付け
        button_stop.place(
            x = 637,
            y = 655,
            width=200,
            height=200,
            anchor=tk.CENTER
        )
        #cw旋回ボタン
        button_cw = tk.Button(
            self,
            image=img_cw,
            command=self.cw
        )
        self.img_cw = img_cw
        #貼り付け
        button_cw.place(
            x = 1185,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )
        #ccw旋回ボタン
        button_ccw = tk.Button(
            self,
            image=img_ccw,
            command=self.ccw
        )
        self.img_ccw = img_ccw
        #貼り付け
        button_ccw.place(
            x = 67,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )

        ######
        '''動画表示''' 
        self.receive_img_data()
        self.disp_image()

    def receive_img_data(self):
        '''UDP'''
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #udp.bind(('192.168.143.133', 9999))
        udp.connect(('192.168.143.152', 9999))
        udp.send(('Hello Raspberry').encode("utf-8"))
        buff = 1024 * 64

        #self.recive_data = bytes()

        with self.lock:
            while True:
                # 送られてくるデータが大きいので一度に受け取るデータ量を大きく設定
                jpg_str, addr = udp.recvfrom(buff)
                is_len = len(jpg_str) == 7
                is_end = jpg_str == b'__end__'
                if is_len and is_end: break
                self.recive_data += jpg_str

            if len(self.recive_data) == 0:
                print("フレームなし")
                return

        #画像更新のために10msスレッドを空ける
        #self.disp_image()
        self.after(10, self.receive_img_data)
       

    '''1フレーム分のデータを受け取って表示する'''
    def disp_image(self):
        #time_sta = time.perf_counter()
        '''canvasに画像を表示'''

        if len(self.recive_data) == 0:
            print("フレームなし")
            return

        #time_sta = time.perf_counter()
        # string型からnumpyを用いuint8に戻す
        narray = numpy.frombuffer(self.recive_data, dtype='uint8')

        # uint8のデータを画像データに戻す
        img = cv2.imdecode(narray, 1)
        #cv2.imshow('recognaize', img)
        #cv2.waitKey(0)


        #BGR->RGB変換
        cv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


        # NumPyのndarrayからPillowのImageへ変換
        
        pil_image = Image.fromarray(cv_image)
    
        #画面のサイズにリサイズ
        pil_image = pil_image.resize((1275, 765))

        #PIL.ImageからPhotoImageへ変換する
        
        self.bg = ImageTk.PhotoImage(pil_image)

        #time_sta = time.perf_counter()
        #画像描画
        self.cvs.create_image(0,0,anchor='nw',image=self.bg)

        #time_end = time.perf_counter()
        #tim = time_end - time_sta
        #print(tim)

        
        #outfile = open('time_test_udp.csv', 'a', newline='')
        #writer = csv.writer(outfile)
        #writer.writerow([tim])

        #画像更新のために10msスレッドを空ける
        self.after(10, self.disp_image)

    '''文字列送信用'''
    def control(self, data):
        #time_sta = time.perf_counter()

        HOST='192.168.143.152'
        PORT=8080
        BUFFER=4096
            # Define socket communication type ipv4, tcp
        soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #connect to the server 
        soc.connect((HOST,PORT))
            #delay
        #time.sleep(1)
        if data == "exit":
            pass
        else:
            try:
                soc.send(data.encode("utf-8"))
            except ConnectionResetError:
                pass
        buf=soc.recv(BUFFER)
        
        #time_end = time.perf_counter()
        #tim = time_end - time_sta
        #print(tim)

        print(buf)

    '''ボタンごとの文字列を文字列送信用の関数controlに送る'''
    #ボタンforward
    def forward(self):
        print("前進")
        self.control("w")
    #ボタンright
    def cw(self):
        print("右旋回")
        self.control("d")
    #ボタンforward
    def ccw(self):
        print("左旋回")
        self.control("a")
    #ボタンstop
    def stop(self):
        print("停止")
        self.control("s")
    #ボタンstop
    def back(self):
        print("後進")
        self.control("x")

if __name__ == "__main__":

    root = tk.Tk()
    frame = MyApp(root, object())

    frame.pack()
    root.mainloop()
    with ThreadPoolExecutor(max_workers=3) as executor:
        while True:
            try:
                executor.submit(frame, frame.receive_img_data, frame.disp_image)
                '''
                executor.submit(frame.__init__)
                executor.submit(frame.receive_img_data)
                executor.submit(frame.disp_image)
                '''
            except KeyboardInterrupt:
                sys.exit()

    