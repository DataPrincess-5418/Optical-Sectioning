import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import glob
import math
import utm
import time
import shutil
import json
import spectral
import cv2
from scipy.stats import chi2
import numpy as np
import os
import matplotlib.pyplot as plt
import matlab.engine
eng = matlab.engine.start_matlab()

##########Define parameters --- Required -- drone height, image_fps, camera fov, image resolution#####################
drone_height = 35.0 #in meters
images_fps = 5 #frames/second
camera_fov = 36 #in degress
image_resolution = 512
#Define Roi of Desired target --- [top_corners_bbox_heigth, bottom_corners_bbox_heigth, left_corners_bbox_width, right_corners_bbox_heigth]
defined_roi = [420, 440, 203,223] #Figure5_LinearMotion
roi = [defined_roi[0]+image_resolution, defined_roi[1]+image_resolution, defined_roi[2]+image_resolution,defined_roi[3]+image_resolution]
virtual_camera_perspective = None
roi_camera_perspective = 0
Optimization_Params = []
current_imagelist =[]
current_image = None

################Define Image Folder and Output images folder

images_dir = os.path.join(r'..\..\IAOS_Data', "Figure5_LinearMotion", 'images')
output_folder =  os.path.join(r'..\..\IAOS_Data', "Figure5_LinearMotion", 'results')

imagelist = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(images_dir,'*.png')))]

import re
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [
        int(text)
        if text.isdigit() else text.lower()
        for text in _nsre.split(s)]

imagelist = sorted(imagelist, key=natural_sort_key)
print(imagelist)

img = cv2.imread(os.path.join(images_dir,imagelist[0]),cv2.IMREAD_GRAYSCALE)

def nl_opt_perim_genSumim(current_img_number, windowsize,radon_filtering):
    if windowsize ==None:
        windowsize = len(imagelist)
        
    current_sum_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    current_sum_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)

    ############# assuming Roi perspective is zeros################
    current_roi = [roi[0],roi[1], roi[2],roi[3]]

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

                current_roi = [current_roi[0]+shift_pixels_y_direction,current_roi[1]+shift_pixels_y_direction, current_roi[2]+shift_pixels_x_direction,current_roi[3]+shift_pixels_x_direction]

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


        ################################################################Added for Radon Transform########################################################
        if radon_filtering:
            if i == 0 and current_img_number > 1:
                p = Optimization_Params[i+1]
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
            current_roi = [current_roi[0]+shift_pixels_y_direction,current_roi[1]+shift_pixels_y_direction, current_roi[2]+shift_pixels_x_direction,current_roi[3]+shift_pixels_x_direction]
            
            #Summation
            current_sum_mask_img = previous_mask_img_shifted + current_curr_mask_img
            current_sum_img = previous_sum_img_shifted + current_rescaled_img
    drawn_rectaangle = cv2.rectangle(current_rescaled_img,(int(current_roi[2]),int(current_roi[0])),(int(current_roi[3]),int(current_roi[1])),(255,255,255),2)
    cv2.imwrite(os.path.join(output_folder, 'rectangledrawn' + str(current_img_number-1) + '.png'),np.uint8(drawn_rectaangle))
    current_cropped_img = current_rescaled_img[int(current_roi[0]):int(current_roi[1]), int(current_roi[2]):int(current_roi[3])]
    cur_img_var = np.var(current_cropped_img)
    cv2.imwrite(os.path.join(output_folder, 'current_cropped' + str(current_img_number-1) + '_'+str(cur_img_var) +'.png'),np.uint8(current_cropped_img))
    return current_sum_img, current_sum_mask_img, current_roi

