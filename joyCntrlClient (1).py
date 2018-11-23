#import subprocess
#subprocess.check_call(["python", '-m', 'pip', 'install', 'numpy'])
import pygame
import numpy as np
import socket
import os
import time
import sys



import paramiko

pygame.init()

display_width = 800
display_height = 600
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

logoImg = pygame.image.load(r'logo.png')
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Control Module')
clock = pygame.time.Clock()

gameDisplay.fill(white)
gameDisplay.blit(logoImg,(0,0))
pygame.draw.rect(gameDisplay, red, [100, 500, 100, 100])
pygame.draw.rect(gameDisplay, red, [300, 500, 100, 100])

myfont = pygame.font.SysFont("monospace", 15)
leftEngineLabel = myfont.render("Left Engine", 1, blue)
rightEngineLabel = myfont.render("Right Engine", 1, blue)


joysticks = []
for i in range(0, pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
    joysticks[-1].init()
    print(joysticks[-1].get_name())



while True:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='169.254.222.19',username='pi',password='raspberry')
    stdin,stdout,stderr=ssh_client.exec_command("sudo python3 server.py")
    ssh_client.close()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('169.254.222.19',5555))

    crashed = False
    # left engine bar based at (100,500)
    # right enggine bar based at (300,500)
    valaxis0 = 0
    valaxis1 = 0
    right_engine = valaxis1
    left_engine = valaxis1

    while not crashed:
        gameDisplay.fill(white)
        gameDisplay.blit(logoImg,(0,0))
        AR = 0
        AL = 0
        if valaxis1>0:
            if valaxis0>0:
                AL = 1-valaxis0
                AR = 1
            else:
                AL = 1
                AR = 1+valaxis0
        else:
            if valaxis0>0:
                AL = 1
                AR = 1-valaxis0
            else:
                AL = 1+valaxis0
                AR = 1
        AR = AR*valaxis1
        AL = AL*valaxis1
        PV = valaxis0
        PVS = 1-abs(valaxis1)*1
        AL = (1-PVS)*AL - PVS*PV
        AR = (1-PVS)*AR + PVS*PV

        gameDisplay.blit(leftEngineLabel, (100, 80))
        gameDisplay.blit(rightEngineLabel, (300, 80))
        pygame.draw.rect(gameDisplay, red, [100, 350, 50, int(200*AL)])
        pygame.draw.rect(gameDisplay, red, [300, 350, 50, int(200*AR)])
        #displaying engines PWM duty cycle
        leftEnginePWM = myfont.render("PWM:"+str("{0:.2f}".format(100*abs(AL)))+"%", 1, blue)
        rightEnginePWM = myfont.render("PWM:"+str("{0:.2f}".format(100*abs(AR)))+"%", 1, blue)
        gameDisplay.blit(leftEnginePWM, (100, 100))
        gameDisplay.blit(rightEnginePWM, (300, 100))
        #displaying engines direction
        leftEnginePWM = myfont.render("Direction:"+str(-np.sign(AL)), 1, blue)
        rightEnginePWM = myfont.render("Direction:"+str(-np.sign(AR)), 1, blue)
        gameDisplay.blit(leftEnginePWM, (100, 120))
        gameDisplay.blit(rightEnginePWM, (300, 120))

        clockR = int((-np.sign(AR))>0)
        clockL = int((-np.sign(AL))>0)
        counterclockR = int((-np.sign(AR))<0)
        counterclockL = int((-np.sign(AL))<0)
        pwmR = int(100*abs(AR))
        pwmL = int(100*abs(AL))

        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    valaxis0 = event.value
                if event.axis == 1:
                    valaxis1 = event.value
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7:
                    counterclockR = 2
                    counterclockL = 2
                    pwmR = 2
                    pwmL = 2
                    clockR = 2
                    clockL = 2
                    crashed = True
                    #kill the engine
                    #print(event)

        #sending data to the server on the raspberry
        send_bytes = str(clockR)+','+str(counterclockR)+','+str(pwmR)+','+str(clockL)+','+str(counterclockL)+','+str(pwmL)
        send_bytes = send_bytes.encode()
        send_bytes += b'\x00'*(256-len(send_bytes))
        client.sendall(send_bytes)
        pygame.display.update()
        clock.tick(30)

    #pygame.quit()
    client.close()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='169.254.222.19', username='pi', password='raspberry')
    stdin, stdout, stderr = ssh_client.exec_command("sudo killall python3")
    ssh_client.close()

quit()
