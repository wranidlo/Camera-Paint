import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import cv2
import numpy as np
import re
from camera import Camera
import brushes.Brushes as Br
from gui import ConfigManager
import imutils
import os

current_tool = Br.brush
current_tool_size = 3
current_tool_type = 0
current_tool_opacity = 1.0
current_shape_size = 10
current_shape_thickness = 2
text_to_draw = ""


# Class to auto hide/show scrollbar
class AutoScrollbar(tk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        None
        # raise tk.TclError, "cannot use pack with this widget"
    def place(self, **kw):
        None
        # raise tk.TclError, "cannot use place with this widget"

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

# class to display current tool config panel
class ToolsConfigPanel(object):
    def __init__(self, root, frame, images, panelNumber=0):
        self.images = images
        self.root = root
        self.frame = frame
        self.panelNumber = panelNumber
        self.tool_size = tk.IntVar()
        self.tool_opacity = tk.DoubleVar()
        self.shape_size = tk.IntVar()
        self.shape_thickness = tk.IntVar()
        self.text = tk.StringVar()
        self.minToolSize = 1
        self.maxToolSize = 20
        self.minShapeSize = 1
        self.maxShapeSize = 100
        self.minToolOpacity = 0.0
        self.maxToolOpacity = 1.0
        self.maxShapeThickness = 20
        self.minShapeThickness = 1
        self.vcmd = (root.register(self.digitOnlyTextEntryCallback))
        self.vcmd2 = (root.register(self.digitdotOnlyTextEntryCallback))
        self.changePanel(self.panelNumber)

    # callback method for digit only text entry widget
    def digitOnlyTextEntryCallback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    # callback method for digit only text entry widget
    def digitdotOnlyTextEntryCallback(self, P):
        if str.isdigit(P) or P == "" or P == ".":
            return True
        else:
            return False

    # provides the correct value of the variable
    def changeTextParam(self, event):
        global text_to_draw
        text_to_draw = self.text.get()

    # provides the correct value of the variable
    def changeShapeParam(self, newSize, newThickness):
        global current_shape_size, current_shape_thickness

        if self.minShapeSize <= newSize <= self.maxShapeSize:
            self.shape_size.set(newSize)
            current_shape_size = newSize
        elif newSize < self.minShapeSize:
            self.shape_size.set(self.minShapeSize)
            current_shape_size = self.minShapeSize
        elif newSize > self.maxShapeSize:
            self.shape_size.set(self.maxShapeSize)
            current_shape_size = self.maxShapeSize

        if self.minShapeThickness <= newThickness <= self.maxShapeThickness:
            self.shape_thickness.set(newThickness)
            current_shape_thickness = newThickness
        elif newThickness < self.minShapeThickness:
            self.shape_thickness.set(self.minShapeThickness)
            current_shape_thickness = self.minShapeThickness
        elif newThickness > self.maxShapeThickness:
            self.shape_thickness.set(self.maxShapeThickness)
            current_shape_thickness = self.maxShapeThickness

    # provides the correct value of the variable
    def changeToolParam(self, newSize, newOpacity):
        global current_tool
        global current_tool_size
        global current_tool_type
        global current_tool_opacity
        # checking new size
        newOpacity = round(newOpacity, 2)
        if newSize >= self.minToolSize and newSize <= self.maxToolSize:
            self.tool_size.set(newSize)
            current_tool_size = newSize
        elif newSize < self.minToolSize:
            self.tool_size.set(self.minToolSize)
            current_tool_size = self.minToolSize
        elif newSize > self.maxToolSize:
            self.tool_size.set(self.maxToolSize)
            current_tool_size = self.maxToolSize
        # checking new opacity
        if newOpacity >= self.minToolOpacity and newOpacity <= self.maxToolOpacity:
            self.tool_opacity.set(newOpacity)
            current_tool_opacity = newOpacity
        elif newOpacity < self.minToolOpacity:
            self.tool_opacity.set(0.0)
            current_tool_opacity = self.minToolOpacity
        elif newOpacity > self.maxToolOpacity:
            self.tool_opacity.set(self.maxToolOpacity)
            current_tool_opacity = self.maxToolOpacity
        #if len(current_tool_opacity) > 3:
        current_tool_opacity = newOpacity
        self.tool_opacity.set(newOpacity)
        # checking current tool
        if current_tool_type == 0:
            Br.b_brush = Br.Brush(Br.influence_brush, current_tool_size, 1, 0, current_tool_opacity)
            Br.brush = Br.b_brush.get_transformed_brush()
            current_tool = Br.brush
        elif current_tool_type == 1:
            Br.b_pencil = Br.Brush(Br.influence_pencil, current_tool_size, 1, 0, current_tool_opacity)
            Br.pencil = Br.b_pencil.get_transformed_brush()
            current_tool = Br.pencil
        elif current_tool_type == 2:
            Br.b_spray = Br.Brush(Br.influence_spray, current_tool_size, 1, 0, current_tool_opacity)
            Br.spray = Br.b_spray.get_transformed_brush()
            current_tool = Br.spray

    # change current panel
    def changePanel(self, panelNumber):
        if panelNumber == 0:
            self.panelNumber = 0
            self.emptyPanel()
        elif panelNumber == 1:
            self.panelNumber = 1
            self.toolsPanel()
        elif panelNumber == 2:
            self.panelNumber = 2
            self.textPanel()
        elif panelNumber == 3:
            self.panelNumber = 3
            self.shapePanel()

    # default empty panel if no tools choosen
    def emptyPanel(self):
        self.TEMP_LABEL_0 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_0.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_1 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_2 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_2.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_3 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_3.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N)
        self.TEMP_LABEL_4 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_4.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)

    # panel for painting tools: spray, pencil, brush
    def toolsPanel(self):
        global current_tool

        # size config widgets
        self.size_label = tk.Label(self.frame, bd=0, text="Size", bg="white")
        self.size_label.grid(row=0, column=0, padx=5, pady=1, sticky=tk.N)
        self.size_entry = ttk.Entry(self.frame, width=4, validate='all', textvariable=self.tool_size,
                                    validatecommand=(self.vcmd, '%P'))
        self.size_entry.grid(row=1, column=0)
        self.size_entry.bind('<Return>', lambda: self.changeToolParam(self.tool_size.get(), current_tool_opacity))
        self.tool_size.set(current_tool_size)
        self.size_decrease_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['minus'],
                                              command=lambda: self.changeToolParam(current_tool_size - 1, current_tool_opacity))
        self.size_decrease_button.grid(row=1, column=1, padx=5, pady=1, sticky=tk.N)
        self.size_increase_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['plus'],
                                              command=lambda: self.changeToolParam(current_tool_size + 1, current_tool_opacity))
        self.size_increase_button.grid(row=1, column=2, padx=5, pady=1, sticky=tk.N)

        # opacity config widgets
        self.opacity_label = tk.Label(self.frame, bd=0, text="Opacity", bg="white")
        self.opacity_label.grid(row=2, column=0, padx=5, pady=1, sticky=tk.N)
        self.opacity_entry = ttk.Entry(self.frame, width=4, validate='all', textvariable=self.tool_opacity,
                                    validatecommand=(self.vcmd2, '%P'))
        self.opacity_entry.grid(row=3, column=0)
        self.opacity_entry.bind('<Return>', lambda: self.changeToolParam(current_tool_size, self.tool_opacity.get()))
        self.tool_opacity.set(current_tool_opacity)
        self.opacity_decrease_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['minus'],
                                              command=lambda: self.changeToolParam(current_tool_size, current_tool_opacity - 0.1))
        self.opacity_decrease_button.grid(row=3, column=1, padx=5, pady=1, sticky=tk.N)
        self.opacity_increase_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['plus'],
                                              command=lambda: self.changeToolParam(current_tool_size, current_tool_opacity + 0.1))
        self.opacity_increase_button.grid(row=3, column=2, padx=5, pady=1, sticky=tk.N)

        # empty space
        self.TEMP_LABEL_4 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_4.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)

    # panel for text tool
    def textPanel(self):
        global current_tool

        # size config widgets
        self.size_label = tk.Label(self.frame, bd=0, text="Size", bg="white")
        self.size_label.grid(row=0, column=0, padx=5, pady=1, sticky=tk.N)
        self.size_entry = ttk.Entry(self.frame, width=4, validate='all', textvariable=self.tool_size,
                                    validatecommand=(self.vcmd, '%P'))
        self.size_entry.grid(row=1, column=0)
        self.size_entry.bind('<Return>', lambda: self.changeToolParam(self.tool_size.get(), current_tool_opacity))
        self.tool_size.set(current_tool_size)
        self.size_decrease_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['minus'],
                                              command=lambda: self.changeToolParam(current_tool_size - 1,
                                                                                   current_tool_opacity))
        self.size_decrease_button.grid(row=1, column=1, padx=5, pady=1, sticky=tk.N)
        self.size_increase_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['plus'],
                                              command=lambda: self.changeToolParam(current_tool_size + 1,
                                                                                   current_tool_opacity))
        self.size_increase_button.grid(row=1, column=2, padx=5, pady=1, sticky=tk.N)

        # text config widgets
        self.text_label = tk.Label(self.frame, bd=0, text="Text", bg="white")
        self.text_label.grid(row=2, column=0, padx=5, pady=1, sticky=tk.N)
        global text_to_draw
        self.text_entry = ttk.Entry(self.frame, width=13, validate='all', textvariable=self.text)
        self.text_entry.grid(row=3, column=0, columnspan=3)
        self.text_entry.bind('<Return>', self.changeTextParam)
        # empty space
        self.TEMP_LABEL_4 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_4.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)

    # panel for shape tool
    def shapePanel(self):

        # size config widgets
        self.size_label = tk.Label(self.frame, bd=0, text="Size", bg="white")
        self.size_label.grid(row=0, column=0, padx=5, pady=1, sticky=tk.N)
        self.size_entry = ttk.Entry(self.frame, width=4, validate='all', textvariable=self.shape_size,
                                    validatecommand=(self.vcmd, '%P'))
        self.size_entry.grid(row=1, column=0)
        self.size_entry.bind('<Return>', lambda: self.changeShapeParam(self.shape_size.get(), current_shape_thickness))
        self.shape_size.set(current_shape_size)
        self.size_decrease_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['minus'],
                                              command=lambda: self.changeShapeParam(current_shape_size - 1,
                                                                                    current_shape_thickness))
        self.size_decrease_button.grid(row=1, column=1, padx=5, pady=1, sticky=tk.N)
        self.size_increase_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['plus'],
                                              command=lambda: self.changeShapeParam(current_shape_size + 1,
                                                                                    current_shape_thickness))
        self.size_increase_button.grid(row=1, column=2, padx=5, pady=1, sticky=tk.N)

        # thickness config widgets
        self.thickness_label = tk.Label(self.frame, bd=0, text="Thickness", bg="white")
        self.thickness_label.grid(row=2, column=0, padx=5, pady=1, sticky=tk.N)
        self.thickness_entry = ttk.Entry(self.frame, width=4, validate='all', textvariable=self.shape_thickness,
                                         validatecommand=(self.vcmd2, '%P'))
        self.thickness_entry.grid(row=3, column=0)
        self.thickness_entry.bind('<Return>', lambda: self.changeShapeParam(current_shape_size, self.shape_thickness.get()))
        self.shape_thickness.set(current_shape_thickness)
        self.thickness_decrease_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['minus'],
                                                 command=lambda: self.changeShapeParam(current_shape_size,
                                                                                       current_shape_thickness - 1))
        self.thickness_decrease_button.grid(row=3, column=1, padx=5, pady=1, sticky=tk.N)
        self.thickness_increase_button = tk.Button(self.frame, bd=0, bg="white", underline=0, image=self.images['plus'],
                                                 command=lambda: self.changeShapeParam(current_shape_size,
                                                                                       current_shape_thickness + 1))
        self.thickness_increase_button.grid(row=3, column=2, padx=5, pady=1, sticky=tk.N)

        # empty space
        self.TEMP_LABEL_4 = tk.Label(self.frame, bd=0, text="", bg="white", compound=tk.CENTER)
        self.TEMP_LABEL_4.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)


