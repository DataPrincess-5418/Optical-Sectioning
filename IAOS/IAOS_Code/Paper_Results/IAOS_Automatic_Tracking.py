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

def nl_opt_perim_genSumim(current_img_number, windowsize,roi,Optimization_Params,output_folder, radon_filtering):

    global images_fps, drone_height, camera_fov, image_resolution,images

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

        #img = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)
        img = images[i]

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
    return current_sum_img, current_sum_mask_img, current_roi

######################  Non Linear  --- Per Image OPtimization #################################
def nl_opt_perim_calvar(x,grad):
    global virtual_camera_perspective, roi_camera_perspective
    global current_image, sum_img, sum_mask_img, previous_roi
    global radon_sum_img, radon_sum_mask_img, radon_previous_roi
    global images_fps, drone_height, camera_fov, image_resolution

    time_between_images = 1/images_fps
    person_movement_meters = x[1]*time_between_images

    person_movement_meters_x_direction = math.cos(math.radians(x[0])) * person_movement_meters
    person_movement_meters_y_direction = math.sin(math.radians(x[0])) * person_movement_meters

    imaged_area_length_meters = 2 * drone_height * math.tan(math.radians(camera_fov/2))
    pixels_per_meter = image_resolution/imaged_area_length_meters

    pixels_movement_x_direction = pixels_per_meter * person_movement_meters_x_direction 
    pixels_movement_y_direction = pixels_per_meter * person_movement_meters_y_direction 

    current_rescaled_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)
    current_curr_mask_img = np.zeros(shape=(3*image_resolution,3*image_resolution),dtype=float)


    current_rescaled_img[image_resolution:current_image.shape[0]+image_resolution,image_resolution:current_image.shape[1]+image_resolution] = current_image
    current_curr_mask_img[image_resolution:current_image.shape[0]+image_resolution,image_resolution:current_image.shape[1]+image_resolution] = 1.0
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
    cropped_img = integral_img[int(current_roi[0]):int(current_roi[1]), int(current_roi[2]):int(current_roi[3])]
    variance = np.var(cropped_img)
    return variance

def perform_optimization(current_roi):
    global imagelist, output_folder, current_image, Optimization_Params,images, Experiments
    global sum_img, sum_mask_img, previous_roi
    global radon_sum_img, radon_sum_mask_img, radon_previous_roi
    for i in range(1,len(imagelist)):
        current_img_number = i
        sum_img, sum_mask_img, previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize, roi=current_roi, Optimization_Params=Optimization_Params,output_folder=output_folder, radon_filtering=False)
        integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
        single = integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
        cv2.imwrite(os.path.join(output_folder, 'integral' , str(i-1) + '.png'),np.uint8(single))
        radon_sum_img, radon_sum_mask_img, radon_previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize, roi=current_roi, Optimization_Params=Optimization_Params,output_folder=output_folder, radon_filtering=True)
        radon_integral_img = np.divide(radon_sum_img, radon_sum_mask_img, out=np.zeros_like(sum_img), where=radon_sum_mask_img!=0)
        radon_single = radon_integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
        cv2.imwrite(os.path.join(output_folder, 'radon_filtered', str(i-1) + '.png'),np.uint8(radon_single))


        #current_image = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)
        current_image = images[i]

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

        Optimization_Params.append(xopt)
    current_img_number = len(imagelist)
    sum_img, sum_mask_img, previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize, roi=current_roi, Optimization_Params=Optimization_Params,output_folder=output_folder, radon_filtering=False)
    integral_img = np.divide(sum_img, sum_mask_img, out=np.zeros_like(sum_img), where=sum_mask_img!=0)
    single = integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    cv2.imwrite(os.path.join(output_folder, 'integral' , str(current_img_number-1) + '.png'),np.uint8(single))
    radon_sum_img, radon_sum_mask_img, radon_previous_roi = nl_opt_perim_genSumim(current_img_number, windowsize, roi=current_roi, Optimization_Params=Optimization_Params,output_folder=output_folder, radon_filtering=True)
    radon_integral_img = np.divide(radon_sum_img, radon_sum_mask_img, out=np.zeros_like(sum_img), where=radon_sum_mask_img!=0)
    radon_single = radon_integral_img[image_resolution:image_resolution+image_resolution,image_resolution:image_resolution+image_resolution]
    cv2.imwrite(os.path.join(output_folder, 'radon_filtered', str(current_img_number-1) + '.png'),np.uint8(radon_single))


def read_images_and_define_global_parameters():
    global images, imagelist, Optimization_Params, current_image
    images = []
    imagelist = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(images_dir,'*.png')))]
    #print(imagelist)  
    for i in range(len(imagelist)):
        img = cv2.imread(os.path.join(images_dir,imagelist[i]),cv2.IMREAD_GRAYSCALE)
        images.append(img)
    imagelist = sorted(imagelist, key=natural_sort_key)
    
    Optimization_Params = []
    FirstParameter = [0.0, 0.0]
    Optimization_Params.append(FirstParameter)
    current_image = None


drone_height = 35.0 #in meters
images_fps = 5 #frames/second
camera_fov = 36 #in degress
image_resolution = 512

virtual_camera_perspective = None
roi_camera_perspective = 0
no_eval = 3000

current_img_number = 0
windowsize =  1000

Experiments = [{"site_name":'Figure5_LinearMotion', "roi":[932, 952, 715,735]}, {"site_name":'Figure5_NonlinearMotion',"roi":[655, 685, 840,870]}]

for exp in range(len(Experiments)):
    images_dir = os.path.join(r'..\..\IAOS_Data', Experiments[exp]["site_name"], 'images')
    output_folder = os.path.join(r'..\..\IAOS_Data', Experiments[exp]["site_name"], 'results')

    read_images_and_define_global_parameters()
    curr_roi = Experiments[exp]["roi"]
    perform_optimization(curr_roi)
    video_written = eng.write_IAOS_videos(Experiments[exp]["site_name"])
    tracking_video_written = eng.tracking_motion(Experiments[exp]["site_name"],'single')
    tracking_video_written = eng.tracking_motion(Experiments[exp]["site_name"],'integral')
eng.quit()



