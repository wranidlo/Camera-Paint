import tkinter as tk
from tkinter import colorchooser
import tkinter.ttk as ttk
from camera import Camera
from PIL import Image, ImageTk
import cv2
import brushes.Brushes as br


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


# MAIN APP CLASS

class Application(tk.Frame):

    # BUTTON COMMANDS METHODS

    # open scan view to configure pointer CAMERA
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
                self.show_image()

    # displaying current scan view CAMERA
    def show_config(self):
        if self.usage.cap.isOpened():
            frame = self.usage.search_for_object()
            quality = self.usage.check_quality(frame)
            if quality == 1:
                cv2.putText(frame, "Very good", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0),
                            thickness=2)
            else:
                if quality < 3:
                    cv2.putText(frame, "Good", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0),
                                thickness=2)
                else:
                    cv2.putText(frame, "Bad", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255),
                                thickness=2)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.display.delete("IMG")
            self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(frame)
            self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
            self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
            self.resize(self.display)
            self.display.after(10, self.show_config)

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

    # open camera view CAMERA
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
            self.show_image()

    # displaying current camera view CAMERA
    def show_center(self):
        if self.usage.cap.isOpened():
            img, _ = self.usage.get_center()

            self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(img)
            self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
            self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
            self.resize(self.display)
            self.display.after(10, self.show_center)

    # displaying image BRUSHES
    def show_image(self):
        self.refresh_image()
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.resize(self.display)

    # opening color_chooser window
    def color_chooser(self):
        self.color = colorchooser.askcolor(title="Select color")
        print(self.color)
        self.TESTINGCOLORBUTTON.configure(bg=self.color[1])

    # GUI SUPPORT METHODS

    # loading using images to list
    def initialize_images(self):
        # Resizing image to fit on button
        # brushIcon = brushIcon.subsample(10, 10)
        brush = ImageTk.PhotoImage(file=r"brush.png")
        pencil = tk.PhotoImage(file=r"pencil.png")
        spray = tk.PhotoImage(file=r"spray.png")
        red_colour = tk.PhotoImage(file=r"redColour.png")
        # greenColourIcon = tk.PhotoImage(file=r"greenColourIcon2.png")
        self.IMAGES['brush'] = brush
        self.IMAGES['pencil'] = pencil
        self.IMAGES['spray'] = spray
        self.IMAGES['redColour'] = red_colour
        # self.IMAGES['greenColour'] = greenColourIcon

    # resizing elements to current widget size after event of changed size
    def resize_event(self, event):
        size = (event.width, event.height)
        self.OBJECT_TO_DISPLAY_IMAGE = self.OBJECT_TO_DISPLAY_IMAGE.resize(size, Image.ANTIALIAS)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        # scale_w = event.width / self.OBJECT_TO_DISPLAY.width()
        # scale_h = event.height / self.OBJECT_TO_DISPLAY.height()
        # self.OBJECT_TO_DISPLAY.zoom(scale_w, scale_h)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")

    # resizing elements to current widget size, for not event cases (toogle view for example)
    def resize(self, canvas):
        size = (canvas.winfo_width(), canvas.winfo_height())
        self.OBJECT_TO_DISPLAY_IMAGE = self.OBJECT_TO_DISPLAY_IMAGE.resize(size, Image.ANTIALIAS)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")

    # load current image state from brushes module
    def refresh_image(self):
        self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(br.canvas_matrix)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)

    # displaying tool tip for widgets
    def create_tool_tip(self, widget, text="Temp"):
        toolTip = ToolTip(widget)

        def enter(event):
            toolTip.showtip(text)

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    # CREATING ALL WIDGETS IN MAIN WINDOW

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
        self.TOOLSFRAME.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)
        self.TOOLSFRAME.columnconfigure(0, weight=1)
        # self.TOOLSFRAME.rowconfigure(0, weight=1)
        # self.TOOLSFRAME.rowconfigure(1, weight=1)
        # (anchor=tk.N, fill=tk.BOTH, expand=False, side=tk.LEFT)

        # central frame for image
        self.IMAGEFRAME = tk.Frame(self, width=540, height=380)
        self.IMAGEFRAME.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGEFRAME.columnconfigure(0, weight=1)
        self.IMAGEFRAME.rowconfigure(0, weight=1)
        # (fill=tk.BOTH, expand=True)

        # SUBFRAMES

        # Creating subframes for different categories
        self.SUB_TOOLSFRAME_1 = tk.Frame(self.TOOLSFRAME, highlightbackground="grey", highlightthickness=1, bg="white")
        self.SUB_TOOLSFRAME_1.grid(row=1, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.SUB_TOOLSFRAME_2 = tk.Frame(self.TOOLSFRAME, bd=1, highlightbackground="grey", highlightthickness=1, bg="white")
        self.SUB_TOOLSFRAME_2.grid(row=4, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)

        # TOOLS FRAME WIDGETS

        # Creating SUB_TOOLSFRAME_1 label
        self.SUB_TOOLSFRAME_1_LABEL = tk.Label(self.TOOLSFRAME, text="Painting tools", anchor=tk.N)
        self.SUB_TOOLSFRAME_1_LABEL.grid(row=0, column=0, sticky=tk.W, padx=5)

        # Creating tools button
        self.TOOLBUTTON = tk.Menubutton(self.SUB_TOOLSFRAME_1, bd=0, image=self.IMAGES['brush'], compound=tk.CENTER, bg="white")
        self.TOOLBUTTON.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.W + tk.E)

        # Creating tools menu
        self.TOOLBUTTON.menu = tk.Menu(self.TOOLBUTTON, tearoff=0)
        self.TOOLBUTTON["menu"] = self.TOOLBUTTON.menu
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['brush'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['pencil'])
        self.TOOLBUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['spray'])
        # ToolTip for button
        self.create_tool_tip(self.TOOLBUTTON, "Tool")

        # Creating colour button
        self.COLOURBUTTON = tk.Button(self.SUB_TOOLSFRAME_1, image=self.IMAGES['redColour'], compound=tk.CENTER, bg="white")
        self.COLOURBUTTON["command"] = self.color_chooser
        self.COLOURBUTTON.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.COLOURBUTTON, "Colour")

        # TESTING button
        self.TESTINGCOLORBUTTON = tk.Button(self.SUB_TOOLSFRAME_1, text="current color", compound=tk.CENTER, bg="red")
        self.TESTINGCOLORBUTTON.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N)

        # Creating separator beetwen sub frames
        self.SEPARATOR_BETWEEN_TOOLSFRAMES = tk.Label(self.TOOLSFRAME, text="", height=1)
        self.SEPARATOR_BETWEEN_TOOLSFRAMES.grid(row=2, column=0)

        # Creating SUB_TOOLSFRAME_2 label
        self.SUB_TOOLSFRAME_2_LABEL = tk.Label(self.TOOLSFRAME, text="Scanner options", anchor=tk.N)
        self.SUB_TOOLSFRAME_2_LABEL.grid(row=3, column=0, sticky=tk.W, padx=5)

        # Creating config button
        self.CONFIGBUTTON = tk.Button(self.SUB_TOOLSFRAME_2, text="Scan", anchor=tk.CENTER, width=9, bg="green")
        self.CONFIGBUTTON["command"] = self.camera_config_action
        self.CONFIGBUTTON.grid(row=0, column=0, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.CONFIGBUTTON, "Start scanning object")

        # Creating toggle button
        self.TOGGLEBUTTON= tk.Button(self.SUB_TOOLSFRAME_2, text="Toggle view", anchor=tk.CENTER, bg="green")
        self.TOGGLEBUTTON["command"] = self.toggle_view_action
        self.TOGGLEBUTTON.grid(row=1, column=0, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.TOGGLEBUTTON, "Toggle view between image and camera")

        # IMAGE FRAME WIDGETS

        # Creating display space for image/camera view
        self.display = tk.Canvas(self.IMAGEFRAME, bd=0, highlightthickness=0, bg="black")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.display.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGEFRAME.bind("<Configure>", self.resize_event)

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
        self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(br.canvas_matrix)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
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


im = Image.open("redColour.png")
print(im.mode)
root = tk.Tk()
app = Application(parent=root)
app.pack(fill="both", expand=True)
app.mainloop()
try:
    root.destroy()
except tk.TclError:
    "App already closed"

