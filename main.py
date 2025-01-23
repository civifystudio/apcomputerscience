import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Chase Game")

# Set up the 3D perspective
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(90, (display[0]/display[1]), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)

# Enable depth testing
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

class Camera:
    def __init__(self):
        self.position = [0, 1.7, 0]  # Eye level height
        self.yaw = 0    # Horizontal rotation
        self.pitch = 0  # Vertical rotation
        self.mouse_sensitivity = 0.15  # Reduced for smoother camera movement

    def update(self, player_pos, is_moving):
        # Update camera position
        self.position = [player_pos[0], player_pos[1] + 1.7, player_pos[2]]
        
        # Set up the camera view
        glLoadIdentity()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])

    def handle_mouse_movement(self, dx, dy):
        self.yaw = (self.yaw - dx * self.mouse_sensitivity) % 360
        self.pitch += dy * self.mouse_sensitivity
        self.pitch = max(-89, min(89, self.pitch))  # Limit looking up/down

class Player:
    def __init__(self):
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.speed = 0.25  # Faster than the enemy (0.2)
        self.acceleration = 0.8
        self.friction = 0.85
        self.vertical_velocity = 0
        self.is_jumping = False
        self.jump_strength = 0.5
        self.gravity = 0.02
        self.is_moving = False

    def move(self, keys, camera):
        # Get movement input
        forward = int(keys[pygame.K_w] or keys[pygame.K_UP])
        backward = int(keys[pygame.K_s] or keys[pygame.K_DOWN])
        left = int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        right = int(keys[pygame.K_d] or keys[pygame.K_RIGHT])

        # Calculate movement direction based on camera angle
        yaw_rad = math.radians(camera.yaw)
        
        # Calculate forward and right vectors
        forward_x = -math.sin(yaw_rad)
        forward_z = -math.cos(yaw_rad)
        right_x = -math.sin(yaw_rad - math.pi/2)
        right_z = -math.cos(yaw_rad - math.pi/2)

        # Calculate movement vector
        move_x = 0
        move_z = 0

        if forward:
            move_x += forward_x
            move_z += forward_z
        if backward:
            move_x -= forward_x
            move_z -= forward_z
        if left:
            move_x += right_x
            move_z += right_z
        if right:
            move_x -= right_x
            move_z -= right_z

        # Normalize movement vector if moving diagonally
        length = math.sqrt(move_x * move_x + move_z * move_z)
        if length > 0:
            move_x /= length
            move_z /= length

            # Apply movement with acceleration
            target_vel_x = move_x * self.speed
            target_vel_z = move_z * self.speed

            # Smooth acceleration
            self.velocity[0] += (target_vel_x - self.velocity[0]) * self.acceleration
            self.velocity[2] += (target_vel_z - self.velocity[2]) * self.acceleration
        else:
            # Apply friction when not moving
            self.velocity[0] *= self.friction
            self.velocity[2] *= self.friction

        # Handle jumping
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vertical_velocity = self.jump_strength
            self.is_jumping = True

        # Apply gravity
        self.vertical_velocity -= self.gravity
        self.position[1] += self.vertical_velocity

        # Ground collision
        if self.position[1] <= 0:
            self.position[1] = 0
            self.vertical_velocity = 0
            self.is_jumping = False

        # Update position
        self.position[0] += self.velocity[0]
        self.position[2] += self.velocity[2]

        # Update movement state
        self.is_moving = abs(self.velocity[0]) > 0.01 or abs(self.velocity[2]) > 0.01

    def draw(self):
        pass  # First person view doesn't need player model

