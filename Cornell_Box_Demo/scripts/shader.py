from pyglet.graphics.shader import Shader, ShaderProgram

# vertex shader 
vertex_source_default = """

#version 330

layout(location = 0) in vec3 vertices;
layout(location = 1) in vec4 colors;
layout(location = 2) in vec3 normals;
layout(location = 3) in vec2 texCoord;

uniform mat4 view_proj;
uniform mat4 model;

out vec4 vertex_color;

out vec3 frag_pos;
out vec3 frag_normal;

out vec2 frag_tex_coord;

void main()
{
    vec4 world_pos = model * vec4(vertices, 1.0);
    frag_pos = world_pos.xyz;

    frag_normal = mat3(transpose(inverse(model))) * normals;
    frag_tex_coord = texCoord;
    
    gl_Position = view_proj * world_pos;
    vertex_color = colors;
}
"""

# fragment shader (Phong lighting)
fragment_source_default = """

#version 330

#define num_lights 100  // 

in vec4 vertex_color;

in vec3 frag_pos;
in vec3 frag_normal;

in vec2 frag_tex_coord;

uniform vec3 light_pos[num_lights];
uniform vec3 light_color[num_lights];
uniform vec3 view_pos;

uniform bool use_texture;
uniform bool use_phong;

uniform float ambient_strength;
uniform float specular_strength;
uniform float diffuse_strength;
uniform float shininess;

uniform sampler2D texture1;

out vec4 fragColor;

void main()
{
    vec3 norm = normalize(frag_normal);
    vec3 result = vec3(0);

    for (int i = 0; i <num_lights; ++i) {

        vec3 light_dir = normalize(light_pos[i] - frag_pos);

        // ambient
        vec3 ambient = ambient_strength * light_color[i];

        // diffuse
        float diff = max(dot(norm, light_dir), 0); // 뒤에서오는거 처리
        vec3 diffuse = diff * diffuse_strength * light_color[i];

        // attenuation
        float distance = length(light_pos[i] - frag_pos);
        float attenuation = 1 / (1 + 0.05 * distance + 0.01 * distance * distance);
        // 거리 및 거리 제곱에 의한 감쇠 (더 자연스럽게)

        // specular
        vec3 specular = vec3(0);

        if (diff > 0) {
            vec3 view_dir = normalize(view_pos - frag_pos);
            vec3 reflect_dir = reflect(-light_dir, norm);
            float spec = pow(max(dot(view_dir, reflect_dir), 0), shininess);
            specular = specular_strength * spec * light_color[i];
        }

        // I(out) = ka * Ia + ...을 구현 
        result += (ambient + attenuation * (diffuse + specular));
    }

    vec4 tex_color;
    vec4 is_phong_color;

    // use_texture로 texture를 보여주거나 안 보여주기

    if (use_texture){
        tex_color = texture(texture1, frag_tex_coord);
    }
    else{
        tex_color = vec4(1.0);
    }

    // use_phong으로 phong shading 적용할지 말지.

    if (use_phong){
        is_phong_color = vec4(result, 1);
    }
    else {
        is_phong_color = vec4(1.0);
    }

    fragColor = is_phong_color * tex_color * vertex_color;
}

"""

def create_shader(vs_source, fs_source):

    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')

    return MaterialShader(vert_shader, frag_shader)

class MaterialShader(ShaderProgram):

    def set_phong(self, ambient, specular, diffuse_strength, shininess):

        self["ambient_strength"] = ambient
        self["specular_strength"] = specular
        self["diffuse_strength"] = diffuse_strength
        self["shininess"] = shininess

    def set_texture(self, texture, unit=0):

        texture.unit = unit
        
        texture.bind(unit)  
        self["texture1"] = unit