######################  Non Linear  --- Per Image OPtimization #################################
def nl_opt_perim_calvar(x,grad):
    global virtual_camera_perspective, roi_camera_perspective
    global current_image, sum_img, sum_mask_img, previous_roi

    time_between_images = 1/images_fps
    person_movement_meters = x[1]*time_between_images

    person_movement_meters_x_direction = math.cos(math.radians(x[0])) * person_movement_meters
    person_movement_meters_y_direction = math.sin(math.radians(x[0])) * person_movement_meters

    imaged_area_length_meters = 2 * drone_height * math.tan(math.radians(camera_fov/2))
    pixels_per_meter = image_resolution/imaged_area_length_meters

    pixels_movement_x_direction = pixels_per_meter * person_movement_meters_x_direction 
    pixels_movement_y_direction = pixels_per_meter * person_movement_meters_y_direction 

    #sum_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    #sum_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)

    current_camera_perspective = len(current_imagelist)-1
    
    current_rescaled_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    current_curr_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)


    current_rescaled_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = current_image
    current_curr_mask_img[image_resolution:img.shape[0]+image_resolution,image_resolution:img.shape[1]+image_resolution] = 1.0
    rows,cols = current_rescaled_img.shape

    if virtual_camera_perspective == None:
        # If virtual_camera_perspective is None than Only Shift the previous sum image and sum mask image which were generated 
        # using last image as virtual perspective in previous rendering
        shift_pixels_x_direction =  pixels_movement_x_direction
        shift_pixels_y_direction = pixels_movement_y_direction

        #transformation_matrix = np.float32([[1,0,-pixels_movement_x_direction*i],[0,1,-pixels_movement_y_direction*i]])
        transformation_matrix = np.float32([[1,0,shift_pixels_x_direction],[0,1,shift_pixels_y_direction]])
        previous_sum_img_shifted = cv2.warpAffine(sum_img,transformation_matrix,(cols,rows))
        previous_mask_img_shifted =  cv2.warpAffine(sum_mask_img,transformation_matrix,(cols,rows))
        
        #Summation
        current_sum_mask_img = previous_mask_img_shifted + current_curr_mask_img
        current_sum_img = previous_sum_img_shifted + current_rescaled_img
        current_roi = [previous_roi[0]+shift_pixels_y_direction,previous_roi[1]+shift_pixels_y_direction, previous_roi[2]+shift_pixels_x_direction,previous_roi[3]+shift_pixels_x_direction]

    integral_img = np.divide(current_sum_img, current_sum_mask_img, out=np.zeros_like(current_sum_img), where=current_sum_mask_img!=0)
    #print("shifted Roi Coordinate", min(result[0]),max(result[0])+1,min(result[1]),max(result[1])+1)
    cropped_img = integral_img[int(current_roi[0]):int(current_roi[1]), int(current_roi[2]):int(current_roi[3])]
    variance = np.var(cropped_img)
    return variance

import nlopt
from numpy import *
FirstParameter = [0.0, 0.0]
Optimization_Params.append(FirstParameter)

current_img_number = 0
windowsize =  1000

virtual_camera_perspective = None
roi_camera_perspective = 0
no_eval = 5000 # define evaluations

current_imagelist.append(imagelist[0])

for i in range(1,len(imagelist)):
    current_img_number = i
    sum_img, sum_mask_img, previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize,radon_filtering=False)
    integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
    cv2.imwrite(os.path.join(output_folder, 'integral_' +str(i-1) + '.png'),np.uint8(integral_img))
    cropped_img = integral_img[int(previous_roi[0]):int(previous_roi[1]), int(previous_roi[2]):int(previous_roi[3])]
    cv2.imwrite(os.path.join(output_folder, 'cropped_' + str(i-1) + '.png'),np.uint8(cropped_img))
    radon_sum_img, radon_sum_mask_img, radon_previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize,radon_filtering=True)
    radon_integral_img = np.divide(radon_sum_img, radon_sum_mask_img, out=np.zeros_like(sum_img), where=radon_sum_mask_img!=0)
    radon_single = radon_integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    cv2.imwrite(os.path.join(output_folder, 'radon_filtered_'+ str(i-1) + '.png'),np.uint8(radon_single))


    current_imagelist.append(imagelist[i])
    current_image = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)

    opt = nlopt.opt(nlopt.GN_DIRECT, 2) #nlopt.LN_SBPLX
    lb = [0.0, 0.0]
    ub = [360.0, 3.0]
    opt.set_lower_bounds(lb)
    opt.set_upper_bounds(ub)
    opt.set_max_objective(nl_opt_perim_calvar)
    opt.set_maxeval(no_eval)
    x0 = [0.0,0.5]
    xopt = opt.optimize(x0)

    minf = opt.last_optimum_value()
    print('optimum at ', xopt)
    print('minimum value = ', minf)
    print('result code = ', opt.last_optimize_result())
    print('nevals = ', opt.get_numevals())
    print('initial step =', opt.get_initial_step(x0))

    Optimization_Params.append(xopt)
    with open(os.path.join(output_folder,'optim_param.txt'), 'a') as f:
        f.write('optimization_list'+ ' ' +(str(Optimization_Params)))
        f.write('\n')
current_img_number = len(imagelist)
sum_img, sum_mask_img, previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize,radon_filtering=False)
integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
cv2.imwrite(os.path.join(output_folder, 'integral' + str(current_img_number-1) + '.png'),np.uint8(integral_img))
cropped_img = integral_img[int(previous_roi[0]):int(previous_roi[1]), int(previous_roi[2]):int(previous_roi[3])]
cv2.imwrite(os.path.join(output_folder, 'cropped' + str(current_img_number-1) + '.png'),np.uint8(cropped_img))
radon_sum_img, radon_sum_mask_img, radon_previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize,radon_filtering=True)
radon_integral_img = np.divide(radon_sum_img, radon_sum_mask_img, out=np.zeros_like(sum_img), where=radon_sum_mask_img!=0)
radon_single = radon_integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
cv2.imwrite(os.path.join(output_folder, 'radon_filtered_'+ str(current_img_number-1) + '.png'),np.uint8(radon_single))