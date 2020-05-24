import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import cv2
import numpy as np
from camera import Camera
import brushes.Brushes as Br


# Class to displaying tool tips
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, txt):
        # "Display text in tooltip window"
        text = txt
        if self.tip_window or not text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 37
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=text, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1,
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

    # TOOLS METHODS

    # open scan view to configure pointer CAMERA
    def camera_config_action(self):
        if self.check_if_already_showing == 0:
            if self.check_if_configured == 0:
                self.check_if_configured = 1

                self.CONFIG_BUTTON.config(text="Stop", bg="red")

                self.usage.set_histogram_created_check_not()
                self.usage.cap = cv2.VideoCapture(0)
                self.show_config()
            else:
                self.CONFIG_BUTTON.config(text="Scan", bg="green")

                self.usage.histogram_created_check = True
                self.check_if_configured = 0
                self.usage.cap.release()
                self.show_image(Br.canvas_matrix)

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
            self.show_image(frame)
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
                self.check_if_already_showing = 1
                self.usage.cap = cv2.VideoCapture(0)

                self.TOGGLE_BUTTON.config(text="Stop view", bg="red")

                self.show_center()
        else:
            self.TOGGLE_BUTTON.config(text="Toggle view", bg="green")
            self.check_if_already_showing = 0
            self.usage.cap.release()
            self.show_image(Br.canvas_matrix)

    # displaying current camera view CAMERA
    def show_center(self):
        if self.usage.cap.isOpened():
            img, _ = self.usage.get_center()
            self.show_image(img)
            self.display.after(10, self.show_center)

    # displaying image BRUSHES
    def show_image(self, image):
        self.refresh_image(image)
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.resize(self.display)

    # opening color_chooser window
    def color_chooser(self):
        color = colorchooser.askcolor(title="Select color")
        print(color)
        self.COLOUR_BUTTON.configure(fg=color[1])

    def change_tool(self, tool):
        if tool == 0:
            self.TOOL_BUTTON.config(image=self.IMAGES['brush'])
            self.TOOL_BUTTON.image = self.IMAGES['brush']
            # TODO connect with BRUSHES
        elif tool == 1:
            self.TOOL_BUTTON.config(image=self.IMAGES['pencil'])
            self.TOOL_BUTTON.image = self.IMAGES['pencil']
            # TODO connect with BRUSHES
        elif tool == 2:
            self.TOOL_BUTTON.config(image=self.IMAGES['spray'])
            self.TOOL_BUTTON.image = self.IMAGES['spray']
            # TODO connect with BRUSHES

    def change_selection(self, type):
        if type == 0:
            self.SELECTION_BUTTON.config(image=self.IMAGES['squaredSelection'])
            self.SELECTION_BUTTON.image = self.IMAGES['squaredSelection']
            # TODO connect with BRUSHES
        elif type == 1:
            self.SELECTION_BUTTON.config(image=self.IMAGES['colourSelection'])
            self.SELECTION_BUTTON.image = self.IMAGES['colourSelection']
            # TODO connect with BRUSHES
        elif type == 2:
            self.SELECTION_BUTTON.config(image=self.IMAGES['wandSelection'])
            self.SELECTION_BUTTON.image = self.IMAGES['wandSelection']
            # TODO connect with BRUSHES

    def use_fill(self):
        None
        # TODO connect with BRUSHES

    def use_pick_color(self):
        None
        # TODO connect with BRUSHES

    def use_zoom(self):
        None
        # TODO connect with BRUSHES

    def use_text(self):
        None
        # TODO connect with BRUSHES

    # FILE MENU METHODS
    def new_project(self):
        if self.savedFlag:
            Br.canvas_matrix = np.empty((Br.size_x, Br.size_y, 3), dtype='uint8')
            Br.canvas_matrix.fill(255)
            self.show_image(Br.canvas_matrix)
        else:
            response = self.open_messagebox(6, "Not saved changes", "You want to continue without saving?")
            print(response)
            if response:
                self.savedFlag = True
                self.new_project()

    def open_project(self):
        if self.savedFlag:
            self.path_to_save = fd.askopenfilename(filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg *.jpe *.jfif"),
                                                                ("GIF", "*.gif"), ("TIFF", "*.tif *.tiff"),
                                                                ("BMP", "*.bmp")],
                                            defaultextension="*.png")  # wywołanie okna dialogowego save file
            if self.path_to_save != "":
                loaded_image = cv2.imread(self.path_to_save)
                self.OBJECT_TO_DISPLAY_IMAGE = Image.open(self.path_to_save)
                self.OBJECT_TO_DISPLAY_IMAGE.load()
                Br.canvas_matrix = np.asarray(self.OBJECT_TO_DISPLAY_IMAGE, dtype="uint8")
                self.show_image(Br.canvas_matrix)
        else:
            response = self.open_messagebox(6, "Not saved changes", "You want to continue without saving?")
            if response:
                self.savedFlag = True
                self.open_project()

    def save_image(self):
        if self.path_to_save == "":
            self.save_image_as()
        else:
            self.OBJECT_TO_DISPLAY_IMAGE.save(self.path_to_save)

    def save_image_as(self):
        self.path_to_save = fd.asksaveasfilename(filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg *.jpe *.jfif"),
                                                            ("GIF", "*.gif"), ("TIFF", "*.tif *.tiff"), ("BMP", "*.bmp")],
                                        defaultextension="*.png")  # wywołanie okna dialogowego save file

        if self.path_to_save != "":
            self.OBJECT_TO_DISPLAY_IMAGE.save(self.path_to_save)

    def recent(self):
        None
        # TODO connect with BRUSHES

    def print_image(self):
        None
        # TODO connect with BRUSHES

    # EDIT MENU METHODS
    def undo(self):
        None
        # TODO connect with BRUSHES

    def redo(self):
        None
        # TODO connect with BRUSHES

    def cut(self):
        None
        # TODO connect with BRUSHES

    def copy(self):
        None
        # TODO connect with BRUSHES

    def paste(self):
        None
        # TODO connect with BRUSHES

    def clear(self):
        None
        # TODO connect with BRUSHES

    # VIEW MENU METHODS
    def zoom_view(self):
        None
        # TODO connect with BRUSHES

    def full_screen(self):
        if self.fullScreenStateFlag:
            self.fullScreenStateFlag = False
            self.VIEW_MENU.entryconfigure(1, label="Fullscreen")
        else:
            self.fullScreenStateFlag = True
            self.VIEW_MENU.entryconfigure(1, label="Exit fullscreen")
        self.parent.attributes("-fullscreen", self.fullScreenStateFlag)
        # TODO connect with BRUSHES

    # IMAGE MENU METHODS
    def size_image(self):
        None
        # TODO connect with BRUSHES

    def color_space(self):
        None
        # TODO connect with BRUSHES

    # TOOLS MENU METHODS
    # TODO connect somehow with tools bar

    # SETTINGS MENU METHODS
    def preferences(self):
        None
        # TODO connect with BRUSHES

    def shortcuts(self):
        None
        # TODO connect with BRUSHES

    def color_space(self):
        None
        # TODO connect with BRUSHES

    # GUI SUPPORT METHODS

    # loading using images to list
    def initialize_images(self):
        # ICONS 24x24 pixels
        # Resizing image to fit on button
        # brushIcon = brushIcon.subsample(10, 10)
        brush = ImageTk.PhotoImage(file=r"data/brush.png")
        pencil = tk.PhotoImage(file=r"data/pencil.png")
        spray = tk.PhotoImage(file=r"data/spray.png")
        colorPicker = tk.PhotoImage(file=r"data/icons8-colors.png")
        squared_selection = tk.PhotoImage(file=r"data/area.png")
        colour_selection = tk.PhotoImage(file=r"data/dropper_2.png")
        wand_selection = tk.PhotoImage(file=r"data/magic.png")
        fill = tk.PhotoImage(file=r"data/icons8-fill.png")
        dropper = tk.PhotoImage(file=r"data/dropper.png")
        zoom = tk.PhotoImage(file=r"data/search.png")
        text = tk.PhotoImage(file=r"data/font.png")
        red_colour = tk.PhotoImage(file=r"data/redColour.png")
        self.IMAGES['brush'] = brush
        self.IMAGES['pencil'] = pencil
        self.IMAGES['spray'] = spray
        self.IMAGES['colorPicker'] = colorPicker
        self.IMAGES['squaredSelection'] = squared_selection
        self.IMAGES['colourSelection'] = colour_selection
        self.IMAGES['wandSelection'] = wand_selection
        self.IMAGES['fill'] = fill
        self.IMAGES['pickColor'] = dropper
        self.IMAGES['zoom'] = zoom
        self.IMAGES['text'] = text
        self.IMAGES['redColour'] = red_colour

    # display message box
    def open_messagebox(self, mode, title, description):
        if mode == 0:
            response = messagebox.showerror(title, description)
        elif mode == 1:
            response = messagebox.showwarning(title, description)
        elif mode == 2:
            response = messagebox.showinfo(title, description)
        elif mode == 3:
            response = messagebox.askquestion(title, description)
        elif mode == 4:
            response = messagebox.askokcancel(title, description)
        elif mode == 5:
            response = messagebox.askretrycancel(title, description)
        elif mode == 6:
            response = messagebox.askyesno(title, description)
        elif mode == 7:
            response = messagebox.askyesnocancel(title, description)
        return response

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
    def refresh_image(self, image):
        self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(image)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)

    # displaying tool tip for widgets
    def create_tool_tip(self, widget, text="Temp"):
        tool_tip = ToolTip(widget)

        def enter(_):
            tool_tip.showtip(text)

        def leave(_):
            tool_tip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    # CREATING ALL WIDGETS IN MAIN WINDOW

    def create_widgets(self):
        # MENUS

        # toplevel menu
        self.MENU = tk.Menu(self)
        # display the menu
        self.parent.config(menu=self.MENU)

        # file menu
        self.FILE_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='File', menu=self.FILE_MENU)
        self.FILE_MENU.add_command(label='New project', command=lambda: self.new_project())
        self.FILE_MENU.add_command(label='Open project', command=lambda: self.open_project())
        self.FILE_MENU.add_command(label='Save', command=lambda: self.save_image())
        self.FILE_MENU.add_command(label='Save as', command=lambda: self.save_image_as())
        self.FILE_MENU.add_command(label='Recent', command=lambda: self.recent())
        self.FILE_MENU.add_command(label='Print', command=lambda: self.print_image())
        self.FILE_MENU.add_separator()
        self.FILE_MENU.add_command(label='Exit', command=self.quit)

        # edit menu
        self.EDIT_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='Edit', menu=self.EDIT_MENU)
        self.EDIT_MENU.add_command(label='Undo', command=lambda: self.undo())
        self.EDIT_MENU.add_command(label='Redo', command=lambda: self.redo())
        self.EDIT_MENU.add_command(label='Cut', command=lambda: self.cut())
        self.EDIT_MENU.add_command(label='Copy', command=lambda: self.copy())
        self.EDIT_MENU.add_command(label='Paste', command=lambda: self.paste())
        self.EDIT_MENU.add_command(label='Clear', command=lambda: self.clear())

        # view menu
        self.VIEW_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='View', menu=self.VIEW_MENU)
        self.VIEW_MENU.add_command(label='Zoom in/out', command=lambda: self.zoom_view())
        self.VIEW_MENU.add_command(label='Fullscreen', command=lambda: self.full_screen())

        # image menu
        self.IMAGE_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='Image', menu=self.IMAGE_MENU)
        self.IMAGE_MENU.add_command(label='Size', command=lambda: self.size_image())
        self.IMAGE_MENU.add_command(label='Colors space', command=lambda: self.color_space())

        # tools menu
        self.TOOLS_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='Tools', menu=self.TOOLS_MENU)
        self.TOOLS_MENU.add_command(label='Tool')
        self.TOOLS_MENU.add_command(label='Color')
        self.TOOLS_MENU.add_command(label='Selection')
        self.TOOLS_MENU.add_command(label='Fill')
        self.TOOLS_MENU.add_command(label='Pick color')
        self.TOOLS_MENU.add_command(label='Zoom')
        self.TOOLS_MENU.add_command(label='Text')

        # settings menu
        self.SETTINGS_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='Settings', menu=self.SETTINGS_MENU)
        self.SETTINGS_MENU.add_command(label='Preferences', command=lambda: self.preferences())
        self.SETTINGS_MENU.add_command(label='Shortcuts', command=lambda: self.shortcuts())

        # FRAMES

        # left frame for tools
        self.TOOLS_FRAME = tk.Frame(self, width=100)
        self.TOOLS_FRAME.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)
        self.TOOLS_FRAME.columnconfigure(0, weight=1)

        # central frame for image
        self.IMAGE_FRAME = tk.Frame(self, width=540, height=380)
        self.IMAGE_FRAME.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGE_FRAME.columnconfigure(0, weight=1)
        self.IMAGE_FRAME.rowconfigure(0, weight=1)

        # SUB_FRAMES

        # Creating sub_frames for different categories
        self.SUB_TOOLS_FRAME_1 = tk.Frame(self.TOOLS_FRAME, highlightbackground="grey", highlightthickness=1, bg="white")
        self.SUB_TOOLS_FRAME_1.grid(row=1, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.SUB_TOOLS_FRAME_2 = tk.Frame(self.TOOLS_FRAME, bd=1, highlightbackground="grey", highlightthickness=1,
                                         bg="white")
        self.SUB_TOOLS_FRAME_2.grid(row=4, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.SUB_TOOLS_FRAME_3 = tk.Frame(self.TOOLS_FRAME, bd=1, highlightbackground="grey", highlightthickness=1,
                                          bg="white")
        self.SUB_TOOLS_FRAME_3.grid(row=7, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)

        # Creating separator beetwen sub frames 1 & 2
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES = tk.Label(self.TOOLS_FRAME, text="", height=1)
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES.grid(row=2, column=0)

        # Creating separator beetwen sub frames 2 & 3
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES_2 = tk.Label(self.TOOLS_FRAME, text="", height=1)
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES_2.grid(row=5, column=0)

        # Creating SUB_TOOLS_FRAME_1 label
        self.SUB_TOOLS_FRAME_1_LABEL = tk.Label(self.TOOLS_FRAME, text="Scanner options", anchor=tk.N)
        self.SUB_TOOLS_FRAME_1_LABEL.grid(row=0, column=0, sticky=tk.W, padx=5)

        # Creating SUB_TOOLS_FRAME_2 label
        self.SUB_TOOLS_FRAME_2_LABEL = tk.Label(self.TOOLS_FRAME, text="Painting tools", anchor=tk.N)
        self.SUB_TOOLS_FRAME_2_LABEL.grid(row=3, column=0, sticky=tk.W, padx=5)

        # Creating SUB_TOOLS_FRAME_3 label
        self.SUB_TOOLS_FRAME_3_LABEL = tk.Label(self.TOOLS_FRAME, text="Tool configuration", anchor=tk.N)
        self.SUB_TOOLS_FRAME_3_LABEL.grid(row=6, column=0, sticky=tk.W, padx=5)

        # CAMERA SUB FRAME

        # Creating config button
        self.CONFIG_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_1, text="Scan", anchor=tk.CENTER, width=9, bg="green",
                                       command=self.camera_config_action)
        self.CONFIG_BUTTON.grid(row=0, column=0, padx=15, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.CONFIG_BUTTON, "Start scanning object")

        # Creating toggle button
        self.TOGGLE_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_1, text="Toggle view", anchor=tk.CENTER, bg="green",
                                       command=self.toggle_view_action)
        self.TOGGLE_BUTTON.grid(row=1, column=0, padx=15, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.TOGGLE_BUTTON, "Toggle view between image and camera")

        # TOOLS SUB FRAME WIDGETS

        # Creating tools button
        self.TOOL_BUTTON = tk.Menubutton(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['brush'], compound=tk.CENTER,
                                        bg="white")
        self.TOOL_BUTTON.grid(row=0, column=0, padx=10, pady=5, sticky=tk.N + tk.S + tk.W + tk.E)

        # Creating tools menu
        self.TOOL_BUTTON.menu = tk.Menu(self.TOOL_BUTTON, tearoff=0)
        self.TOOL_BUTTON["menu"] = self.TOOL_BUTTON.menu
        self.TOOL_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['brush'],
                                         command=lambda: self.change_tool(0))
        self.TOOL_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['pencil'],
                                         command=lambda: self.change_tool(1))
        self.TOOL_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['spray'],
                                         command=lambda: self.change_tool(2))
        # ToolTip for button
        self.create_tool_tip(self.TOOL_BUTTON, "Tool")

        # Creating colour button
        self.COLOUR_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, image=self.IMAGES['colorPicker'], bd=0, compound=tk.CENTER,
                                      command=self.color_chooser)
        self.COLOUR_BUTTON.grid(row=0, column=1, padx=0, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.COLOUR_BUTTON, "Colour")

        self.SELECTION_BUTTON = tk.Menubutton(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['squaredSelection'],
                                              compound=tk.CENTER, bg="white")
        self.SELECTION_BUTTON.grid(row=1, column=0, padx=10, pady=5, sticky=tk.N)

        # Creating selection menu
        self.SELECTION_BUTTON.menu = tk.Menu(self.SELECTION_BUTTON, tearoff=0)
        self.SELECTION_BUTTON["menu"] = self.SELECTION_BUTTON.menu
        self.SELECTION_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['squaredSelection'],
                                               command=lambda: self.change_selection(0))
        self.SELECTION_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['colourSelection'],
                                               command=lambda: self.change_selection(1))
        self.SELECTION_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['wandSelection'],
                                               command=lambda: self.change_selection(2))
        # ToolTip for button
        self.create_tool_tip(self.SELECTION_BUTTON, "Selection")

        # Creating fill button
        self.FILL_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['fill'], compound=tk.CENTER, bg="white",
                                       command=lambda: self.use_fill())
        self.FILL_BUTTON.grid(row=1, column=1, padx=0, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.FILL_BUTTON, "Fill")

        # Creating pobierz kolor
        self.PICK_COLOR_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['pickColor'], compound=tk.CENTER,
                                     bg="white",
                                     command=lambda: self.use_pick_color())
        self.PICK_COLOR_BUTTON.grid(row=2, column=0, padx=10, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.PICK_COLOR_BUTTON, "Pick color")

        # Creating zoom button
        self.ZOOM_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['zoom'], compound=tk.CENTER,
                                     bg="white",
                                     command=lambda: self.use_zoom())
        self.ZOOM_BUTTON.grid(row=2, column=1, padx=0, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.ZOOM_BUTTON, "Zoom")

        # Creating text button
        self.TEXT_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['text'], compound=tk.CENTER,
                                     bg="white", command=lambda: self.use_text())
        self.TEXT_BUTTON.grid(row=3, column=0, padx=10, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.TEXT_BUTTON, "Text")

        # TOOLS SUB FRAME WIDGETS

        self.TEMP_LABEL_0 = tk.Label(self.SUB_TOOLS_FRAME_3, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_0.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_1 = tk.Label(self.SUB_TOOLS_FRAME_3, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_2 = tk.Label(self.SUB_TOOLS_FRAME_3, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_2.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_3 = tk.Label(self.SUB_TOOLS_FRAME_3, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_3.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_4 = tk.Label(self.SUB_TOOLS_FRAME_3, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_4.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)

        # IMAGE FRAME WIDGETS

        # Creating display space for image/camera view
        self.display = tk.Canvas(self.IMAGE_FRAME, bd=0, highlightthickness=0, bg="black")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.display.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.IMAGE_FRAME.bind("<Configure>", self.resize_event)

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.IMAGES = {}
        self.style = ttk.Style()
        self.style.theme_use('alt')
        # self.style = ThemedStyle(self.parent)
        # self.style.set_theme("scidgrey")
        # initializing camera module
        # VARIABLES
        self.usage = Camera.camera()
        self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(Br.canvas_matrix)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        self.path_to_save = ""
        # FLAGS
        self.fullScreenStateFlag = False
        self.savedFlag = True
        # INIT WINDOW
        self.parent.attributes("-fullscreen", self.fullScreenStateFlag)
        self.init_gui()
        self.check_if_already_showing = 0
        self.check_if_configured = 0

    def init_gui(self):
        self.parent.title("Camera Paint")
        self.parent.geometry('1280x720')
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

