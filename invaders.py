from clientpy3 import run
from time import sleep
from math import pi, sqrt, atan
from pyautogui import click, screenshot
from PIL import Image, ImageDraw
import pyautogui
user = 'a'
pw = 'a'
pyautogui.FAILSAFE = True
def dist(x1,y1,x2,y2):
    return sqrt((x2-x1)**2 + (y2-y1)**2)
def acc(rad, v):
    return run(user, pw, 'ACCELERATE ' + str(rad) + ' ' + str(v))
def brake():
    return run(user, pw, 'BRAKE')
def current_xy():
    s = run(user, pw, 'STATUS').split()
    return (float(s[1]), float(s[2]))
# current_xy() returns an array (x,y), which is the current location of the ship
#   in game coordinates (instead of pixels)
def angle(src_x, src_y, dest_x, dest_y):
    dest_y = 10000 - dest_y
    src_y = 10000 - src_y
    dx = dest_x - src_x
    dy = dest_y - src_y
    if dx == 0:
        if dy > 0:
            return 3*pi/2
        else:
            return pi/2
    elif dx > 0:
        if dy > 0:
            return 2*pi - atan(abs(dy/dx))
        else:
            return atan(abs(dy/dx))
    else:
        if dy > 0:
            return pi + atan(abs(dy/dx))
        else:
            return pi - atan(abs(dy/dx))
    # This computes the acceleration vector that is needed to get to a desired
    #   location (dest_x,dest_y), assuming zero initial velocity.
def get_coords():
    s = run(user, pw, 'STATUS').split()
    n = int(s[6])
    if n > 0:
        return (float(s[8]), float(s[9]), s[7])
    # get_coors() returns an array which consists of info on a nearby mine:
    #   (x_coord,y_coord,owner)
    
click(661, 745, duration = 0.2) # Clicks on the Chrome icon to go to the game
sleep(0.5) # Allows for a brief pause before taking the screenshot

box = screenshot(region=(405, 82, 943, 629)) # Takes a screenshot of the game
box.save('box.png') # saves the screenshot as 'box.png'
s = current_xy() # s is the current coordinate of the ship, in game coordinates
start_x = s[0] * 0.0943 # start_x is the current x position of the ship, in pixels
start_y = s[1] * 0.0629 # start_y is the current y position of the ship, in pixels
# print('start_x, start_y:', start_x, start_y)
mines = []
for y in range(629): # 629 is the height of the game window, in pixels
    for x in range(943): # 943 is the width of the game window, in pixels
        rgb = box.getpixel((x,y))
        if rgb[1] != 0 and rgb[0] == rgb[1] and dist(start_x, start_y, x, y) > 25:
            if mines == []:
                mines.append((x,y))
            else:
                for i in range(len(mines)):
                    if dist(mines[i][0], mines[i][1], x, y) <= 12:
                        break
                    if i == len(mines) - 1:
                        mines.append((x,y))
                    # This for loop does two things:
                    # 1.if the pixel is part of a mine, then it is recorded onto the image
                    # called "rep1"
                    # 2.if a group of pixels are within a radius of 25 pixels of each 
                    # other, then they are grouped together                    
fo = open('mines.txt', 'w')
fo.write(str(len(mines)) + '\n')        
rep1 = Image.new('RGB', (943,629), (255,255,255)) # Creates a blank white canvas of the size 943*629, which is the size of the game window
for y in range(629):
    for x in range(943):
        rgb = box.getpixel((x,y))
        if rgb[1] != 0 and rgb[0] == rgb[1] and dist(start_x, start_y, x, y) > 25:
            rep1.putpixel((x,y),(0,0,0)) # Drawing a mine in black pixels on the white canvas previously created

draw = ImageDraw.Draw(rep1)
def worm_test(src_x, src_y, dest_x, dest_y):
    slope = (dest_y - src_y) / (dest_x - src_x)
    for i in range(-3, 6):
        for x in range(int(src_x), int(dest_x)):             
            if box.getpixel((x, (int(src_y + (x-src_x)*slope)) + i)) == (102,0,102):
                return False
    draw.line([(src_x, src_y), (dest_x, dest_y)], (255,0,0))
    return True

s = current_xy()
current_x = s[0]
current_y = s[1]
mine_num = 1
v = 1

#draw.ellipse((mines[mine_num][0] - 2, mines[mine_num][1] - 2, mines[mine_num][0] + 2, mines[mine_num][1] + 2), (0,0,255), (0,0,255))
to_delete = []
for i in range(len(mines)-1):
    for j in range(i+1, len(mines)):
        if dist(mines[i][0], mines[i][1], mines[j][0], mines[j][1]) < 15:
            to_delete.append(j)
mines = [mines[j] for j in range(len(mines)) if j not in to_delete]
fo.write(str(len(mines)))
fo.close()
for mine in mines:
    draw.ellipse((mine[0], mine[1], mine[0]+3, mine[1]+3), (255,255,255), (255,0,0)) # Draws a red ellipse at the top-left corner of the mine circle
rep1.save('replica.png')
rep4 = rep1.copy()
draw = ImageDraw.Draw(rep4) # What is ImageDraw?
while True:
    if not worm_test(s[0] * 0.0943, s[1] * 0.0629, mines[mine_num][0], mines[mine_num][1]):
        mine_num = (mine_num + 1) % len(mines)
        continue
    mx = mines[mine_num][0] * 10000/943
    my = mines[mine_num][1] * 10000/629
    for i in range(80): # Where does 80 come from?
        s = current_xy()
        current_x = s[0]
        current_y = s[1]
        a = angle(current_x, current_y, mx, my)
        #print('x,y,a =', current_x * 0.0943, current_y * 0.0629, a/pi)
        d = dist(current_x, current_y, mx, my) # (mx,my) is the coordinate of the red ellipse we drew
        print(d)
        if d < 500:
            c = get_coords() # gets the coordinate of the mine
            print(c)
            if c != None:
                mx = c[0] # this changes mx to the x value of the actual mine
                my = c[1] # this changes my to the y value of the actual mine
                if c[2] == 'MFZ':
                    break # If the mine is already owned by us, then we exit the for loop to look for the next red ellipse
            brake()
            v = 0.2
        draw.ellipse((current_x * 0.0943-2, current_y * 0.0629-2, current_x * 0.0943+2, current_y * 0.0629+2), (0,255,0), (0,255,0))
        # The above draws the route of the ship in green dots 
        rep4.save('replica4.png')
        acc(a, v)    
        sleep(0.25)
    brake()
    v = 1
    mine_num = (mine_num + 1) % len(mines) # If you have gone through all the mines, go back to the first one and start over.
    print("mine_num = %d" % mine_num)