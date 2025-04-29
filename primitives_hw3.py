import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

import numpy as np
from scipy.interpolate import BSpline
import shader

class CustomGroup(pyglet.graphics.Group):
    '''
    To draw multiple 3D shapes in Pyglet, you should make a group for an object.
    '''
    def __init__(self, transform_mat: Mat4, order, type, group, rotation_matrix = Mat4.from_translation(vector=Vec3(x=0, y=0, z=0))):
        super().__init__(order)

        '''
        Create shader program for each shape
        '''
        self.shader_program = shader.create_program(
            shader.vertex_source_default, shader.fragment_source_default
        )

        # shape.ransform_mat
        self.type = type
        self.group = group
        self.rotation_matrix = rotation_matrix

        self.transform_mat = transform_mat
        self.indexed_vertices_list = None
        self.shader_program.use()

    def set_state(self):
        self.shader_program.use()
        model = self.transform_mat
        self.shader_program['model'] = model

    def unset_state(self):
        self.shader_program.stop()

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.order == other.order and
                self.parent == other.parent)
    
    def __hash__(self):
        return hash((self.order)) 

class SplineRail:
    def __init__(self, ctrl_pts, degree=3, samples=100, thickness=5):
        self.ctrl_pts = np.array(ctrl_pts)
        self.degree = degree
        self.samples = samples
        self.thickness = thickness

        self.verts = []
        self.indices = []
        self.colors = []

        self.path_points = []

        self.generate()

    def generate(self):
        # make closed B-spline
        closed_ctrl = np.vstack((self.ctrl_pts, self.ctrl_pts[:self.degree]))
        n = len(closed_ctrl)
        knot = np.concatenate((
            np.zeros(self.degree),
            np.linspace(0, 1, n - self.degree + 1),
            np.ones(self.degree)
        ))
        spline = BSpline(knot, closed_ctrl, self.degree)
        t_vals = np.linspace(0, 1, self.samples, endpoint=False)
        points = spline(t_vals)

        # simple rectangular strips between segments
        idx = 0
        for i in range(len(points)-1):
            p1 = points[i]
            p2 = points[(i+1) % len(points)]

            dir = p2 - p1
            dir /= np.linalg.norm(dir)
            up = np.array([0, 1, 0])
            if abs(np.dot(dir, up)) > 0.9:  #  dir과 up이 거의 평행하면 뒤틀림 방지
                up = np.array([1, 0, 0])
            side = np.cross(dir, up)
            side = side / (np.linalg.norm(side) + 1e-8) * self.thickness

            # quad: 2 triangles
            a = p1 + side
            b = p1 - side
            c = p2 - side
            d = p2 + side

            for pt in [a, b, c, d]:
                self.verts.extend(pt.tolist())
                self.colors.extend([100, 180, 255, 255])  # light blue

            self.indices.extend([
                idx, idx+1, idx+2,
                idx, idx+2, idx+3,

                idx+2, idx+1, idx,
                idx+3, idx+2, idx
            ])
            idx += 4
        
        self.path_points = points

    def add_to_renderer(self, renderer):
        transform = Mat4()
        renderer.add_shape(
            transform=transform,
            vertice=self.verts,
            indice=self.indices,
            color=self.colors,
            type="rail",
            group=self.path_points
        )

class Cube:
    '''
    default structure of cube
    '''
    def __init__(self, scale_x=1.0, scale_y=1.0, scale_z=1.0):
        # RenderWindow.update[0~23]
        # indexed_vertices_list.vertices
        self.vertices = [
            -0.5*scale_x, -0.5*scale_y, 0.5*scale_z,
            0.5*scale_x, -0.5*scale_y, 0.5*scale_z,
            0.5*scale_x, 0.5*scale_y, 0.5*scale_z,
            -0.5*scale_x, 0.5*scale_y, 0.5*scale_z,
            -0.5*scale_x, -0.5*scale_y, -0.5*scale_z,
            0.5*scale_x, -0.5*scale_y, -0.5*scale_z,
            0.5*scale_x,0.5*scale_y,-0.5*scale_z,
            -0.5*scale_x,0.5*scale_y,-0.5*scale_z]
        # self.vertices = [scale[idx%3] * x for idx, x in enumerate(self.vertices)]
    
        self.indices = [0, 1, 2, 2, 3, 0,
                    4, 7, 6, 6, 5, 4,
                    4, 5, 1, 1, 0, 4,
                    6, 7, 3, 3, 2, 6,
                    5, 6, 2, 2, 1, 5,
                    7, 4, 0, 0, 3, 7]
    
        self.colors = [
            255, 255, 0, 255, # 노랑
            255, 255, 0, 255, 
            255, 255, 0, 255, 
            255, 255, 0, 255, 
            255, 255, 0, 255, 
            255, 255, 0, 255, 
            255, 255, 0, 255, 
            255, 255, 0, 255
        ]