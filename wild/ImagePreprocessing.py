'''
    Copyright (C) 2017 Luca Surace - University of Calabria, Plymouth University
    
    This file is part of Deemotions. Deemotions is an Emotion Recognition System
    based on Deep Learning method.

    Deemotions is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Deemotions is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Deemotions.  If not, see <http://www.gnu.org/licenses/>.
    
    -----------------------------------------------------------------------

    This code crops the faces in the given image and then scales it
    to match the CNN input size.

'''

import sys, glob, os
import cv2
import numpy as np

from PIL import Image, ImageDraw
from GoogleDetector import GoogleDetector


class ImagePreprocessing:
    """ 
        It crops and scales images
    """

    def scale_images(self, input_path, NEW_SIZE, image_path):
        image_path_no_ext = image_path[0:len(image_path) - 4];
        for file in glob.glob(input_path+"*.jpg"):
            if ((image_path_no_ext+"_face" in file) and (file[file.find(image_path_no_ext)-1] == '/')):
                fileTokens = file.split("/")
                fileName = fileTokens[len(fileTokens)-1]
                img = cv2.imread(file)
                high = img.shape[0]
                width = img.shape[1]
                # computes scaling factor
                scaling_factor_y = float(NEW_SIZE / high)
                scaling_factor_x = float(NEW_SIZE / width)
                # scales the image
                res = cv2.resize(img, None, fx=scaling_factor_x, fy=scaling_factor_y, interpolation=cv2.INTER_CUBIC)
                if not os.path.exists("Scaled/"): os.makedirs("Scaled")
                cv2.imwrite("Scaled/" + fileName, res)

    def crop_faces(self, file_name, image, faces):
        """Crop faces, then saves each detected face into a separate file.

        Args:
          image: a file containing the image with the faces.
          faces: a list of faces found in the file. This should be in the format
              returned by the Vision API.
        """
        img = np.asarray(Image.open(image))
        img_length = img.shape[1]
        img_high = img.shape[0]
        count = 0

        for face in faces:
            box = [(bound.x_coordinate, bound.y_coordinate)
                   for bound in face.bounds.vertices]

            x0 = box[0][0]
            y0 = box[0][1]
            x1 = box[1][0]
            y1 = box[1][1]
            x2 = box[2][0]
            y2 = box[2][1]
            x3 = box[3][0]
            y3 = box[3][1]
            top_left_x = x0
            top_left_y = y0
            length = x1 - x0
            high = y3 - y0

            if length != high:
                padding = np.abs(high - length)
                padding = float(padding)
                if (length > high):
                    y0 = y0 - (padding / 2)
                    y1 = y1 - (padding / 2)
                    y2 = y2 + (padding / 2)
                    y3 = y3 + (padding / 2)
                    top_left_y = y0
                    high = high + padding
                else:
                    x0 = x0 - (padding / 2)
                    x3 = x3 - (padding / 2)
                    x1 = x1 + (padding / 2)
                    x2 = x2 + (padding / 2)
                    top_left_x = x0
                    length = length + padding

                # shift if the window is outside the image
                # move left
                if (x1 > img_length and x2 > img_length):
                    gap = x1 - img_length
                    x0 = x0 - gap
                    x3 = x3 - gap
                    x1 = x1 - gap
                    x2 = x2 - gap
                    top_left_x = top_left_x - gap
                # move down
                if (y0 < 0 and y1 < 0):
                    print "caso 2"
                    top_left_y = top_left_y + np.abs(y0)
                # move right
                if (x0 < 0 and x3 < 0):
                    gap = np.abs(x0)
                    x0 = x0 + gap
                    x3 = x3 + gap
                    x1 = x1 + gap
                    x2 = x2 + gap
                    top_left_x = top_left_x + gap
                # move left
                if (y2 > img_high and y3 > img_high):
                    top_left_y = top_left_y - (y2 - img_high)

            top_left_x = int(top_left_x)
            length = int(length)
            top_left_y = int(top_left_y)
            high = int(high)
            cropped = img[top_left_y:top_left_y + high, top_left_x:top_left_x + length]
            cropped = Image.fromarray(cropped)
            fileNoExtension = file_name[0:len(file_name) - 4];
            if not os.path.exists("Faces/"): os.makedirs("Faces")
            cropped.save("Faces/" + fileNoExtension + "_face_" + str(count) + ".jpg")
            count += 1
