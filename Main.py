import math
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "150,120"
import pygame as pg 
import pygame_gui as pgg # type: ignore
import sys

class settings:
    screen_width = 1200
    screen_height = 800
    projection_angle:int = 90 #FOV
    control_width = 300
    show_grid:bool = True
    grid_height = -6
    move_amount:float = 0.3

class experiments:
    draw_faces:bool = False # Draws the cube faces

class cube:
    position_x:float = 0.0
    position_z:float = 0.0
    position_y:float = 0.0
    rotation_x:float = 0.0
    rotation_y:float = 0.0
    rotation_z:float = 0.0

class world:
    position_x:float = 0.0
    position_y:float = 0.0
    position_z:float = 0.0
    rotation_x:float = 0.0
    rotation_y:float = 0.0
    rotation_z:float = 0.0
    orientation = [
        [1,0,0],
        [0,1,0],
        [0,0,1]
    ]

pg.init()
screen = pg.display.set_mode((settings.screen_width, settings.screen_height))
pg.display.set_caption("Objector")
clock = pg.time.Clock()
manager = pgg.UIManager((settings.screen_width, settings.screen_height))
running = True
extras_rendered:bool = False

#### CORE START ####

def pg_cords(x, y):
    CENTER_X = settings.screen_width/2
    CENTER_Y = settings.screen_height/2
    return int(CENTER_X + x+settings.control_width/2), int(CENTER_Y - y) 

def map_color(color):
    if color == "blue":
        return(0,0,255)
    elif color == "green":
        return(0,255,0)
    elif color == "red":
        return(255,0,0)
    elif color == "white":
        return(255,255,255)


#### Vector 2 Functions ####

def v2(x:float,y:float):
    return [x,y]

def v2x(v2:list):
    return v2[0]

def v2y(v2:list):
    return v2[1]

#### Vector 3 Functions ####

def v3(x:float,y:float,z:float):
    return [x,y,z]

def v3x(v3:list):
    return v3[0]

def v3y(v3:list):
    return v3[1]

def v3z(v3:list):
    return v3[2]

#### 3x3 Matrix Functions ###
def v3_m33(v3:list):
    x = [v3[0],0,0]
    y = [0,v3[1],0]
    z = [0,0,v3[2]]
    return [x,y,z]

def m33x(m33:list):
    return m33[0]
def m33y(m33:list):
    return m33[1]
def m33z(m33:list):
    return m33[2]

def multi_m33_v3(m33:list,v3:list):
    x = []
    y = []
    z = []
    xnew:float = 0
    ynew:float = 0
    znew:float = 0
    for i in range(3):
        x.append(m33x(m33)[i] * v3[i])
        xnew += x[i]
    for i in range(3):
        y.append(m33y(m33)[i] * v3[i])
        ynew += y[i]
    for i in range(3):
        calculation = m33z(m33)[i] * v3[i]
        z.append(calculation)
        znew += z[i]
    return [xnew,ynew,znew]

def multi_m33_m33(a, b):
    # Multiplies two 3x3 matrices
    return [
        [
            sum(a[i][k] * b[k][j] for k in range(3))
            for j in range(3)
        ]
        for i in range(3)
    ]

def is_positive(n):
    return n > 0 

#### CORE END ####


def normalize_x(normal, data):
    min_x = -settings.screen_width / 2
    max_x = settings.screen_width / 2
    x1, y1 = v2x(normal), v2y(normal)
    x2, y2 = v2x(data), v2y(data)
    if x1 < min_x or x1 > max_x:
        # Clamp x1 to the screen edge and interpolate y1
        if x1 < min_x:
            edge_x = min_x
        else:
            edge_x = max_x
        if x1 != x2:
            t = (edge_x - x2) / (x1 - x2)
            edge_y = y2 + (y1 - y2) * t
        else:
            edge_y = y1
        return v2(edge_x, edge_y)
    else:
        return v2(x1, y1)

