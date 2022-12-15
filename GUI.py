#import time
import socket
#from tkinter import *
import tkinter as tk
from tkinter import ttk
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
        ttk.Frame.__init__(self, root, width=400, height=400, padding=10)
        self.controller = controller
        #画像読み込み
        origin_image = tk.PhotoImage(file='sample_arrow.png')
        print(origin_image)
        big_img = origin_image.zoom(5,5)
        small_img = origin_image.subsample(1,1.5)
        #前進用ボタン
        button_forward = tk.Button(
            self,
            text="FORWARD",
            font=("",18),
            fg='red',
            image=small_img,
            compound="top",
            width=200,
            height=100,
            command=self.forward
        )
        #self.origin_image = origin_image
        self.small_img = small_img
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
    def right(self):
        print("右旋回")
        self.control("d")
    #ボタンforward
    def left(self):
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