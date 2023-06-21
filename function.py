import uuid
import os

def uploading(doc):
    file_id = str(uuid.uuid4())
    root,ext = os.path.splitext(doc)
    filename='./Server_data'+str(file_id)+str(ext)
    return file_id, filename
    
import cv2
import numpy as np
from collections import defaultdict,OrderedDict

def preprocessing(image):    
    im1 = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    thresh,im1 = cv2.threshold(im1,150,250,cv2.THRESH_BINARY_INV)
        
    kernel = np.array([[1,1,1], 
                    [1, 5,1],
                    [1,1,1]])
    im1 = cv2.filter2D(im1, -1, kernel) # applying the sharpening kernel to the input image & displaying it.
        
    kernel = np.ones((4,4),np.uint8)  # initially is 5,5
    im1 = cv2.dilate(im1,kernel,iterations = 1)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/preprocess.png',im1)
    return im1

def preprocessing2(image):
    #thresholding the image to a binary image
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    thresh,img_bin = cv2.threshold(image,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    #inverting the image 
    img_bin = 255-img_bin
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/preprocess.png',img_bin)
    # kernel = np.array([[1,1,1], 
    #                 [1, 5,1],
    #                 [1,1,1]])
    # im1 = cv2.filter2D(img_bin, -1, kernel) # applying the sharpening kernel to the input image & displaying it.
    # kernel = np.ones((2,2),np.uint8)  # initially is 5,5
    # im1= cv2.erode(im1,kernel,iterations=1)
    # im1 = cv2.dilate(im1,kernel,iterations = 1)
    # cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/preprocess.png',im1)
    return img_bin
    # return im1

def horizontal_line(horizontal):

    # horizontal = np.copy(im1)
    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    # print(shape)
    horizontal_size = cols // 4
    # Create structure element for extracting horizontal lines through morphology operations
    # horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1)) # This is a kernel
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 3))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure,iterations=1)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/horizontal_erode.png',horizontal)

    horizontal = cv2.dilate(horizontal, horizontalStructure,iterations=1)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/horizontal_dilate.png',horizontal)
    return horizontal

def vertical_line(vertical):

    # vertical = np.copy(im1)
    rows = vertical.shape[0]
    vertical_size = rows // 12
    # Create structure element for extracting horizontal lines through morphology operations
    VerticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (3, vertical_size))
    # Apply morphology operations
    vertical = cv2.erode(vertical, VerticalStructure,iterations=1)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/vertical_erode.png',vertical)

    vertical = cv2.dilate(vertical, VerticalStructure,iterations=1)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/vertical_dilate.png',vertical)
    return vertical

# def hough_line(edges,image,orientation):
def hough_line(edges,image,orientation):

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=120, maxLineGap=100)
    # print(lines)
    # print('\n')
    points=[]
    if lines is not None:
        lines = lines.tolist()
            
        for i in range(len(lines)):
            # implementation for cv2.HoughLinesP()
            pt1 = (lines[i][0][0],lines[i][0][1]) 
            points.append(pt1) 
            pt2 = (lines[i][0][2],lines[i][0][3])
            cv2.line(image, pt1, pt2, (0,0,255), 3)
            points.append(pt2)
        
        if orientation=='h':
            sorted_lines = [ l for l in sorted(lines,key = lambda x:x[0][1])]
            return sorted_lines,image
        elif orientation=='v':
            sorted_lines = [ l for l in sorted(lines,key = lambda x:x[0][0])] 
            return sorted_lines,image
        # return image,line,points

def hough(hv_image,image):
    rho, theta, thresh = 2, np.pi/180, 400
    lines = cv2.HoughLines(hv_image, rho, theta, thresh)

    for line in lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 3000*(-b))
            y1 = int(y0 + 3000*(a))
            x2 = int(x0 - 3000*(-b))
            y2 = int(y0 - 3000*(a))
            cv2.line(image,(x1,y1),(x2,y2),(0,255,0),10)
    return lines
    

def segment_by_angle_kmeans(lines, k=2):
    """Groups lines based on angle with k-means.

    Uses k-means on the coordinates of the angle on the unit circle 
    to segment `k` angles inside `lines`.
    """

    # Define criteria = (type, max_iter, epsilon)
    default_criteria_type = cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER
    criteria = default_criteria_type, 10, 1.0
    flags = cv2.KMEANS_RANDOM_CENTERS
    attempts = 10

    # returns angles in [0, pi] in radians
    angles = np.array([line[0][1] for line in lines])
    # multiply the angles by two and find coordinates of that angle
    pts = np.array([[np.cos(2*angle), np.sin(2*angle)]
                    for angle in angles], dtype=np.float32)

    # run kmeans on the coords
    labels, centers = cv2.kmeans(pts, k, None, criteria, attempts, flags)[1:]
    labels = labels.reshape(-1)  # transpose to row vec

    # segment lines based on their kmeans label
    segmented = defaultdict(list)
    for i, line in enumerate(lines):
        segmented[labels[i]].append(line)
    segmented = list(segmented.values())
    return segmented

