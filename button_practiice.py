from tkinter import *
from tkinter import ttk

#ボタンforward
def forward():
    print("前進")

#ボタンstop
def stop():
    print("停止")

root = Tk()
root.geometry('1280x750')
root.title("button_practice")

print(root.winfo_screenwidth())
print(root.winfo_screenheight())
#ウィジェット
frame1 = ttk.Frame(root,padding=10)
#前進用ボタン
button_forward = ttk.Button(
    frame1,
    text="forward",
    command=forward()
)
#停止用ボタン
button_stop =ttk.Button(
    frame1,
    text="stop",
    command=stop()
)

#レイアウト
#frame1.propagate(False)
frame1.pack(expand=True, fill=BOTH)
button_forward.pack(side=TOP, ipadx=50, ipady=50)
button_stop.pack(side=BOTTOM, ipadx=50, ipady=50)
root.mainloop()