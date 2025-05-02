import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3, Vec4, Quaternion
from pyglet.gl import *

from primitives_hw3 import Cylinder

import shader
import sys, math
import time
import camera
import numpy as np

from primitives import CustomGroup

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
        self.cam_eye = Vec3(0,0,0)
        self.cam_target = Vec3(0,10,0)
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
        self.cart_speed = 1.0
        self.cart_shape = None 

        self.cart_s = 0.0 # arc length 누적 

        # 카메라 수정용
        self.camera_cart_front = False
        self.camera_save = None

        # frenet frame용 원통 3개
        self.tangent_cyl = Cylinder(radius=0.5, height=2, colors=[0,0,255,255])
        self.normal_cyl = Cylinder(radius=0.5, height=2, colors=[255,255,0,255])
        self.binormal_cyl = Cylinder(radius=0.5, height=2, colors=[255,0,0,255])

        dummy_dir = Vec3(1, 0, 0)  # 초기 방향은 X축으로 설정
        init_transform = self.get_transform(dummy_dir, Vec3(0, 10000, 0))

        # 초기 transform은 cart 위치 기준
        self.tangent_shape = self.add_shape(init_transform, self.tangent_cyl.vertices, self.tangent_cyl.indices, self.tangent_cyl.colors, "tangent", None)
        self.normal_shape = self.add_shape(init_transform, self.normal_cyl.vertices, self.normal_cyl.indices, self.normal_cyl.colors, "normal", None)
        self.binormal_shape = self.add_shape(init_transform, self.binormal_cyl.vertices, self.binormal_cyl.indices, self.binormal_cyl.colors, "binormal", None)

    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST) # 앞뒤 
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
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov
        )
        self.speed_label.y = height - 20
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

        view_proj = self.proj_mat @ self.view_mat

        for shape in self.shapes:
            if self.animate and shape.type == "cart":
                # arc-length 기반..
                self.cart_s += self.cart_speed * dt
                if self.cart_s >= self.rail.total_length:
                    self.cart_s -= self.rail.total_length

                t = self.rail.find_t_from_s(self.cart_s)
                p1 = np.array(self.rail.spline(t))
                y = p1[1] # 에너지 보존 법칙용 높이 계산

                g = 9.8
                y_max = np.max([pt[1] for pt in self.rail.path_points])  # 높이 최댓값

                # 최고점에서 최소 속도 세팅
                v = math.sqrt(2 * g * max(0.0, y_max - y)) + 0.01

                self.cart_s += v * dt

                if self.cart_s >= self.rail.total_length:
                    self.cart_s -= self.rail.total_length

                # tangent 계산용: 주변 위치 샘플링

                eps = 0.01
                t_prev = self.rail.find_t_from_s(self.cart_s - eps)
                t_next = self.rail.find_t_from_s(self.cart_s + eps)

                p0 = np.array(self.rail.spline(t_prev))
                p2 = np.array(self.rail.spline(t_next))

                cart_pos = Vec3(*p1)
                shape.transform_mat = Mat4.from_translation(cart_pos)

                # Frenet Frame 계산
                tangent = p2 - p1
                tangent /= np.linalg.norm(tangent) + 0.000000001

                # 카메라 따라가기
                if self.camera_cart_front:
                    eye = cart_pos - Vec3(*tangent) * 2 + Vec3(0, 1, 0) 
                    target = cart_pos + Vec3(*tangent) * 2
                    self.view_mat = Mat4.look_at(eye, target=target, up=Vec3(0, 1, 0))

                prev_tangent = p1 - p0
                prev_tangent /= np.linalg.norm(prev_tangent) + 0.000000001

                # Gram-Schmidt 사용 ~> 급격한 normal과 binormal 흔들림 방지
                up = np.array([0, 1, 0])
                if abs(np.dot(tangent, up)) > 0.99: up = np.array([1, 0, 0])  # tangent가 거의 Y축

                # normal: tangent에 수직인 벡터
                normal = up - np.dot(up, tangent) * tangent
                normal /= np.linalg.norm(normal) + 0.000000001

                # binormal: tangent와 normal의 외적
                binormal = np.cross(tangent, normal)
                binormal /= np.linalg.norm(binormal) + 0.000000001            

                self.tangent_shape.transform_mat = self.get_transform(tangent, cart_pos)
                self.normal_shape.transform_mat = self.get_transform(normal, cart_pos)
                self.binormal_shape.transform_mat = self.get_transform(binormal, cart_pos)

        # tangent/normal/binormal도 업데이트
        for shape in self.shapes + [self.tangent_shape, self.normal_shape, self.binormal_shape]:
            shape.shader_program['view_proj'] = view_proj
            shape.shader_program['model'] = shape.transform_mat

    def get_transform(self, vec, cart_pos):

        vec3 = Vec3(*vec)
        length = 1.0 
        base_to_tip = vec3 * (length / 2)
        pos = cart_pos + base_to_tip

        y_axis = Vec3(0, 1, 0)
        dot = y_axis.dot(vec3)

        if abs(dot - 1) < 0.000000001: rot = Mat4()
        elif abs(dot + 1) < 0.000000001:
            rot = Mat4.from_rotation(math.pi, Vec3(1, 0, 0))
        else:
            axis = y_axis.cross(vec3)
            angle = math.acos(np.clip(dot, -1.0, 1.0))
            rot = Mat4.from_rotation(angle, axis)

        return (
            Mat4.from_translation(pos) @
            rot @
            Mat4.from_scale(Vec3(0.05, length / 2, 0.05))
        )

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()