import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3, Vec4, Quaternion
from pyglet.gl import *

import shader
import sys, math
import time
import camera
from primitives import CustomGroup

# 상태 변수
cart_index = 0
cart_speed = 20.0  # 샘플 index/초

class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()

        '''
        View (camera) parameters
        '''
        self.cam_eye = Vec3(0,0,camera.dolly)
        self.cam_target = Vec3(0,0,0)
        self.cam_vup = Vec3(0,1,0)
        self.view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 100
        self.fov = 46
        self.proj_mat = None

        self.shapes = []
        self.setup()

        self.animate = False

        self.rail = None        
        self.cart_index = 0
        self.cart_speed = 20.0
        self.cart_shape = None 

    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.fov)

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()


    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov)
        return pyglet.event.EVENT_HANDLED
    

    def add_shape(self, transform, vertice, indice, color, type, group, rotation_matrix=Mat4.from_translation(vector=Vec3(x=0, y=0, z=0))):
        
        '''
        Assign a group for each shape
        '''
        shape = CustomGroup(
            transform_mat=transform,
            order=len(self.shapes),
            type=type,
            group=group,
            rotation_matrix=rotation_matrix
        )
        shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                        batch = self.batch,
                        group = shape,
                        indices = indice,
                        vertices = ('f', vertice),
                        colors = ('Bn', color))
        self.shapes.append(shape)
        return shape
        
    def update(self, dt):
        global cart_index
        path_points = []

        view_proj = self.proj_mat @ self.view_mat

        for shape in self.shapes:
            if shape.type == "rail":
                path_points = shape.group

        for shape in self.shapes:
            if self.animate:
                if shape.type == "cart":
                    # 카트 위치 업데이트
                    cart_index += cart_speed * dt
                    i = int(cart_index) % len(path_points)
                    cart_pos = Vec3(*path_points[i])
                    new_transform = Mat4.from_translation(cart_pos)
                    shape.transform_mat = new_transform

            # 모든 shape에 대해 view-proj, model 넘기기
            shape.shader_program['view_proj'] = view_proj
            shape.shader_program['model'] = shape.transform_mat

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()