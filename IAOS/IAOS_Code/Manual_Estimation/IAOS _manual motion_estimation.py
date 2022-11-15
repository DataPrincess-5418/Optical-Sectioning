from configparser import Interpolation
import numpy as np
import cv2
import os
from scipy.stats import chi2
from skimage.data import shepp_logan_phantom
from skimage.transform import radon, rescale
import matlab.engine
eng = matlab.engine.start_matlab()
import matplotlib.pyplot as plt
import glob
import math

######### Parameters ###########

drone_height = 35.0 # altitude in meters
images_fps = 1 # frames/second
camera_fov = 36 # in degress
image_resolution = 1024

################################

images_dir = os.path.join(r'..\..\IAOS_Data', "Figure3k_3l", 'images')
output_folder = os.path.join(r'..\..\IAOS_Data', "Figure3k_3l", 'results')
imagelist = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(images_dir,'*.png')))]
import re
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [
        int(text)
        if text.isdigit() else text.lower()
        for text in _nsre.split(s)]

imagelist = sorted(imagelist, key=natural_sort_key)
img = cv2.imread(os.path.join(images_dir,imagelist[0]),cv2.IMREAD_GRAYSCALE)
virtual_camera_perspective = None
Optimization_Params = []
current_imagelist =[]
current_image = None

def nl_opt_perim_genSumim(current_img_number, windowsize):
  
    if windowsize ==None:
        windowsize = len(imagelist)
       
    current_sum_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    current_sum_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    if virtual_camera_perspective == None:
        if max((current_img_number - windowsize),0) > 0 :
            for j in range(0,max((current_img_number - windowsize),0),1):
                x = Optimization_Params[j]
                time_between_images = 1/images_fps
                person_movement_meters = x[1] * time_between_images

                person_movement_meters_x_direction = math.cos(math.radians(x[0])) * person_movement_meters
                person_movement_meters_y_direction = math.sin(math.radians(x[0])) * person_movement_meters

                imaged_area_length_meters = 2 * drone_height * math.tan(math.radians(camera_fov/2))
                pixels_per_meter = image_resolution/imaged_area_length_meters

                pixels_movement_x_direction = pixels_per_meter * person_movement_meters_x_direction 
                pixels_movement_y_direction = pixels_per_meter * person_movement_meters_y_direction 

                shift_pixels_x_direction =  pixels_movement_x_direction
                shift_pixels_y_direction = pixels_movement_y_direction

    for i in range(max((current_img_number - windowsize),0),current_img_number,1):

        x = Optimization_Params[i]
        time_between_images = 1/images_fps
        person_movement_meters = x[1] * time_between_images

        person_movement_meters_x_direction = math.cos(math.radians(x[0])) * person_movement_meters
        person_movement_meters_y_direction = math.sin(math.radians(x[0])) * person_movement_meters

        imaged_area_length_meters = 2 * drone_height * math.tan(math.radians(camera_fov/2))
        pixels_per_meter = image_resolution/imaged_area_length_meters

        pixels_movement_x_direction = pixels_per_meter * person_movement_meters_x_direction 
        pixels_movement_y_direction = pixels_per_meter * person_movement_meters_y_direction 

        current_rescaled_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
        current_curr_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)

        img = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)

        current_rescaled_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = img 
        current_curr_mask_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = 1.0
        rows,cols = current_rescaled_img.shape

        if virtual_camera_perspective == None:

            shift_pixels_x_direction =  pixels_movement_x_direction
            shift_pixels_y_direction = pixels_movement_y_direction
            transformation_matrix = np.float32([[1,0,shift_pixels_x_direction],[0,1,shift_pixels_y_direction]])
            previous_sum_img_shifted = cv2.warpAffine(current_sum_img,transformation_matrix,(cols,rows))
            previous_mask_img_shifted =  cv2.warpAffine(current_sum_mask_img,transformation_matrix,(cols,rows))
            current_sum_mask_img = previous_mask_img_shifted + current_curr_mask_img
            current_sum_img = previous_sum_img_shifted + current_rescaled_img
    
    return current_sum_img, current_sum_mask_img
  
