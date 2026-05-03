import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
import sys
import math

# --- Shaders ---
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec3 aOffset;

out vec3 ourColor;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * vec4(aPos + aOffset, 1.0f);
    // Add simple directional fake lighting based on normal/color variation
    ourColor = aColor;
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(ourColor, 1.0f);
}
"""

# --- Camera Globals ---
camera_pos = glm.vec3(0.0, 5.0, 0.0)
camera_front = glm.vec3(0.0, 0.0, -1.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)

delta_time = 0.0
last_frame = 0.0

last_x = 400.0
last_y = 300.0
yaw = -90.0
pitch = 0.0
first_mouse = True

def process_input(window):
    global camera_pos, camera_front, camera_up, delta_time
    camera_speed = 10.0 * delta_time
    
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += camera_speed * camera_front
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= camera_speed * camera_front
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        camera_pos += camera_speed * camera_up
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        camera_pos -= camera_speed * camera_up

def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y, yaw, pitch, camera_front

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos # Reversed since y-coordinates range from bottom to top
    last_x = xpos
    last_y = ypos

    sensitivity = 0.1
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset

    if pitch > 89.0:
        pitch = 89.0
    if pitch < -89.0:
        pitch = -89.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    camera_front = glm.normalize(front)

def generate_terrain(size):
    offsets = []
    for x in range(-size, size):
        for z in range(-size, size):
            # Simple procedural generation using sine waves for rolling hills
            y = int(math.sin(x * 0.2) * 2.0 + math.cos(z * 0.2) * 2.0)
            
            # Surface layer (Grass)
            offsets.append([x, y, z])
            # Dirt layer
            offsets.append([x, y - 1, z])
            # Stone layer
            offsets.append([x, y - 2, z])
    
    return np.array(offsets, dtype=np.float32)

def main():
    global delta_time, last_frame

    if not glfw.init():
        sys.exit()
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(1280, 720, "Python Minecraft Clone - First Person Terrain", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE) # Optimization: don't render inside faces

    shader_program = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    vertices = np.array([
        # Format: X, Y, Z, R, G, B
        # Back face
        -0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
         0.5,  0.5, -0.5,  0.2, 0.8, 0.2,
         0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
         0.5,  0.5, -0.5,  0.2, 0.8, 0.2,
        -0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
        -0.5,  0.5, -0.5,  0.2, 0.8, 0.2,
        # Front face
        -0.5, -0.5,  0.5,  0.5, 0.3, 0.1,
         0.5, -0.5,  0.5,  0.5, 0.3, 0.1,
         0.5,  0.5,  0.5,  0.3, 0.9, 0.3,
         0.5,  0.5,  0.5,  0.3, 0.9, 0.3,
        -0.5,  0.5,  0.5,  0.3, 0.9, 0.3,
        -0.5, -0.5,  0.5,  0.5, 0.3, 0.1,
        # Left face
        -0.5,  0.5,  0.5,  0.4, 0.2, 0.0,
        -0.5,  0.5, -0.5,  0.4, 0.2, 0.0,
        -0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
        -0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
        -0.5, -0.5,  0.5,  0.4, 0.2, 0.0,
        -0.5,  0.5,  0.5,  0.4, 0.2, 0.0,
        # Right face
         0.5,  0.5,  0.5,  0.4, 0.2, 0.0,
         0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
         0.5,  0.5, -0.5,  0.4, 0.2, 0.0,
         0.5, -0.5, -0.5,  0.4, 0.2, 0.0,
         0.5,  0.5,  0.5,  0.4, 0.2, 0.0,
         0.5, -0.5,  0.5,  0.4, 0.2, 0.0,
        # Bottom face
        -0.5, -0.5, -0.5,  0.3, 0.15, 0.0,
         0.5, -0.5, -0.5,  0.3, 0.15, 0.0,
         0.5, -0.5,  0.5,  0.3, 0.15, 0.0,
         0.5, -0.5,  0.5,  0.3, 0.15, 0.0,
        -0.5, -0.5,  0.5,  0.3, 0.15, 0.0,
        -0.5, -0.5, -0.5,  0.3, 0.15, 0.0,
        # Top face
        -0.5,  0.5, -0.5,  0.3, 0.9, 0.3,
         0.5,  0.5,  0.5,  0.3, 0.9, 0.3,
         0.5,  0.5, -0.5,  0.3, 0.9, 0.3,
         0.5,  0.5,  0.5,  0.3, 0.9, 0.3,
        -0.5,  0.5, -0.5,  0.3, 0.9, 0.3,
        -0.5,  0.5,  0.5,  0.3, 0.9, 0.3
    ], dtype=np.float32)

    # Instanced array data
    instance_offsets = generate_terrain(32) # Generates a 64x64 grid of blocks
    instance_count = len(instance_offsets)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    instanceVBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    # Setup standard block vertices
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Position
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    # Color
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))

    # Setup instance offsets
    glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
    glBufferData(GL_ARRAY_BUFFER, instance_offsets.nbytes, instance_offsets, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 3 * instance_offsets.itemsize, ctypes.c_void_p(0))
    glVertexAttribDivisor(2, 1) # Tell OpenGL this is an instanced attribute

    view_loc = glGetUniformLocation(shader_program, "view")
    proj_loc = glGetUniformLocation(shader_program, "projection")

    glClearColor(0.5, 0.8, 0.9, 1.0)

    # --- Main Loop ---
    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(window)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader_program)

        projection = glm.perspective(glm.radians(70.0), 1280.0 / 720.0, 0.1, 1000.0)
        view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)

        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        glBindVertexArray(VAO)
        # Render thousands of blocks in a single draw call
        glDrawArraysInstanced(GL_TRIANGLES, 0, 36, instance_count)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [instanceVBO])
    glfw.terminate()

if __name__ == '__main__':
    main()