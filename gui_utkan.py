from tkinter import *
# from tkinter.ttk import Scale
from tkinter import colorchooser
#filedialog,messagebox
# import PIL.ImageGrab as ImageGrab
import time
# import numpy as np
# import requests
import socket

url = 'http://192.168.164.159'

prev_time = 0
MAX_DATA_POINTS = 25000
last_data_point = 0
text_number = 0
M=0
TEXTPATH = r"C:\Users\erdem\OneDrive\Belgeler\guidata"
import sys



import math

def subsample(x, y, speed, M):
    M = int(M,10)
    # speed = [float(s) for s in speed]
    """
    Subsample a set of 2D points and calculate the angle to the next point for each point.

    Arguments:
    x -- a list of x coordinates of the points
    y -- a list of y coordinates of the points
    speed -- the speed of the moving object
    M -- the sampling rate (every Mth point is taken)

    Returns:
    A tuple containing:
    - a list of x coordinates of the subsampled points
    - a list of y coordinates of the subsampled points
    - a list of angles (in radians) to the next point for each subsampled point
    """
    # Initialize lists to store the subsampled points and angles
    subsampled_x = []
    subsampled_y = []
    angles = []

    # Loop through the points and subsample every Mth point
    # print(x,M)
    for i in range(0, len(x), M):
        # Add the subsampled point to the lists
        subsampled_x.append(x[i])
        subsampled_y.append(y[i])

    
        # Calculate the angle to the next point
        if i == 0:
            angle = 0
            angles.append(angle)
        elif i+M < len(x):
            dx = x[i+M] - x[i]
            dy = y[i+M] - y[i]
            angle = -math.atan2(dy, dx) - angle
            angles.append(angle)
        else:
            break
        

    # Calculate the time it takes to travel between each pair of subsampled points
    times = [math.sqrt((x2-x1)*(x2-x1)
                        + (y2-y1)*(y2-y1)) 
                        for x1, y1, x2, y2,s in 
                        zip(subsampled_x[:-1], subsampled_y[:-1], subsampled_x[1:], subsampled_y[1:], speed[:-1])]

    # Return the subsampled points and angles as a tuple
    return subsampled_x, subsampled_y, angles, times



#Defining Class and constructor of the Program
class Draw():
    def __init__(self,root):
        self.coords_list = [[0,0,0] for i in range(MAX_DATA_POINTS)]
        self.processed_data = []
#Defining title and Size of the Tkinter Window GUI
        self.root =root
        self.root.title("GUI for the Copycat")
        self.root.geometry("740x690")
        self.root.configure(background="darkblue")
        self.root.resizable(0,0)
    
#variables for pointer and Eraser   
        self.pointer= "white"
        self.erase="black"

#Widgets for Tkinter Window

# Configure the alignment , font size and color of the text
        text=Text(root,height=3,width=64,bd=-3,pady=0,borderwidth=-3)
        text.tag_configure("tag_name", justify='left', font=('verdana',29),background='darkblue',foreground='white')

# Insert a Text
        text.insert("1.0", "GUI for El Gato Imitador")
        text.config(state=DISABLED)
# Add the tag for following given text
        text.tag_add("tag_name", "1.0", "end")
        text.pack()
        
         
# Reset Button to clear the entire screen (227 before)
        self.clear_all= Button(self.root,text="Clear All",bd=4,bg='white',command= self.clear_all,width=9,relief=RIDGE)
        self.clear_all.place(x=640,y=50)

# Background Button for choosing color of the Canvas (287)
        self.bg_btn= Button(self.root,text="Background",bd=4,bg='white',command=self.canvas_color,width=9,relief=RIDGE)
        self.bg_btn.place(x=640,y=90)

# Print coordinates Button
        self.print_coords = Button(self.root, text="Print Coords", bd=4, bg="white", command=self.print_coords_list, width=9, relief=RIDGE)
        self.print_coords.place(x=640, y=170)

# Create Save Data Button
        self.save_coords_list= Button(self.root,text="Save",bd=4,bg='white',command=self.save_coords_list,width=9,relief=RIDGE)
        self.save_coords_list.place(x=640,y=130)

# Create Paint Data Button
        self.paint_data_button = Button(self.root, text="Smooth", bd=4, bg="white", command=self.paint_processed_data, width=9, relief=RIDGE)
        self.paint_data_button.place(x=640, y=310)
        self.pointer_size=2


