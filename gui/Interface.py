import tkinter as tk
import tkinter.ttk as ttk
from camera import Camera
from PIL import Image, ImageTk
import cv2


# Class to displaying tool tips
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        # "Display text in tooltip window"
        self.text = text
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 37
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# main application class
class Application(tk.Frame):
    def camera_config_action(self):
        if self.check_if_already_showing == 0:
            if self.check_if_configured == 0:
                self.check_if_configured = 1

                self.CONFIGBUTTON.config(text="Stop", bg="red")

                self.usage.set_histogram_created_check_not()
                self.usage.cap = cv2.VideoCapture(0)
                self.show_config()
            else:
                self.CONFIGBUTTON.config(text="Scan", bg="green")

                self.usage.histogram_created_check = True
                self.check_if_configured = 0
                self.usage.cap.release()

        """
        self.usage.set_histogram_created_check_not()
        cv2.namedWindow('Scan', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Scan', 800, 600)
        self.usage.cap = cv2.VideoCapture(0)
        while self.usage.histogram_created_check is False:
            frame = self.usage.scan_object()
            cv2.imshow('Scan', frame)
            self.original_frame = Image.fromarray(frame)
            self.frame = ImageTk.PhotoImage(self.original_frame)

            # Creating display space for image/camera view
            self.display.delete("IMG")

            self.display.create_image(0, 0, image=self.frame, anchor=tk.NW, tags="IMG")
            self.display.update()
        self.usage.cap.release()

        cv2.destroyAllWindows()
        """

    def show_config(self):
        if self.usage.cap.isOpened():
            frame = self.usage.search_for_object()
            self.display.delete("IMG")
            self.original_frame = Image.fromarray(frame)
            self.frame = ImageTk.PhotoImage(self.original_frame)
            self.display.create_image(0, 0, image=self.frame, anchor=tk.NW, tags="IMG")
            self.display.after(10, self.show_config)

    def toggle_view_action(self):
        if self.check_if_already_showing == 0:
            if self.usage.histogram_created_check is True:
                print("here")
                self.check_if_already_showing = 1
                self.usage.cap = cv2.VideoCapture(0)

                self.TOGGLEBUTTON.config(text="Stop view",bg="red")

                self.show_center()
        else:
            self.TOGGLEBUTTON.config(text="Toggle view", bg="green")
            self.check_if_already_showing = 0
            self.usage.cap.release()

    def show_center(self):
        if self.usage.cap.isOpened():
            img, _ = self.usage.get_center()

            self.original_frame = Image.fromarray(img)
            self.frame = ImageTk.PhotoImage(self.original_frame)
            self.display.create_image(0, 0, image=self.frame, anchor=tk.NW, tags="IMG")
            self.display.after(10, self.show_center)

    # gui support methods

    # loading using images to list
    def initialize_images(self):
        # Resizing image to fit on button
        # brushIcon = brushIcon.subsample(10, 10)
        brush = tk.PhotoImage(file=r"brush.png")
        pencil = tk.PhotoImage(file=r"pencil.png")
        spray = tk.PhotoImage(file=r"spray.png")
        red_colour = tk.PhotoImage(file=r"redColour.png")
        # greenColourIcon = tk.PhotoImage(file=r"greenColourIcon2.png")
        self.IMAGES['brush'] = brush
        self.IMAGES['pencil'] = pencil
        self.IMAGES['spray'] = spray
        self.IMAGES['redColour'] = red_colour
        # self.IMAGES['greenColour'] = greenColourIcon

    # resizing elements to current window size
    def resize(self, event):
        size = (event.width, event.height)
        resized = self.original_frame.resize(size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.image, anchor=tk.NW, tags="IMG")

    # displaying tool tip for widgets
    def create_tool_tip(self, widget, text="Temp"):
        toolTip = ToolTip(widget)

        def enter(event):
            toolTip.showtip(text)

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    # function creating all frames, buttons, etc in main window
    def create_widgets(self):
        # MENUS

        # toplevel menu
        self.MENU = tk.Menu(self)

        # file menu
        self.FILEMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='File', menu=self.FILEMENU)
        self.FILEMENU.add_command(label='New project')
        self.FILEMENU.add_command(label='Open project')
        self.FILEMENU.add_command(label='Save')
        self.FILEMENU.add_command(label='Save as')
        self.FILEMENU.add_separator()
        self.FILEMENU.add_command(label='Exit', command=self.quit)
        # display the menu
        self.parent.config(menu=self.MENU)

        # edit menu
        self.EDITMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='Edit', menu=self.EDITMENU)
        self.EDITMENU.add_command(label='Undo')
        self.EDITMENU.add_command(label='Redo')

        # view menu
        self.VIEWMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='View', menu=self.VIEWMENU)
        self.VIEWMENU.add_command(label='Not implemented yet')

        # settings menu
        self.SETTINGSMENU = tk.Menu(self.MENU)
        self.MENU.add_cascade(label='Settings', menu=self.SETTINGSMENU)
        self.SETTINGSMENU.add_command(label='Not implemented yet')

        # FRAMES

        # left frame for tools
        self.TOOLSFRAME = tk.Frame(self, width=100)
        self.TOOLSFRAME.grid(row=0, column=0, sticky=tk.W, )
        self.TOOLSFRAME.grid(sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)
        self.TOOLSFRAME.columnconfigure(0, weight=1)
        self.TOOLSFRAME.rowconfigure(0, weight=1)
        self.TOOLSFRAME.rowconfigure(1, weight=1)
        # (anchor=tk.N, fill=tk.BOTH, expand=False, side=tk.LEFT)

        # central frame for image
        self.IMAGEFRAME = tk.Frame(self, width=540, height=380)
        self.IMAGEFRAME.grid(row=0, column=1)
        self.IMAGEFRAME.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGEFRAME.columnconfigure(0, weight=1)
        self.IMAGEFRAME.rowconfigure(0, weight=1)
        # (fill=tk.BOTH, expand=True)

        # SUBFRAMES

        # Creating subframes for different categories
        self.SUB_TOOLSFRAME_1 = tk.LabelFrame(self.TOOLSFRAME, text="Painting tools")
        self.SUB_TOOLSFRAME_1.grid(row=0, column=0)
        self.SUB_TOOLSFRAME_1.grid(sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)
        self.SUB_TOOLSFRAME_2 = tk.LabelFrame(self.TOOLSFRAME, text="Scanner options")
        self.SUB_TOOLSFRAME_2.grid(row=1, column=0)
        self.SUB_TOOLSFRAME_2.grid(sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)

        # TOOLS FRAME WIDGETS

        # Creating tools button
        self.TOOLBUTTON = tk.Menubutton(self.SUB_TOOLSFRAME_1, bd=0, image=self.IMAGES['brush'], compound=tk.CENTER)
        self.TOOLBUTTON.grid(row=0, column=0, pady=5, sticky=tk.N)

        # Creating tools menu
        self.TOOLBUTTON.menu = tk.Menu(self.TOOLBUTTON, tearoff=0)
        self.TOOLBUTTON["menu"] = self.TOOLBUTTON.menu
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['brush'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['pencil'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['spray'])
        # ToolTip for button
        self.create_tool_tip(self.TOOLBUTTON, "Tool")

        # Creating colour button
        self.COLOURBUTTON = tk.Menubutton(self.SUB_TOOLSFRAME_1, bd=0, image=self.IMAGES['redColour'],
                                          compound=tk.CENTER, bg="white")
        self.COLOURBUTTON.grid(row=1, column=0, pady=5, sticky=tk.N)

        # Creating colour menu
        self.COLOURBUTTON.menu = tk.Menu(self.COLOURBUTTON, tearoff=0)
        self.COLOURBUTTON["menu"] = self.COLOURBUTTON.menu
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        self.COLOURBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['redColour'])
        # ToolTip for button
        self.create_tool_tip(self.COLOURBUTTON, "Colour")

        # Creating config button
        self.CONFIGBUTTON = tk.Button(self.SUB_TOOLSFRAME_2, text="Scan", anchor=tk.CENTER, bg="green")
        self.CONFIGBUTTON.grid(row=0, column=0, pady=5, sticky=tk.N)
        self.CONFIGBUTTON["command"] = self.camera_config_action
        # ToolTip for button
        self.create_tool_tip(self.CONFIGBUTTON, "Start scanning object")

        # Creating toggle button
        self.TOGGLEBUTTON= tk.Button(self.SUB_TOOLSFRAME_2, text="Toggle view", anchor=tk.CENTER, bg="green")
        self.TOGGLEBUTTON.grid(row=1, column=0, pady=5, sticky=tk.N)
        self.TOGGLEBUTTON["command"] = self.toggle_view_action
        # ToolTip for button
        self.create_tool_tip(self.TOGGLEBUTTON, "Toggle view between image and camera")

        # IMAGE FRAME WIDGETS

        # Creating label with background for image grid
        self.original_frame = Image.open('bird.jpg')
        self.frame = ImageTk.PhotoImage(self.original_frame)

        # Creating display space for image/camera view
        self.display = tk.Canvas(self.IMAGEFRAME, bd=0, highlightthickness=0, bg="white")
        self.display.create_image(0, 0, image=self.frame, anchor=tk.NW, tags="IMG")
        self.display.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGEFRAME.bind("<Configure>", self.resize)

        # tutorial buttons
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

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.IMAGES = {}
        self.style = ttk.Style()
        self.style.theme_use('alt')
        # self.style = ThemedStyle(self.parent)
        # self.style.set_theme("scidgrey")
        # initializing camera module
        self.usage = Camera.camera()
        self.initGui()
        self.check_if_already_showing = 0
        self.check_if_configured = 0

    def initGui(self):
        self.parent.title("Camera Paint")
        self.parent.geometry('840x480')
        self.parent.resizable(width=tk.TRUE, height=tk.TRUE)
        self.grid(sticky=tk.W + tk.E + tk.N + tk.S, padx=20, pady=20)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.initialize_images()
        self.create_widgets()


# style = ttk.Style()
# print(style.theme_names())


root = tk.Tk()
app = Application(parent=root)
app.pack(fill="both", expand=True)
app.mainloop()
try:
    root.destroy()
except tk.TclError:
    "App already closed"

