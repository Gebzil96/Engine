#version 330 core

in vec2 in_pos;
uniform mat4 u_proj;

void main() {
    gl_Position = u_proj * vec4(in_pos, 0.0, 1.0);
}
