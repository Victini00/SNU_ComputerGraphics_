import pyglet
from pyglet.math import Mat4, Vec3
import sys, math
import numpy as np
from scipy.interpolate import BSpline

sys.path.append("./scripts")

from render_hw3 import RenderWindow
from primitives_hw3 import SplineRail, Cube
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

    center_point = [12/7, 50/7, 26/7] # x, y, height

    converted_ctrl_pts = [[x, height, y] for (x, y, height) in ctrl_pts]

    rail = SplineRail(converted_ctrl_pts, samples=150, thickness=0.2, gap=0.3)

    # 작은 큐브: 움직이는 '카트'역할을 합니다.
    cart = Cube(scale_x=0.5, scale_y=0.5, scale_z=0.5, colors=[255,255,0,255])  

    start_pos = Vec3(*rail.path_points[0])
    cart_transform = Mat4.from_translation(start_pos)
    renderer.cart_shape = renderer.add_shape(
        transform=cart_transform,
        vertice=cart.vertices,
        indice=cart.indices,
        color=cart.colors,
        type="cart",
        group=None
    )

    rail.add_to_renderer(renderer)
    renderer.rail = rail

    # 미관용
    tile_temp = Cube(scale_x=16, scale_y=2, scale_z=12, colors=[102,205,170,255])
    
    tile_temp_translation = Mat4.from_translation(vector=Vec3(x=1, y=-5, z=-1))

    renderer.add_shape(
        tile_temp_translation, 
        tile_temp.vertices, 
        tile_temp.indices, 
        tile_temp.colors, 
        type="tile", 
        group=None
    )

    '''
    # 중심부 레일
    renderer.main_rail_shape = renderer.add_shape(
        transform=Mat4(),
        vertice=rail.rail_line_verts,
        indice=rail.rail_line_indices,
        color=rail.rail_line_colors,
        type="debug-line",  # GL_LINES로 렌더링되도록 해야 함
        group=None
    )
    '''

    @renderer.event
    def on_resize(width, height):
        camera.resize(renderer, width, height )
        return pyglet.event.EVENT_HANDLED

    @renderer.event
    def on_draw():
        renderer.clear()
        if not renderer.camera_cart_front:
            camera.apply(renderer)
        renderer.batch.draw()

    @renderer.event
    def on_key_press( key, mods ):	
        if key==pyglet.window.key.Q:
            pyglet.app.exit()
        if key==pyglet.window.key.F:
            if not renderer.camera_cart_front:
                renderer.camera_save = renderer.view_mat  # 현재 카메라 저장해두고 나중에 사용 
                renderer.camera_cart_front = True
            else:
                renderer.view_mat = renderer.camera_save  # 복원
                renderer.camera_cart_front = False
            
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