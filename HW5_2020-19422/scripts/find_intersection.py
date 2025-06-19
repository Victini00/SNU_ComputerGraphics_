# https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection.html
# https://en.wikipedia.org/wiki/Slab_method

import numpy as np

EPSILON = 0.00001

class Hit:
    def __init__(self, ray_distance=np.inf, point=None, normal=None, material=None, object=None):
        self.ray_distance = ray_distance
        self.point = point
        self.normal = normal

        self.material = material # 얘는 색이랑 Phong
        self.object = object # 얘는 텍스쳐 

class Ray:
    def __init__(self, origin, direction):
        self.origin = np.array(origin, dtype=np.float32)

        self.direction = np.array(direction, dtype=np.float32) 
        self.direction /= np.linalg.norm(self.direction)

def intersect_plane(ray, plane):

    # 각도, 거리 예외 처리 
    lean = np.dot(ray.direction, plane.normal)
    if abs(lean) < EPSILON: return None 

    ray_distance = np.dot(np.array(plane.center) - ray.origin, plane.normal) / lean
    if ray_distance < 0: return None

    # 
    hit_point = ray.origin + ray_distance * ray.direction
    point_center = hit_point - np.array(plane.center)

    width, height = plane.size[0] / 2, plane.size[1] / 2

    u = np.cross(plane.normal, (1, 0, 0))
    if np.linalg.norm(u) < EPSILON: u = np.cross(plane.normal, (0, 0, 1))
    u = u / np.linalg.norm(u)

    v = np.cross(plane.normal, u)

    x = np.dot(point_center, u)
    y = np.dot(point_center, v)

    if abs(x) > width or abs(y) > height: return None

    return Hit(ray_distance=ray_distance, point=hit_point, normal=np.array(plane.normal), material=plane.material, object=plane)

def intersect_hole_plane(ray, face):

    # plane을 기본적으로 사용, 중심 구멍만 따로 처리리
    hit = intersect_plane(ray, face)
    if hit is None: return None

    point_center = hit.point - np.array(face.center)

    u_axis = np.cross(face.normal, (0, 1, 0))
    if np.linalg.norm(u_axis) < EPSILON: u_axis = np.cross(face.normal, (1, 0, 0))
    u_axis = u_axis / np.linalg.norm(u_axis)

    v_axis = np.cross(face.normal, u_axis)

    x = np.dot(point_center, u_axis)
    y = np.dot(point_center, v_axis)

    hole_w, hole_h = face.hole_size[0] / 2, face.hole_size[1] / 2

    if abs(x) < hole_w and abs(y) < hole_h: return None

    hit.object = face
    return hit

# Cube ~ Slab method 사용
def intersect_cube(ray, cube):
    min_point = np.array(cube.center) - 1/2 * np.array(cube.size)
    max_point = np.array(cube.center) + 1/2 * np.array(cube.size)

    ray_start = (min_point - ray.origin) / ray.direction
    ray_exit  = (max_point - ray.origin) / ray.direction

    start_min = np.minimum(ray_start, ray_exit)
    start_max = np.maximum(ray_start, ray_exit)

    start_distance = np.max(start_min)
    exit_distance  = np.min(start_max)

    if start_distance > exit_distance or exit_distance < 0: return None # 바깥쪽 

    ray_distance = start_distance if start_distance > 0 else exit_distance

    point = ray.origin + ray_distance * ray.direction

    for i in range(3):
        if abs(point[i] - min_point[i]) < EPSILON:
            normal = np.zeros(3)
            normal[i] = -1
            break
        elif abs(point[i] - max_point[i]) < EPSILON:
            normal = np.zeros(3)
            normal[i] = 1
            break
    else:
        normal = np.zeros(3)

    return Hit(ray_distance=ray_distance, point=point, normal=normal, material=cube.material, object=cube)

def intersect_hollow_cylinder(ray, cyl):
    origin = ray.origin
    direction = ray.direction

    center = np.array(cyl.center)
    origin_center = origin[[0, 2]]  - center[[0, 2]]

    dir_xz = direction[[0, 2]]

    a = np.dot(dir_xz, dir_xz)
    b = np.dot(dir_xz, origin_center) * 2 # 2배 

    c_outer = np.dot(origin_center, origin_center) - (cyl.outer_radius ** 2)
    c_inner = np.dot(origin_center, origin_center) - (cyl.inner_radius ** 2)

    roots_outer = [r.real for r in np.roots([a, b, c_outer]) if np.isreal(r) and r.real > 0]
    roots_inner = [r.real for r in np.roots([a, b, c_inner]) if np.isreal(r) and r.real > 0]

    checklist = []

    # 밖 
    for t in roots_outer:
        y = origin[1] + t * direction[1]
        half_height = cyl.height / 2

        if cyl.center[1] - half_height <= y <= cyl.center[1] + half_height: # 포함되는 경우 
            point = origin + t * direction
            normal = point - center
            normal[1] = 0
            normal /= np.linalg.norm(normal)

            checklist.append(Hit(ray_distance=t, point=point, normal=normal, material=cyl.material, object=cyl))

    # 안 ~ normal만 반대 
    for t in roots_inner:
        y = origin[1] + t * direction[1]
        half_height = cyl.height / 2

        if cyl.center[1] - half_height <= y <= cyl.center[1] + half_height:
            point = origin + t * direction
            normal = point - center
            normal[1] = 0
            normal /= np.linalg.norm(normal)

            checklist.append(Hit(ray_distance=t, point=point, normal=-normal, material=cyl.material, object=cyl))

    # 위아래 
    for y_plane, normal_signature in [(center[1] + cyl.height / 2, 1), (center[1] - cyl.height / 2, -1)]:
        if abs(direction[1]) < EPSILON: continue

        t_cap = (y_plane - origin[1]) / direction[1]
        if t_cap < 0: continue

        point = origin + t_cap * direction
        dist_xz = np.linalg.norm(point[[0, 2]] - center[[0, 2]])

        if cyl.inner_radius <= dist_xz <= cyl.outer_radius:
            normal = np.array([0, normal_signature, 0], dtype=np.float32)
            checklist.append(Hit(ray_distance=t_cap, point=point, normal=normal, material=cyl.material, object=cyl))

    if not checklist: return None

    return min(checklist, key= lambda x: x.ray_distance)

