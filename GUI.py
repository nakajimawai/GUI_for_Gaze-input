#import time
import socket
#from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import cv2, numpy, time, csv, sys
import threading, multiprocessing, queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
#Set server ip address, port, buffer capacity

q = queue.Queue()

class MyApp(tk.Tk):
    
    '''ボタンやキャンバスの設定、表示'''
    def __init__(self, *args, **kwargs):  

        tk.Tk.__init__(self, *args, **kwargs)

        #ウィンドウタイトル
        self.title("GUI_for_gaze input")

        #ウィンドウサイズ
        self.geometry('1275x765')
        
        #配置がずれないようにウィンドウのグリッドを1×1に設定
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #フレームごとで映像を表示するためのフラグ
        self.flag = '0'

#-----------------------------forward_frame------------------------------

        #前進画面フレーム作成
        self.forward_frame = ttk.Frame()
        self.forward_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs = tk.Canvas(self.forward_frame,width=1275,height=765)
        self.cvs.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

        ###シンボル作成###
        #前進シンボル
        self.img_forward = Image.open('forward_3d.png')
        self.img_forward = self.img_forward.resize((200, 100))
        self.img_forward = ImageTk.PhotoImage(self.img_forward)
        #停止シンボル
        self.img_stop = Image.open('stop_3d.png')
        self.img_stop = self.img_stop.resize((200, 200))
        self.img_stop = ImageTk.PhotoImage(self.img_stop)
        #cw旋回シンボル
        self.img_cw = Image.open('cw_3d.png')
        self.img_cw = self.img_cw.resize((150, 200))
        self.img_cw = ImageTk.PhotoImage(self.img_cw)
        #ccwシンボル
        self.img_ccw = Image.open('ccw_3d.png')
        self.img_ccw = self.img_ccw.resize((150, 200))
        self.img_ccw = ImageTk.PhotoImage(self.img_ccw)

        ######

        ###ボタン設置###
        #前進ボタン
        self.button_forward = tk.Button(
            self.forward_frame,
            image=self.img_forward,
            command=self.forward
        )
        #貼り付け
        self.button_forward.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )

        #停止ボタン
        self.button_stop = tk.Button(
            self.forward_frame,
            image=self.img_stop,
            command=self.stop
        )
        #貼り付け
        self.button_stop.place(
            x = 637,
            y = 660,
            width=200,
            height=200,
            anchor=tk.CENTER
        )

        #cw旋回ボタン
        self.button_cw = tk.Button(
            self.forward_frame,
            image=self.img_cw,
            command=self.cw
        )
        #貼り付け
        self.button_cw.place(
            x = 1185,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )

        #ccw旋回ボタン
        self.button_ccw = tk.Button(
            self.forward_frame,
            image=self.img_ccw,
            command=self.ccw
        )
        #貼り付け
        self.button_ccw.place(
            x = 67,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )
#----------------------------------------------------------------------
#-----------------------stop_frame-------------------------------------
        #停止時のフレームを作成
        self.stop_frame = ttk.Frame()
        self.stop_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_stop = tk.Canvas(self.stop_frame,width=1275,height=765)
        self.cvs_stop.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

         ###シンボル作成###       
        #前方向への画面遷移シンボル
        self.img_change_forward = Image.open('change_forward.png')
        self.img_change_forward = self.img_change_forward.resize((300, 150))
        self.img_change_forward = ImageTk.PhotoImage(self.img_change_forward)
        #後ろ方向への画面遷移シンボル
        self.img_change_back = Image.open('change_back.png')
        self.img_change_back = self.img_change_back.resize((300, 150))
        self.img_change_back = ImageTk.PhotoImage(self.img_change_back)
        #終了シンボル
        self.img_finish = Image.open('finish_letter.png')
        self.img_finish = self.img_finish.resize((150, 100))
        self.img_finish = ImageTk.PhotoImage(self.img_finish)

        ###ボタン設置###
        #前方画面に戻るボタン
        self.button_change_forward_frame = tk.Button(
            self.stop_frame,
            image=self.img_change_forward,
            command=lambda : [self.changePage(self.forward_frame), self.change_frame_flag("0")]
        )
        #貼り付け
        self.button_change_forward_frame.place(
            x = 637,
            y = 80,
            anchor=tk.CENTER
        )

        #後方画面に戻るボタン
        self.button_change_back_frame = tk.Button(
            self.stop_frame,
            image=self.img_change_back,
            command=lambda : [self.changePage(self.forward_frame), self.change_frame_flag("0")]
        )
        #貼り付け
        self.button_change_back_frame.place(
            x = 637,
            y = 680,
            anchor=tk.CENTER
        )

        #終了ボタン
        self.button_finish = tk.Button(
            self.stop_frame,
            image=self.img_finish,
            command=self.Finish
        )
        #貼り付け
        self.button_finish.place(
            x = 80,
            y = 720,
            width=150,
            height=110,
            anchor=tk.CENTER
        )
