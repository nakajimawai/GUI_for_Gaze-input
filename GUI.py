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

#受信する画像データをスレッド間で共有するためのキュー
q = queue.Queue()

msg_q = queue.Queue()
#前方カメラか後方カメラ、どちらを受け取る画像データにするか判断するための変数（F：前方、B：後方、M：Menu、S：停止中）
img_flag = 'M_F'

time_start = 0

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
        self.flag = 'M_F'

        self.str = 'first'
        
#-----------------------------menu_frame------------------------------

        #前方画面フレーム作成
        self.menu_frame = ttk.Frame()
        self.menu_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_menu = tk.Canvas(self.menu_frame,width=1275,height=765)
        self.cvs_menu.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

        ###シンボル作成###
        #走行開始シンボル
        self.img_start = Image.open('start.png')
        self.img_start = self.img_start.resize((250, 150))
        self.img_start = ImageTk.PhotoImage(self.img_start)

        #終了シンボル
        self.img_finish = Image.open('finish_letter.png')
        self.img_finish = self.img_finish.resize((150, 100))
        self.img_finish = ImageTk.PhotoImage(self.img_finish) 

        #走行開始ボタン
        self.button_start = tk.Button(
            self.menu_frame,
            image=self.img_start,
            command= self.start_running
        )
        #貼り付け
        self.button_start.place(
            x = 637,
            y = 280,
            width=240,
            height=145,
            anchor=tk.CENTER
        )

        #終了ボタン
        self.button_finish = tk.Button(
            self.menu_frame,
            image=self.img_finish,
            command=self.Finish
        )
        #貼り付け
        self.button_finish.place(
            x = 1195,
            y = 720,
            width=150,
            height=110,
            anchor=tk.CENTER
        )

#------------------------------------------------------------------------
#-----------------------------menu_back_frame------------------------------

        #後方メニューフレーム作成
        self.menu_back_frame = ttk.Frame()
        self.menu_back_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_menu_back = tk.Canvas(self.menu_back_frame,width=1275,height=765)
        self.cvs_menu_back.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

        ###シンボル作成###

        #後方の走行開始シンボル
        self.img_start_back = Image.open('start_back.png')
        self.img_start_back = self.img_start_back.resize((250, 150))
        self.img_start_back = ImageTk.PhotoImage(self.img_start_back)

        #後方の走行開始ボタン
        self.button_start_back = tk.Button(
            self.menu_back_frame,
            image=self.img_start_back,
            command= self.start_running
        )
        #貼り付け
        self.button_start_back.place(
            x = 637,
            y = 280,
            width=240,
            height=145,
            anchor=tk.CENTER
        )

        #終了ボタン
        self.button_finish = tk.Button(
            self.menu_back_frame,
            image=self.img_finish,
            command=self.Finish
        )
        #貼り付け
        self.button_finish.place(
            x = 1195,
            y = 720,
            width=150,
            height=110,
            anchor=tk.CENTER
        )