def normalize_y(normal, data):
    min_y = -settings.screen_height / 2
    max_y = settings.screen_height / 2
    x1, y1 = v2x(normal), v2y(normal)
    x2, y2 = v2x(data), v2y(data)
    if y1 < min_y or y1 > max_y:
        # Clamp y1 to the screen edge and interpolate x1
        if y1 < min_y:
            edge_y = min_y
        else:
            edge_y = max_y
        if y1 != y2:
            t = (edge_y - y2) / (y1 - y2)
            edge_x = x2 + (x1 - x2) * t
        else:
            edge_x = x1
        return v2(edge_x, edge_y)
    else:
        return v2(x1, y1)
    
def pg_draw(vert1:list,vert2:list,color,surface=screen):
    vert1 = normalize_y(vert1,vert2)
    vert2 = normalize_y(vert2,vert1)
    vert1 = normalize_x(vert1,vert2)
    vert2 = normalize_x(vert2,vert1)
    pg.draw.line(surface,map_color(color),pg_cords(v2x(vert1),v2y(vert1)),pg_cords(v2x(vert2),v2y(vert2)),1)

def pg_draw_poly(polycords:list,color,surface=screen):
    if len(polycords) < 4 or len(polycords) > 4:
        raise ValueError("Draw call rejected: Polygon must have 4 point")
    
    

    pg.draw.polygon(surface, map_color(color), [pg_cords(v2x(pt), v2y(pt)) for pt in polycords],width=0)


        
#Initialises cube vertecies
ve1 = v3(-5,-5,-5)
ve2 = v3(5,-5,-5)
ve3 = v3(-5,5,-5)
ve4 = v3(5,5,-5)
ve5 = v3(-5,-5,5)
ve6 = v3(5,-5,5)
ve7 = v3(-5,5,5)
ve8 = v3(5,5,5)
verts = [ve1,ve2,ve3,ve4,ve5,ve6,ve7,ve8]
original_verts = [v3(*v) for v in verts]

axis_xx = v3(-100,0,1)
axis_x = v3(100,0,1)
axis_yy = v3(0,-100,1)
axis_y = v3(0,100,1)
axis_zz = v3(0,0,-100)
axis_z = v3(0,0,100)

axes = [axis_xx, axis_x, axis_yy, axis_y, axis_zz, axis_z]

original_axes = [v3(*axis) for axis in axes]

edge_len = v3x(ve2) - v3x(ve1)

mult = 2700
def map_projection(array: list, camera_z=world.position_z):
    cords = []
    for vert in array:
        z = v3z(vert) + camera_z  
        if z > 0:
            cords.append(
                v2(
                    v3x(vert) / (z * math.tan(math.radians(settings.projection_angle / 2))) * mult,
                    v3y(vert) / (z * math.tan(math.radians(settings.projection_angle / 2))) * mult
                )
            )
        else:
            cords.append(
                v2(
                    v3x(vert) / 0.001 * math.tan(math.radians(settings.projection_angle / 2)) * mult,
                    v3y(vert) / 0.001 * math.tan(math.radians(settings.projection_angle / 2)) * mult
                )
            )
    return cords

def get_transformed_verts():
    center = [
        sum(v3x(v) for v in original_verts) / len(original_verts),
        sum(v3y(v) for v in original_verts) / len(original_verts),
        sum(v3z(v) for v in original_verts) / len(original_verts)
    ]
    transformed = []
    for v in original_verts:
        # Move to cube center
        v0 = [v3x(v) - center[0], v3y(v) - center[1], v3z(v) - center[2]]
        # Apply cube's own rotation
        v_rot = multi_m33_v3([
            [1,0,0],
            [0,math.cos(math.radians(cube.rotation_x)),-math.sin(math.radians(cube.rotation_x))],
            [0,math.sin(math.radians(cube.rotation_x)),math.cos(math.radians(cube.rotation_x))]
        ], v0)
        v_rot = multi_m33_v3([
            [math.cos(math.radians(cube.rotation_y)),0,math.sin(math.radians(cube.rotation_y))],
            [0,1,0],
            [-math.sin(math.radians(cube.rotation_y)),0,math.cos(math.radians(cube.rotation_y))]
        ], v_rot)
        v_rot = multi_m33_v3([
            [math.cos(math.radians(cube.rotation_z)), -math.sin(math.radians(cube.rotation_z)), 0],
            [math.sin(math.radians(cube.rotation_z)), math.cos(math.radians(cube.rotation_z)), 0],
            [0,0,1]
        ], v_rot)
        # Move back from center and apply cube translation
        v_rot = [
            v_rot[0] + center[0] + float(cube.position_x),
            v_rot[1] + center[1] + float(cube.position_y),
            v_rot[2] + center[2] + float(cube.position_z)
        ]
        transformed.append(v_rot)
    # Now apply camera transformation to all cube verts
    return get_camera_transformed(transformed)

