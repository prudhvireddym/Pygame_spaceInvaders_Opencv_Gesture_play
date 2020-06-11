# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 20:40:26 2020

@author: prudh
"""

import numpy as np
import cv2
import pickle

import pygame
import random
import math
from pygame import mixer


##########################################################
width = 640
height = 480
threshold = 0.65
##########################################################


cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)


pickel_in = open("model_trained_rps2.p","rb")
model = pickle.load(pickel_in)

def preprocessing(img):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Convert image to grey - sets the depth to 0
    img = cv2.equalizeHist(img) #Equalize the light in the image
    img = img/255
    return img


# Initializing pygame
pygame.init()

# initializing the screen
screen = pygame.display.set_mode((800, 600))

# Titile & Icon
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("alien.png")
pygame.display.set_icon(icon)

# score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 45)

textX = 300
textY = 20

game_over = pygame.font.Font('freesansbold.ttf', 65)


def display_font(x, y):
    score = font.render("Score:" + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def display_gameover():
    over = game_over.render("Game Over", True, (255, 255, 255))
    screen.blit(over, (250, 280))


# Background
background = pygame.image.load("background.png")

# Background sound
# mixer.music.load("background.wav")
# mixer.music.play(-1)

# player
playerimg = pygame.image.load("space-invaders.png")
playerimg = pygame.transform.scale(playerimg, (45, 45))

playerX = 350
playerY = 500
playerX_change = 0


def player(x, y):
    screen.blit(playerimg, (x, y))


# Enemy
enemyimg = []
enemyimgT = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []

for i in range(0, 6):
    enemyimg.append(pygame.image.load("alien.png"))
    enemyimgT.append(pygame.transform.scale(enemyimg[i], (45, 45)))
    enemyX.append(random.randint(0, 755))
    enemyY.append(random.randint(50, 200))
    enemyX_change.append(4)
    enemyY_change.append(45)


def enemy(x, y, i):
    screen.blit(enemyimgT[i], (x, y))


# Bullet
bulletimg = pygame.image.load("bullet.png")
bulletimg = pygame.transform.scale(bulletimg, (35, 35))

bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"


def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletimg, (x + 5, y + 16))


def Collusion(aX, aY, bX, bY):
    distance = math.sqrt(math.pow((aX - bX), 2) + math.pow((aY - bY), 2))
    if distance <= 25:
        return True
    else:
        return False



while True:

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    success,imgOriginal = cap.read()
    img = np.asarray(imgOriginal)
    img = cv2.resize(img,(32,32))
    img = preprocessing(img)
    cv2.imshow("Preprocesses Imgs",img)
    img = img.reshape(1,32,32,1)
    
    #Prediction
    classIndex = int(model.predict_classes(img))
    print(classIndex)
    predictions = model.predict(img)
    probValue = np.amax(predictions)
    print(classIndex,probValue)


    if probValue> threshold:
        if(classIndex==0):
            playerX_change = -8
            action = "Left"

        elif(classIndex==1):
            playerX_change = 8
            action = "Right"

        elif(classIndex==2):
            if bullet_state is "ready":
                bulletX = playerX
                fire_bullet(bulletX, bulletY)
                mixer.music.load("laser.wav")
                mixer.music.play()
                action = "Fire"
            
        cv2.putText(imgOriginal,str(classIndex) + "   "+str(probValue)+" " +str(action) ,
                    (50,50),cv2.FONT_HERSHEY_COMPLEX,
                    1,(0,0,255),1)


    '''for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5

            if event.key == pygame.K_RIGHT:
                playerX_change = 5

            if event.key == pygame.K_SPACE:
                if bullet_state is "ready":
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
                    mixer.music.load("laser.wav")
                    mixer.music.play()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0'''

    # Player Boundry & Movement

    if playerX <= 0:
        playerX = 0
    elif playerX >= 750:
        playerX = 750

    playerX += playerX_change

    # Bullet Movement
    if bullet_state is "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    if bulletY <= 0:
        bullet_state = "ready"
        bulletY = 480

    # Enemy Boundary & Movement

    for i in range(0, 6):
        if enemyY[i] >= 480:
            for j in range(0, 6):
                enemyY[j] = 2000
            display_gameover()
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 3.5
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 750:
            enemyX_change[i] = -3.5
            enemyY[i] += enemyY_change[0]

        colide = Collusion(enemyX[i], enemyY[i], bulletX, bulletY)

        enemy(enemyX[i], enemyY[i], i)

        if colide:
            bullet_state = "ready"
            bulletY = 480
            enemyX[i] = random.randint(0, 755)
            enemyY[i] = random.randint(50, 200)
            score_value += 1
            mixer.music.load("explosion.wav")
            mixer.music.play()

    display_font(textX, textY)
    player(playerX, playerY)
    pygame.display.update()

    cv2.imshow("Original Image",imgOriginal)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
