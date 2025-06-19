import os
import numpy as np
import sys

from tqdm import tqdm
from PIL import Image

sys.path.append("./scripts")

from ray_tracing_fresnel import trace_ray
from find_intersection import build_bvh

from camera_hw5 import Camera
from Cornell_scene import create_cornell_box

camera = Camera(
    eye=(0, 0, 45),
    target=(0, 0, 0),
    up=(0, 1, 0),
    fov=46,
    width=640,
    height=480
)

objects, lights = create_cornell_box()

# BVH 생성
BVH = build_bvh(objects)

output_dir = "hw5_result"
os.makedirs(output_dir, exist_ok=True)

# 파일 이름 결정 
def get_next_filename(directory):
    existing = [f for f in os.listdir(directory) if f.endswith(".png")]
    nums = [int(f.split(".")[0]) for f in existing if f.split(".")[0].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    return os.path.join(directory, f"{next_num}.png")

# tqdm이 적용된 렌더링 함수 (overwrite render)
def render_with_progress(camera, objects, lights, width=640, height=480):

    image = np.zeros((height, width, 3), dtype=np.float32)

    for y in tqdm(range(height), desc="Rendering"):
        for x in range(width):
            ray = camera.generate_ray(x, y)
            color = trace_ray(ray, objects, lights, camera.eye)
            image[y, x] = color
    return image

def save_image(image_array, filename="output_image.png"):

    # gamma correction - 자주 사용하는 2.2를 사용 
    gamma_correction = np.clip(image_array, 0, 1) ** (1 / 2.2)

    image = Image.fromarray((255* gamma_correction).astype(np.uint8)) # Error 처리 uint8 
    image.save(filename)

    # 확인용 
    print(f"{filename} saved")


# 렌더링
image = render_with_progress(camera, BVH, lights)
filename = get_next_filename(output_dir)
save_image(image, filename)