grid_x = []
grid_z = []
render_done:bool = True

for i in range(-10, 11):
    line = [v3(-100,settings.grid_height,i*10),v3(100,settings.grid_height,i*10)]
    grid_x.append(line)
    pg_draw(line[0], line[1], "white")
for i in range(-10, 11):
    line = [v3(i*10,settings.grid_height,-100),v3(i*10,settings.grid_height,100)]
    grid_z.append(line)
    pg_draw(line[0], line[1], "white")

original_grid_x = [ [v3(*pt) for pt in line] for line in grid_x ]
original_grid_z = [ [v3(*pt) for pt in line] for line in grid_z ]


def render_grid():
    for line in grid_x:
        d2_line = map_projection(line)
        pg_draw(d2_line[0], d2_line[1], "white")
        
    for line in grid_z:
        d2_line = map_projection(line)
        pg_draw(d2_line[0], d2_line[1], "white")

def get_camera_transformed(points):
    transformed = []
    orientation_T = [list(row) for row in zip(*world.orientation)]
    for v in points:
        v_t = [
            v3x(v) - world.position_x,
            v3y(v) - world.position_y,
            v3z(v) - world.position_z
        ]
        v_r = [
            sum(orientation_T[i][j] * v_t[j] for j in range(3))
            for i in range(3)
        ]
        transformed.append(v_r)
    return transformed

def get_camera_transformed_grid(original_grid):
    return [get_camera_transformed(line) for line in original_grid]

def get_camera_directions():
    orientation = world.orientation
    right = [orientation[0][0], orientation[1][0], orientation[2][0]]
    up = [orientation[0][1], orientation[1][1], orientation[2][1]]
    forward = [-orientation[0][2], -orientation[1][2], -orientation[2][2]]
    return forward, right, up

def render():
    screen.fill((0, 0, 0))
    # Axes
    axes_projection = map_projection(get_camera_transformed(original_axes))
    pg_draw(axes_projection[0], axes_projection[1], "red")
    pg_draw(axes_projection[2], axes_projection[3], "green")
    pg_draw(axes_projection[4], axes_projection[5], "blue")

    # Grid
    if settings.show_grid:
        grid_x_lines = get_camera_transformed_grid(original_grid_x)
        grid_z_lines = get_camera_transformed_grid(original_grid_z)
        for line in grid_x_lines:
            d2_line = map_projection(line)
            pg_draw(d2_line[0], d2_line[1], "white")
        for line in grid_z_lines:
            d2_line = map_projection(line)
            pg_draw(d2_line[0], d2_line[1], "white")

    # Cube
    projection = map_projection(get_transformed_verts())
    p1 = projection[0]
    p2 = projection[1]
    p3 = projection[2]
    p4 = projection[3]
    p5 = projection[4]
    p6 = projection[5]
    p7 = projection[6]
    p8 = projection[7]

    pg_draw(p5, p7, "blue")
    pg_draw(p6, p8, "blue")
    pg_draw(p5, p6, "blue")
    pg_draw(p7, p8, "blue")
    pg_draw(p1, p5, "green")
    pg_draw(p2, p6, "green")
    pg_draw(p3, p7, "green")
    pg_draw(p4, p8, "green")
    pg_draw(p1, p2, "red")
    pg_draw(p3, p4, "red")
    pg_draw(p1, p3, "red")
    pg_draw(p2, p4, "red")
    
    if experiments.draw_faces:
        pg_draw_poly([p5, p7, p8, p6], "blue")
        pg_draw_poly([p1, p3, p4, p2], "red")
        pg_draw_poly([p1, p2, p6, p5], "green")
        pg_draw_poly([p3, p4, p8, p7], "green")
        pg_draw_poly([p5, p6, p8, p7], "blue")