def intersect_sphere(ray, sphere):
    origin = ray.origin - np.array(sphere.center)
    dir = ray.direction

    a = np.dot(dir, dir)
    b = 2 * np.dot(origin, dir)
    c = np.dot(origin, origin) - sphere.radius ** 2

    Quadratic = b ** 2 - 4 * a * c
    if Quadratic < 0: return None 

    sqrt_disc = np.sqrt(Quadratic)

    x1 = (-b - sqrt_disc) / (2 * a)
    x2 = (-b + sqrt_disc) / (2 * a)

    t = min(t for t in [x1, x2] if t > 0) if any(t > 0 for t in [x1, x2]) else None

    if t is None: return None

    point = ray.origin + t * dir 
    normal = (point - sphere.center) / sphere.radius

    return Hit(ray_distance=t, point=point, normal=normal, material=sphere.material, object=sphere)


def build_bvh(objects):
    return BVHNode(objects)

# -------------------- AABB

class AABB:
    def __init__(self, min_corner, max_corner):

        self.min = np.array(min_corner, dtype=np.float32)
        self.max = np.array(max_corner, dtype=np.float32)

    def intersect(self, ray):

        tmin = (self.min - ray.origin) / ray.direction
        tmax = (self.max - ray.origin) / ray.direction

        t1 = np.minimum(tmin, tmax)
        t2 = np.maximum(tmin, tmax)

        t_near = np.max(t1)
        t_far = np.min(t2)

        return t_near <= t_far and t_far >= 0 # 교차판별 

    @staticmethod
    def surrounding_box(box1, box2):

        small = np.minimum(box1.min, box2.min) 
        big = np.maximum(box1.max, box2.max)
        return AABB(small, big)

# ---------- BVH 노드 ----------

class BVHNode:
    def __init__(self, objects):
        # 자식 노드 
        self.left = None
        self.right = None

        self.object = None
        self.aabb = None

        if len(objects) == 1: # root 
            self.object = objects[0] # 맨 앞이자 본인 

            self.aabb = compute_aabb(self.object)

        elif len(objects) == 2:
            self.left = BVHNode([objects[0]])
            self.right = BVHNode([objects[1]])

            self.aabb = AABB.surrounding_box(self.left.aabb, self.right.aabb)

        else:
            # longest axis 기준으로 
            boxes = [compute_aabb(obj) for obj in objects]
            centers = [(b.min + b.max) / 2 for b in boxes]
            axis_lengths = np.ptp(centers, axis=0)
            axis = np.argmax(axis_lengths)
            objects.sort(key=lambda obj: compute_aabb(obj).min[axis])
            mid = len(objects) // 2

            self.left = BVHNode(objects[:mid])
            self.right = BVHNode(objects[mid:])
            
            self.aabb = AABB.surrounding_box(self.left.aabb, self.right.aabb)

# ---------- AABB 생성기 ----------

def compute_aabb(obj):
    # class 기준으로, 서로 다른 aabbf를 세팅 
    class_name = obj.__class__.__name__ 

    if class_name == 'Cube':
        center = np.array(obj.center)
        size = np.array(obj.size)
        half = size / 2
        return AABB(center - half, center + half)
    
    elif class_name == 'HollowCylinder':
        center = np.array(obj.center)
        r = obj.outer_radius
        h = obj.height / 2
        return AABB(center - [r, h, r], center + [r, h, r])
    
    elif class_name in ('Plane', 'Hole_Plane'):
        center = np.array(obj.center)
        normal = np.array(obj.normal, dtype=np.float32)

        # intersect_plane과 동일한 방식으로 u, v 축 계산
        u_axis = np.cross(normal, (1, 0, 0))  

        if np.linalg.norm(u_axis) < EPSILON: u_axis = np.cross(normal, (0, 0, 1))  

        u_axis = u_axis / np.linalg.norm(u_axis)
        v_axis = np.cross(normal, u_axis)
        v_axis = v_axis / np.linalg.norm(v_axis)

        half_u = (obj.size[0] / 2) * u_axis
        half_v = (obj.size[1] / 2) * v_axis

        corners = [center + dx * half_u + dy * half_v for dx in [-1, 1] for dy in [-1, 1]] # uv와 동일 처리 

        min_corner = np.min(corners, axis=0)
        max_corner = np.max(corners, axis=0)

        min_corner -= 0.1
        max_corner += 0.1 # 최소 두께 

        return AABB(min_corner, max_corner)
    
    elif class_name == 'Sphere':
        center = np.array(obj.center)
        r = obj.radius
        return AABB(center - r, center + r)
    else:
        raise NotImplementedError("Unknown object type")

# 최근접 교차 찾기 

def Nearest_HIT_finder_bvh(ray, node):

    # 예외 처리 
    if not node.aabb.intersect(ray): return None

    if node.object is not None: return node.object.intersect(ray)

    hit_left = Nearest_HIT_finder_bvh(ray, node.left) if node.left else None
    hit_right = Nearest_HIT_finder_bvh(ray, node.right) if node.right else None

    if hit_left and hit_right:
        return hit_left if hit_left.ray_distance < hit_right.ray_distance else hit_right
    
    return hit_left or hit_right