def intersection(line1, line2):
    """Finds the intersection of two lines given in Hesse normal form.
    """
    rho1, theta1 = line1[0]
    rho2, theta2 = line2[0]
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])
    x0, y0 = np.linalg.solve(A, b)
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    return [[x0, y0]]

def segmented_intersections(lines):
    """Finds the intersections between groups of lines."""

    intersections = []
    for i, group in enumerate(lines[:-1]):
        for next_group in lines[i+1:]:
            for line1 in group:
                for line2 in next_group:
                    intersections.append(intersection(line1, line2)) 

    return intersections

def combine_nearby_keys(dictionary):
        new_dict = {}
        for key in dictionary:
            updated = False
            for new_key in new_dict:
                if abs(new_key - key) <= 50:
                    new_dict[new_key].extend(dictionary[key])
                    updated = True
                    break
            if not updated:
                new_dict[key] = dictionary[key]
        return new_dict

def remove_nearby_values(dictionary, min_difference):
        new_dict = {}
        for key in dictionary:
            values = dictionary[key]
            if key not in new_dict:
                new_dict[key] = []
            for value in values:
                if not new_dict[key] or abs(value - new_dict[key][-1]) >= min_difference:
                    new_dict[key].append(value)
        return new_dict    

def remove_duplicate_points(points_tuple):
    temp = set()
    return [pt for pt in points_tuple if not(tuple(pt) in temp or temp.add(tuple(pt)))]

def line_intersection(line1,line2):
    overlapping_distance = 12
    x1,y1 = line1[0][0],line1[0][1]
    x2,y2 = line1[0][2],line1[0][3]
    x3,y3 = line2[0][0],line2[0][1]
    x4,y4 = line2[0][2],line2[0][3]
    try:        


        x = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/\
            ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
        y = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/\
            ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))#Formula to find interection point of two straight line 
        if((x>= min(x1-overlapping_distance,x2-overlapping_distance) and x<= max(x1+overlapping_distance,x2+overlapping_distance))\
            and (y>= min(y1-overlapping_distance,y2-overlapping_distance) and y<= max(y1+overlapping_distance,y2+overlapping_distance)) \
            and (x>= min(x3-overlapping_distance,x4-overlapping_distance) and x<= max(x3+overlapping_distance,x4+overlapping_distance))\
            and (y>= min(y3-overlapping_distance,y4-overlapping_distance) and y<= max(y3+overlapping_distance,y4+overlapping_distance))):

            return (int(x),int(y))

    except ZeroDivisionError:
        return 
    

def box_creation(final_tuple_list):
    rectangle_pts=[]
    pt4=None
    for i in range(len(final_tuple_list)-1):
        pt1=final_tuple_list[i]
        # print('pt1: ',pt1)
        i=0
        for down in range(i+1,len(final_tuple_list)-1):
            pt3=None  
            j=0    
            if pt1[0] == final_tuple_list[down][0] and 500 > abs(int(pt1[1])-int(final_tuple_list[down][1])) > 25:
            # if i<3 and  pt1[0] == final_tuple_list[down][0] and abs(int(pt1[1])-int(final_tuple_list[down][1])) > 25:
                pt3=final_tuple_list[down]
                i=i+1
                # print('pt3: ',pt3)
                for up in range(len(final_tuple_list)):
                    # print("fail pt2")
                    pt2=None
                    # if  j<3 and pt1[1] == final_tuple_list[up][1] and int(final_tuple_list[up][0]-int(pt1[0])) > 25:
                    if  pt1[1] == final_tuple_list[up][1] and int(final_tuple_list[up][0]-int(pt1[0])) > 25:
                        pt2=final_tuple_list[up]
                        j=j+1
                        # print('pt2: ',pt2)
                        for dwn_nxt in range(up+1,len(final_tuple_list)):
                            pt4=None
                            if pt3[1] == final_tuple_list[dwn_nxt][1] and pt2[0] == final_tuple_list[dwn_nxt][0]:
                                pt4=final_tuple_list[dwn_nxt]
                                # print('pt4: ',pt4)
                                rectangle_pts.append((pt1,pt2,pt3,pt4))
                            if pt4:
                                break
                   
                    if not pt4:
                        continue        
                    if pt2:
                        break
            if not pt4:
                continue       
            if pt3:
                break
    return rectangle_pts



    