def translate_verts(v3: list,vertexes:list = verts):
    list_of_verts = []
    for vert in vertexes:
        vert = [v3x(vert) + float(v3x(v3)), v3y(vert) + float(v3y(v3)), v3z(vert) + float(v3z(v3))]
        list_of_verts.append(vert)
    return list_of_verts
    if vertexes == verts:
        original_verts = verts

def rotate_verts_x(angle: float,vertexes:list = verts, silent:bool = False):
    for vert in vertexes:
        vert = multi_m33_v3([
            [1,0,0],
            [0,math.cos(math.radians(angle)),-math.sin(math.radians(angle))],
            [0,math.sin(math.radians(angle)),math.cos(math.radians(angle))]
        ], vert)
    if not silent:
        cube.rotation_x += angle
    

def rotate_verts_y(angle: float,vertexes:list = verts,silent:bool = False):
    for vert in vertexes:
        vert = multi_m33_v3([
            [math.cos(math.radians(angle)),0,math.sin(math.radians(angle))],
            [0,1,0],
            [-math.sin(math.radians(angle)),0,math.cos(math.radians(angle))]
        ], vert)
    if not silent:
        cube.rotation_y += angle

def rotate_verts_z(angle: float,vertexes:list = verts, silent:bool = False):
    for vert in vertexes:
        vert = multi_m33_v3([
            [math.cos(math.radians(angle)), -math.sin(math.radians(angle)), 0],
            [math.sin(math.radians(angle)), math.cos(math.radians(angle)), 0],
            [0,0,1]
        ], vert)
    if not silent:  
        cube.rotation_z += angle

def exe_translation(vector:list, silent:bool = False):
    trans_vector = v3(
        float(v3x(vector)) -float(cube.position_x), 
        float(v3y(vector)) - float(cube.position_y), 
        float(v3z(vector)) - float(cube.position_z)
    )
    if not silent:
        cube.position_x = v3x(vector)
        cube.position_y = v3y(vector)
        cube.position_z = v3z(vector)
    translate_verts(vector,verts)

def exe_world_translation(vector:list, vertexes):
    trans_vector = v3(
        -float(v3x(vector)) - float(world.position_x), 
        -float(v3y(vector)) - float(world.position_y), 
        -float(v3z(vector)) - float(world.position_z)
    )
    return translate_verts(vector,vertexes)

def exe_rotation(vector, silent:bool = False):
    # Only update the cube's own rotation
    cube.rotation_x = float(v3x(vector))
    cube.rotation_y = float(v3y(vector))
    cube.rotation_z = float(v3z(vector))

def exe_world_rotation(vector,vertexes:list = verts,silent:bool = True):
    delta_x = float(v3x(vector)) + float(world.rotation_x)
    delta_y = float(v3y(vector)) + float(world.rotation_y)
    delta_z = float(v3z(vector)) + float(world.rotation_z)
    rotate_verts_x(delta_x, vertexes=vertexes, silent=silent)
    rotate_verts_y(delta_y, vertexes=vertexes, silent=silent)
    rotate_verts_z(delta_z, vertexes=vertexes, silent=silent)
    return vertexes


def change_fov(fov):
    settings.projection_angle = int(float(fov))


