import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Mat4, Vec3, Vec4, Quaternion

from pyglet.gl import *

import shader
import sys, math
import time
import camera
import shader
from primitives_hw4 import CustomGroup

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

        self.lights = 4

        self.Cornell_height = 25

    def setup(self):
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)

        glFrontFace(GL_CCW)
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_CULL_FACE)
        
        glCullFace(GL_BACK)

        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.fov)
        
    def update(self, dt):
        # view_projection 행렬 계산
        view_projection_matrix = self.proj_mat @ self.view_mat

        # 광원 위치와 색상
        # (x, y, z) = (9.5, 4.5, 12.5) -> 4.75, 2.25, 12.5
        light_positions = []

        for i in range(10):
            for j in range(10):
                x = -4.75 + 9.5 * i / 9
                z = -2.25 + 4.5 * j / 9

                light_positions.append(Vec3(x, 12.5, z))

        light_colors = [Vec3(0.01 * self.lights, 0.01 * self.lights, 0.01 * self.lights)] * 100


        camera_pos = self.cam_eye

        for shape in self.shapes:
            shader = shape.shader_program
            shader.use()
            shader['view_proj'] = view_projection_matrix

            shader['light_pos'] = [tuple(pos) for pos in light_positions]
            shader['light_color'] = [tuple(col) for col in light_colors]

            shader['view_pos'] = camera_pos

            # 할 일) 클래스 별로 구분해서 적용하기
            # 각 재질에 따라

            if shape.type == "Box":
                shader['ambient_strength'] = 0.1
                shader['specular_strength'] = 0.1
                shader['diffuse_strength'] = 0.2
                shader['shininess'] = 12
            
            elif shape.type == "Cornell Box": 
                shader['ambient_strength'] = 0.05
                shader['specular_strength'] = 0.3
                shader['diffuse_strength'] = 0.5
                shader['shininess'] = 2

            elif shape.type == "Tape": # Tape
                shader['ambient_strength'] = 0.1
                shader['specular_strength'] = 0.3
                shader['diffuse_strength'] = 0.4
                shader['shininess'] = 9

            else:
                shader['ambient_strength'] = 1
                shader['specular_strength'] = 1
                shader['diffuse_strength'] = 1
                shader['shininess'] = 50

    def on_resize(self, width, height):
        
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov)
        return pyglet.event.EVENT_HANDLED
    

    def add_shape(self, transform, vertice, indice, color, normal, type, group, text_coords = None, rotation_matrix=Mat4.from_translation(vector=Vec3(x=0, y=0, z=0)), texture = None):
        
        '''
        Assign a group for each shape
        '''
        shape = CustomGroup(transform, len(self.shapes), type, group, rotation_matrix=rotation_matrix, texture = texture)

        if text_coords is None:
            shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                            batch = self.batch,
                            group = shape,
                            indices = indice,
                            vertices = ('f', vertice),
                            colors = ('Bn', color),
                            normals=('f', normal)
                            )
        else:
            shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                            batch = self.batch,
                            group = shape,
                            indices = indice,
                            vertices = ('f', vertice),
                            colors = ('Bn', color),
                            normals=('f', normal),
                            texCoord = ('f', text_coords)
                            )

        
        self.shapes.append(shape)
         
    def run(self):
        pyglet.app.run()

    