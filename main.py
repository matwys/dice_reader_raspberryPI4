import pywebio
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
from matplotlib.pyplot import imshow
import skimage.io as io
from pylab import *
import skimage
from skimage import data, filters, exposure, feature, morphology
from skimage.filters import rank
from skimage.util.dtype import convert
from skimage import img_as_float, img_as_ubyte
from skimage.color import rgb2hsv, hsv2rgb, rgb2gray
from skimage.filters.edges import convolve
from matplotlib import pylab as plt
import numpy as np
from numpy import array
from scipy import ndimage
from skimage import measure
from picamera import PiCamera
import picamera.array
import sqlite3 as sql
import pandas as pd

import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.cleanup()
# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 11 as an output, and define as servo1 as PWM pin
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz

# Start PWM running, with value of 0 (pulse off)
servo1.start(0)
camera = PiCamera()
camera.resolution = (300,300)

import warnings
warnings.simplefilter("ignore")

def show_gray(img):
    imshow(img, cmap='gray')

def servo180():
    #servo1.ChangeDutyCycle(11.5)
    #time.sleep(0.5)
    servo1.ChangeDutyCycle(7)
    time.sleep(0.25)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(11)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(11)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.5)
    servo1.ChangeDutyCycle(11)
    time.sleep(0.5)    
    servo1.ChangeDutyCycle(6)
    time.sleep(0.25)
    servo1.ChangeDutyCycle(0)
def photo():
    time.sleep(1.5)
    camera.capture('/home/pi/Desktop/projekt/image.jpg')


class Graph:
  
    def __init__(self, row, col, g):
        self.ROW = row
        self.COL = col
        self.graph = g
  
    # A function to check if a given cell 
    # (row, col) can be included in DFS
    def isSafe(self, i, j, visited):
        # row number is in range, column number
        # is in range and value is 1 
        # and not yet visited
        return (i >= 0 and i < self.ROW and 
                j >= 0 and j < self.COL and 
                not visited[i][j] and self.graph[i][j])
              
  
    # A utility function to do DFS for a 2D 
    # boolean matrix. It only considers
    # the 8 neighbours as adjacent vertices
    def DFS(self, i, j, visited):
  
        # These arrays are used to get row and 
        # column numbers of 8 neighbours 
        # of a given cell
        rowNbr = [-1, -1, -1,  0, 0,  1, 1, 1];
        colNbr = [-1,  0,  1, -1, 1, -1, 0, 1];

        # Mark this cell as visited
        visited[i][j] = True

        # Recur for all connected neighbours
        for k in range(8):
            if self.isSafe(i + rowNbr[k], j + colNbr[k], visited):
                self.DFS(i + rowNbr[k], j + colNbr[k], visited)


    # The main function that returns
    # count of islands in a given boolean
    # 2D matrix
    def countIslands(self):
        # Make a bool array to mark visited cells.
        # Initially all cells are unvisited
        visited = [[False for j in range(self.COL)]for i in range(self.ROW)]

        # Initialize count as 0 and traverse
        # through the all cells of
        # given matrix
        count = 0
        for i in range(self.ROW):
            for j in range(self.COL):
                # If a cell with value 1 is not visited yet,
                # then new island found
                if visited[i][j] == False and self.graph[i][j] == 1:
                    # Visit all cells in this island
                    # and increment island count
                    self.DFS(i, j, visited)
                    count += 1

        return count
    
def wynik():
    img1=img_as_float(io.imread('image.jpg'))
    img2 = np.zeros((len(img1), len(img1[0])))
    for i in range(len(img1)):
        for j in range(len(img1[0])):
            img2[i][j]=mean(img1[i][j])         
    img2**=0.35
    img2=skimage.feature.canny(img2, sigma=3)
    row = len(img2)
    col = len(img2[0])
    g = Graph(row, col, img2)
    wynik = g.countIslands()
    return wynik

class Database():
    def __init__(self):
        self.connection = sql.connect('project_DB.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute( """ CREATE TABLE IF NOT EXISTS wyniki(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            number INTEGER,
                            timestamp DATE DEFAULT(datetime('now','localtime'))
                            )
                            """)
        self.connection.commit()
        
    def insert_to_database(self,dice_roll):
        self.cursor.execute("""
                            INSERT INTO wyniki(number)
                            VALUES(?)
                            """,(dice_roll,))

        self.connection.commit()
    
    def select_database(self):
        self.cursor.execute("""
                            SELECT id,number,timestamp
                            FROM wyniki
                            """)
        df = pd.DataFrame(self.cursor.fetchall(),columns=['id','dice_roll','timestamp'])
        return df


def rool():
    x = Database()
    while(1):
        with use_scope('res', clear=True):
            #put_text(x.select_database())
            df = x.select_database()
            put_html(df.to_html(border=0))
            confirm = actions('rool?', ['rool'],help_text='Kliknij rool')
            servo180()
            time.sleep(0.2)
            servo180()
            #servo1.stop()
            #GPIO.cleanup()
            photo()
            x.insert_to_database(wynik())

if __name__ == '__main__':
    pywebio.start_server(rool, port=7777, host="192.168.1.4")