def translate_camera(vector:list):
    global axes
    axes = exe_world_translation(v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))), vertexes=original_axes)
    exe_translation(v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))), silent=True)
    for i in range(len(grid_x)):
        grid_x[i] = exe_world_translation(
            v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))),
            vertexes=original_grid_x[i]
        )
        grid_z[i] = exe_world_translation(
            v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))),
            vertexes=original_grid_z[i]
        )
    world.position_x = float(v3x(vector))
    world.position_y = float(v3y(vector))
    world.position_z = float(v3z(vector))

    

def rotate_camera(vector: list):
    world.rotation_x = float(v3x(vector))
    world.rotation_y = float(v3y(vector))
    world.rotation_z = float(v3z(vector))


def rotate_camera_local(axis, angle_deg):
    angle = math.radians(angle_deg)
    c = math.cos(angle)
    s = math.sin(angle)
    if axis == 'x':
        rot = [
            [1,0,0],
            [0,c,-s],
            [0,s,c]
        ]
    elif axis == 'y':
        rot = [
            [c,0,s],
            [0,1,0],
            [-s,0,c]
        ]
    elif axis == 'z':
        rot = [
            [c,-s,0],
            [s,c,0],
            [0,0,1]
        ]
    # Multiply from the right for local rotation
    world.orientation = multi_m33_m33(world.orientation, rot)

#### UI Elements ####

# Translation
label_pos = pgg.elements.UILabel(relative_rect=pg.Rect((10, 10), (100, 30)), text="Position", manager=manager)

entry_x = pgg.elements.UITextEntryLine(pg.Rect((10, 50), (80, 30)), manager)
entry_x.set_text(str(cube.position_x))
entry_y = pgg.elements.UITextEntryLine(pg.Rect((100, 50), (80, 30)), manager)
entry_y.set_text(str(cube.position_y))
entry_z = pgg.elements.UITextEntryLine(pg.Rect((190, 50), (80, 30)), manager)
entry_z.set_text(str(cube.position_z))

translate_btn = pgg.elements.UIButton(pg.Rect((190, 90), (80, 30)), "Translate", manager)

# Rotation
label_rot = pgg.elements.UILabel(pg.Rect((10, 140), (100, 30)), "Rotation", manager)

entry_rx = pgg.elements.UITextEntryLine(pg.Rect((10, 180), (80, 30)), manager)
entry_rx.set_text(str(cube.rotation_x))
entry_ry = pgg.elements.UITextEntryLine(pg.Rect((100, 180), (80, 30)), manager)
entry_ry.set_text(str(cube.rotation_y))
entry_rz = pgg.elements.UITextEntryLine(pg.Rect((190, 180), (80, 30)), manager)
entry_rz.set_text(str(cube.rotation_z))

rotate_btn = pgg.elements.UIButton(pg.Rect((190, 220), (80, 30)), "Rotate", manager)

# FOV
label_fov = pgg.elements.UILabel(pg.Rect((10, 270), (100, 30)), "FOV", manager)
entry_fov = pgg.elements.UITextEntryLine(pg.Rect((100, 270), (80, 30)), manager)
entry_fov.set_text(str(settings.projection_angle))

change_fov_btn = pgg.elements.UIButton(pg.Rect((190, 270), (80, 30)), "Change", manager)


#### Main Loop ####
clock = pg.time.Clock()
running = True

render()

# Movement flags
moving_backward = False
moving_forward = False
moving_left = False
moving_right = False
moving_up = False
moving_down = False
rotating_up = False
rotating_down = False
rotating_left = False
rotating_right = False
rotating_left2 = False
rotating_right2 = False 