#Defining a background color for the Canvas 
        self.background = Canvas(self.root,bg='black',bd=4,relief=GROOVE,height=600,width=600)
        self.background.place(x=10,y=50)
        self.background.old_coords=None
        self.background.bind("<ButtonRelease-1>", self.reset_coords)
        self.background.bind("<B1-Motion>", self.paint)

        self.window=Entry(self.root, bd=4,width=5)
        self.window.place(x=660, y= 230)

        self.smoothdata=Button(self.root, text="Parameter", bd=4, bg="white", command=self.get_value, width=9, relief=RIDGE)
        self.smoothdata.place(x=640, y= 270)

        self.senddata=Button(self.root, text="Send", bd=4, bg="white", command=self.send_data, width=9, relief=RIDGE)
        self.senddata.place(x=640, y= 350)

        self.drawz=Button(self.root, text="Z", bd=4, bg="white", command=self.draw_Z, width=3, relief=RIDGE)
        self.drawz.place(x=640, y= 390)

        self.drawO=Button(self.root, text="O", bd=4, bg="white", command=self.draw_O, width=3, relief=RIDGE)
        self.drawO.place(x=680, y= 390)

        self.drawsq=Button(self.root, text="[]", bd=4, bg="white", command=self.draw_sq, width=3, relief=RIDGE)
        self.drawsq.place(x=640, y= 425)

        self.drawtr=Button(self.root, text="^", bd=4, bg="white", command=self.draw_tr, width=3, relief=RIDGE)
        self.drawtr.place(x=680, y= 425)

####### Functions are defined here

# Paint Function for Drawing the lines on Canvas

    def paint(self,event): 
            if self.background.winfo_containing(event.x_root, event.y_root) == self.background:
                global last_data_point
                x, y = event.x, event.y
                if self.background.old_coords:
                        x1, y1 = self.background.old_coords
                        real_speed = self.calculate_speed(x,x1,y,y1)
                        self.pointer = self.get_color(real_speed)
                        self.coords_list.insert(last_data_point,[x,y,real_speed])
                        last_data_point = last_data_point+1
                        self.background.create_line(x, y, x1, y1, fill=self.pointer, width=self.pointer_size)
                        
            
                self.background.old_coords = x, y
                #real_speed = self.calculate_speed(x,x1,y,y1)
                #self.pointer = self.get_color(real_speed)

            else:
                self.reset_coords(event)
# Function for reseting coordinates on memory   
    def reset_coords(self,event):
        self.background.old_coords = None


#### Function for converting speed
    def speed_converter(self, speed):
        real_speed = speed 
        return real_speed

# Function for choosing the color of pointer  

    def calculate_speed(self,x,x1,y,y1):
        global prev_time
        curr_time = time.time()
        #time.sleep(0.001)
        dt = curr_time - prev_time
        dx = x - x1
        dy = y - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
     # Calculate the speed
        prev_time = curr_time
        try :
            #real_speed = self.speed_converter(distance / dt)
            real_speed = (distance/dt)/2000
            #print(real_speed)
            return real_speed
        except ZeroDivisionError:
            real_speed = self.coords_list[last_data_point-1][2]
            #print (real_speed)
            return real_speed

# Function for choosing the color of pointer  

    def get_color(self, real_speed):
        # Check the value of 'real_speed' and return the appropriate color
        if real_speed > 2.0:
            return "darkred"
        elif real_speed > 1.2:
            return "red"
        elif real_speed > 0.6:
            return "orange"
        elif real_speed > 0:
            return "yellow"
        else:
            return "blue"

