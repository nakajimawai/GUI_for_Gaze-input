import time
import socket
from tkinter import *
from tkinter import ttk
import cv2
#Set server ip address, port, buffer capacity
HOST='192.168.11.26'
PORT=8008
BUFFER=4096

def init(root):
    root.geometry('1275x765')
    root.title("GUI_for_gaze input")
    #ウィジェット
    frame1 = ttk.Frame(root,padding=10)
    #画像読み込み
    origin_image = PhotoImage(file='sample_arrow.png')
    print(origin_image)
    big_img = origin_image.zoom(5,5)
    small_img = origin_image.subsample(5,5)
    #前進用ボタン
    button_forward = Button(
        frame1,
        text="FORWARD",
        font=("",18),
        fg='red',
        #image=origin_image,
        compound="top",
        width=30,
        height=5,
        command=forward
    )
    #button_forward.bind("<Button-1>",forward)
    #右旋回用ボタン
    button_right = Button(
        frame1,
        text="CW",
        font=("",18),
        fg='purple',
        width=10,
        height=15,
        command=right
    )#左旋回用ボタン
    button_left = Button(
        frame1,
        text="CCW",
        font=("",18),
        fg='green',
        width=10,
        height=15,
        command=left
    )
    #停止用ボタン
    button_stop =Button(
        frame1,
        text="STOP",
        font=("",18),
        fg='gold',
        width=30,
        height=5,
        command=stop
    )
    #レイアウト
    frame1.pack(expand=True, fill=BOTH)
    button_forward.pack(side=TOP)
    button_stop.pack(side=BOTTOM)
    button_right.pack(side=RIGHT)
    button_left.pack(side=LEFT)#文字とボタン端までの間隔ipadx=50, ipady=50
    #button_forward.bind("Button-1",forward)

#文字列送信用
def control(data):
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
def forward():
    print("前進")
    control("w")
#ボタンright
def right():
    print("右旋回")
    control("d")
#ボタンforward
def left():
    print("左旋回")
    control("a")
#ボタンstop
def stop():
    print("停止")
    control("s")


if __name__ == "__main__":

    root = Tk()
    init(root)
    root.mainloop()