move_amt = settings.move_amount

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # UI Events
        if event.type == pgg.UI_BUTTON_PRESSED:
            if event.ui_element == translate_btn:
                exe_translation(v3(entry_x.get_text(),entry_y.get_text(),entry_z.get_text()))
                render()
            elif event.ui_element == rotate_btn:
                exe_rotation(v3(entry_rx.get_text(),entry_ry.get_text(),entry_rz.get_text()))
                render()
            elif event.ui_element == change_fov_btn:
                change_fov(entry_fov.get_text())
                render()

                render()
        elif event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif key == pg.K_w:
                moving_backward = True
            elif key == pg.K_s:
                moving_forward = True
            elif key == pg.K_a:
                moving_left = True
            elif key == pg.K_d:
                moving_right = True
            elif key == pg.K_LSHIFT:
                moving_down = True
            elif key == pg.K_SPACE:
                moving_up = True
            # Camera rotation keys
            elif key == pg.K_f:
                rotating_left = True
            elif key == pg.K_h:
                rotating_right = True
            elif key == pg.K_t:
                rotating_down = True
            elif key == pg.K_g:
                rotating_up = True
            elif key == pg.K_r:
                rotating_right2 = True
            elif key == pg.K_y:
                rotating_left2 = True
            # Speed
            elif key == pg.K_LCTRL:
                move_amt = settings.move_amount * 2

        elif event.type == pg.KEYUP:
            key = event.key
            # Unset the flag when the key is released
            if key == pg.K_w:
                moving_backward = False
            elif key == pg.K_s:
                moving_forward = False
            elif key == pg.K_a:
                moving_left = False
            elif key == pg.K_d:
                moving_right = False
            elif key == pg.K_LSHIFT:
                moving_down = False
            elif key == pg.K_SPACE:
                moving_up = False
            # Camera rotation keys
            elif key == pg.K_f:
                rotating_left = False
            elif key == pg.K_h:
                rotating_right = False
            elif key == pg.K_t:
                rotating_down = False
            elif key == pg.K_g:
                rotating_up = False
            elif key == pg.K_r:
                rotating_right2 = False
            elif key == pg.K_y:
                rotating_left2 = False
            #Speed
            elif key == pg.K_LCTRL:
                move_amt = settings.move_amount
            


    manager.process_events(event)

    cam_pos = [world.position_x, world.position_y, world.position_z]
    cam_rot = [world.rotation_x, world.rotation_y, world.rotation_z]
    moved = False

    forward, right, up = get_camera_directions()

    if moving_forward:
        cam_pos[0] += forward[0] * move_amt * 2
        cam_pos[1] += forward[1] * move_amt * 2
        cam_pos[2] += forward[2] * move_amt * 2
        moved = True
    if moving_backward:
        cam_pos[0] -= forward[0] * move_amt * 2
        cam_pos[1] -= forward[1] * move_amt * 2
        cam_pos[2] -= forward[2] * move_amt * 2
        moved = True
    if moving_left:
        cam_pos[0] -= right[0] * move_amt
        cam_pos[1] -= right[1] * move_amt
        cam_pos[2] -= right[2] * move_amt
        moved = True
    if moving_right:
        cam_pos[0] += right[0] * move_amt
        cam_pos[1] += right[1] * move_amt
        cam_pos[2] += right[2] * move_amt
        moved = True
    if moving_up:
        cam_pos[0] += up[0] * move_amt
        cam_pos[1] += up[1] * move_amt
        cam_pos[2] += up[2] * move_amt
        moved = True
    if moving_down:
        cam_pos[0] -= up[0] * move_amt
        cam_pos[1] -= up[1] * move_amt
        cam_pos[2] -= up[2] * move_amt
        moved = True
    if rotating_up:
        rotate_camera_local('x', move_amt)
        moved = True
    if rotating_down:
        rotate_camera_local('x', -move_amt)
        moved = True
    if rotating_left:
        rotate_camera_local('y', -move_amt)
        moved = True
    if rotating_right:
        rotate_camera_local('y', move_amt)
        moved = True
    if rotating_left2:
        rotate_camera_local('z', -move_amt)
        moved = True
    if rotating_right2:
        rotate_camera_local('z', move_amt)
        moved = True
    if moved:
        translate_camera(cam_pos)
        rotate_camera(cam_rot)
    render()

    manager.update(time_delta)

    control_area = screen.subsurface((0, 0,settings.control_width, settings.screen_height))
    control_area.fill((20, 20, 20))
    
    manager.draw_ui(screen)
    pg.display.update()

pg.quit()