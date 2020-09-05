# Camera-Paint
[![.Python](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue)]()
---
System that allows to paint images with use of camera.  
You can scan any object you want and use it as your pointer.  
You can use a lot of diffrent types of pencils, brushes and other graphic tools. 

## Motivation

## Features
Basic feature of the program is to map the motion captured by the camera onto the image. We have created several different tools with different effect for this purpose. In the current version of the project ther are five types of tools to choose from:
1. Painting tool
    * Brush
    * Pencil
    * Spray
2. Shapes
    * Empty square
    * Full circle
    * Empty circle
3. Fill
4. Pick color
5. Text

Some of these tools have configuration options like size or opacity.
Except these tool, we also offer other options that are typical for graphic editors (undo, redo, cut, copy, paste, clear, changing image size) and saving images in five types (PNG, JPEG, GIF, TIFF and BMP).

## Technology
Project is created in Python 3 and uses several libraries:
1. OpenCV - for camera and image operations
2. Tkinter - for graphical user interface
3. Other libraries listed in the file requirements.txt

## How to use

### Instalation

### Instruction
1. Scan object that will be your pointer.
2. Check if scanned object is correctly tracked.
3. Start paint mode to use diffrent painting tools.
   * Press spacebar to draw with chosen drawing tool (brush, spray, pnecil) or to add chosen shape (square, empty circle, filled cirlce).
   * To add text choose option "text" and input chosen letters, after inputing press enter to confirm text and press "text" icon to add text to painting.
   * Change color by "change color" option or with use of clor picker.
   * Fill image with given color by pressing icon "fill".
4.Other options are in top bar (rotating image, clearing image, saving and loading images, undoing and redoing changes).

## Screenshots
![app_start_view_scr](/resources/screenshots/CP-startView.PNG)
*Screen. 1: The start view of a Camera Paint*

## Future updates
Project version is 1.0 and for now we are not planning any bigger changes. Possible updates can add more tools, increase efficiency and improve the interface.

## Credits
All icons used in Camera Paint are taken from https://www.flaticon.com and https://icons8.com. Detailed references are in the file CREDITS.

## License
The project is under MIT license, more information in LICENSE file.
