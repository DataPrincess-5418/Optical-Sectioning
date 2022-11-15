import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# not sure about what this glob.glob means and what should be the input image name
images = glob.glob('*.jpg')   # glob.glob will conduct blur search based on your string, but in this case, it can only give you the "left12.jpg" as the name is fixed
                              # I changed this to glob.glob('*.jpg'), now you can do it iteratively
                              # The glob module is a useful part of the Python standard library. glob (short for global) is used to return all file paths that match a specific pattern.
                              # all files in similar pattern of curretn directory


i = 0

for fname in images:
    print(fname)
    

print("#################################")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    a = "grayimg" + str(i) + ".png"
    cv2.imwrite(a, gray)
    print(fname)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
    print("Hello, are you there?")
    
    print(fname + " : " + str(ret))

    # If found, add object points, image points (after refining them)
    if ret == True:
        print("Found it!!")
        objpoints.append(objp)

        print(fname)
        print(ret)

        print("#################################")
        
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        aa = "outputs/img" + str(i) + ".png"
        cv2.imwrite(aa,img)   # originally cvs.imshow("img",img), this does not seem work here, so I save it
        # cv2.waitKey(500)
        i = i + 1
        
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

# cv2.destroyAllWindows()


# undistortion
img = cv2.imread('myleft.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# undistort: method 1 (easiest)
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png', dst)


# undistort: method 2, using remapping
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
dst = cv2.remap(img, mapx, mapy, cv.INTER_LINEAR)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png', dst)
