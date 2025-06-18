import math
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "150,120"
import pygame as pg 
import pygame_gui as pgg # type: ignore
import sys

class settings:
    screen_width = 1200
    screen_height = 800
    projection_angle:int = 90
    recursive_rendering:bool = True
    control_width = 300
    show_grid:bool = True
    grid_height = -6
    move_amount:float = 1.0
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

pg.init()
screen = pg.display.set_mode((settings.screen_width, settings.screen_height))
pg.display.set_caption("Objector")
clock = pg.time.Clock()
manager = pgg.UIManager((settings.screen_width, settings.screen_height))
running = True
extras_rendered:bool = False

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

def pg_draw(vert1:list,vert2:list,color,surface=screen):
    pg.draw.line(surface,map_color(color),pg_cords(v2x(vert1),v2y(vert1)),pg_cords(v2x(vert2),v2y(vert2)),1)

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
###########################


#Initialises cube vertecies
ve1 = v3(-5,-5,100)
ve2 = v3(5,-5,100)
ve3 = v3(-5,5,100)
ve4 = v3(5,5,100)
ve5 = v3(-5,-5,110)
ve6 = v3(5,-5,110)
ve7 = v3(-5,5,110)
ve8 = v3(5,5,110)
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

mult = 3000
def map_projection(array: list, camera_z=200):
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
        v0 = [v3x(v) - center[0], v3y(v) - center[1], v3z(v) - center[2]]
        v_rot = multi_m33_v3([
            [1,0,0],
            [0,math.cos(math.radians(cube.rotation_x-world.rotation_x)),-math.sin(math.radians(cube.rotation_x-world.rotation_x))],
            [0,math.sin(math.radians(cube.rotation_x-world.rotation_x)),math.cos(math.radians(cube.rotation_x-world.rotation_x))]
        ], v0)
        v_rot = multi_m33_v3([
            [math.cos(math.radians(cube.rotation_y-world.rotation_y)),0,math.sin(math.radians(cube.rotation_y-world.rotation_y))],
            [0,1,0],
            [-math.sin(math.radians(cube.rotation_y-world.rotation_y)),0,math.cos(math.radians(cube.rotation_y-world.rotation_y))]
        ], v_rot)
        v_rot = multi_m33_v3([
            [math.cos(math.radians(cube.rotation_z-world.rotation_z)), -math.sin(math.radians(cube.rotation_z-world.rotation_z)), 0],
            [math.sin(math.radians(cube.rotation_z-world.rotation_z)), math.cos(math.radians(cube.rotation_z-world.rotation_z)), 0],
            [0,0,1]
        ], v_rot)
        v_rot = [
            v_rot[0] + center[0] + float(cube.position_x) - float(world.position_x),
            v_rot[1] + center[1] + float(cube.position_y) - float(world.position_y),
            v_rot[2] + center[2] + float(cube.position_z) - float(world.position_z)
        ]
        transformed.append(v_rot)
    return transformed
grid_x = []
grid_z = []
render_done:bool = True

for i in range(-10, 10):
    line = [v3(-100,settings.grid_height,i*10),v3(100,settings.grid_height,i*10)]
    grid_x.append(line)
    pg_draw(line[0], line[1], "white")
for i in range(-10, 10):
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
        #print("z",line)
        pg_draw(d2_line[0], d2_line[1], "white")

def render():
    render_done = False 
    screen.fill((0, 0, 0))
    axes_projection = map_projection(axes)
    pg_draw(axes_projection[0], axes_projection[1], "red")
    pg_draw(axes_projection[2], axes_projection[3], "green")
    pg_draw(axes_projection[4], axes_projection[5], "blue")

    
    projection = map_projection(get_transformed_verts())
    if settings.show_grid:
        render_grid()
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

    render_done = True



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

def exe_rotation(vector,silent:bool = False):
    if not silent:
        position = v3(cube.position_x,cube.position_y,cube.position_z)
        exe_translation(v3(0,0,0))
        rotate_verts_x(float(v3x(vector)) - cube.rotation_x,vertexes=verts,silent = silent)
        rotate_verts_y(float(v3y(vector)) - cube.rotation_y,vertexes=verts,silent = silent)
        rotate_verts_z(float(v3z(vector)) - cube.rotation_z,vertexes=verts,silent = silent)
        exe_translation(position)
    else:
        rotate_verts_x(float(v3x(vector)) - cube.rotation_x,vertexes=verts,silent = silent)
        rotate_verts_y(float(v3y(vector)) - cube.rotation_y,vertexes=verts,silent = silent)
        rotate_verts_z(float(v3z(vector)) - cube.rotation_z,vertexes=verts,silent = silent)

