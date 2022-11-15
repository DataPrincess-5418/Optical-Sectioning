import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import glob
import math
import cv2
from scipy.stats import chi2
import numpy as np
import os
import matplotlib.pyplot as plt
import nlopt
from numpy import *
import re

import matlab.engine
eng = matlab.engine.start_matlab()

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [
        int(text)
        if text.isdigit() else text.lower()
        for text in _nsre.split(s)]

def nl_opt_perim_genSumim(current_img_number, windowsize,Parameters,output_folder, radon_filtering,drone_height):

    global images_fps, camera_fov, image_resolution,images

    current_sum_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    current_sum_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)


    if virtual_camera_perspective == None:
        if max((current_img_number - windowsize),0) > 0 :
            for j in range(0,max((current_img_number - windowsize),0),1):
                x = Parameters[j]
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

        x = Parameters[i]
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

        #img = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)
        img = images[i]

        ################################################################Added for Radon Transform########################################################
        if radon_filtering:
            if i == 0 and current_img_number > 1:
                p = Parameters[i+1]
                x[0] = p[0]
            mat_img = matlab.double(img.tolist())
            img2 = eng.remove_integration_angles(mat_img,(abs(90 - (int(x[0])))))
            img_radon_removed = np.array(img2)
            current_rescaled_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = img_radon_removed
        else:
            current_rescaled_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = img

        current_curr_mask_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = 1.0
        rows,cols = current_rescaled_img.shape

        if virtual_camera_perspective == None:

            shift_pixels_x_direction =  pixels_movement_x_direction
            shift_pixels_y_direction = pixels_movement_y_direction

            #transformation_matrix = np.float32([[1,0,-pixels_movement_x_direction*i],[0,1,-pixels_movement_y_direction*i]])
            transformation_matrix = np.float32([[1,0,shift_pixels_x_direction],[0,1,shift_pixels_y_direction]])

            previous_sum_img_shifted = cv2.warpAffine(current_sum_img,transformation_matrix,(cols,rows))
            previous_mask_img_shifted =  cv2.warpAffine(current_sum_mask_img,transformation_matrix,(cols,rows))
            
            #Summation
            current_sum_mask_img = previous_mask_img_shifted + current_curr_mask_img
            current_sum_img = previous_sum_img_shifted + current_rescaled_img
    return current_sum_img, current_sum_mask_img

def read_images_and_define_global_parameters(Angle, Speed):
    global images, imagelist, Parameters, current_image
    images = []
    imagelist = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(images_dir,'*.png')))]
    Parameters = []
    FirstParameter = [0.0, 0.0]
    Parameters.append(FirstParameter)
    #print(imagelist)  
    for i in range(len(imagelist)):
        img = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)
        images.append(img)
        if i >= 1:
            Parameters.append([Angle-90.0, Speed])
    imagelist = sorted(imagelist, key=natural_sort_key)
    current_image = None
    print(imagelist)


#drone_height = 35.0 #in meters
images_fps = 1 #frames/second
camera_fov = 36 #in degress
image_resolution = 1024

virtual_camera_perspective = None
roi_camera_perspective = 0
current_img_number = 0
windowsize =  1000

Experiments = [{"site_name":'Figure3k_3l', "drone_height":35.0,"Angle":118.0, "Speed":0.5}, {"site_name":'Figure3n_3o', "drone_height":35.0,"Angle":108.0, "Speed":0.6},
{"site_name":'Figure3q_3r', "drone_height":35.0,"Angle":90.0, "Speed":0.6},{"site_name":'Figure4l_4m', "drone_height":10.0,"Angle":260.0, "Speed":0.27}]

for exp in range(len(Experiments)):
    images_dir = os.path.join(r'..\..\IAOS_Data', Experiments[exp]["site_name"], 'images')
    output_folder = os.path.join(r'..\..\IAOS_Data', Experiments[exp]["site_name"], 'results')

    read_images_and_define_global_parameters(Experiments[exp]["Angle"],Experiments[exp]["Speed"])
    current_img_number = len(imagelist)
    sum_img, sum_mask_img = nl_opt_perim_genSumim(current_img_number, windowsize,  Parameters=Parameters,output_folder=output_folder, radon_filtering=False,drone_height = Experiments[exp]["drone_height"])
    integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
    single = integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    cv2.imwrite(os.path.join(output_folder, 'integral_' + str(current_img_number-1) + '.png'),np.uint8(integral_img))
    cv2.imwrite(os.path.join(output_folder, 'integral_cropped_' + str(current_img_number-1) + '.png'),np.uint8(single))
    radon_sum_img, radon_sum_mask_img = nl_opt_perim_genSumim(current_img_number, windowsize,  Parameters=Parameters,output_folder=output_folder, radon_filtering=True, drone_height = Experiments[exp]["drone_height"])
    radon_integral_img = np.divide(radon_sum_img, radon_sum_mask_img, out=np.zeros_like(sum_img), where=radon_sum_mask_img!=0)
    radon_single = radon_integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    cv2.imwrite(os.path.join(output_folder, 'radon_filtered_' + str(current_img_number-1) + '.png'),np.uint8(radon_integral_img))
    cv2.imwrite(os.path.join(output_folder, 'radon_filtered_cropped_'+ str(current_img_number-1) + '.png'),np.uint8(radon_single))
    #video_written = eng.write_IAOS_videos(Experiments[exp]["site_name"])
    #tracking_video_written = eng.tracking_motion(Experiments[exp]["site_name"],'single')
    #tracking_video_written = eng.tracking_motion(Experiments[0]["site_name"],'integral')
eng.quit()



