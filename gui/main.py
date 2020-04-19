#from tkinter import *
import tkinter as tk
from tkinter import ttk


class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        #"Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 37
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class Application(tk.Frame):
    def say_hi(self):
        print("hi there, everyone!")

    def initializeImages(self):
        # Resizing image to fit on button
        # brushIcon = brushIcon.subsample(10, 10)
        brush = tk.PhotoImage(file=r"brush.png")
        pencil = tk.PhotoImage(file=r"pencil.png")
        spray = tk.PhotoImage(file=r"spray.png")
        redColour = tk.PhotoImage(file=r"redColour.png")
        #greenColourIcon = tk.PhotoImage(file=r"greenColourIcon2.png")
        self.IMAGES['brush'] = brush
        self.IMAGES['pencil'] = pencil
        self.IMAGES['spray'] = spray
        self.IMAGES['redColour'] = redColour
        #self.IMAGES['greenColour'] = greenColourIcon

    def createToolTip(self, widget, text="Temp"):
        toolTip = ToolTip(widget)

        def enter(event):
            toolTip.showtip(text)

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def createWidgets(self):
        #toplevel menu
        self.MENU = tk.Menu(self.master)

        #file menu
        self.FILEMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='File', menu=self.FILEMENU)
        self.FILEMENU.add_command(label='New project')
        self.FILEMENU.add_command(label='Open project')
        self.FILEMENU.add_command(label='Save')
        self.FILEMENU.add_command(label='Save as')
        self.FILEMENU.add_separator()
        self.FILEMENU.add_command(label='Exit', command=self.master.quit)
        # display the menu
        self.master.config(menu=self.MENU)

        #edit menu
        self.EDITMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='Edit', menu=self.EDITMENU)
        self.EDITMENU.add_command(label='Undo')
        self.EDITMENU.add_command(label='Redo')

        #view menu
        self.VIEWMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='View', menu=self.VIEWMENU)
        self.VIEWMENU.add_command(label='Not implemented yet')

        #settings menu
        self.SETTINGSMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='Settings', menu=self.SETTINGSMENU)
        self.SETTINGSMENU.add_command(label='Not implemented yet')

        #left frame for tools
        self.TOOLSFRAME = tk.Frame(self.master, width=100)
        self.TOOLSFRAME.pack(anchor=tk.N, fill=tk.BOTH, expand=False, side=tk.LEFT)

        #central frame for image
        self.IMAGEFRAME = tk.Frame(self.master, background="White")
        self.IMAGEFRAME.pack(fill=tk.BOTH, expand=True)

        #tools widgets
        #Creating button
        self.TOOLBUTTON = tk.Menubutton(self.TOOLSFRAME, bd=0, image=self.IMAGES['brush'], compound=tk.CENTER)
        self.TOOLBUTTON.pack(side=tk.TOP)
        #Creating tools menu
        self.TOOLBUTTON.menu = tk.Menu(self.TOOLBUTTON, tearoff=0)
        self.TOOLBUTTON["menu"] = self.TOOLBUTTON.menu
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['brush'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['pencil'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['spray'])
        #ToolTip for button
        self.createToolTip(self.TOOLBUTTON, "Tool")

        # Creating button
        self.COLOURBUTTON = tk.Menubutton(self.TOOLSFRAME, bd=0, image=self.IMAGES['redColour'], compound=tk.CENTER)
        self.COLOURBUTTON.pack(side=tk.TOP)
        # Creating colour menu
        self.COLOURBUTTON.menu = tk.Menu(self.COLOURBUTTON, tearoff=0)
        self.COLOURBUTTON["menu"] = self.COLOURBUTTON.menu
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        #ToolTip for button
        self.createToolTip(self.COLOURBUTTON, "Colour")

        #tutorial buttons
        # self.QUIT = tk.Button(self)
        # self.QUIT["text"] = "QUIT"
        # self.QUIT["fg"]   = "red"
        # self.QUIT["command"] =  self.quit
        #
        # self.QUIT.pack({"side": "left"})
        #
        # self.hi_there = tk.Button(self)
        # self.hi_there["text"] = "Hello",
        # self.hi_there["command"] = self.say_hi
        #
        # self.hi_there.pack({"side": "left"})

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        #self.pack()
        self.IMAGES = {}
        self.initializeImages()
        self.createWidgets()

root = tk.Tk()
root.title('Camera Paint')
root.geometry('640x480')
app = Application(master=root)
app.mainloop()
root.destroy()