import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4, Quaternion
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
        self.indexed_vertices_lst = None
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

# 전체 레일을 구현하는 primitive입니다.
class SplineRail:
    def __init__(self, ctrl_pts, degree=3, samples=100, thickness=5, gap=0.3):

        self.ctrl_pts = np.array(ctrl_pts)
        self.degree = degree
        self.samples = samples
        self.thickness = thickness

        self.gap = gap

        self.verts = []
        self.indices = []       
        self.colors = []

        self.path_points = []

        self.rail_line_verts = []
        self.rail_line_indices = []
        self.rail_line_colors = []

        self.left_path = []
        self.right_path = []

        self.fix_coordinate()
        self.generate_rail_tile()

    # 좌표 값 조정
    # Trackball viewer가 중심점을 기준으로 회전할 수 있도록..
    def fix_coordinate(self):
        sum_x = 0
        sum_height = 0 
        sum_y = 0

        for i in self.ctrl_pts:
            sum_x += i[0]
            sum_height += i[1]
            sum_y += i[2]

        n = len(self.ctrl_pts)

        # 평균 내기 
        center = np.array([
            sum_x / n,
            sum_height / n,
            sum_y / n
        ])

        # 모든 제어점에서 중심 좌표를 빼서 평행이동시킴
        self.ctrl_pts = self.ctrl_pts - center

    # arc-length parameterization과, 레일의 타일을 만드는 함수
    def generate_rail_tile(self):
        
        ctrl = np.vstack([self.ctrl_pts, self.ctrl_pts[:self.degree]])
        n = len(ctrl)

        # B-spline을 사용함 -> knot vector 정의 
        knot = np.arange(0, n + self.degree + 1)

        t_dense = np.linspace(self.degree, n, 10 *self.samples, endpoint=False)
        spline = BSpline(knot, ctrl, self.degree)
        pts_dense = spline(t_dense)

        # arc-length parameterization
        s_lst = [0.0]

        for i in range(1, len(pts_dense)):
            d = np.linalg.norm(pts_dense[i] - pts_dense[i-1]) # 유클리드 거리
            s_lst.append(s_lst[-1] +d)
        total_length = s_lst[-1]

        s_target = np.linspace(0, total_length, self.samples)
        reparameterized_t_vals = []

        index_pointer = 0
        for s_target in s_target:
            while index_pointer < len(s_lst)-1 and s_lst[index_pointer+1] < s_target: index_pointer += 1

            s0, s1 = s_lst[index_pointer], s_lst[index_pointer+1]
            t0, t1 = t_dense[index_pointer], t_dense[index_pointer+1]

            # 핵심) t 선형 보간
            alpha = (s_target - s0) / (s1 - s0 + 0.00000001)
            t_interpolation = (1 - alpha) *t0 + alpha * t1

            reparameterized_t_vals.append(t_interpolation)

        points = spline(reparameterized_t_vals)
        self.path_points = points

        # arc-length parameterization ends

        # rail tile 생성 
        idx = 0
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % (len(points))]

            dir = p2 - p1
            dir /= np.linalg.norm(dir)

            up = np.array([0, 1, 0])
            if abs(np.dot(dir,up)) > 0.99: up = np.array([1, 0, 0])

            side = np.cross(dir, up)
            side = side / (np.linalg.norm(side) + 0.00000001) * self.thickness

            a = p1 + side
            b = p1 - side
            c = p2 - side
            d = p2 + side # 끝 점들 

            for pt in [a, b, c, d]:
                self.verts.extend(pt.tolist())
                if i % 5 == 0:
                    self.colors.extend([150, 150, 0, 255])
                else:
                    self.colors.extend([102, 205, 170, 255])

            self.indices.extend([
                idx, idx+1, idx+2,
                idx, idx+2, idx+3,
                idx+2, idx+1, idx,
                idx+3, idx+2, idx
            ])

            idx += 4

        self.s_lst = s_lst
        self.t_dense = t_dense
        self.spline = spline
        self.total_length = total_length

    # t -> s 매핑 찾는 함수
    def find_t_from_s(self, s):

        if s <= 0: return self.t_dense[0]
        elif s >= self.total_length: return self.t_dense[-1]

        # binary search 
        low, high = 0, len(self.s_lst) - 1
        while low <= high:
            mid = (low + high)//2
            if self.s_lst[mid] < s: low = mid + 1
            else: high = mid - 1

        j = max(0, low - 1)
        s0, s1 = self.s_lst[j], self.s_lst[j + 1]
        t0, t1 = self.t_dense[j], self.t_dense[j + 1]

        alpha = (s - s0) / (s1 - s0 + 0.00000001)
        result = (1 - alpha) * t0 + alpha * t1
        return result

    # 미관용) 양쪽 레일 추가
    def add_rail_cylinders(self, renderer):

        for i in range(len(self.path_points)):
            p = self.path_points[i]
            next_p = self.path_points[(i + 1) % len(self.path_points)]

            direction = np.array(next_p) - np.array(p)
            direction /= np.linalg.norm(direction) + 0.00000001

            up = np.array([0, 1, 0])
            if abs(np.dot(direction, up)) > 0.99: up = np.array([1, 0, 0])

            side = np.cross(direction, up)
            side = side / (np.linalg.norm(side) + 0.00000001) * self.gap

            self.left_path.append(np.array(p) -side)
            self.right_path.append(np.array(p) +side)

        # 마무리 연결
        self.left_path.append(self.left_path[0])
        self.right_path.append(self.right_path[0])

        self.add_cylinders_along(self.left_path, renderer)
        self.add_cylinders_along(self.right_path, renderer)

    def add_cylinders_along(self, path, renderer):

        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            direction = p2 - p1

            length = np.linalg.norm(direction)
            if length < 0.000000001: continue # 오차처리

            direction = direction / length
            center = (p1 + p2) / 2

            y_axis = np.array([0, 1, 0])
            dot = np.dot(y_axis, direction)
            if np.allclose(direction, y_axis): rotation = Mat4()
            elif np.allclose(direction, -y_axis): rotation = Mat4.from_rotation(math.pi, Vec3(1, 0, 0))
            else:
                axis = np.cross(y_axis, direction)
                axis_norm = np.linalg.norm(axis)
                if axis_norm < 0.000000001: rotation = Mat4()
                else:
                    axis = Vec3(*axis / axis_norm)
                    angle = math.acos(np.clip(dot, -1.0, 1.0))
                    rotation = Mat4.from_rotation(angle, axis)

            transform = (
                Mat4.from_translation(Vec3(*center))@
                rotation@
                Mat4.from_scale(Vec3(0.05, length / 2, 0.05))
            )

            cylinder = Cylinder(radius=1.0, height=2.0, colors=[34,139,34,255])

            renderer.add_shape(
                transform=transform,
                vertice=cylinder.vertices,
                indice=cylinder.indices,
                color=cylinder.colors,
                type="rail-cylinder",
                group=None
            )


    # 미관용) 기둥
    def generate_pillar(self, renderer):
        for i, p in enumerate(self.path_points):
            if i % 10 != 0:
                continue


            x, y, z = p
            bottom_y = -4
            height = y - bottom_y
            if height < 0.1: continue  # 너무 짧으면 생성 X

            center_y = (y + bottom_y) / 2
            center = Vec3(x, center_y - 0.05, z) # 레일이랑 안 겹치게

            transform = (
                Mat4.from_translation(center) @
                Mat4.from_scale(Vec3(0.1, height / 2.0, 0.1))
            )

            cylinder = Cylinder(radius=1.0, height=2.0, colors=[46, 139, 87, 255]) 

            renderer.add_shape(
                transform=transform,
                vertice=cylinder.vertices,
                indice=cylinder.indices,
                color=cylinder.colors,
                type="pillar",
                group=None
            )

            # 받침대
            base_cube = Cube(scale_x=1, scale_y=0.5, scale_z=1, colors=[0,0,0,255])
            base_center = Vec3(x, bottom_y - 0.4 / 2.0, z)  # 중심: 아래로 절반
            base_transform = Mat4.from_translation(base_center)

            renderer.add_shape(
                base_transform, 
                base_cube.vertices, 
                base_cube.indices, 
                base_cube.colors, 
                "pillar-under", 
                None
            )

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

        self.add_rail_cylinders(renderer)
        self.generate_pillar(renderer)

    # 변환에 사용하는 함수 
    def rotation_matrix_from_axis_angle(axis, angle):

        axis = axis / np.linalg.norm(axis)
        x, y, z = axis
        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c

        rotation = Mat4((
            t*x*x + c,     t*x*y - s*z,   t*x*z + s*y,   0,
            t*x*y + s*z,   t*y*y + c,     t*y*z - s*x,   0,
            t*x*z - s*y,   t*y*z + s*x,   t*z*z + c,     0,
            0,             0,             0,             1
        ))

        return rotation

