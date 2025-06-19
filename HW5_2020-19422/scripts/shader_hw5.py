import numpy as np
from find_intersection import Ray, Nearest_HIT_finder_bvh

EPSILON = 0.01
LIGHT_NUM = 6

# 면광원 ~ 점광원 근사. 
def lights_sampling(light, num=LIGHT_NUM):
    points = []

    center = np.array(light.center)
    width, height = light.size

    x = np.linspace(-width / 2, width / 2, num)
    z = np.linspace(-height / 2, height / 2, num)

    for i in z[::-1]:  # 위에서 아래
        for j in x:
            points.append(center + np.array([j, 0, i]))

    return points

# Phong shading ~ hw4 그대로 사용 
def shade(hit, lights, bvh_root, view_pos):
    norm = hit.normal / np.linalg.norm(hit.normal)
    frag_pos = hit.point
    material = hit.material

    result = np.zeros(3) # init 

    for light in lights:
        sample_points = lights_sampling(light, num=LIGHT_NUM)
        contribution = np.zeros(3)

        for sp in sample_points:
            light_dir = sp - frag_pos
            light_distance = np.linalg.norm(light_dir)

            light_dir /= light_distance # normalize

            shadow_origin = frag_pos + EPSILON * norm
            shadow_ray = Ray(shadow_origin, light_dir)
    
            shadow_hit = Nearest_HIT_finder_bvh(shadow_ray, bvh_root)

            # 계산 생략 조건
            if shadow_hit and shadow_hit.ray_distance < light_distance : continue 

            # ambient
            ambient = material.ambient * np.array(light.intensity)

            # diffuse
            diff = max(np.dot(norm, light_dir), 0.0)
            diffuse = material.diffuse * diff * np.array(light.intensity)

            # attenuation
            attenuation = 1 / (1 + 0.05 * light_distance + 0.01 * (light_distance ** 2)) # 2차 보정 

            # specular
            specular = np.zeros(3)

            if diff > 0:

                view_dir = (np.array(view_pos) - frag_pos) 
                view_dir /= np.linalg.norm(view_dir)

                reflect_dir = (2 * np.dot(norm, light_dir) * norm - light_dir) 
                reflect_dir /=  np.linalg.norm(reflect_dir)

                spec = max(np.dot(view_dir, reflect_dir), 0)
                specular = material.specular * (spec ** material.shininess) * np.array(light.intensity)

            contribution += (ambient + attenuation * (diffuse + specular))

        result += contribution / len(sample_points)

    # Texture 적용
    base_color = np.array(material.color)

    if (material.texture is not None) and hasattr(hit.object, 'get_uv'): 
        u, v = hit.object.get_uv(frag_pos)

        h, w, no_use = material.texture.shape

        mapping_x = min(int(u*w), w - 1)
        # mapping_y = min(int(v*h), h - 1)
        mapping_y = min(int((1 - v)*h), h - 1) # 위아래반대 

        tex_color = material.texture[mapping_y, mapping_x][:3] # 반대!!!! 
        base_color *= tex_color

    final_color = result * base_color
    return np.clip(final_color, 0, 1)
