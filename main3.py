import cv2
import numpy as np
import pandas as pd
import csv
import xlsxwriter

import pdf2img_converter
import os
from pathlib import Path
import subprocess
from itertools import groupby
from collections import defaultdict

from functions import preprocessing2, horizontal_line, vertical_line, hough_line, box_creation, preprocessing
from functions import combine_nearby_keys, remove_nearby_values, remove_duplicate_points, line_intersection

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/nitins/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

def ocr(file,img_folder,size):

    o_folder,image=pdf2img_converter.img_converter(file,img_folder,size)
    image = np.array(image)

    ########################Denoise#############################

    cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/denoise.png',image)

    #####################PREPROCESSING######################
    
    # im1=preprocessing(image)
    im1=preprocessing2(image)

    #########Horizontal##########

    horizontal=horizontal_line(im1)
    
    ##############Vertical############

    vertical=vertical_line(im1)

    ###############################Hough_line##################################
    # ###  Combine horizontal and vertical lines in a new third image, with both having same weight.
    img_vh = cv2.addWeighted(vertical, 0.5, horizontal, 0.5, 0.0)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/combine.png',img_vh)

    image2=np.copy(image)
    cv2.Canny(horizontal,50,150)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/h_canny.png',horizontal)

    line_h,image_line=hough_line(horizontal,image2,'h')
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/hh_image.png',image_line)

    cv2.Canny(vertical,50,150)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/v_canny.png',vertical)

    line_v,image_line=hough_line(vertical,image2,'v')
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/vh_image.png',image_line)

    # print(len(line_h))
    # print(line_h)
    # print(len(line_h))
    # print(line_v)

    contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    margin=[]
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)
        # Don't plot small false positives that aren't text
        if (w >300 and h> 200):
                margin.append([x, y, x + w, y + h, w+h])
    points = [ l for l in sorted(margin,key = lambda x:(x[1]))]
    print(points)


    ############################POINTS############################################
    intersection_pt=[]
    for i in range(len(line_h)):
            for j in range(len(line_v)):
                intersection_pt.append(line_intersection(line_h[i],line_v[j]))
    intersection_pt = [i for i in intersection_pt if i is not None]
    intersection_set = set(intersection_pt) # removing repetition
    intersection_pt = list(intersection_set)
    
    print(intersection_pt)
    # print(len(intersection_pt))

    ###############################Preparation of points#############################
    # ###  Sorting the list of points -First by x axis , then by y-axis

    sorted_lines = [ l for l in sorted(intersection_pt,key = lambda x:(x[0],x[1]))] 
    # print(sorted_lines[0:100])
    # print(len(sorted_lines))


    ###  converting list of tuples into dictionary with the first value of a tuple as key and second value as value.
    
    result = {}
    for (key, value) in sorted_lines:
        result.setdefault(key, []).append(value) #setting the default value as list([])
    # print(result)
    
    ###  Combining the values of all the keys whose differeneces is less than 38 with one and another.(In ascending order)

    arranged_dict=combine_nearby_keys(result)
    for key in arranged_dict.keys():
        arranged_dict[key] = sorted(arranged_dict[key])
    # print(arranged_dict)

    ####  Removing all values in one key, which have difference less than 38. ###

    final_dict=remove_nearby_values(arranged_dict,33)
    # print(final_dict)
    #### Finding maximum distance between the two consecutive keys ###
    # keysList = list(final_dict.keys())
    # # print(keysList)

    # max_diff=0
    # for i in range(len(keysList)-1):
    #     diff=keysList[i+1]-keysList[i]
    #     if diff > max_diff:
    #         max_diff=diff
    # # print(max_diff)        

    ###  Converting dictionary back to list of tuples. ###
 
    cleaned_tuple_list = [(key, value) for key, values in final_dict.items() for value in values]
    # print(final_tuple_list)
    # print(len(cleaned_tuple_list))

    ### Removing duplicate tuples

    final_tuple_list=remove_duplicate_points(cleaned_tuple_list)
    # print(final_tuple_list)
    # print(final_tuple_list[0][0])
    # print(len(final_tuple_list))
    min_x = min(final_tuple_list, key=lambda tup: tup[0])[0]
    max_x = max(final_tuple_list, key=lambda tup: tup[0])[0]
    min_y = min(final_tuple_list, key=lambda tup: tup[1])[1]
    max_y = max(final_tuple_list, key=lambda tup: tup[1])[1]
    # print(min_x)
    # print(max_x)
    # print(min_y)
    # print(max_y)
 
    c2=np.copy(image)
    for i in range(len(final_tuple_list)):
        l=list(final_tuple_list[i])
        cv2.circle(c2, (int(l[0]),int(l[1])), radius=1, color=(0, 0, 255), thickness=3)
    cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/Upper_points.png',c2)

    ########################box_creation####################################
    
    rectangle_pts=box_creation(final_tuple_list)
    # print(rectangle_pts)
    # print(len(rectangle_pts))
    # print(rectangle_pts[0:3])
    # print(rectangle_pts[0][0])
    
    for i in range(len(rectangle_pts)):
        c2=np.copy(image)
        cv2.rectangle(c2,rectangle_pts[i][0],rectangle_pts[i][3],(0,0,255),3)
        cv2.imwrite('C:/Users/nitins/Documents/CRE_OCR2/image'+str(i)+'.png',c2)

    ### Creating a dictionary with keys as y-axis of x1 point and values of all points of box with same y-axis of X1 point ###
   
    result = {}

    for item in rectangle_pts:
        key = item[0][1]
        value = item       
        if key in result:
            result[key].append(value)
        else:
            result[key] = [value]
    # print(result)

    ### Sorting dictionary in ascending order of y-axis of x1 point. ###
       
    # sorted_dict = dict(sorted(result.items(), key=lambda x: x[0]))
    # print(sorted_dict)

    # c2=np.copy(image)
    # text_data = defaultdict(list)

    # for key , value in sorted_dict.items():
    #     for val in value:
    #         cropped = c2[val[0][1]-1:val[3][1]+1,val[0][0]+2:val[3][0]+1]  # 3 is best ...changing from 1
    #         cropped = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
    #         # kernel = np.ones((3,3),np.uint8)
           
    #         # cropped = cv2.morphologyEx(cropped, cv2.MORPH_CLOSE, kernel)  ##working for X
    #         # cropped = cv2.morphologyEx(cropped, cv2.MORPH_OPEN, kernel)
    #         text = ""
    #         text = pytesseract.image_to_string(cropped,lang = 'eng')
    #         # print(text)
    #         text_data[val]=text
    # # max(text_data)
    # print(text_data)
   


    ### Creating a dictionary with keys as y-axis of X1 point and value as number of boxes with same y-axis of X1 point ###  
    # len_key={}
    # for key , value in sorted_dict.items():
    #     len_key[key]=(len(value))
    # # print(len_key)
    # num_rows=len(len_key.keys())
    # # print(num_rows)
    # num_cols=max(len_key.values())
    # print(num_cols)

    ############################# Creating excel file#################################
    # workbook = xlsxwriter.Workbook('hello.xlsx')
    # worksheet = workbook.add_worksheet()
    # row=0
    # x_diff = max_x-min_x
    # x_avg_cell = int(x_diff/num_cols)
    # last_point_y=0
    # second_point_x=0
    # second_point_y=0
    # for key in text_data.keys():
    #     cell_in_row=len_key[key[0][1]]
    #     print(key[0][1])
    #     # print('No._of column',cell_in_row)

    #     ## Single Boxes in a row which starts with min_x. 

    #     if cell_in_row == 1 and key[0][0] == min_x:
    #         row=row+1
    #         next_row_col=0
    #         worksheet.merge_range(row,0,row,num_cols-1,text_data[key])
    #         last_point_y=key[3][1]
    #         print('(1)col_ends: ',num_cols-1)
    #         # print(row)
        
    #     ### First box out of more than one boxes in a row which start with min_x.
         
    #     count=0
    #     if cell_in_row > 1 and key[0][0] == min_x:
    #         row=row+1
    #         next_row_col=0
    #         next_row_col_start=0
    #         jump=0
    #         for key1 in text_data.keys():
    #             if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                 count=count+1
    #         new_col=int((key[1][0]-min_x)/x_avg_cell)
    #         if new_col<count:
    #             new_col=count
    #         if new_col==0:
    #             new_col=new_col+1
    #         last_point_y=key[3][1]
    #         second_point_y=key[1][1]
    #         second_point_x=key[1][0]
    #         if new_col-1==0:
    #             worksheet.write(row,0,text_data[key])
    #             nxt_col=new_col
    #         else:
    #             worksheet.merge_range(row,0,row,new_col-1,text_data[key])
    #             nxt_col=new_col
    #         print('y: ',last_point_y)
    #         print('(2)col_ends: ',new_col-1)
    #         # print(row)

    #     ### box out of other boxes in a row which do not starts with mix_x. These boxes starts from the starting height point of first box and  are smaller or equal to the first box height. 
    #     count=0
    #     if cell_in_row > 1 and key[0][0] > min_x and key[3][1] <= last_point_y and key[0][1] == second_point_y:
    #         ### Height of box is same as first box of row ###
    #         if key[3][1] == last_point_y and key[2][0] == second_point_x:
    #             second_point_x=key[1][0]
    #             for key1 in text_data.keys():
    #                 if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                     count=count+1
    #             new_col=int((key[1][0]-key[0][0])/x_avg_cell)
    #             if new_col<count:
    #                 new_col=count
    #             if new_col==0:
    #                 new_col=new_col+1
    #             # if next_row_col_start+nxt_col ==  next_row_col_start+nxt_col+new_col-1:
    #             if nxt_col ==  nxt_col+new_col-1:
    #                 worksheet.write(row,nxt_col,text_data[key])
    #                 print('(3a)col_end: ',next_row_col_start+nxt_col+new_col-1)
    #                 nxt_col=nxt_col+new_col
    #             else:
    #                 worksheet.merge_range(row,nxt_col,row,nxt_col+new_col-1,text_data[key])
    #                 # print('(3a)col_start: ',next_row_col_start+nxt_col)
    #                 print('(3a)col_end: ',next_row_col_start+nxt_col+new_col-1)
    #                 # print(row)
    #                 nxt_col=nxt_col+new_col
    #                 # jump=new_col+nxt_col
    #                 # nxt_col=new_col+nxt_col 
    #                 # print('y: ',last_point_y)
            
    #         ### Height of box is less than first box of row. ###

    #         if key[3][1] != last_point_y:
    #             for key1 in text_data.keys():
    #                 if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                     count=count+1
    #             new_col=int((key[1][0]-key[0][0])/x_avg_cell)
    #             if new_col<count:
    #                 new_col=count
    #             if new_col==0:
    #                 new_col=new_col+1
    #             if next_row_col_start+nxt_col ==  next_row_col_start+nxt_col+new_col-1:
    #                 worksheet.write(row,next_row_col_start+nxt_col,text_data[key])
    #                 print('(3b)col_end: ',next_row_col_start+nxt_col+new_col-1)
    #                 next_row_col_start=next_row_col_start+new_col    
    #             else:
    #                 worksheet.merge_range(row,next_row_col_start+nxt_col,row,next_row_col_start+nxt_col+new_col-1,text_data[key])
    #                 # print('(3b)col_start: ',next_row_col_start+nxt_col)
    #                 print('(3b)col_end: ',next_row_col_start+nxt_col+new_col-1)
    #                 # print(row)
    #                 next_row_col_start=next_row_col_start+new_col
    #                 # print('y: ',last_point_y)

    #     ### Second column of two column row having height same or less than first column.

    #     count=0
    #     if cell_in_row == 1 and key[0][0] > min_x and key[3][1] <= last_point_y:
    #         row=row+1
    #         for key1 in text_data.keys():
    #             if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                 count=count+1
    #         new_col=int((key[1][0]-key[0][0])/x_avg_cell)
    #         if new_col<count:
    #             new_col=count
    #         if nxt_col == nxt_col+new_col-1:
    #             worksheet.write(row,nxt_col,text_data[key])
    #         else:
    #             worksheet.merge_range(row,nxt_col,row,nxt_col+new_col-1,text_data[key])
    #         # print('(4)col_strat: ',nxt_col)
    #         print('(4)col_ends: ',nxt_col+new_col-1)
    #         # print(row)

    #     ### row having more than one column. Start with second column having same or less height than first column but start at higher height than the first column         
    #     if cell_in_row > 1 and key[0][0] > min_x and key[3][1] <= last_point_y and key[0][1] > second_point_y:
    #         count=0
    #         ###  column start adjustand from the end of first column row wise   ###
    #         if key[0][0] == second_point_x :
    #             row=row+1
    #             next_row_col=0
    #             for key1 in text_data.keys():
    #                 if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                     count=count+1
    #             new_col=int((key[1][0]-key[0][0])/x_avg_cell)
    #             if new_col<count:
    #                 new_col=count
    #             next_row_col=next_row_col+nxt_col
    #             if next_row_col == next_row_col+new_col-1:
    #                 worksheet.write(row,next_row_col,text_data[key]) 
    #                 print('(5)col_ends: ',next_row_col+new_col-1)
    #                 next_row_col=next_row_col+1
                    
    #             else:
    #                 worksheet.merge_range(row,next_row_col,row,next_row_col+new_col-1,text_data[key])
    #                 # print('(5)col_start: ',next_row_col)
    #                 print('(5)col_ends: ',next_row_col+new_col-1)
    #                 # print(row)
    #                 next_row_col=nxt_col+new_col
                
                

    #         if key[0][0] != second_point_x :
    #             # print('yes')
    #             for key1 in text_data.keys():
    #                 if key[2][0] <= key1[0][0] < key[3][0] and key1[1][0] <= key[3][0] and key[2][1] == key1[0][1]:
    #                     count=count+1
    #             new_col=int((key[1][0]-key[0][0])/x_avg_cell)
    #             if new_col<count:
    #                 new_col=count
    #             if new_col==0:
    #                 new_col=new_col+1
    #             if next_row_col == next_row_col+new_col-1:
    #                 worksheet.write(row,next_row_col,text_data[key])
    #                 print('(6)col_ends: ',next_row_col+new_col-1)
    #                 next_row_col=next_row_col+new_col
    #             else:
    #                 worksheet.merge_range(row,next_row_col,row,next_row_col+new_col-1,text_data[key])
    #                 # print('(6)col_start: ',next_row_col)
    #                 print('(6)col_ends: ',next_row_col+new_col-1)
    #                 # print(row)
    #                 next_row_col=next_row_col+new_col




    # workbook.close()
    
    
    

        
            




if __name__=='__main__':

    file = input("enter file path\n")
    img_folder = input('enter folder path to saved images\n')
    ocr(file,img_folder,350)
    
    # C:\Users\nitins\Documents\CRE_OCR2\001_Acord25.pdf
    # C:\Users\nitins\Documents\CRE_OCR2\psp1.pdf
    # C:\Users\nitins\Documents\CRE_OCR2\june.pdf