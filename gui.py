from tkinter import *
from tkinter import ttk

class VideoQueryGUI(Tk):
    root = Tk()
    root.title("CSCI 576 Project - A/V Video Player")
    #root.configure(background="black")

    frame1 = LabelFrame(root)
    frame1.config(height=200,width=800,text='Frame1',relief=RAISED)
    frame1.grid(row=0,column=0)

    button1 = Button(frame1,text="add")
    button1.grid(row=0,column=0)
    def callback_button1():
        print('working')
    button1.config(command=callback_button1)

    button2 = Button(frame1,text="select")
    button2.grid(row=0,column=1)
    def callback_button2():
        print('working')
    button2.config(command=callback_button2)

    lb=Listbox(frame1,height=4)
    lb.insert(0,"abfd","adfdv","rwg","reg","rgwgg","yhyjjy","areg","ergth","teh")
    yscroll = Scrollbar(frame1,orient=VERTICAL)
    lb['yscrollcommand'] = yscroll.set
    yscroll['command'] = lb.yview
    lb.grid(row=0,column=2,rowspan=2)
    yscroll.grid(row=0,column=2,rowspan=2,sticky=N+S+E) 

    """
    menu = StringVar()
    combobox = Combobox(root, textvariable=menu)
    combobox.grid(row=0,column=5,rowspan=2)
    combobox.config(values=('fef','gefverb','gbs'))
    """

    frame2 = LabelFrame(root)
    frame2.config(height=200,width=800,text='Frame2',relief=RAISED)
    frame2.grid(row=3,column=0)

    label_1 = Label(frame2,text="status",bg="black",fg="white",height=15,width=30)
    label_1.grid(row=3,column=0)

    """
    def callback_label1(event)
        print('<ButtonPress> Label')
    label_1.bind('<ButtonPress>',lambda e: callback_label1)
    """

    label_2 = Label(frame2,text="corr",bg="black",fg="white",height=15,width=30)
    label_2.grid(row=3,column=6)

    """
    progressbar = Progressbar(root,orient=HORIZONTAL,length=200)
    progressbar.grid(row=,column=)
    progressbar.config(value=)
    progressbar.start()
    progressbar.stop()
    value = DoubleVar()
    progressbar.config(variable=value)
    scale = Scale(root,orient=HORIZONTAL,length=400,variable=value,from_=0.0,to=11.0)
    scale.grid(row=,column=)
    """

    frame3 = LabelFrame(root)
    frame3.config(height=200,width=800,text='Frame3',relief=RAISED)
    frame3.grid(row=6,column=0)

    label_3 = Label(frame3,text="label1",bg="black",fg="white",height=25,width=30)
    label_3.grid(row=5,column=0)

    label_4 = Label(frame3,text="label2",bg="black",fg="white",height=25,width=30)
    label_4.grid(row=5,column=6) 

    button3 = Button(frame3,text="quit")
    button3.grid(row=6,column=6,sticky=E)
    def callback_button3():
        print('working')
    button3.config(command=callback_button3)

    root.rowconfigure(0,weight=1)
    root.rowconfigure(3,weight=3)
    root.rowconfigure(5,weight=3)
    root.rowconfigure(6,weight=3)
    root.columnconfigure(0,weight=1)
    root.columnconfigure(1,weight=3)
    root.columnconfigure(2,weight=3)
    root.columnconfigure(6,weight=3)

    root.mainloop()