class Cube:
    '''
    default structure of cube
    '''
    def __init__(self, scale_x=1.0, scale_y=1.0, scale_z=1.0, colors=[255,255,255,255]):
        # RenderWindow.update[0~23]
        # indexed_vertices_lst.vertices

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
    
        self.colors = colors * 8

class Cylinder:
    def __init__(self, radius=1, height=1, slices=8, option="rail", colors = [0, 0, 0, 255]):

        self.vertices = []
        self.indices = []
        self.colors = []

        for i in range(slices + 1):
            angle = 2 * i * math.pi / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

            self.vertices.extend([x, height/2, z])

            # 위아래 원
            self.colors.extend(colors)

            self.vertices.extend([x, -height/2, z])

            self.colors.extend(colors)

        # 옆면
        for i in range(slices):
            index1 = i * 2
            index2 = (i + 1) * 2
            index3 = index1 + 1
            index4 = index2 + 1

            self.indices.extend([index1, index2, index3, 
                                 index2, index4, index3])

        top_center = len(self.vertices) // 3
        bottom_center = top_center + 1

        # 중심
        self.vertices.extend([0, height/2, 0])  

        self.colors.extend(colors)

        self.vertices.extend([0, -height/2, 0]) 

        self.colors.extend(colors)


        for i in range(slices):
            index1 = i * 2
            index2 = ((i + 1) % slices) * 2

            # 윗면은 시계 방향
            self.indices.extend([top_center, index2, index1])
            
            # 아랫면은 시계 방향
            self.indices.extend([bottom_center, index1 + 1, index2 + 1])