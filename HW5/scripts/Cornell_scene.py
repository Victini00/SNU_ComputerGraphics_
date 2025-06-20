from PIL import Image
import numpy as np

from find_intersection import intersect_plane, intersect_cube, intersect_hollow_cylinder, intersect_hole_plane, intersect_sphere

EPSILON = 0.01
PI = np.pi

def load_texture(path):
    return np.array(Image.open(path)).astype(np.float32) / 255

paper_texture = load_texture("textures/paper.png")
tape_texture = load_texture("textures/Tape.png")
wood_texture = load_texture("textures/wood.png")

class Material:
    def __init__(self, color, ambient=0.1, diffuse=0.9, specular=0.0, shininess=0, reflective=0.0, refractive=0.0, ior=1.0, texture=None):
        self.color = color

        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess # PHong 

        self.reflective = reflective
        self.refractive = refractive # 반사 / 굴절 

        self.ior = ior

        self.texture = texture

class Plane:
    def __init__(self, center, normal, size, material):
        self.center = center 
        self.normal = normal  
        self.size = size      
        self.material = material

    def intersect(self, ray):
        return intersect_plane(ray, self)
    
    # for texture
    def get_uv(self, point):

        point_center = np.array(point) - np.array(self.center)

        u_axis = np.cross(self.normal, (0, 1, 0)).astype(np.float64) # 외적 

        # 거의 평행일때 처리해줘야 함 
        if np.linalg.norm(u_axis) < EPSILON: 
            u_axis = np.cross(self.normal, (1, 0, 0)).astype(np.float64)

        u_axis /= np.linalg.norm(u_axis)
        v_axis = np.cross(self.normal, u_axis)

        u = 1/2 + np.dot(point_center, u_axis) / self.size[0]
        v = 1/2 + np.dot(point_center, v_axis) / self.size[1]

        return np.clip(u, 0, 1), np.clip(v, 0, 1)
    
class Hole_Plane:
    def __init__(self, center, normal, size, hole_size, material):
        self.center = center        
        self.normal = normal        
        self.size = size            
        self.hole_size = hole_size  
        self.material = material 

    def intersect(self, ray):
        return intersect_hole_plane(ray, self)

    # 그냥 plane이랑 동일 
    def get_uv(self, point):

        point_center = np.array(point) - np.array(self.center)
        u_axis = np.cross(self.normal, (0, 1, 0))

        # 거의 평행일때 처리해줘야 함 
        if np.linalg.norm(u_axis) < EPSILON: u_axis = np.cross(self.normal, (1, 0, 0))

        u_axis = u_axis.astype(float) # 오류처리 

        u_axis /= np.linalg.norm(u_axis)
        v_axis = np.cross(self.normal, u_axis)

        u = 1/2 + np.dot(point_center, u_axis) / self.size[0]
        v = 1/2 + np.dot(point_center, v_axis) / self.size[1]

        return np.clip(u, 0, 1), np.clip(v, 0, 1)

class Cube:
    def __init__(self, center, size, material):
        self.center = center  
        self.size = size     
        self.material = material

    def intersect(self, ray):
        return intersect_cube(ray, self)
    
    def get_uv(self, point):

        point_center = np.array(point) - np.array(self.center)

        max_axis = np.argmax(np.abs(point_center)) # 가장 긴 쪽 

        u = 0
        v = 0

        if max_axis == 0: # X 
            u = 1/2 + point_center[2] / self.size[2]
            v = 1/2 + point_center[1] / self.size[1]

        elif max_axis == 1: # Y
            u = 1/2 + point_center[0] / self.size[0]
            v = 1/2 + point_center[2] / self.size[2]

        else: # Z
            u = 1/2 + point_center[0] / self.size[0]
            v = 1/2 + point_center[1] / self.size[1]

        return np.clip(u, 0, 1), np.clip(v, 0, 1)