# class to display new change image size window
class ImageSizeWindow(object):
    def __init__(self, root):
        self.image_height = tk.IntVar()
        self.image_width = tk.IntVar()
        self.vcmd = (root.register(self.callback))
        self.imageSizeWindow = tk.Toplevel(root)
        self.imageSizeWindow.title("Image size")
        self.imageSizeWindow.resizable(False, False)

        self.labelWidth = tk.Label(self.imageSizeWindow, text="Width")
        self.labelWidth.grid(row=0, column=0)
        self.sliderWidth = tk.Scale(self.imageSizeWindow, orient=tk.HORIZONTAL, from_=1, to=2000, resolution=1,
                                    length=300, sliderlength=5, variable=self.image_width)
        self.sliderWidth.grid(row=0, column=1)
        self.entryWidth = ttk.Entry(self.imageSizeWindow, width=4, validate='all', textvariable=self.image_width,
                                    validatecommand=(self.vcmd, '%P'))
        self.entryWidth.grid(row=0, column=2)
        self.image_width.set(Br.size_y)

        self.labelHeight = tk.Label(self.imageSizeWindow, text="Height")
        self.labelHeight.grid(row=1, column=0)
        self.sliderHeight = tk.Scale(self.imageSizeWindow, orient=tk.HORIZONTAL, from_=1, to=2000, resolution=1,
                                     length=300, sliderlength=5, variable=self.image_height)
        self.sliderHeight.grid(row=1, column=1)
        self.entryHeight = ttk.Entry(self.imageSizeWindow, width=4, validate='all', textvariable=self.image_height,
                                     validatecommand=(self.vcmd, '%P'))
        self.entryHeight.grid(row=1, column=2)
        self.image_height.set(Br.size_x)

        self.buttonOk = tk.Button(self.imageSizeWindow, text="Ok", command=self.choiceOk)
        self.buttonOk.grid(row=2, column=1)

    def callback(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def choiceOk(self):
        self.image_width = self.sliderWidth.get()
        self.image_height = self.sliderHeight.get()
        self.imageSizeWindow.destroy()

# MAIN APP CLASS

class Application(tk.Frame):

    # BUTTON COMMANDS METHODS

    # TOOLS METHODS

    # open scan view to configure pointer CAMERA
    def camera_config_action(self):
        if not self.check_if_showing_painting and not self.check_if_showing_point:
            if not self.check_if_scanning:
                self.check_if_scanning = True

                self.CONFIG_BUTTON.config(text="Stop", bg="red")

                self.usage.set_histogram_created_check_not()
                self.usage.cap = cv2.VideoCapture(0)
                self.show_config()
            else:
                self.CONFIG_BUTTON.config(text="Scan", bg="green")

                self.usage.histogram_created_check = True
                self.check_if_scanning = False
                self.usage.cap.release()
                self.show_image(Br.canvas_matrix_temp)

    # displaying current scan view CAMERA
    def show_config(self):
        if self.check_if_scanning:
            frame = self.usage.search_for_object()
            quality = self.usage.check_quality(frame)
            if quality == 1:
                cv2.putText(frame, "Very good", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0),
                            thickness=2)
            else:
                if quality < 6:
                    cv2.putText(frame, "Good", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0,),
                                thickness=2)
                else:
                    if quality < 15:
                        cv2.putText(frame, "Fine", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                                    color=(0, 255, 255),
                                    thickness=2)
                    else:
                        cv2.putText(frame, "Bad", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255),
                                    thickness=2)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.display.delete("IMG")
            self.show_image(frame)
            self.display.after(10, self.show_config)


    # open camera view CAMERA
    def point_view_action(self):
        if not self.check_if_showing_painting:
            if not self.check_if_showing_point:
                if self.usage.histogram_created_check is True:
                    self.check_if_showing_point = True

                    self.POINT_BUTTON.config(text="Stop view", bg="red")
                    self.usage.cap = cv2.VideoCapture(0)
                    self.show_center()
            else:
                if self.usage.histogram_created_check is True:
                    self.usage.cap.release()
                    self.POINT_BUTTON.config(text="Show point", bg="green")
                    self.check_if_showing_point = False
                    self.show_image(Br.canvas_matrix_temp)

    # displaying current camera view CAMERA
    def show_center(self):
        if self.check_if_showing_point:
            img, _ = self.usage.get_center()
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            self.show_image(img)

            self.display.after(10, self.show_center)

    def paint_toggle_action(self):
        if not self.check_if_showing_point:
            if not self.check_if_showing_painting:
                if self.usage.histogram_created_check is True:
                    self.check_if_showing_painting = True

                    self.PAINT_BUTTON.config(text="Stop paint mode", bg="red")
                    self.usage.cap = cv2.VideoCapture(0)
                    self.draw_something()
            else:
                if self.usage.histogram_created_check is True:
                    self.painting_flag = False
                    self.usage.cap.release()
                    self.PAINT_BUTTON.config(text="Paint mode", bg="green")
                    Br.save_step()
                    self.check_if_showing_painting = False
                    self.show_image(Br.canvas_matrix_temp)

    def draw_something(self):
        global current_tool
        if self.check_if_showing_painting:
            img, loc = self.usage.get_center()
            x, y = loc
            x = int(Br.size_x / self.usage.rows) * x
            y = int(Br.size_y / self.usage.cols) * y
            if self.painting_flag:
                if isinstance(current_tool, int):
                    if current_tool == 0:
                        cv2.rectangle(Br.canvas_matrix_temp, (x, y), (x+current_shape_size, y+current_shape_size),
                                      self.current_color, current_shape_thickness)
                        self.painting_flag = False
                        Br.save_step()
                        Br.canvas_matrix_temp = Br.canvas_matrix
                    else:
                        if current_tool == 1:
                            cv2.circle(Br.canvas_matrix_temp, (x, y), current_shape_size, self.current_color, -1)
                            self.painting_flag = False
                            Br.save_step()
                            Br.canvas_matrix_temp = Br.canvas_matrix
                        else:
                            if current_tool == 2:
                                cv2.circle(Br.canvas_matrix_temp, (x, y), current_shape_size, self.current_color,
                                           current_shape_thickness)
                                self.painting_flag = False
                                Br.save_step()
                                Br.canvas_matrix_temp = Br.canvas_matrix
                else:
                    Br.draw(y, x, current_tool, self.current_color)
            tmp = Br.canvas_matrix_temp.copy()
            cv2.circle(tmp, (x, y), 5, [0, 0, 0], -1)
            self.show_image(tmp)
            self.display.after(1, self.draw_something)

    # displaying image BRUSHES
    def show_image(self, image):
        self.refresh_image(image)
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")

    # opening color_chooser window
    def color_chooser(self):
        color = colorchooser.askcolor(title="Select color")
        self.COLOUR_BUTTON.configure(fg=color[1])
        h = str(color[1]).lstrip('#')
        self.current_color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def change_tool(self, tool):
        global current_tool
        global current_tool_type
        global current_tool_opacity
        current_tool_type = tool
        if tool == 0:
            self.TOOL_BUTTON.config(image=self.IMAGES['brush'])
            self.TOOL_BUTTON.image = self.IMAGES['brush']
            Br.b_brush = Br.Brush(Br.influence_brush, current_tool_size, 1, 0, current_tool_opacity)
            Br.brush = Br.b_brush.get_transformed_brush()
            current_tool = Br.brush
        elif tool == 1:
            self.TOOL_BUTTON.config(image=self.IMAGES['pencil'])
            self.TOOL_BUTTON.image = self.IMAGES['pencil']
            Br.b_pencil = Br.Brush(Br.influence_pencil, current_tool_size, 1, 0, current_tool_opacity)
            Br.pencil = Br.b_pencil.get_transformed_brush()
            current_tool = Br.pencil
        elif tool == 2:
            self.TOOL_BUTTON.config(image=self.IMAGES['spray'])
            self.TOOL_BUTTON.image = self.IMAGES['spray']
            Br.b_spray = Br.Brush(Br.influence_spray, current_tool_size, 1, 0, current_tool_opacity)
            Br.spray = Br.b_spray.get_transformed_brush()
            current_tool = Br.spray
        self.clearConfigPanel()
        self.toolsConfigPanel = ToolsConfigPanel(root, self.SUB_TOOLS_FRAME_3, self.IMAGES, 1)

    def change_shape(self, type):
        global current_tool
        if type == 0:
            self.SHAPES_BUTTON.config(image=self.IMAGES['square'])
            self.SHAPES_BUTTON.image = self.IMAGES['square']
            current_tool = 0
        elif type == 1:
            self.SHAPES_BUTTON.config(image=self.IMAGES['filled_circle'])
            self.SHAPES_BUTTON.image = self.IMAGES['filled_circle']
            current_tool = 1
        elif type == 2:
            self.SHAPES_BUTTON.config(image=self.IMAGES['circle'])
            self.SHAPES_BUTTON.image = self.IMAGES['circle']
            current_tool = 2
        self.clearConfigPanel()
        self.toolsConfigPanel = ToolsConfigPanel(root, self.SUB_TOOLS_FRAME_3, self.IMAGES, 3)

    def use_fill(self):
        _, x_y = self.usage.get_center()
        Br.fill(x_y[0], x_y[1], self.current_color)

    def use_pick_color(self):
        _, x_y = self.usage.get_center()
        self.current_color = Br.canvas_matrix[x_y[1]][x_y[0]]

    def use_text(self):
        global text_to_draw
        if len(text_to_draw) == 0:
            self.clearConfigPanel()
            self.toolsConfigPanel = ToolsConfigPanel(root, self.SUB_TOOLS_FRAME_3, self.IMAGES, 2)
        if self.check_if_showing_painting:
            font = cv2.FONT_HERSHEY_SIMPLEX
            _, loc = self.usage.get_center()
            x, y = loc
            cv2.putText(Br.canvas_matrix, text_to_draw, (x, y), font, current_tool_size, self.current_color, 1, cv2.LINE_AA)
            Br.canvas_matrix_temp = Br.canvas_matrix
            self.show_image(Br.canvas_matrix_temp)
            Br.save_step()

    # FILE MENU METHODS
    def new_project(self):
        Br.clean_canvas()
        Br.clear_steps()
        if self.savedFlag:
            Br.canvas_matrix = np.empty((Br.size_x, Br.size_y, 3), dtype='uint8')
            Br.canvas_matrix.fill(255)
            self.show_image(Br.canvas_matrix_temp)
        else:
            response = self.open_messagebox(6, "Not saved changes", "You want to continue without saving?")
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
                self.config.add_recent(self.path_to_save)
                self.reload_recent_menu()
                self.OBJECT_TO_DISPLAY_IMAGE = Image.open(self.path_to_save)
                self.OBJECT_TO_DISPLAY_IMAGE.load()
                Br.load(np.array(self.OBJECT_TO_DISPLAY_IMAGE, dtype="uint8"))
                self.show_image(Br.canvas_matrix_temp)
        else:
            response = self.open_messagebox(6, "Not saved changes", "You want to continue without saving?")
            if response:
                self.savedFlag = True
                self.open_project()

    def quick_open_project(self, path):
        self.OBJECT_TO_DISPLAY_IMAGE = Image.open(path)
        self.OBJECT_TO_DISPLAY_IMAGE.load()
        Br.load(np.array(self.OBJECT_TO_DISPLAY_IMAGE, dtype="uint8"))
        self.path_to_save = path
        self.config.add_recent(self.path_to_save)
        self.reload_recent_menu()
        self.show_image(Br.canvas_matrix_temp)

    def save_image(self):
        if self.path_to_save == "":
            self.save_image_as()
        else:
            self.OBJECT_TO_DISPLAY_IMAGE.save(self.path_to_save)
            self.config.add_recent(self.path_to_save)
            self.reload_recent_menu()

    def save_image_as(self):
        self.path_to_save = fd.asksaveasfilename(filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg *.jpe *.jfif"),
                                                            ("GIF", "*.gif"), ("TIFF", "*.tif *.tiff"), ("BMP", "*.bmp")],
                                        defaultextension="*.png")  # wywołanie okna dialogowego save file

        if self.path_to_save != "":
            self.OBJECT_TO_DISPLAY_IMAGE.save(self.path_to_save)
            self.config.add_recent(self.path_to_save)
            self.reload_recent_menu()

    def recent(self):
        self.config.read()
        self.config.display_config()

    # EDIT MENU METHODS
    def undo(self):
        Br.b_undo()
        self.show_image(Br.canvas_matrix_temp)

    def redo(self):
        Br.b_redo()
        self.show_image(Br.canvas_matrix_temp)

    def cut(self):
        Br.cut()
        Br.save_step()

    def copy(self):
        Br.copy()
        Br.save_step()

    def paste(self):
        _, x_y = self.usage.get_center()
        Br.paste(x_y[0], x_y[1])
        Br.save_step()

    def clear(self):
        Br.clean_canvas()
        Br.save_step()

    # VIEW MENU METHODS
    def full_screen(self):
        if self.fullScreenStateFlag:
            self.fullScreenStateFlag = False
            self.VIEW_MENU.entryconfigure(0, label="Fullscreen")
        else:
            self.fullScreenStateFlag = True
            self.VIEW_MENU.entryconfigure(0, label="Exit fullscreen")
        self.parent.attributes("-fullscreen", self.fullScreenStateFlag)
        self.config.change_options(self.fullScreenStateFlag, self.blockWindowSizeFlag)

    def block_resize(self):
        if self.blockWindowSizeFlag:
            self.blockWindowSizeFlag = False
            self.parent.resizable(width=True, height=True)
            self.VIEW_MENU.entryconfigure(1, label="Block window size")
        else:
            self.blockWindowSizeFlag = True
            self.parent.resizable(width=False, height=False)
            self.VIEW_MENU.entryconfigure(1, label="Unblock window size")
        self.config.change_options(self.fullScreenStateFlag, self.blockWindowSizeFlag)


    # IMAGE MENU METHODS
    def size_image(self):
        window = ImageSizeWindow(root)
        root.wait_window(window.imageSizeWindow)
        Br.resize(window.image_height, window.image_width)
        self.image_resized()


    def rotate(self, degrees):
        Br.canvas_matrix = imutils.rotate(Br.canvas_matrix, angle=degrees)
        Br.canvas_matrix_temp = Br.canvas_matrix
        self.show_image(Br.canvas_matrix_temp)
        Br.save_step()

    # clear config panel
    def clearConfigPanel(self):
        self.SUB_TOOLS_FRAME_3.destroy()
        self.SUB_TOOLS_FRAME_3 = tk.Frame(self.TOOLS_FRAME, bd=1, highlightbackground="gray", highlightthickness=1,
                                          bg="white")
        self.SUB_TOOLS_FRAME_3.grid(row=7, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)

    # EVENTS METHODS

    # resizing elements to current widget size after event of changed size
    def windows_resized(self, event):
        if self.window_width != root.winfo_width() or self.window_height != root.winfo_height():
            self.window_height = root.winfo_height()
            self.window_width = root.winfo_width()
            temp_width = self.window_width - 108
            temp_height = self.window_height
            temp2_width = self.window_width - 152
            temp2_height = self.window_height - 20
            self.IMAGE_FRAME.config(width=temp_width, height=temp_height)
            self.display.config(width=temp2_width, height=temp2_height)
            self.display_hbar.config(command=self.display.xview)
            self.display_vbar.config(command=self.display.yview)
            self.display.config(xscrollcommand=self.display_hbar.set, yscrollcommand=self.display_vbar.set,
                                scrollregion=(0, 0, Br.size_y, Br.size_x))
            self.IMAGE_FRAME.update()
            self.place_image_in_canvas(Br.canvas_matrix_temp)

    def resize_in_canvas_event(self, event):
        size = (event.width, event.height)
        self.OBJECT_TO_DISPLAY_IMAGE = self.OBJECT_TO_DISPLAY_IMAGE.resize(size, Image.ANTIALIAS)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")

    # painting mode activator
    def painting_activator(self, event):
        if not self.check_if_scanning and not self.check_if_showing_point:
            if self.check_if_showing_painting:
                if self.painting_flag:
                    self.painting_flag = False
                    Br.save_step()
                else:
                    self.painting_flag = True

    # GUI SUPPORT METHODS

    # loading using images to list
    def initialize_images(self):
        # ICONS 24x24 pixels
        brush = ImageTk.PhotoImage(file=r"../resources/data/brush.png")
        pencil = tk.PhotoImage(file=r"../resources/data/pencil.png")
        spray = tk.PhotoImage(file=r"../resources/data/spray.png")
        colorPicker = tk.PhotoImage(file=r"../resources/data/icons8-colors.png")
        fill = tk.PhotoImage(file=r"../resources/data/icons8-fill.png")
        dropper = tk.PhotoImage(file=r"../resources/data/dropper.png")
        text = tk.PhotoImage(file=r"../resources/data/font.png")
        plus = tk.PhotoImage(file=r"../resources/data/plus.png")
        minus = tk.PhotoImage(file=r"../resources/data/minus.png")
        square = tk.PhotoImage(file=r"../resources/data/rectangle.png")
        filled_circle = tk.PhotoImage(file=r"../resources/data/filled_circle.png")
        circle = tk.PhotoImage(file=r"../resources/data/circle.png")
        self.IMAGES['square'] = square
        self.IMAGES['filled_circle'] = filled_circle
        self.IMAGES['circle'] = circle
        self.IMAGES['brush'] = brush
        self.IMAGES['pencil'] = pencil
        self.IMAGES['spray'] = spray
        self.IMAGES['colorPicker'] = colorPicker
        self.IMAGES['fill'] = fill
        self.IMAGES['pickColor'] = dropper
        self.IMAGES['text'] = text
        self.IMAGES['plus'] = plus
        self.IMAGES['minus'] = minus

    def reload_recent_menu(self):
        self.RECENT_MENU.delete(0, self.RECENT_MENU.index("end"))
        path_1 = self.config.config.get('RECENT_IMAGES', 'first')
        path_2 = self.config.config.get('RECENT_IMAGES', 'second')
        path_3 = self.config.config.get('RECENT_IMAGES', 'third')
        path_4 = self.config.config.get('RECENT_IMAGES', 'fourth')
        path_5 = self.config.config.get('RECENT_IMAGES', 'fifth')
        if path_1 != "none":
            self.RECENT_MENU.add_command(label=path_1, command=lambda: self.quick_open_project(path_1))
        if path_2 != "none":
            self.RECENT_MENU.add_command(label=path_2, command=lambda: self.quick_open_project(path_2))
        if path_3 != "none":
            self.RECENT_MENU.add_command(label=path_3, command=lambda: self.quick_open_project(path_3))
        if path_4 != "none":
            self.RECENT_MENU.add_command(label=path_4, command=lambda: self.quick_open_project(path_4))
        if path_5 != "none":
            self.RECENT_MENU.add_command(label=path_5, command=lambda: self.quick_open_project(path_5))

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

    # resizing elements to current widget size, for not event cases (toogle view for example)
    def resize_in_canvas(self, canvas):
        size = (canvas.winfo_width(), canvas.winfo_height())
        self.OBJECT_TO_DISPLAY_IMAGE = self.OBJECT_TO_DISPLAY_IMAGE.resize(size, Image.ANTIALIAS)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")

    def image_resized(self):
        self.display_hbar.config(command=self.display.xview)
        self.display_vbar.config(command=self.display.yview)
        self.display.config(xscrollcommand=self.display_hbar.set, yscrollcommand=self.display_vbar.set, scrollregion=(0, 0, Br.size_y, Br.size_x))
        self.place_image_in_canvas(Br.canvas_matrix_temp)

    def place_image_in_canvas(self, image):
        self.refresh_image(image)
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.display.config(xscrollcommand=self.display_hbar.set, yscrollcommand=self.display_vbar.set)


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
        self.RECENT_MENU = tk.Menu(self.FILE_MENU)
        self.reload_recent_menu()
        self.FILE_MENU.add_cascade(label='Recent', menu=self.RECENT_MENU)
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
        self.VIEW_MENU.add_command(label='Fullscreen', command=lambda: self.full_screen())
        self.VIEW_MENU.add_command(label='Block window size', command=lambda: self.block_resize())
        if self.fullScreenStateFlag == True:
            self.VIEW_MENU.entryconfigure(0, label="Exit fullscreen")
        if self.blockWindowSizeFlag == True:
            self.VIEW_MENU.entryconfigure(1, label="Unblock window size")

        # image menu
        self.IMAGE_MENU = tk.Menu(self.MENU, tearoff=0)
        self.MENU.add_cascade(label='Image', menu=self.IMAGE_MENU)
        self.IMAGE_MENU.add_command(label='Size', command=lambda: self.size_image())
        self.IMAGE_MENU.add_command(label='Rotate 45% to right', command=lambda: self.rotate(45))
        self.IMAGE_MENU.add_command(label='Rotate 90% to right', command=lambda: self.rotate(90))
        self.IMAGE_MENU.add_command(label='Rotate 45% to left', command=lambda: self.rotate(-45))
        self.IMAGE_MENU.add_command(label='Rotate 90% to left', command=lambda: self.rotate(-90))

        # FRAMES

        # left frame for tools
        self.TOOLS_FRAME = tk.Frame(self, width=100)
        self.TOOLS_FRAME.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5, pady=5)
        self.TOOLS_FRAME.columnconfigure(0, weight=1)
        temp_height = self.window_height
        temp_width = self.window_width - 100
        # central frame for image
        self.IMAGE_FRAME = tk.Frame(self,  width=temp_width, height=temp_height)
        self.IMAGE_FRAME.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

        # SUB_FRAMES

        # Creating sub_frames for different categories
        self.SUB_TOOLS_FRAME_1 = tk.Frame(self.TOOLS_FRAME, highlightbackground="gray", highlightthickness=1, bg="white")
        self.SUB_TOOLS_FRAME_1.grid(row=1, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.SUB_TOOLS_FRAME_2 = tk.Frame(self.TOOLS_FRAME, bd=1, highlightbackground="gray", highlightthickness=1,
                                         bg="white")
        self.SUB_TOOLS_FRAME_2.grid(row=4, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)
        self.SUB_TOOLS_FRAME_3 = tk.Frame(self.TOOLS_FRAME, bd=1, highlightbackground="gray", highlightthickness=1,
                                          bg="white")
        self.SUB_TOOLS_FRAME_3.grid(row=7, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=5)

        # Creating separator beetwen sub frames 1 & 2
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES = tk.Label(self.TOOLS_FRAME, text="", height=1)
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES.grid(row=2, column=0)

        # Creating separator beetwen sub frames 2 & 3
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES_2 = tk.Label(self.TOOLS_FRAME, text="", height=1)
        self.SEPARATOR_BETWEEN_TOOLS_FRAMES_2.grid(row=5, column=0)

        # Creating SUB_TOOLS_FRAME_1 label
        self.SUB_TOOLS_FRAME_1_LABEL = tk.Label(self.TOOLS_FRAME, text="Modes of work", anchor=tk.N)
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
        self.POINT_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_1, text="Show point", anchor=tk.CENTER, bg="green",
                                      command=self.point_view_action)
        self.POINT_BUTTON.grid(row=1, column=0, padx=15, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.POINT_BUTTON, "Toggle showing point view")

        # Creating toggle button
        self.PAINT_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_1, text="Paint mode", anchor=tk.CENTER, bg="green",
                                      command=self.paint_toggle_action)
        self.PAINT_BUTTON.grid(row=2, column=0, padx=15, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.PAINT_BUTTON, "Toggle point view (pressing spacebar activate drawing)")

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

        self.SHAPES_BUTTON = tk.Menubutton(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['square'],
                                              compound=tk.CENTER, bg="white")
        self.SHAPES_BUTTON.grid(row=1, column=0, padx=10, pady=5, sticky=tk.N)

        # Creating selection menu
        self.SHAPES_BUTTON.menu = tk.Menu(self.SHAPES_BUTTON, tearoff=0)
        self.SHAPES_BUTTON["menu"] = self.SHAPES_BUTTON.menu
        self.SHAPES_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['square'],
                                               command=lambda: self.change_shape(0))
        self.SHAPES_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['filled_circle'],
                                               command=lambda: self.change_shape(1))
        self.SHAPES_BUTTON.menu.add_command(label='', underline=0, image=self.IMAGES['circle'],
                                               command=lambda: self.change_shape(2))
        # ToolTip for button
        self.create_tool_tip(self.SHAPES_BUTTON, "Shape")

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

        # Creating text button
        self.TEXT_BUTTON = tk.Button(self.SUB_TOOLS_FRAME_2, bd=0, image=self.IMAGES['text'], compound=tk.CENTER,
                                     bg="white", command=lambda: self.use_text())
        self.TEXT_BUTTON.grid(row=2, column=1, padx=10, pady=5, sticky=tk.N)
        # ToolTip for button
        self.create_tool_tip(self.TEXT_BUTTON, "Text")

        # TOOLS SUB FRAME WIDGETS
        self.clearConfigPanel()
        self.toolsConfigPanel = ToolsConfigPanel(root, self.SUB_TOOLS_FRAME_3, self.IMAGES, 1)

        # IMAGE FRAME WIDGETS

        # Creating display space for image/camera view
        temp2_height = self.window_height - 20
        temp2_width = self.window_width - 144
        self.display = tk.Canvas(self.IMAGE_FRAME, bd=0, highlightthickness=0, bg="gray", width=temp2_width, height=temp2_height, scrollregion=(0, 0, Br.size_y, Br.size_x))
        self.display.create_image(0, 0, image=self.OBJECT_TO_DISPLAY_PHOTOIMAGE, anchor=tk.NW, tags="IMG")
        self.display.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        # self.IMAGE_FRAME.bind("<Configure>", self.resize_in_canvas_event)
        self.display_hbar = tk.Scrollbar(self.IMAGE_FRAME, orient=tk.HORIZONTAL)
        self.display_hbar.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.display_hbar.config(command=self.display.xview)
        self.display_vbar = tk.Scrollbar(self.IMAGE_FRAME, orient=tk.VERTICAL)
        self.display_vbar.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        self.display_vbar.config(command=self.display.yview)
        self.display.config(xscrollcommand=self.display_hbar.set, yscrollcommand=self.display_vbar.set)


    def __init__(self, parent):
        global current_tool
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.style = ttk.Style()
        self.style.theme_use('alt')
        # initializing camera module
        # VARIABLES
        self.toolsConfigPanel = None
        self.usage = Camera.camera()
        Br.size_x = self.usage.rows
        Br.size_y = self.usage.cols
        self.OBJECT_TO_DISPLAY_IMAGE = Image.fromarray(Br.canvas_matrix_temp)
        self.OBJECT_TO_DISPLAY_PHOTOIMAGE = ImageTk.PhotoImage(self.OBJECT_TO_DISPLAY_IMAGE)
        self.path_to_save = ""
        if os.path.isfile('./config.ini'):
            self.config = ConfigManager.ConfigManager("config.ini")
        else:
            self.config = ConfigManager.ConfigManager("config.ini")
            self.config.write_default()
        self.config.read()
        self.IMAGES = {}
        # self.current_tool = Br.brush
        self.current_color = [0, 0, 255]
        self.window_width = 1280
        self.window_height = 720
        # FLAGS
        self.check_if_showing_painting = False
        self.check_if_showing_point = False
        self.check_if_scanning = False
        self.fullScreenStateFlag = self.config.get_fullscreen()
        self.savedFlag = True
        self.painting_flag = False
        self.blockWindowSizeFlag = self.config.get_blocksize()
        # GLOBAL EVENTS
        self.parent.bind("<space>", self.painting_activator)
        # self.parent.bind("<Configure>", self.windows_resized)
        root.bind("<Configure>", self.windows_resized)
        # INIT WINDOW
        self.parent.attributes("-fullscreen", self.fullScreenStateFlag)
        self.init_gui()


    def init_gui(self):
        self.parent.title("Camera Paint")
        self.parent.geometry('1280x720')
        self.parent.resizable(width=True, height=True)
        if self.blockWindowSizeFlag == True:
            self.parent.resizable(width=False, height=False)
        self.grid(sticky=tk.NSEW)
        self.initialize_images()
        self.create_widgets()


root = tk.Tk()
app = Application(parent=root)
app.mainloop()
try:
    root.destroy()
except tk.TclError:
    "App already closed"