import tkinter as tk   
from tkinter import *                                     
from PIL import Image, ImageTk    
from numpy import *  
 
root = tk.Tk()
root.title('IAOS')
canvas = tk.Canvas(root,width=1900,height=1500)
canvas.pack()
                                                
def loadImage(event):
   
    global Integral
    global current_direction_param
    global current_speed_param
    global single
    global labelDir3
    
    FirstParameter = [0.0, 0.0]
    
    Optimization_Params.append(FirstParameter)
    current_img_number = 0
    windowsize =  1000
    direction_param = current_direction_param.get()
    speed_param= current_speed_param.get()
    current_imagelist.append(imagelist[0])
    
    for i in range(1,len(imagelist)):
        current_img_number = i
        x0 = [(direction_param - 90),speed_param]    
        Optimization_Params.append(x0)  
    current_img_number = len(imagelist)
    sum_img, sum_mask_img = nl_opt_perim_genSumim(current_img_number, windowsize)
    integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
    single = integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    img_resize = cv2.resize(single, dsize=(900, 900))
    Integral = ImageTk.PhotoImage(image=Image.fromarray(img_resize))
    canvas.create_image(1000,570, image=Integral)
    canvas.pack() 
    Optimization_Params.clear()
    labelDir3.destroy()
    labelText2=tk.StringVar()
    labelText2.set("Integral")
    labelDir2=tk.Label(root, textvariable=labelText2 , font = ("Helvetica", 30))
    labelDir2.pack(side="right")
    labelDir2.place(x=910, y= 30)
    return single


def radon():
   
    global Radon_Transform_Integral
    global current_direction_param
    global current_speed_param
    global single
    global labelDir3
    
    direction_param = current_direction_param.get()
    mat_img = matlab.double(single.tolist())
    img2 = eng.Radon_Transform_Filtering(mat_img,(abs(90 - (direction_param))))
    img_radon_removed = np.array(img2, dtype=uint8)
    img_resize = cv2.resize(img_radon_removed, dsize=(900, 900))
    Radon_Transform_Integral = ImageTk.PhotoImage(image=Image.fromarray(img_resize))
    canvas.create_image(1000,570, image=Radon_Transform_Integral)
    canvas.pack() 
    labelText3=tk.StringVar()
    labelText3.set("Radon Transform Filtering")
    labelDir3=tk.Label(root, textvariable=labelText3 , font = ("Helvetica", 30))
    labelDir3.pack(side="right")
    labelDir3.place(x=780, y= 30)
                                

labelText3=tk.StringVar()
labelText3.set("Integral")
labelDir3=tk.Label(root, textvariable=labelText3 , font = ("Helvetica", 30))
labelDir3.pack(side="right")
labelDir3.place(x=910, y= 30)

labelText5=tk.StringVar()
labelText5.set("direction (deg)")
labelDir5=tk.Label(root, textvariable=labelText5 , font = ("Helvetica", 15))
labelDir5.pack(side="right")
labelDir5.place(x=60, y= 110)

labelText6=tk.StringVar()
labelText6.set("speed (m/s)")
labelDir6=tk.Label(root, textvariable=labelText6 , font = ("Helvetica", 15))
labelDir6.pack(side="right")
labelDir6.place(x=60, y=210)

current_value5 = tk.IntVar()
current_value6 = tk.DoubleVar()

current_direction_param = tk.Scale(root, from_= 0, to= 360, length= 150, sliderlength= 15, resolution = 1, orient=tk.HORIZONTAL, variable=current_value5)
current_direction_param.bind("<ButtonRelease-1>", loadImage)
current_direction_param.pack()
current_direction_param.place(x=220, y=100)  

current_speed_param = tk.Scale(root, from_= 0, to= 1, length= 150, sliderlength= 15, resolution = 0.1,  orient=tk.HORIZONTAL, variable=current_value6)
current_speed_param.pack()
current_speed_param.place(x=220, y=200)    

button_live = tk.Button(root, text='RTF',font= ("Helvetica", 15),  width=20, height=2,command=radon)
button_live.place(x=90, y=300)

root.mainloop() 
           
    
    
                                               
             
                            
  