#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:34:32 2017

@author: cli
"""

import os
import cv2
import numpy as np
import pandas as pd
import scipy.io

ver = 180
gray=True
image_size=64

""" set the dirs to load views"""
car_path = os.path.join( 'data', 'cars')

car_files = map(lambda x: os.path.join(car_path, x), os.listdir(car_path) )
car_files = filter(lambda x: x.endswith('.mat'), car_files)

car_idx = map(lambda x: int(x.split('car_')[1].split('_mesh')[0]), car_files )
car_df = pd.DataFrame( {'idx': car_idx, 'path': car_files}).sort('idx')

car_files = car_df['path'].values


""" extract views"""

car_images = []
classes = []

n_cars = len(car_files)
for car_file in car_files:
    if not car_file.endswith('.mat'): continue
    car_mat = scipy.io.loadmat(car_file)
    car_ims = car_mat['im']
        
    if ver == 180:
        for idx,i in enumerate(range(5,-1,-1) + range(23,18,-1)):
            car_image = car_ims[:,:,:,i,3]
            car_image = cv2.resize(car_image, (image_size,image_size))
            if gray:
                car_image = cv2.cvtColor(car_image, cv2.COLOR_BGR2GRAY)
                car_image = np.repeat(car_image[:,:,None], 3, 2)
            car_image = car_image.transpose(2,0,1)
            car_image = car_image.astype(np.float32)/255.
            car_images.append( car_image )
            classes.append( idx ) 
          
np_car_images = np.stack(car_images)
np_classes    = np.array(classes)
          

""" save views"""

nr = 2; nc = 11; padding = 0

rN = nr*image_size + (nr-1)*padding
cN = nc*image_size + (nc-1)*padding
m  = np.zeros((rN,cN, 3))
extent=np.array([0,rN,0,cN])
xmin, xmax, ymin, ymax = extent

for i in range( np_car_images.shape[0] ):
    filename_prefix = os.path.join('data', 'cars_views' )
    if not os.path.exists(filename_prefix):
        os.makedirs(filename_prefix)
    img = np.squeeze(np_car_images[i,:,:,:]).transpose(1,2,0)    
    scipy.misc.imsave( filename_prefix + '/'+ str(i) + '.jpg', img)

    x = i/nc*image_size+padding
    y = i%nc*image_size+padding       
    m[x:x+image_size][:, y:y+image_size] = (img)               
               
               
scipy.misc.imsave( filename_prefix + '/full_views.jpg', m)
    
    
    
  