class HollowCylinder:
    def __init__(self, center, outer_radius, inner_radius, height, material):
        self.center = center 
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.height = height
        self.material = material

    def intersect(self, ray):
        return intersect_hollow_cylinder(ray, self)
    
    def get_uv(self, point):
        x = point[0] - self.center[0] 
        z = point[2] - self.center[2]

        theta = np.arctan2(z, x) # 오차 최소화하여 각도 계산 

        u = (theta + PI) / (2 * PI)
        v = (point[1] - (self.center[1] - self.height / 2)) / self.height

        return np.clip(u, 0, 1), np.clip(v, 0, 1)
    
class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        return intersect_sphere(ray, self)

    def get_uv(self, point):
        point_center = np.array(point) - np.array(self.center)

        x, y, z = point_center / self.radius

        u = 1/2 + (np.arctan2(z, x) / (2 * PI))
        v = 1/2 - (np.arcsin(y) / PI)

        return np.clip(u, 0, 1), np.clip(v, 0, 1)


class AreaLight:
    def __init__(self, center, normal, size, intensity):
        self.center = center    
        self.normal = normal    
        self.size = size       

        self.intensity = intensity  # 세기 


# Cornell Box 정의 #######################################################################

def create_cornell_box():
    white = Material(color=(1.0, 1.0, 1.0), ambient=0.05, diffuse=0.5, specular=0.3, shininess=2, reflective=0.05, refractive=0.0, texture=paper_texture)
    red = Material(color=(1.0, 0.0, 0.0), ambient=0.05, diffuse=0.5, specular=0.3, shininess=2, reflective=0.05, refractive=0.0, texture=paper_texture)
    green = Material(color=(0.0, 1.0, 0.0), ambient=0.05, diffuse=0.5, specular=0.3, shininess=2, reflective=0.05, refractive=0.0, texture=paper_texture)
    wood = Material(color=(0.7, 0.5, 0.3), ambient=0.1, diffuse=0.2, specular=0.1, shininess=12, reflective=0.1, refractive=0.0, texture=wood_texture)
    tape = Material(color=(0.95, 0.9, 0.8), ambient=0.1, diffuse=0.4, specular=0.3, shininess=9, reflective=0.05, refractive=0.0, texture=tape_texture)
    glass_ball = Material(color=(0.9, 0.95, 1.0), ambient=0.2, diffuse=0.8, specular=0.3, shininess=250, reflective=0.1, refractive=0.9, ior=1.5)

    objects = [
        # Back wall # ok
        Plane(center=(0, 0, -9.75), normal=(0, 0, 1), size=(25, 32), material=white),

        # Floor
        Plane(center=(0, -12.5, 0), normal=(0, 1, 0), size=(19.5, 32), material=white),

        # Ceiling
        Hole_Plane(center=(0, 12.5, 0), normal=(0, -1, 0), size=(19.5, 32), hole_size= (4.5, 9.5), material=white),
        # Plane(center=(0, 12.5, 0), normal=(0, -1, 0), size=(19.5, 32), material=white),

        # Hole Ceiling
        Plane(center=(0, 12.55, 0), normal=(0, -1, 0), size=(15, 25), material=white),

        # Left wall (red) 
        Plane(center=(-16, 0, 0), normal=(1, 0, 0), size=(25, 19.5), material=red),

        # Right wall (green)
        Plane(center=(16, 0, 0), normal=(-1, 0, 0), size=(25, 19.5), material=green),

        # Box
        Cube(center=(-8, -6.5, -3), size=(8, 12, 5.5), material=wood), # original center = (-5, -6.5, 0)

        # Tape (hollow cylinder)
        HollowCylinder(center=(8, -10, -3), outer_radius=4.5, inner_radius=3.75, height=5, material=tape), # original center = (5, -10, 0)
    
        # 추가) 유리구슬
        Sphere(center=(0, -10 ,3), radius = 3, material=glass_ball)
    ]

    lights = [
        AreaLight(center=(0, 12.51, 0), normal=(0, -1, 0), size=(9, 4), intensity=(5, 5, 5))
    ]

    return objects, lights