class Enemy:
    def __init__(self):
        self.position = [5, 0, 5]
        self.speed = 0.2  # Increased from 0.1 to 0.2
        self.size = 4.0  # Increased from 2.0 to 4.0
        # Load the enemy texture
        self.texture = self.load_texture('diddyimage (1).png')
        # Load sound
        self.sound = pygame.mixer.Sound('aint-no-party-like-a-diddy-party.mp3')
        self.sound_playing = False
        self.sound_distance = 15.0  # Increased from 5.0 to 15.0 - can hear from much further away

    def load_texture(self, image_path):
        textureSurface = pygame.image.load(image_path)
        textureData = pygame.image.tostring(textureSurface, 'RGBA', 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        return texture

    def move(self, player_pos):
        # Calculate direction to player
        dx = player_pos[0] - self.position[0]
        dz = player_pos[2] - self.position[2]
        
        # Calculate distance to player
        distance = math.sqrt(dx * dx + dz * dz)
        
        # Handle sound based on distance
        if distance <= self.sound_distance:
            if not self.sound_playing:
                self.sound.play(-1)  # -1 means loop indefinitely
                self.sound_playing = True
        else:
            if self.sound_playing:
                self.sound.stop()
                self.sound_playing = False
        
        # Move towards player if there's a distance
        if distance > 0:
            dx /= distance
            dz /= distance
            
            # Move towards player
            self.position[0] += dx * self.speed
            self.position[2] += dz * self.speed

    def draw(self, camera_pos):
        # Enable texturing
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Calculate direction to camera
        dx = camera_pos[0] - self.position[0]
        dz = camera_pos[2] - self.position[2]
        
        # Calculate rotation angle to face camera
        angle = math.degrees(math.atan2(dx, dz))
        
        # Draw billboard
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1] + self.size/2, self.position[2])
        glRotatef(angle, 0, 1, 0)  # Rotate to face camera
        
        # Draw textured quad
        glColor4f(1.0, 1.0, 1.0, 1.0)  # Reset color to white for proper texture colors
        glBegin(GL_QUADS)
        # Front face
        glTexCoord2f(0, 0); glVertex3f(-self.size/2, -self.size/2, 0)
        glTexCoord2f(1, 0); glVertex3f(self.size/2, -self.size/2, 0)
        glTexCoord2f(1, 1); glVertex3f(self.size/2, self.size/2, 0)
        glTexCoord2f(0, 1); glVertex3f(-self.size/2, self.size/2, 0)
        glEnd()
        
        glPopMatrix()
        
        # Disable texturing and blending
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

def draw_floor():
    glBegin(GL_QUADS)
    size = 50  # Larger floor
    grid_size = 2
    
    for x in range(-size, size, grid_size):
        for z in range(-size, size, grid_size):
            if (x + z) % (grid_size * 2) == 0:
                glColor3f(0.8, 0.8, 0.8)  # Light gray
            else:
                glColor3f(0.6, 0.6, 0.6)  # Darker gray
            
            glVertex3f(x, 0, z)
            glVertex3f(x, 0, z + grid_size)
            glVertex3f(x + grid_size, 0, z + grid_size)
            glVertex3f(x + grid_size, 0, z)
    
    glEnd()

def check_collision(pos1, pos2, threshold=1.5):
    dx = pos1[0] - pos2[0]
    dz = pos1[2] - pos2[2]
    distance = math.sqrt(dx * dx + dz * dz)
    return distance < threshold

def draw_text(text, x, y):
    font = pygame.font.SysFont("Arial", 30)
    text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 255))
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    glRasterPos3d(x, y, 0)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize sound system
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # Set up perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    camera = Camera()
    player = Player()
    enemy = Enemy()
    
    game_over = False
    start_time = time.time()
    
    # Hide and lock the mouse cursor
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    while True:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r and game_over:
                    # Reset game
                    player.position = [0, 0, 0]
                    enemy.position = [5, 0, 5]
                    game_over = False
                    start_time = time.time()
            if event.type == pygame.MOUSEMOTION:
                camera.handle_mouse_movement(event.rel[0], event.rel[1])

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys, camera)
            enemy.move(player.position)
            
            if check_collision(player.position, enemy.position):
                game_over = True
            
            score = int(current_time - start_time)

        camera.update(player.position, player.is_moving)

        glClearColor(0.529, 0.808, 0.922, 1.0)  # Sky blue background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        draw_floor()
        enemy.draw(camera.position)
        
        # Draw score
        draw_text(f"Score: {score}", -0.9, 0.9)
        if game_over:
            draw_text("Game Over! Press R to restart", -0.3, 0)
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()
