from Tkinter import *
import os
top = Tk()

 top.title('Package installer')
L1 = Label(top, text="Package")
L1.pack( side = LEFT)
E1 = Entry(top, bd =5)
E1.pack(side = RIGHT)

 def installCallBack():
   eval(os.system('cmd /k "' + pkg + '"'))
   pkg = L1.get()
   tkMessageBox.showinfo( "Installer", "Installed :)")

 B = Button(top, text ="Install", command = installCallBack)

 top.mainloop()
