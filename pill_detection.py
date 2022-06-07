#기본 library
import pandas as pd
import numpy  as np

#shape에 필요한 library
import cv2
import sys
from matplotlib import pyplot as plt
import numpy as np

#color에 필요한 library
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000, delta_e_cmc

#imprint에 필요한 library
import easyocr
from pytesseract import pytesseract # pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

#webbrowsing에 필요한 library
import webbrowser

class pillDetection:
    def __init__(self, image_path):
        self.img_path = image_path

    def shapeDetection(self):
        # image를 array로 변환
        image = cv2.imread(self.img_path)
        
        # image를 원하는 size맞게 resize
        img_size = (425,640)
        image = cv2.resize(image, img_size)
        
        # edge detection
        image_edges = cv2.Canny(image, 200,200)
        
        # edge connection
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,15))
        closed = cv2.morphologyEx(image_edges, cv2.MORPH_CLOSE, kernel)
        
        # edge info 가져오기
        contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # self-variable로 지정해주기 (color에서 사용하기 때문에)
        self.contours = contours
        
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True), True)
            x = approx.ravel()[0]
            y = approx.ravel()[1] -8

            if len(approx) == 3:
                shape = 'triangle'             
            elif len(approx) == 4:
                X,Y,W,H = cv2.boundingRect(approx)
                isSquare = float(W/H)
                if isSquare >= 0.9 and isSquare <= 1.1:
                    shape = 'square'
                else:
                    shape = 'rectangle'
            elif len(approx) == 5:
                shape = 'pentagon'
            elif len(approx) == 6:
                shape = 'hexagon'
            elif len(approx) == 7:
                shape = 'heptagon'
            elif len(approx) == 8:
                shape = 'octagon'
            else:
                shape = 'circle'
        return shape
    
    def colorDetection(self):
        RGBDICT = {'beige':(245,245,220), 'black':(0,0,0), 'blue':(0,0,255), 'brown':(165,42,42), 'gold':(255,215,0), 
                   'green':(0,128,0), 'marron':(88,41,0), 'orange':(255,165,0), 'peach':(255,229,180), 'pink':(255,192,203), 
                   'purple':(128,0,128), 'red':(255,0,0), 'tan':(210,180,140), 'white':(255,255,255), 'yellow':(255,255,0)}
        
        # image 불러오기
        image = cv2.imread(self.img_path)
        img_size = (425,640)
        image = cv2.resize(image, img_size)
        
        # input 이미지의 RGB 찾기
        for contour in self.contours:
            if cv2.contourArea(contour) > 800:
                x,y,w,h = cv2.boundingRect(contour)
                BGR_color = np.array(cv2.mean(image[y:y+h, x:x+w])).astype(np.uint8)
        R = BGR_color[2]
        G = BGR_color[1]
        B = BGR_color[0]        
        
        delta_e_cmc_ = []
        for idx, color in enumerate(RGBDICT):
            input_img = sRGBColor(R/255, G/255, B/255)
            compa_img = sRGBColor(RGBDICT[color][0]/255, RGBDICT[color][1]/255, RGBDICT[color][2]/255)

            input_img_lab = convert_color(input_img, LabColor)
            compa_img_lab = convert_color(compa_img, LabColor)

            delta_e = delta_e_cmc(input_img_lab, compa_img_lab)
            delta_e_cmc_.append(delta_e)

        delta_e_cmc_map = dict(zip(RGBDICT.keys(), delta_e_cmc_))
        delta_e_cmc_map = dict(sorted(delta_e_cmc_map.items(), key=lambda item: item[1]))
        color = list(delta_e_cmc_map.keys())[0]
        return color
    
    def imprintDetection(self):
        text_list = []
        reader = easyocr.Reader(['en'])
        result = reader.readtext(self.img_path)
        for box,text,prob in result:
            text_list.append(text)
        imprint = ' '.join(text_list)
        return imprint
    
    def main(self):
        try:
            resShape = self.shapeDetection()
        except:
            resShape = ''
            
        try:
            resColor = self.colorDetection()
        except:
            resColor = ''
            
        try:
            resImprint = self.imprintDetection()
        except:
            resImprint = ''
    
    
    
        SHAPEDICT = {'circle':24,'rectangle':23,'triangle':3,'square':4,'pentagon':5,'hexagon':6,'heptagon':7,'octagon':8}
    
        COLORDICT = {'white':12,'beige':14,'black':73,'blue':1,'brown':2,'gold':4,'green':6,'green':6,
                     'maroon':44,'orange':7,'peach':74,'pink':8,'purple':9,'red':10,'tan':11,'yellow':13}    
            
        url = f"https://www.drugs.com/imprints.php?imprint={resImprint}&color={COLORDICT.get(resColor)}&shape={SHAPEDICT.get(resShape)}"
#         webbrowser.open(url, new=1)
        return url    