#--------------------------------------------------------------------------------------------------------
#------------------------------------後方フレーム---------------------------------------------------------



        #前進画面を最前面で表示
        self.forward_frame.tkraise()
        
                   
    '''1フレーム分のデータを受け取って表示する'''
    def disp_image(self):
        '''canvasに画像を表示'''
        
        #キューから画像データを取得
        data = q.get(block=True, timeout=None)

        # string型からnumpyを用いuint8に戻す
        narray = numpy.frombuffer(data, dtype='uint8')

        # uint8のデータを画像データに戻す
        img = cv2.imdecode(narray, 1)

        #BGR->RGB変換
        cv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # NumPyのndarrayからPillowのImageへ変換
        pil_image = Image.fromarray(cv_image)
    
        #画面のサイズにリサイズ
        pil_image = pil_image.resize((1275, 765))

        #PIL.ImageからPhotoImageへ変換する
        self.bg = ImageTk.PhotoImage(pil_image)

        #画像描画
        if self.flag == '0':
            self.cvs.create_image(0,0,anchor='nw',image=self.bg)
        elif self.flag == '1':
            self.cvs_stop.create_image(0,0,anchor='nw',image=self.bg)
        
        #キューのタスクが完了したことをキューに教える
        q.task_done()
        
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
        self.changePage(self.stop_frame)
        self.flag = '1'
        #self.control("s")
    #ボタンstop
    def back(self):
        print("後進")
        self.control("x")

    '''フレームごとで映像を表示し続けるために、フラグを変更する関数'''
    def change_frame_flag(self, frame_flag):
        self.flag = frame_flag

    '''画面遷移用の関数'''
    def changePage(self, page):
        #指定のフレームを最前面に移動
        page.tkraise()

    '''終了の関数'''
    def Finish(self):
        #destroy()クラスメソッドでtkinterウィンドウを閉じる
        self.destroy()
        #sys.exit()



def receive_img_data():
    '''ソケット通信で画像データを受信'''
    while True:
            #接続
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.connect(('192.168.143.152', 9999))
            udp.send(('Hello Raspberry').encode("utf-8"))

            #画像データ受信用の変数を用意
            buff = 1024 * 64
            recive_data =bytes()

            #画像データを分割して受け取り
            while True:
                # 送られてくるデータが大きいので一度に受け取るデータ量を大きく設定
                jpg_str, addr = udp.recvfrom(buff)
                is_len = len(jpg_str) == 7
                is_end = jpg_str == b'__end__'
                if is_len and is_end: break
                recive_data += jpg_str

                if len(recive_data) == 0:
                    print("受信失敗")
                    return
            
            #キューに画像データを追加
            q.put(recive_data)

            #キューから画像データが取り出されるまで処理をブロック
            q.join()



if __name__ == "__main__":

    root = MyApp()
    
    thread1 = threading.Thread(target=receive_img_data)
    thread1.start()
    root.disp_image()
    root.mainloop()


    