# Function for choosing the background color of the Canvas    
    def canvas_color(self):
        color=colorchooser.askcolor()
        self.background.configure(background=color[1])
        self.erase= color[1]

    def draw_Z(self):
        global last_data_point
        self.background.delete('all')  
        self.background.create_line(110, 100, 510, 100, fill="cyan", width=3)
        self.background.create_line(510, 100, 110, 500, fill="cyan", width=3)
        self.background.create_line(110, 500, 510, 500, fill="cyan", width=3)
        self.coords_list=[[110,100,1],[510,500,1],[110,500,1],[510,500,1]]
        last_data_point = 4

    def draw_O(self):
        global last_data_point
    # Draw a circle on the canvas
        self.background.delete('all')  
        x0, y0, x1, y1 = 110, 100, 510, 500
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        radius = (x1 - x0) / 2
        last_data_point = 100  # number of points used to approximate the circle
        self.coords_list = []
        for i in range(last_data_point):
            angle = 2 * math.pi * i / last_data_point
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.coords_list.append([x, y])
        self.background.create_polygon(self.coords_list, outline="cyan", width=3)


    def draw_sq(self):
        global last_data_point
        # Draw a circle on the canvas
        self.background.delete('all')  
        self.background.create_rectangle(110, 100, 510, 500, outline="cyan",width=3)
        self.coords_list=[[110,100,1],[110,500,1],[510,500,1],[510,100,1]]
        last_data_point=4


    def draw_tr(self):
        global last_data_point
        # Draw a circle on the canvas
        self.background.delete('all')  
        self.background.create_polygon(110, 500, 510, 500, 310, 100, outline="cyan",width=3)
        self.coords_list=[[110,500,1],[510,500,1],[310,100,1]]
        last_data_point=3


    def print_coords_list(self):
        global last_data_point
        for i in range(last_data_point):
                print (self.coords_list[i])
        # print(last_data_point)
        #last_data_point = 0
        #self.coords_list = [[0,0,0] for i in range(MAX_DATA_POINTS)]
        #self.background.delete('all')

    def save_coords_list(self):
        global last_data_point
        global text_number
        
        with open(TEXTPATH + "\GUI_data_" + str(text_number) + ".txt",'w') as file:
            for i in range(last_data_point):
                file.write (str(self.coords_list[i])+"\n")
        
        with open(TEXTPATH + "\GUI_data_" + str(text_number) + ".txt",'r') as file:
            contents = file.read()
            contents = contents.replace('[', '')
            contents = contents.replace(']', ';')

        with open(TEXTPATH + "\GUI_data_" + str(text_number) + ".txt",'w') as file:
            file.write(contents)
        text_number = text_number + 1

    def clear_all(self):
        global last_data_point
        self.background.delete('all')
        last_data_point = 0
        self.coords_list = [[0,0,0] for i in range(MAX_DATA_POINTS)]

    def get_value(self):
        self.value = self.window.get()
        self.window.delete(0,"end")
    
    def paint_processed_data(self):
        #For now we need a coords_temp to not include [0,0,0] values
        self.processed_data = self.coords_list[:last_data_point]
        self.get_value()
        M=self.value
        x = []
        y = []
        speed = []
        for a, b, c in self.processed_data:
            x.append(a)
            y.append(b)
            speed.append(c)

        # print(len(x))

        positionPath = 1
        sys.path.insert(positionPath, r"C:\Users\erdem\gui")
        # print(x,y,speed,M)
        self.processed_data = subsample(x,y,speed,M)
        
        #self.processed_data[0],self.processed_data[1],self.processed_data[2],
        #This Line is for processed_data
        #temp_coords_list = self.processed_data_list
        
        self.background.delete('all')    
        prev_x, prev_y, prev_speed = self.processed_data[0][0], self.processed_data[1][0], self.processed_data[2]
        #prev_color = self.get_color(prev_speed)
        for i in range(len(self.processed_data[0]) - 1):
            x1, y1 = self.processed_data[0][i], self.processed_data[1][i]
            x2, y2 = self.processed_data[0][i+1], self.processed_data[1][i+1]
            speed = self.processed_data[2][i]
            self.pointer=self.get_color(speed)
            self.background.create_line(x1, y1, x2, y2, fill = self.pointer, width=self.pointer_size) 
        

    def send_data(self):
        # self.xys = [(self.processed_data[0][i], 
        #              self.processed_data[1][i], 
        #              self.processed_data[2][i],
        #              self.processed_data[3][i]) 
        #             for i in range(len(self.processed_data[0]))]
        # # print(self.xys)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.137.135', 8080))
        # data_send=""
        # self.processed_data[3].append(0)
        # self.processed_data[2]
        
        # print((len(self.processed_data[0])))
        for i in  range(len(self.processed_data[2])):
            print(self.processed_data[2][i],self.processed_data[3][i])
            data_send = "{0:.3f}".format(self.processed_data[2][i]) + " " + "{0:.3f}".format(self.processed_data[3][i]) + 'n'
            # print(data_send)
            data = data_send.encode('ascii')
        #     # num_bytes_sent = 
            sock.send(data)
        sock.close()
            
            
            # data_send+="{0:.1f}".format(self.processed_data[2][i]) + "{0:.1f}".format(self.processed_data[3][i]) + " "

        # print(data_send)
        # return
        
    
#Bind the background Canvas with mouse click

if __name__ =="__main__":
    root = Tk()
    p= Draw(root)
    root.mainloop()