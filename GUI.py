import time
import socket
from tkinter import *
from tkinter import ttk
#Set server ip address, port, buffer capacity
HOST='192.168.143.152'
PORT=8008
BUFFER=4096

def control(data):
         # Define socket communication type ipv4, tcp
    soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
         #connect to the server 
    soc.connect((HOST,PORT))
         #delay
    time.sleep(1)
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

#ボタンstop
def stop():
    print("停止")
    control("s")


if __name__ == "__main__":

    root = Tk()
    root.geometry('1280x750')
    root.title("GUI_for_gaze input")
    #ウィジェット
    frame1 = ttk.Frame(root,padding=10)
    #前進用ボタン
    button_forward = ttk.Button(
        frame1,
        text="forward",
        command=forward
    )
    #停止用ボタン
    button_stop =ttk.Button(
        frame1,
        text="stop",
        command=stop
    )
    #レイアウト
    frame1.pack(expand=True, fill=BOTH)
    button_forward.pack(side=TOP, ipadx=50, ipady=50)
    button_stop.pack(side=BOTTOM, ipadx=50, ipady=50)
    root.mainloop()