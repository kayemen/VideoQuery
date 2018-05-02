from tkinter import *
#create window
root = Tk()
"""
#create text
theLabel = Label(root, text = "bruu")
#.pack used to display
theLabel.pack()

#create 2 invisble frames
topFrame = Frame(root)
topFrame.pack()
bottomFrame = Frame(root)
bottomFrame.pack(side = BOTTOM)
#create buttons
-->button1 = Button(topFrame, text="1", fg="red")
button2 = Button(bottomFrame, text="2", fg="blue")
button3 = Button(topFrame, text="3", fg="green")
button1.pack(side = LEFT)
button3.pack(side = LEFT)
button2.pack()

#fitting widgets
one = Label(root, text="1", bg="red", fg="white")
one.pack()
two = Label(root, text="2", bg="green")
two.pack(fill=X)
three = Label(root, text="3", bg="blue")
-->three.pack(side= LEFT, fill=Y)

#grid layout fill left or right
label1 = Label(root, text="name")
label2 = Label(root, text="psw")
#create entry
entry1 = Entry(root)
entry2 = Entry(root)
#.grid for rows and column, default column is 0
label1.grid(row=0, sticky=E)
#E = right alignment
label2.grid(row=1, sticky=W)
#W = left
entry1.grid(row=0, column=1)
entry2.grid(row=1, column=1) 
#checking button
c = Checkbutton(root, text="done")
c.grid(columnspan=2)

#function calling and click button to get output
def printName(event):
    print("Brinal")
button1 = Button(root, text="name", command=printName)
button1.pack()
#left click button to function
button1.bind("<Button-1>", printName)
#event = button click or scroll
"""

#sizing the frame window
frame = Frame(root, width=)


#keeps displaying the window
root.mainloop()

"""
root.scrollbar_V = Scrollbar(root)
root.scrollbar_H = Scrollbar(root, orient=HORIZONTAL)
root.scrollbar_V.grid(row=0,column=6)
root.scrollbar_H.grid(row=2,column=5)

root.listbox1 = Listbox(root,font=('',12),width=10,height=10,yscrollcommand=root.scrollbar_V.set, xscrollcommand=root.scrollbar_H.set)
root.listbox1.bind('<<ListboxSelect>>',root.select_item)
root.listbox1.insert(1,'brinal')
root.listbox1.insert(2,'karan')
root.listbox1.insert(3,'brina')
root.listbox1.grid(row=0,column=5)

root.scrollbar_V.config(command=root.listbox1.yview)
root.scrollbar_H.config(command=root.listbox1.xview)
"""
