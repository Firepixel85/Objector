#       #####    ####     ####     ####    #     #
#       #       #        #    #   #    #    #   #  
#       ###     #   ##   ######   #          # #  
#       #       #    #   #    #   #    #     # 
#####   #####    ####    #    #    ####     # 

#This is the legacy renderer
#This version is built on turtle and as such is not performant at all
#It is meant to be used as an educational tool to study the basics of 3D rendering

import turtle as tr
import math
import tkinter as tk
 
class settings: #Here you can change some of the renderers settings
    screen_width = 800
    screen_height = 800
    projection_angle:int = 90   #Field of view (FOV), the larger it is, the more perspective distortion
    recursive_rendering:bool = True  #Allows for "Animations" to be programmed in line 217 (Keeps rendering and then discrading the render)
    show_controls:bool = True
 
if settings.recursive_rendering:
    settings.show_controls = False #Disables controls if recursive rendering is enabled, as it would be pointless
 
win = tr.Screen()
win.bgcolor("black")
win.setup(width=settings.screen_width, height=settings.screen_height)
 
old_draws = [] #Holds all the lines rendered in a frame, used in the next frame to clear the screen
 
def draw(vert1:list, vert2:list, color:str): #Draws an edge, take's in 2 Vector2 as coordinates for the vertecies to join
    if len(vert1) > 2 or len(vert2) > 2: #Value safety check
        raise ValueError("Vector 2 can't have more than 2 entries!")
    else: #Draw the line
        pen = tr.Turtle()
        pen.speed(0)
        pen.up()
        pen.goto(v2x(vert1), v2y(vert1))
        pen.down()
        pen.pencolor(color)
        pen.goto(v2x(vert2), v2y(vert2))

        #Clean up after operation
        pen.hideturtle()
        old_draws.append(pen)
        del pen
 
 
#Below are some helper function to impliment Vectors

#### Vector 2 Functions ####
 
def v2(x:float,y:float): #Creates a Vector2
    return [x,y]
 
def v2x(v2:list): #Returns the x value of a Vector2
    return v2[0]
 
def v2y(v2:list): #Returns the y value of a Vector2
    return v2[1]
 
#### Vector 3 Functions ####
 
def v3(x:float,y:float,z:float): #Creates a Vector3
    return [x,y,z]
 
def v3x(v3:list): #Returns the x value of a Vector3
    return v3[0]
 
def v3y(v3:list): #Returns the y value of a Vector3
    return v3[1]
 
def v3z(v3:list): #Returns the z value of a Vector3
    return v3[2]

###########################
 
 
#Initialises cube vertecies
ve1 = v3(1,1,1)
ve2 = v3(10,1,1)
ve3 = v3(1,10,1)
ve4 = v3(10,10,1)
ve5 = v3(1,1,1.5)
ve6 = v3(10,1,1.5)
ve7 = v3(1,10,1.5)
ve8 = v3(10,10,1.5)
verts = [ve1,ve2,ve3,ve4,ve5,ve6,ve7,ve8] #Places all the vertecis in a list for easier procesing
 
mult = 15 #Makes the final output of map_projection more exaggerated (bigger on the screen)
def map_projection(): #This is the core of the renderer, maps 3D point to a 2D plane
    cords = []
    for i in range(len(verts)):
        if v3z(verts[i]) != 0:
            cords.append(
                v2(
                    v3x(verts[i]) / (v3z(verts[i]) * math.tan(math.radians(settings.projection_angle / 2)))*mult,
                    v3y(verts[i]) / (v3z(verts[i]) * math.tan(math.radians(settings.projection_angle / 2)))*mult
                )
 
            )
        else:
            cords.append(v2(0,0))
    return cords
 
render_done:bool = True
 
def render(): #Main render function, runs all operation in order to complete a render call
    render_done = False

    discard_render() #Discrad the old frame

    projection = map_projection() #Map vertecies to 2D plane
 
    #Move data from list to point
    p1 = projection[0]
    p2 = projection[1]
    p3 = projection[2]
    p4 = projection[3]
    p5 = projection[4]
    p6 = projection[5]
    p7 = projection[6]
    p8 = projection[7]
 
    #Render points
    draw(p5, p7, "blue")
    draw(p6, p8, "blue")
    draw(p5, p6, "blue")
    draw(p7, p8, "blue")
    draw(p1, p5, "green")
    draw(p2, p6, "green")
    draw(p3, p7, "green")
    draw(p4, p8, "green")
    draw(p1, p2, "red")
    draw(p3, p4, "red")
    draw(p1, p3, "red")
    draw(p2, p4, "red")
 
    render_done = True
 
def discard_render(): #Clears the screen to render the next frame
    if old_draws != []:
        for i in range(len(old_draws)):
            old_draws[i].clear()
        old_draws.clear()
 
def translate_verts(trans_vector: list): #Translates all the cube's vertecis based on the translation vector given
    for i in range(len(verts)):
        verts[i] = [
            v3x(verts[i]) + v3x(trans_vector),
            v3y(verts[i]) + v3y(trans_vector),
            v3z(verts[i]) + v3z(trans_vector)
        ]
 
if settings.show_controls: #Initialises the UI if settings.show_controls is True 
    root = tk.Tk()
else:
    root = None
 
def redraw_dynamic_ui(): #Some parts of the UI are dynamic meaning they change durring the runtime, this updates them
    current_x = tk.Label(root, text=str(v3x(verts[0])))
    current_x.grid(column=3, row=1)
    current_y = tk.Label(root, text=str(v3y(verts[0])))
    current_y.grid(column=3, row=2)
 
def exe_translation(): #Runs all the needed commands to translate the cube
    trans_vector = v3(float(entry_x.get()) - v3x(verts[0]), float(entry_y.get()) - v3y(verts[0]),0) #Transforms absolute input to a relative transformation vector
    translate_verts(trans_vector)
    redraw_dynamic_ui()
    if not settings.recursive_rendering: #Recursive rendering renders every frame so there's no need to render again
        render()
 
translate_verts(v3(-5,-5, 0)) #Due to how the cube coordinates are placed, it is placed off-center this centers it
 
while settings.recursive_rendering:
    if render_done: #Awaits for a frame to finish rendering so it can start on the next one
        render()
        #### Recursive rendering loop ####
        
        translate_verts(v3(-1,-1,0)) #Example animations: moves the cube by -1,-1,0 every frame

        #### End of recursive rendering loop ####
 
if not settings.recursive_rendering:
    render()
 
##### UI #####
 
if settings.show_controls: #Draws the static part of the UI
    root.title("Controls")
    root.geometry("300x400")
 
    translate_label = tk.Label(root, text="Position")
    translate_label.grid()
 
    x_label = tk.Label(root, text = "X:")
    x_label.grid(column=0, row=1)
    entry_x = tk.Entry(root)
    entry_x.grid(column=1, row=1)
    entry_x.insert(tk.END,str(v3x(verts[0])))
 
    y_label = tk.Label(root, text = "Y:")
    y_label.grid(column=0, row=2)
    entry_y = tk.Entry(root)
    entry_y.grid(column=1, row=2)
    entry_y.insert(tk.END,str(v3y(verts[0])))
 
    translate_button = tk.Button(root, text="Translate", command=exe_translation)
    translate_button.grid(column=1, row=4)
    redraw_dynamic_ui()
 
##### UI END #####
 
tr.exitonclick()