def exe_world_rotation(vector,vertexes:list = verts,silent:bool = False):
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
    camera_x.set_text(str(world.position_x))
    camera_y.set_text(str(world.position_y))
    camera_z.set_text(str(world.position_z))
    

def rotate_camera(vector:list):
    global axes
    exe_world_rotation(v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))), vertexes=original_axes)
    exe_world_rotation(v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))), vertexes=verts)
    for i in range(len(grid_x)):
        exe_world_rotation(
            v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))),
            vertexes=original_grid_x[i]
        )
        exe_world_rotation(
            v3(-float(v3x(vector)), -float(v3y(vector)), -float(v3z(vector))),
            vertexes=original_grid_z[i]
        )
    world.rotation_x = float(v3x(vector))
    world.rotation_y = float(v3y(vector))
    world.rotation_z = float(v3z(vector))
    camera_rx.set_text(str(world.rotation_x))
    camera_ry.set_text(str(world.rotation_y))
    camera_rz.set_text(str(world.rotation_z))



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

# Camera Translation
label_cpos = pgg.elements.UILabel(pg.Rect((10, 320), (120, 30)), "Camera Position", manager)

camera_x = pgg.elements.UITextEntryLine(pg.Rect((10, 360), (80, 30)), manager)
camera_x.set_text(str(world.position_x))
camera_y = pgg.elements.UITextEntryLine(pg.Rect((100, 360), (80, 30)), manager)
camera_y.set_text(str(world.position_y))
camera_z = pgg.elements.UITextEntryLine(pg.Rect((190, 360), (80, 30)), manager)
camera_z.set_text(str(world.position_z))

translate_camera_btn = pgg.elements.UIButton(pg.Rect((190, 400), (80, 30)), "Translate", manager)

#Camera Rotation
label_crot = pgg.elements.UILabel(pg.Rect((10, 450), (120, 30)), "Camera Rotation", manager)

camera_rx = pgg.elements.UITextEntryLine(pg.Rect((10, 490), (80, 30)), manager)
camera_rx.set_text(str(world.rotation_x))
camera_ry = pgg.elements.UITextEntryLine(pg.Rect((100, 490), (80, 30)), manager)
camera_ry.set_text(str(world.rotation_y))
camera_rz = pgg.elements.UITextEntryLine(pg.Rect((190, 490), (80, 30)), manager)
camera_rz.set_text(str(world.rotation_z))

rotate_camera_btn = pgg.elements.UIButton(pg.Rect((190, 530), (80, 30)), "Rotate", manager)

#### Main Loop ####
clock = pg.time.Clock()
running = True

render()

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
            elif event.ui_element == translate_camera_btn:
                translate_camera(v3(
                    float(camera_x.get_text()),
                    float(camera_y.get_text()),
                    float(camera_z.get_text())
                ))
                render()
            elif event.ui_element == rotate_camera_btn:
                rotate_camera(v3(
                    float(camera_rx.get_text()),
                    float(camera_ry.get_text()),
                    float(camera_rz.get_text())
                ))
                render()
        elif event.type == pg.KEYDOWN:
            key = event.key
            if key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif key == pg.K_w:
                translate_camera(v3(world.position_x, world.position_y, world.position_z + settings.move_amount))
                render()
            elif key == pg.K_s:
                translate_camera(v3(world.position_x, world.position_y, world.position_z - settings.move_amount))
            elif key == pg.K_a:
                translate_camera(v3(world.position_x - settings.move_amount, world.position_y, world.position_z))
                render()
            elif key == pg.K_d: 
                translate_camera(v3(world.position_x + settings.move_amount, world.position_y, world.position_z))
                render()
            elif key == pg.K_LSHIFT:
                translate_camera(v3(world.position_x, world.position_y - settings.move_amount, world.position_z))
                render()
            elif key == pg.K_SPACE:
                translate_camera(v3(world.position_x, world.position_y + settings.move_amount, world.position_z))
                render()

        manager.process_events(event)

    manager.update(time_delta)

    control_area = screen.subsurface((0, 0,settings.control_width, settings.screen_height))
    control_area.fill((20, 20, 20))
    
    manager.draw_ui(screen)
    pg.display.update()

pg.quit()