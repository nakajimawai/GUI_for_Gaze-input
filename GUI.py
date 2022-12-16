#import time
import socket
#from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
#Set server ip address, port, buffer capacity
HOST='192.168.11.26'
PORT=8008
BUFFER=4096

class MyApp(ttk.Frame):
    def __init__(self, root, controller):
        root.geometry('1275x765')
        root.title("GUI_for_gaze input")
        #ウィジェット
        #frame1 = tk.Frame(root)
        ttk.Frame.__init__(self, root, width=1275, height=765, padding=10)
        #self.controller = controller
        #画像読み込み
        #背景画像用のキャンバス
        cvs = tk.Canvas(self,width=1275,height=765)
        cvs.place(
            relx=0,
            rely=0,
            bordermode=tk.OUTSIDE
        )
        bg = Image.open('bg-test.jpg')
        bg = bg.resize((1275, 765))
        bg = ImageTk.PhotoImage(bg)
        cvs.create_image(0,0,anchor='nw',image=bg)
        self.controller = controller
        self.bg = bg
        #リサイズするため
        #前進シンボル
        img_forward = Image.open('forward.png')
        img_forward = img_forward.resize((200, 100))
        img_forward = ImageTk.PhotoImage(img_forward)
        #停止シンボル
        img_stop = Image.open('stop.2.png')
        img_stop = img_stop.resize((195, 195))
        img_stop = ImageTk.PhotoImage(img_stop)
        #cw旋回シンボル
        img_cw = Image.open('cw.png')
        img_cw = img_cw.resize((125, 125))
        img_cw = ImageTk.PhotoImage(img_cw)
        #ccwシンボル
        img_ccw = Image.open('ccw.png')
        img_ccw = img_ccw.resize((125, 125))
        img_ccw = ImageTk.PhotoImage(img_ccw)
        #img = tk.PhotoImage(img)
        #
        #tkinterで初めから読み込み
        origin_image = tk.PhotoImage(file='sample_arrow.png')
        big_img = origin_image.zoom(5,5)
        small_img = origin_image.subsample(2,2)
        resize_img = origin_image
        '''
        #前進用ボタン
        button_forward = tk.Button(
            self,
            #text="FORWARD",
            font=("",18),
            fg='red',
            image=img,
            compound="top",
            width=200,
            height=100,
            command=self.forward
        )
        #self.origin_image = origin_image
        #self.small_img = small_img
        self.img = img
        #button_forward.bind("<Button-1>",forward)
        #右旋回用ボタン
        button_right = tk.Button(
            self,
            text="CW",
            font=("",18),
            fg='purple',
            width=10,
            height=15,
            command=self.stop
        )#左旋回用ボタン
        button_left = tk.Button(
            self,
            text="CCW",
            font=("",18),
            fg='green',
            width=10,
            height=15,
            command=self.left
        )
        #後進用ボタン
        button_stop =tk.Button(
            self,
            text="BACK",
            font=("",18),
            fg='blue',
            width=30,
            height=5,
            command=self.back
        )
        #レイアウト
        self.pack(expand=True, fill=tk.BOTH)
        button_forward.pack(side=tk.TOP)
        button_stop.pack(side=tk.BOTTOM)
        button_right.pack(side=tk.RIGHT)
        button_left.pack(side=tk.LEFT)#文字とボタン端までの間隔ipadx=50, ipady=50
        #button_forward.bind("Button-1",forward)
        '''
        #前進ボタン
        button_forward = tk.Button(
            self,
            image=img_forward,
            command=self.forward
        )
        self.img_forward = img_forward
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
            width=250,
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

    #文字列送信用
    def control(self, data):
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

        print(buf)

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


#if __name__ == "__main__":

root = tk.Tk()
frame = MyApp(root, object())
frame.pack()
root.mainloop()