#-----------------------------forward_frame------------------------------

        #前方画面フレーム作成
        self.forward_frame = ttk.Frame()
        self.forward_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_forward = tk.Canvas(self.forward_frame,width=1275,height=765)
        self.cvs_forward.place(
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
        #前進ロックシンボル
        self.img_forward_lock = Image.open('forward_3d_lock.png')
        self.img_forward_lock = self.img_forward_lock.resize((200, 100))
        self.img_forward_lock = ImageTk.PhotoImage(self.img_forward_lock)
        #cw旋回ロックシンボル
        self.img_cw_lock = Image.open('cw_3d_lock.png')
        self.img_cw_lock = self.img_cw_lock.resize((150, 200))
        self.img_cw_lock = ImageTk.PhotoImage(self.img_cw_lock)
        #ccw旋回ロックシンボル
        self.img_ccw_lock = Image.open('ccw_3d_lock.png')
        self.img_ccw_lock = self.img_ccw_lock.resize((150, 200))
        self.img_ccw_lock = ImageTk.PhotoImage(self.img_ccw_lock)
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
            command=lambda : [self.changePage(self.stop_forward_frame), self.change_frame_flag("S_F"), self.stop()]
        )
        #貼り付け
        self.button_stop.place(
            x = 337,
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
#-----------------------stop__forward_frame-------------------------------------
        #前方走行中の停止時フレームを作成
        self.stop_forward_frame = ttk.Frame()
        self.stop_forward_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_stop_forward = tk.Canvas(self.stop_forward_frame,width=1275,height=765)
        self.cvs_stop_forward.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

         ###シンボル作成###       
        #前方向への画面遷移シンボル
        self.img_change_forward = Image.open('change_forward.png')
        self.img_change_forward = self.img_change_forward.resize((200, 100))
        self.img_change_forward = ImageTk.PhotoImage(self.img_change_forward)
        #後ろ方向への画面遷移シンボル
        self.img_change_back = Image.open('change_back.png')
        self.img_change_back = self.img_change_back.resize((200, 100))
        self.img_change_back = ImageTk.PhotoImage(self.img_change_back)
        #メニューへの画面遷移シンボル
        self.img_menu = Image.open('menu.png')
        self.img_menu = self.img_menu.resize((200, 100))
        self.img_menu = ImageTk.PhotoImage(self.img_menu)

        ###ボタン設置###
        '''ロボット操作ボタン'''
        #停止画面の前進ボタン
        self.button_stop_forward = tk.Button(
            self.stop_forward_frame,
            image=self.img_forward,
            command=lambda : [self.changePage(self.forward_frame), self.change_frame_flag("F"), self.forward()]
        )
        #貼り付け
        self.button_stop_forward.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )

        #停止画面のcw旋回ボタン
        self.button_stop_cw = tk.Button(
            self.stop_forward_frame,
            image=self.img_cw,
            command=lambda : [self.changePage(self.forward_frame), self.change_frame_flag("F"), self.cw()]
        )
        #貼り付け
        self.button_stop_cw.place(
            x = 1185,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )

        #停止画面のccw旋回ボタン
        self.button_stop_ccw = tk.Button(
            self.stop_forward_frame,
            image=self.img_ccw,
            command=lambda : [self.changePage(self.forward_frame), self.change_frame_flag("F"), self.ccw()]
        )
        #貼り付け
        self.button_ccw.place(
            x = 67,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )
        ''''''
        '''ロックボタン'''
        #停止画面の前進ロックボタン
        self.button_stop_forward_lock = tk.Button(
            self.stop_forward_frame,
            image=self.img_forward_lock,
        )
        #貼り付け
        self.button_stop_forward_lock.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )

        #停止画面のcw旋回ロックボタン
        self.button_stop_cw_lock = tk.Button(
            self.stop_forward_frame,
            image=self.img_cw_lock,
        )
        #貼り付け
        self.button_stop_cw_lock.place(
            x = 1185,
            y = 382,
            anchor=tk.CENTER
        )

        #停止画面のccw旋回ロックボタン
        self.button_stop_ccw_lock = tk.Button(
            self.stop_forward_frame,
            image=self.img_ccw_lock,
        )
        #貼り付け
        self.button_stop_ccw_lock.place(
            x = 67,
            y = 382,
            anchor=tk.CENTER
        )
        ''''''
        '''ロボット操作以外のボタン'''
        #後方画面に遷移するボタン
        self.button_change_back_frame = tk.Button(
            self.stop_forward_frame,
            image=self.img_change_back,
            command=lambda : [self.changePage(self.stop_back_frame), self.change_frame_flag("S_B")]
        )
        #貼り付け
        self.button_change_back_frame.place(
            x =1150,
            y = 682,
            anchor=tk.CENTER
        )
        #メニューへのボタン
        self.button_menu = tk.Button(
            self.stop_forward_frame,
            image=self.img_menu,
            command=lambda : [self.changePage(self.menu_frame), self.change_frame_flag("M_F")]
        )
        #貼り付け
        self.button_menu.place(
            x = 110,
            y = 682,
            width=190,
            height=100,
            anchor=tk.CENTER
        )
        ''''''
