import pyglet
from pyglet.math import Mat4, Vec3
import sys, math

from render_hw3 import RenderWindow
from primitives_hw2 import Cube, Face, Face_with_Hole, Hollow_Cylinder
from control import Control

import camera

if __name__ == '__main__':
    width = 1280
    height = 720

    mouseRotatePressed = False
    mouseMovePressed   = False
    mouseDollyPressed   = False

    # Render window.
    renderer = RenderWindow(width, height, "Roller Coaster", resizable = True)   
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)


    @renderer.event
    def on_resize(width, height):
        camera.resize(renderer, width, height )
        return pyglet.event.EVENT_HANDLED

    @renderer.event
    def on_draw():
        renderer.clear()
        camera.apply(renderer)
        renderer.batch.draw()

    @renderer.event
    def on_key_press( key, mods ):	
        if key==pyglet.window.key.Q:
            pyglet.app.exit()
            
    @renderer.event
    def on_mouse_release( x, y, button, mods ):
        global mouseRotatePressed, mouseMovePressed, mouseDollyPressed

        mouseMovePressed   = False
        mouseRotatePressed = False
        mouseDollyPressed   = False

    @renderer.event
    def on_mouse_press( x, y, button, mods ):
        global mouseRotatePressed, mouseMovePressed, mouseDollyPressed

        if button & pyglet.window.mouse.LEFT and mods & pyglet.window.key.MOD_SHIFT:
            mouseMovePressed   = True
            mouseRotatePressed = False
            mouseDollyPressed   = False
        elif button & pyglet.window.mouse.LEFT and mods & pyglet.window.key.MOD_CTRL:
            mouseMovePressed   = False
            mouseRotatePressed = False
            mouseDollyPressed   = True
        elif button & pyglet.window.mouse.LEFT:
            camera.beginRotate(x, y)
            mouseMovePressed   = False
            mouseRotatePressed = True
            mouseDollyPressed   = False

    @renderer.event
    def on_mouse_drag( x, y, dx, dy, button, mods ):	
        if mouseRotatePressed:
            camera.rotate(x, y)
        elif mouseMovePressed:
            camera.move(dx/width, dy/height, 0.0)
        elif mouseDollyPressed:
            camera.zoom(dy/height)	

    #draw shapes
    renderer.run()
