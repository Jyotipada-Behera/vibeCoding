import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

angle = 0.0
vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
]
faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (0, 3, 7, 4),
]
colors = [
    (0.6, 0.4, 0.2),
    (0.4, 0.8, 0.4),
    (0.8, 0.8, 0.4),
    (0.4, 0.6, 1.0),
    (0.8, 0.5, 0.2),
    (0.6, 0.6, 0.6),
]
cube_positions = [
    (x, -1.5, z)
    for x in range(-2, 2)
    for z in range(-2, 2)
] + [
    (0, -0.5, 0),
    (1, 0.5, -1),
    (-1, 0.5, 1),
    (2, -0.5, 2),
]

def init():
    glClearColor(0.07, 0.07, 0.07, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

def draw_cube(position):
    glPushMatrix()
    glTranslatef(*position)
    for i, face in enumerate(faces):
        glColor3f(*colors[i % len(colors)])
        glBegin(GL_QUADS)
        for vertex in face:
            glVertex3f(*[v * 0.5 for v in vertices[vertex]])
        glEnd()
    glPopMatrix()

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    eye_x = 5 * math.sin(math.radians(angle))
    eye_z = 5 * math.cos(math.radians(angle))
    gluLookAt(eye_x, 2.5, eye_z, 0, 0, 0, 0, 1, 0)
    for pos in cube_positions:
        draw_cube(pos)
    glutSwapBuffers()

def reshape(width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)

def idle():
    global angle
    angle += 1
    if angle >= 360:
        angle -= 360
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Minecraft Game")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