#--------------------------------------------------------------------------------------------------------
#------------------------------------back_frame---------------------------------------------------------
        #後方画面フレーム作成
        self.back_frame = ttk.Frame()
        self.back_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_back = tk.Canvas(self.back_frame,width=1275,height=765)
        self.cvs_back.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )

        ###シンボル作成###
        #後退シンボル
        self.img_back = Image.open('back_3d.png')
        self.img_back = self.img_back.resize((200, 100))
        self.img_back = ImageTk.PhotoImage(self.img_back)
        #後退ロックシンボル
        self.img_back_lock = Image.open('back_3d_lock.png')
        self.img_back_lock = self.img_back_lock.resize((200, 100))
        self.img_back_lock = ImageTk.PhotoImage(self.img_back_lock)
        ######

        ###ボタン設置###
        #後進ボタン
        self.button_back = tk.Button(
            self.back_frame,
            image=self.img_back,
            command=self.back
        )
        #貼り付け
        self.button_back.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )

        #停止ボタン
        self.button_stop = tk.Button(
            self.back_frame,
            image=self.img_stop,
            command=lambda : [self.changePage(self.stop_back_frame), self.change_frame_flag("S_B"), self.stop()]
        )
        #貼り付け
        self.button_stop.place(
            x = 337,
            y = 660,
            width=200,
            height=200,
            anchor=tk.CENTER
        )

        #cw旋回ボタン
        self.button_cw = tk.Button(
            self.back_frame,
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
            self.back_frame,
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
#-----------------------stop_back_frame-------------------------------------
        #後方走行中の停止時フレームを作成
        self.stop_back_frame = ttk.Frame()
        self.stop_back_frame.grid(row=0, column=0, sticky="nsew")

        ###背景画像用のキャンバス###
        self.cvs_stop_back = tk.Canvas(self.stop_back_frame,width=1275,height=765)
        self.cvs_stop_back.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )


        ###ボタン設置###

        #後進ボタン
        self.button_back = tk.Button(
            self.stop_back_frame,
            image=self.img_back,
            command=lambda : [self.changePage(self.back_frame), self.change_frame_flag("B"), self.back()]
        )
        #貼り付け
        self.button_back.place(
            x = 637,
            y = 50,
            anchor=tk.CENTER
        )

        #cw旋回ボタン
        self.button_cw = tk.Button(
            self.stop_back_frame,
            image=self.img_cw,
            command=lambda : [self.changePage(self.back_frame), self.change_frame_flag("B"), self.cw()]
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
            self.stop_back_frame,
            image=self.img_ccw,
            command=lambda : [self.changePage(self.back_frame), self.change_frame_flag("B"), self.ccw()]
        )
        #貼り付け
        self.button_ccw.place(
            x = 67,
            y = 382,
            width=150,
            height=200,
            anchor=tk.CENTER
        )

        #前方停止画面に遷移するボタン
        self.button_change_forward_frame = tk.Button(
            self.stop_back_frame,
            image=self.img_change_forward,
            command=lambda : [self.changePage(self.stop_forward_frame), self.change_frame_flag("S_F")]
        )
        #貼り付け
        self.button_change_forward_frame.place(
            x = 950,
            y = 682,
            anchor=tk.CENTER
        )
        #後方メニューへのボタン
        self.button_menu = tk.Button(
            self.stop_back_frame,
            image=self.img_menu,
            command=lambda : [self.changePage(self.menu_back_frame), self.change_frame_flag("M_B")]
        )
        #貼り付け
        self.button_menu.place(
            x = 110,
            y = 682,
            width=190,
            height=100,
            anchor=tk.CENTER
        )
