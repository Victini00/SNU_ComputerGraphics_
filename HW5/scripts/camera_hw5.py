import math
import numpy as np

from find_intersection import Ray

class Camera:
    def __init__(self, eye, target, up, fov, width, height):

        # 카메라 기본 설정 
        self.eye = np.array(eye, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov              
        self.width = width
        self.height = height

        # Viewing Coord
        self.compute_camera_coord()

    def compute_camera_coord(self):
        # z 먼저 
        camera_z = self.eye - self.target
        camera_z = camera_z / np.linalg.norm(camera_z)

        camera_x = np.cross(self.up, camera_z)
        camera_x = camera_x / np.linalg.norm(camera_x)

        camera_y = np.cross(camera_z, camera_x)

        self.camera_x = camera_x
        self.camera_y = camera_y
        self.camera_z = camera_z

        self.aspect_ratio = self.width / self.height

        self.scale = math.tan(math.radians(self.fov) * 1/2)

    def generate_ray(self, x, y):
        px = (2 * ((x + 1/2) / self.width) -1) * self.aspect_ratio
        py = 1 - 2*((y + 1/2) / self.height)

        px *= self.scale
        py *= self.scale

        # 정면 방향에 좌우 보정 
        direction = -self.camera_z + px * self.camera_x + py * self.camera_y 
        direction /= np.linalg.norm(direction)

        return Ray(self.eye, direction)
