import numpy as np

from find_intersection import Ray, Nearest_HIT_finder_bvh
from shader_hw5 import shade

NUM_recursive = 4
EPSILON = 0.01

# 간접광용 
def random_hemisphere(normal):

    # 랜덤 2개 추출 
    r1 = np.random.rand() # phi
    r2 = np.random.rand() # theta ~ 고도 

    phi = 2 * np.pi * r1

    x = np.cos(phi) * np.sqrt(1 - r2)
    y = np.sqrt(r2)
    z = np.sin(phi) * np.sqrt(1 - r2)

    up = np.array([0, 1, 0], dtype=np.float64)
    normal = np.array(normal, dtype=np.float64)

    # normal과 up이 거의 같은 경우 (회전 불필요)
    if np.allclose(normal, up): return np.array([x, y, z])
    elif np.allclose(normal, -up): return np.array([x, -y, -z])  # 반대 방향 hemisphere 

    axis = np.cross(up, normal).astype(np.float64)
    axis /= np.linalg.norm(axis)
    angle = np.arccos(np.clip(np.dot(up, normal), -1, 1))

    return rotate_vector(np.array([x, y, z]), axis, angle)

# Rodrigues 회전공식 
def rotate_vector(v, axis, angle):
    return (v * np.cos(angle) + np.cross(axis, v) * np.sin(angle) + axis * np.dot(axis, v) * (1 - np.cos(angle)))

# 메인 ray 함수 
def trace_ray(ray, bvh_root, lights, camera_pos, depth=0):

    # 재귀 종료 
    if depth > NUM_recursive: return np.array([0, 0, 0]) # 검정 

    # hit check 
    hit = Nearest_HIT_finder_bvh(ray, bvh_root)
    if not hit: return np.array([0, 0, 0]) 

    local_color = shade(hit, lights, bvh_root, camera_pos)

    # 1-bounce diffuse lighting
    # depth == 0 -> 1번 반사됐을 때, 1번만 적용 
    if depth == 0:
        indirect = np.zeros(3)

        num_samples = 10  # 조절 가능! 
        norm = hit.normal
        origin = hit.point + norm * EPSILON

        for i in range(num_samples):
            dir = random_hemisphere(norm) # 랜덤 방향 가져옴 

            sample_ray = Ray(origin, dir)
            sample_color = trace_ray(sample_ray, bvh_root, lights, camera_pos, depth + 1)
            indirect += sample_color

        indirect /= num_samples
        local_color += 0.2 * indirect

    reflected_color = np.zeros(3) # 반사
    refracted_color = np.zeros(3) # 굴절 

    # 반사
    if hit.material.reflective > 0:
        reflect_dir = ray.direction - 2 * np.dot(ray.direction, hit.normal) * hit.normal
        reflect_origin = hit.point + EPSILON * hit.normal

        reflect_ray = Ray(reflect_origin, reflect_dir)

    # 굴절 
    has_refract = False # 굴절 체크 
    refract_ray = None

    if hit.material.refractive > 0:
        n1 = 1  # 공기
        n2 = hit.material.ior

        normal = hit.normal
        cos_i = -np.dot(ray.direction, normal)

        # 내부
        if cos_i < 0:  
            n1, n2 = n2, n1 # swap

            normal = -normal
            cos_i = -cos_i

        n_diff = n1 / n2
        sin_t2 = n_diff **2 * (1 - cos_i**2)

        if sin_t2 <= 1:
            cos_t = np.sqrt(1 - sin_t2)
            refract_dir = n_diff * ray.direction + (n_diff * cos_i - cos_t) * normal
            refract_origin = hit.point - EPSILON * normal 

            refract_ray = Ray(refract_origin, refract_dir)
            has_refract = True 

    # Fresnel ~ Schlick
    R0 = ((1 - hit.material.ior) / (1 + hit.material.ior)) ** 2

    cos_theta = max(np.dot(-ray.direction, hit.normal), 0.0)
    fresnel = R0 + (1 - R0) * (1 - cos_theta) ** 5

    # 재귀 호출
    if hit.material.reflective > 0 or hit.material.refractive > 0:

        # 반사, 굴절 
        reflected_color = trace_ray(reflect_ray, bvh_root, lights, camera_pos, depth + 1)
        if has_refract: refracted_color = trace_ray(refract_ray, bvh_root, lights, camera_pos, depth + 1)

        # Fresnel 기반 반사-굴절 혼합
        color = (1 - fresnel) * refracted_color + fresnel * reflected_color

    else: # 아니면 유지 
        color = local_color

    # 비율에 맞춰 최종 color 결정 
    final_color = (1 - hit.material.reflective - hit.material.refractive) * local_color + hit.material.reflective * color + hit.material.refractive * color

    return np.clip(final_color, 0, 1)

# 메인 렌더링 함수
# Diffuse Sampling 
def render(camera, bvh_root, lights, width=640, height=480):
    image = np.zeros((height, width, 3), dtype=np.float32)

    rays_pixel = 10

    for y in range(height):
        for x in range(width):
            color_sum = np.zeros(3)

            for _ in range(rays_pixel):
                # 픽셀 내의 무작위 오프셋 (0~1 사이)
                rand1 = np.random.rand()
                rand2 = np.random.rand()

                ray = camera.generate_ray(x + rand1, y + rand2)
                color = trace_ray(ray, bvh_root, lights, camera.eye)
                color_sum += color

            image[y, x] = color_sum / rays_pixel

    return image