#--------------------------------------------------------------------------------------------------------

        #メニュー画面を最前面で表示
        self.menu_frame.tkraise()
        
                   
    '''1フレーム分のデータを受け取って表示する'''
    def disp_image(self):
        '''canvasに画像を表示'''
        #time_sta = time.perf_counter()
        #キューから画像データを取得
        
        data = q.get(block=True, timeout=None)

        # string型からnumpyを用いuint8に戻す
        narray = numpy.frombuffer(data, dtype='uint8')

        # uint8のデータを画像データに戻す
        img = cv2.imdecode(narray, 1)

        #エラー処理
        if img is None:
            print("受け取りエラー")
            q.task_done()
        else:
            #BGR->RGB変換
            cv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # NumPyのndarrayからPillowのImageへ変換
            pil_image = Image.fromarray(cv_image)
        
            #画面のサイズにリサイズ
            pil_image = pil_image.resize((1275, 765))

            #PIL.ImageからPhotoImageへ変換する
            self.bg = ImageTk.PhotoImage(pil_image)

            #画像描画
            if self.flag == 'F':
                self.cvs_forward.create_image(0,0,anchor='nw',image=self.bg)
            elif self.flag == 'S_F':
                self.cvs_stop_forward.create_image(0,0,anchor='nw',image=self.bg)
            elif self.flag == 'B':
                self.cvs_back.create_image(0,0,anchor='nw',image=self.bg)
            elif self.flag == 'S_B':
                self.cvs_stop_back.create_image(0,0,anchor='nw',image=self.bg)         
            elif self.flag == 'M_F':
                self.cvs_menu.create_image(0,0,anchor='nw',image=self.bg)
            elif self.flag == 'M_B':
                self.cvs_menu_back.create_image(0,0,anchor='nw',image=self.bg)          
            
            #キューのタスクが完了したことをキューに教える
            q.task_done()
            #time_end = time.perf_counter()
            #tim = time_end - time_sta
            #print("メイン："+str(tim))
            #画像更新のために10msスレッドを空ける
        self.after(10, self.disp_image)

    
    '''文字列送信用'''
    def control(self, data):
        #time_sta = time.perf_counter()

        HOST='192.168.11.26'
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
    #ボタンback
    def back(self):
        print("後進")
        self.control("x")
    #ボタン走行開始
    '''後方走行時 → メニュー画面 → 走行開始 を選んだ場合も後方カメラ映像を映すため'''
    def start_running(self):
        print("走行開始")
        self.control("run")
        if self.flag == "M_F":
            self.stop_forward_frame.tkraise()
            self.change_frame_flag("S_F")
        elif self.flag == "M_B":
            self.stop_back_frame.tkraise()
            self.change_frame_flag("S_B")

    '''フレームごとで映像を表示し続けるために、フラグを変更する関数'''
    def change_frame_flag(self, frame_flag):
        global img_flag

        self.flag = frame_flag
        img_flag = frame_flag

    '''画面遷移用の関数'''
    def changePage(self, page):
        #指定のフレームを最前面に移動
        page.tkraise()

    '''終了の関数'''
    def Finish(self):
        self.control("fin")
        #destroy()クラスメソッドでtkinterウィンドウを閉じる
        self.destroy()
        #sys.exit()

    '''ボタンロック用の関数'''
    def lock_button(self):
        global time_start

        if not msg_q.empty():
            laser_msg = msg_q.get(block=True, timeout=True)
            print(laser_msg)
            '''前進ボタンの処理'''
            if laser_msg[0] == 'F_O':
                #ボタン変更
                self.button_stop_forward.place_forget()
                #貼り付け
                self.button_stop_forward_lock.place(
                    x = 637,
                    y = 50,
                    anchor=tk.CENTER
                )
                #msg_q.task_done
            elif laser_msg[0] == 'F_V':
                #ボタン変更
                self.button_stop_forward_lock.place_forget()
                
                #貼り付け
                self.button_stop_forward.place(
                    x = 637,
                    y = 50,
                    anchor=tk.CENTER
                )
            ''''''
            '''cw旋回ボタンの処理'''
            if laser_msg[1] == 'CW_O':
                #ボタン変更
                self.button_stop_cw.place_forget()
                #貼り付け
                self.button_stop_cw_lock.place(
                    x = 1185,
                    y = 382,
                    anchor=tk.CENTER
                )
                #msg_q.task_done
            elif laser_msg[1] == 'CW_V':
                #ボタン変更
                self.button_stop_cw_lock.place_forget()
                #貼り付け
                self.button_stop_cw.place(
                    x = 1185,
                    y = 382,
                    anchor=tk.CENTER
                )
            ''''''
            '''ccw旋回ボタンの処理'''
            if laser_msg[2] == 'CCW_O':
                #ボタン変更
                self.button_stop_ccw.place_forget()
                #貼り付け
                self.button_stop_ccw_lock.place(
                    x = 67,
                    y = 382,
                    anchor=tk.CENTER
                )
                #msg_q.task_done
            elif laser_msg[2] == 'CCW_V':
                #ボタン変更
                self.button_stop_ccw_lock.place_forget()
                #貼り付け
                self.button_stop_ccw.place(
                    x = 67,
                    y = 382,
                    anchor=tk.CENTER
                )
            ''''''
            time_end = time.time()
            exe_time = time_end - time_start
            print("処理時間: {:.10f} seconds".format(exe_time))

            msg_q.task_done()
        self.after(10, self.lock_button)
            
    '''周辺障害物の情報を受け取る関数'''
