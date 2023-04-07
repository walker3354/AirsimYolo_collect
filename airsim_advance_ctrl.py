import sys
import cv2
import time
import airsim
import pygame
import numpy as np 
import pprint


counter = 0
pygame.init()#初始化pygame
screen = pygame.display.set_mode((854,480))#顯示攝影機
pygame.display.set_caption('press c to collect element')
screen.fill((0, 0, 0))
    
AirSim_client = airsim.MultirotorClient()#宣告airsim物件
AirSim_client.confirmConnection()
AirSim_client.enableApiControl(True)#啟用API控制
AirSim_client.armDisarm(True)


AirSim_client.takeoffAsync().join
time.sleep(2)
image_types = {
            "scene": airsim.ImageType.Scene,
            "depth": airsim.ImageType.DepthVis,
            "seg": airsim.ImageType.Segmentation,
            "normals": airsim.ImageType.SurfaceNormals,
            "segmentation": airsim.ImageType.Segmentation,
            "disparity": airsim.ImageType.DisparityNormalized
        }
base_rate = 0.2
base_throttle = 0.55
speedup_ratio = 4.0
speedup_flag = False
change_time = 0.0
enable_change = True
control_iteration = False


while True:
    pitch_rate = 0.0
    yaw_rate = 0.0
    roll_rate = 0.0
    throttle = base_throttle
    control_iteration = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    scan_wrapper = pygame.key.get_pressed()


    if scan_wrapper[pygame.K_SPACE]:
        scale_ratio = speedup_ratio
    else:
        scale_ratio = speedup_ratio / speedup_ratio
    

    if time.time() - change_time > 2:
        enable_change = True
    

    if scan_wrapper[pygame.K_LCTRL] and scan_wrapper[pygame.K_c] and enable_change:
        enable_change = False
        change_time = time.time()


    if scan_wrapper[pygame.K_a] or scan_wrapper[pygame.K_d]:
        control_iteration = True
        yaw_rate = (scan_wrapper[pygame.K_a] - scan_wrapper[pygame.K_d]) * scale_ratio * base_rate

    if scan_wrapper[pygame.K_UP] or scan_wrapper[pygame.K_DOWN]:
        control_iteration = True
        pitch_rate = (scan_wrapper[pygame.K_UP] - scan_wrapper[pygame.K_DOWN]) * scale_ratio * base_rate

    if scan_wrapper[pygame.K_LEFT] or scan_wrapper[pygame.K_RIGHT]:
        control_iteration = True
        roll_rate = -(scan_wrapper[pygame.K_LEFT] - scan_wrapper[pygame.K_RIGHT]) * scale_ratio * base_rate

    if scan_wrapper[pygame.K_w] or scan_wrapper[pygame.K_s]:
        control_iteration = True
        throttle = base_throttle + (scan_wrapper[pygame.K_w] - scan_wrapper[pygame.K_s]) * scale_ratio * base_rate
    
    if pitch_rate > 1.0:
        pitch_rate = 1.0
    elif pitch_rate < -1.0:
        pitch_rate = -1.0

    if yaw_rate > 1.0:
        yaw_rate = 1.0
    elif yaw_rate < -1.0:
        yaw_rate = -1.0

    if roll_rate > 1.0:
        roll_rate = 1.0
    elif roll_rate < -1.0:
        roll_rate = -1.0

    if throttle > 1.0:
        throttle = 1.0
    elif throttle < 0.0:
        throttle = 0.0

    if control_iteration:
        AirSim_client.moveByRollPitchYawrateThrottleAsync(pitch=pitch_rate, roll=roll_rate, yaw_rate=yaw_rate,
                                                          throttle=throttle, duration=0.05)
    else:
        AirSim_client.hoverAsync()
    
    temp_image = AirSim_client.simGetImage('0', image_types["scene"])
    AirSim_client.simAddDetectionFilterMeshName("0", image_types["scene"], "Ball*")
    if temp_image is None:
        print("Warning: Failed to read a frame!! ")
        pygame.quit()
    else:
        pass

    image = cv2.imdecode(airsim.string_to_uint8_array(temp_image), cv2.IMREAD_COLOR)
    cylinders = AirSim_client.simGetDetections("0", image_types["scene"])
    if cylinders:
        for cylinder in cylinders:
            cv2.imwrite('obj/visual'+str(counter)+'.png', image)
            s = pprint.pformat(cylinder)
            print("Cylinder: %s" % s)
            cv2.rectangle(image,(int(cylinder.box2D.min.x_val),int(cylinder.box2D.min.y_val)),(int(cylinder.box2D.max.x_val),int(cylinder.box2D.max.y_val)),(255,0,0),2)
            cv2.putText(image, cylinder.name, (int(cylinder.box2D.min.x_val),int(cylinder.box2D.min.y_val - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12))
            x_center = (int(cylinder.box2D.min.x_val) + int(cylinder.box2D.max.x_val)) / (2 * 854)
            y_center = (int(cylinder.box2D.min.y_val) + int(cylinder.box2D.max.y_val)) / (2 * 480)
            width = (int(cylinder.box2D.max.x_val) - int(cylinder.box2D.min.x_val)) / 480
            height = (int(cylinder.box2D.max.y_val) - int(cylinder.box2D.min.y_val)) / 854
            f = open('obj/visual'+str(counter)+'.txt','a')
            f.write('0 '+str(x_center)+' '+str(y_center)+' '+str(width)+' '+str(height))
            counter = counter+1

    cv2.imwrite('obj/visual.png', image)
    screen_image = pygame.image.load('obj/visual.png')
    screen.blit(screen_image, (0, 0))
    pygame.display.flip()
    pygame.display.update()

    # press 'Esc' to quit
    if scan_wrapper[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()