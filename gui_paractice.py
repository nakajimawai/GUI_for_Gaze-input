from tkinter import *
from tkinter import ttk

root = Tk()
root.title('My Frist App')

#ウィジェットの作成
frame1 = ttk.Frame(root,padding=100)
label1 = ttk.Label(frame1, text='Your name')
t = StringVar()
entry1 =ttk.Entry(frame1, textvariable=t)
button1 = ttk.Button(
    frame1,
    text='OK',
    command=lambda: print('Hello, %s.'% t.get()))

#レイアウト
frame1.pack()
label1.pack()
entry1.pack()
button1.pack()

#ウィンドウの表示開始
root.mainloop()