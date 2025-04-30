import pyglet
from pyglet.math import Mat4, Vec3
import sys, math
import numpy as np
from scipy.interpolate import BSpline

from render_hw3 import RenderWindow
from primitives_hw3 import SplineRail, Cube
from control import Control

import camera

# 상태 변수
cart_index = 0
cart_speed = 20.0  # 샘플 index/초

if __name__ == '__main__':
    width = 2560
    height = 1440

    mouseRotatePressed = False
    mouseMovePressed   = False
    mouseDollyPressed   = False

    # Render window.
    renderer = RenderWindow(width, height, "Roller Coaster", resizable = True)   
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    # Control points : x, y, height
    ctrl_pts = [
        [0, 0, 0],
        [11, 3, 4],
        [8, 12, 8],
        [1, 8, 3],
        [-3, 12, 3],
        [-5, 8, 3],
        [-1, 7, 2]
    ]
    converted_ctrl_pts = [[x, height, y] for (x, y, height) in ctrl_pts]

    rail = SplineRail(converted_ctrl_pts, samples=100, thickness=0.2)
    cart = Cube(scale_x=0.5, scale_y=0.5, scale_z=0.5)  # 작은 큐브

    start_pos = Vec3(*rail.path_points[0])
    cart_transform = Mat4.from_translation(start_pos)

    rail.add_to_renderer(renderer)
    rail.draw_debug_lines(renderer) # 양 옆 rail
    renderer.rail = rail

    renderer.cart_shape = renderer.add_shape(
        transform=cart_transform,
        vertice=cart.vertices,
        indice=cart.indices,
        color=cart.colors,
        type="cart",
        group=None
    )

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
    def on_mouse_drag( x, y, dx, dy, button, mods):	
        if mouseRotatePressed:
            camera.rotate(x, y)
        elif mouseMovePressed:
            camera.move(dx/width, dy/height, 0.0)
        elif mouseDollyPressed:
            camera.zoom(dy/height)	

    renderer.run()