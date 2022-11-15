Source Code and Data: Inverse Airborne Optical Sectioning
====================================================================
Supplementary Dataset for the article Inverse Airborne Optical Sectioning.

**Abstract:**
In this article we present Inverse Airborne Optical Sectioning (IAOS) – an optical analogy to In-verse Synthetic Aperture Radar (ISAR). Moving targets, such as walking people, that are heavily occluded by vegetation can be made visible and tracked with a stationary optical sensor (e.g., a hovering camera drone above forest). We introduce the principles of IAOS (i.e., inverse synthetic aperture imaging), explain how the signal of occluders can be further suppressed by filtering the Radon transform of the image integral, and present how targets’ motion parameters can be es-timated manually and automatically. Finally, we show that while tracking occluded targets in conventional aerial images is infeasible, it is efficiently possible in integral images that result from IAOS. 

**Authors:** Rakesh John Amala Arokia Nathan, Indrajit Kurmi and Oliver Bimber

# Content [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6966437.svg)](https://doi.org/10.5281/zenodo.6966437)

The data and code for evaluation is available open access at [Zenodo](https://doi.org/10.5281/zenodo.6966437). Further details can be found in the main article and supplementary material of our article.
The package contains the following zip files: `IAOS_Code`, `IAOS_Data`. 
This data is required to reproduce the results explained in the [Demo](#Demo) section (e.g., to compute figures 3,4,5 and supplementary videos 1,2,3).

## General Structure
We provide 2 main packages (`IAOS_Code.zip` and `IAOS_Data.zip`), which correspond to code and data utilized in our main article.


## IAOS_Code.zip
The zip packages contains the code to compute figures 3,4,5 and supplementary videos 1,2,3 of our article. Additionally we publish code to perform Automatic and Manual Motion Parameters Estimation for performing IAOS.

Folder `Paper_Results` contains two python scripts. 

The First script `IAOS_Manual_Parameter_Estimation.py` generates results for Figure 3 and 4, specifically Figure 3k, 3l by utilizing rectified images provided in folder `Figure3k` within `IAOS_Data.zip`, Figure 3n, 3o utilizing rectified images provided in folder `Figure3n`, Figure 3q, 3r utilizing rectified images provided in folder `Figure3q` and Figure 4l, 4m utilizing rectified images provided in folder `Figure4l`.

The second script `IAOS_Automatic_Tracking.py` generates results for Figure 5, specifically Figure 5b,5c and 5e, 5f by utilizing rectified images provided in folder `Figure5_LinearMotion/images` and `Figure5_NonLinearMotion/images`. It automatically estimates the correct motion parameters of the target using variance as focussing metric as expalained within the article. It first generates integral images and radon filtered integral images using the estimated parameters and utizes the matlab script to track the target within them to generate Figures 5c anndd 5f. Similarly the matlab script also tries to track the target within the single images provided in folder `Figure5_LinearMotion/images` and `Figure5_NonLinearMotion/images` to generate Figures 5b and 5f.

Folder `Automatic_Estimation` contains python script `IAOS_Automatic_Estimation.py` contains code for performing automatic estimation of motion paraameters for the specified target. 

Folder `Manual_Estimation` contains python script `IAOS_Manual_Estimation.py` contains code demonstrating a GUI for Manual estimation of motion parameters for the specified scene.
Linear motion parameters i.e angle and speed can be adjusted using GUI to perform IAOS. The resultant IAOS integral image is displayed within the GUI.


## IAOS_Data.zip
The zip packages contains the data of flights used to compute figures 3,4,5 and supplementary videos 1,2,3 of our article. 


# System Requirements

## Hardware 
The evaluation script requires only a standard computer with enough RAM. We tested on a computer with 16 GB RAM and 4 CPU cores. 

## Software 
We ran and tested our algorithms on *Windows 10* operating system running *Matlab R2019b* and *Python 3.7.9*. However, our evaluation scripts and the IAOS algorithm should also work on Linux or Mac OS operating systems. 

The following software is required:
* Mathworks Matlab with the Computer Vision Toolbox.
* Python (>3) and some common packages (numpy, pandas, opencv2, ...)

# Installation
* Download the [Zenodo packages](https://doi.org/10.5281/zenodo.6966437) and extract them.
* Install Mathworks Matlab and the Computer Vision Toolbox. 
* Install Python (>3) and the required packages (common data science packages such as numpy, pandas, opencv2, ...). 
* Open Matlab and use command `matlabroot` within Matlab command window to retrieve the Matlab installation path.
* Open Command prompt and navigate to the returned Matlab installation path. 
* Change to the Python Engine support within Matlab by entering command `cd extern\engines\python`.
* Install Support for Python Within Matlab using Command `python3 setup.py install`.


# Demo
## Evaluation Script for Generating Figures 3k, 3l, 3n, 3o, 3q, 3r, 4l,4m 
Simply open folder `Paper_Results` within unzipped `IAOS_Code` folder and execute the python script `IAOS_Manual_Parameter_Estimation.py`.

## Evaluation Script for Generating Figures 5b, 5c, 5e, 5f 
Simply open folder `Paper_Results` within unzipped `IAOS_Code` folder and execute the python script `IAOS_Automatic_Tracking.py`. It would generate results within folders `Figure5_LinearMotion/results` and `Figure5_NonLinearMotion/results`. The generated videos  `integral_tracked_projected.mp4` and `single_tracked.mp4` are videos which are combined to generate Videos 2 and 3 of supplementary material. Last frames of each videos are used for generating Figures 5b, 5c, 5e, 5f.



# License:
* Data: Creative Commons Attribution 4.0 International
* Code: MIT License (license text below)
    
        Copyright 2020 Johannes Kepler University Linz

        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.