def receive_laser_data():
    global time_start
    while True:
        HOST = '0.0.0.0'
        PORT = 50000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)  # 接続の待ち受け
            print('Waiting for connection...')
            s.settimeout(100)
            conn, addr = s.accept()  # 接続されるまで待機
            data = conn.recv(1024)  # データの受信
            time_start = time.time()
            received_data = data.decode()  #文字列にデコード
            array = received_data.split('|')

            msg_q.put(array)
            msg_q.join()



def receive_img_data():
    '''ソケット通信で画像データを受信'''
    global img_flag
    while True:
            #time_staa = time.perf_counter()
            #接続
            socket.setdefaulttimeout(1.0)
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.connect(('192.168.11.26', 9999))

            #前方か後方どっちのカメラ映像を取得したいのかをラズパイに伝える
            if img_flag == 'F':
                udp.send(('F').encode("utf-8"))
            elif img_flag == 'S_F':
                udp.send(('F').encode("utf-8"))
            elif img_flag == 'B':
                udp.send(('B').encode("utf-8"))
            elif img_flag == 'S_B':
                udp.send(('B').encode("utf-8"))
            elif img_flag == 'M_F':
                udp.send(('F').encode("utf-8"))
            elif img_flag == 'M_B':
                udp.send(('B').encode("utf-8"))

            #画像データ受信用の変数を用意
            buff = 1024 * 64
            recive_data =bytes()
            time_staa = time.time()
            #画像データを分割して受け取り
            try:
                while True:
                    # 送られてくるデータが大きいので一度に受け取るデータ量を大きく設定
                    jpg_str, addr = udp.recvfrom(buff)
                    is_len = len(jpg_str) == 7
                    is_end = jpg_str == b'__end__'
                    if is_len and is_end: break
                    recive_data += jpg_str
                    
                    #人力タイムアウト処理
                    if (time.time() - time_staa) >= 1:
                        print("データ受信タイムアウト")
                        break
                
                #キューに画像データを追加
                q.put(recive_data)
                #time_endd = time.perf_counter()
                #timm = time_endd - time_staa
                #print("サブ："+str(timm))
                #キューから画像データが取り出されるまで処理をブロック
                q.join()
            except:
                print("Wi-Fi切断")





if __name__ == "__main__":

    root = MyApp()
    
    thread1 = threading.Thread(target=receive_img_data)
    thread1.start()
    thread2 = threading.Thread(target=receive_laser_data)
    thread2.start()
    #root.disp_image()
    root.lock_button()
    root.mainloop()


    