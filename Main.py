import face_recognition
import cv2
import numpy as np
import logging
from datetime import datetime
import os
import time
try:
    os.mkdir("LogFiles/")
except :
    pass
format = "%(asctime)s: %(message)s"
logname =  "./LogFiles/Log_"+str(datetime.now().month) +"_"+ str(datetime.now().day)+"_"+ str(datetime.now().hour)+"_"+ str(datetime.now().minute)+".log"
logging.basicConfig(filename=logname,format=format, level=logging.DEBUG,datefmt="%H:%M:%S")
class Console():
    def Log(*arg):
        logging.info("INFO ",arg)
        print(arg)
    def Warning(*arg):
        logging.warning("WARNING ",arg)
        print(arg)
    def error(*arg):
        logging.error("ERROR ",arg)
        print(arg)

class DataBase():
    Face_encodings = []
    Face_names = []

class DataBase_Handler():
    def New_entry(Name,Face_path):
        image = face_recognition.load_image_file(Face_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        DataBase.Face_names.append(Name)
        DataBase.Face_encodings.append(face_encoding)
    def Delete_entry(Name):
        pass

    
    
class Nhan_dang():
    def __init__(self):
        print("Starting")
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.Running = True
        DataBase_Handler.New_entry("Dummy","./examples/obama.jpg")
        self.Bat_dau()
        
    def Bat_dau(self):
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        count = 0
        frame_count = 0
        start_cooldown = 0.0f
        while self.Running:
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # BGR -> RGB
            rgb_small_frame = small_frame[:, :, ::-1]

           
            if process_this_frame:
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                if not frame_count == 0 :
                    frame_count = 0 if time.time() - start_cooldown > 3f else frame_count - 1
                
                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(DataBase.Face_encodings, face_encoding)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(DataBase.Face_encodings, face_encoding)
                    print("Dist",face_distances)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = DataBase.Face_names[best_match_index]
                    self.face_names.append(name)
                    Console.Log("Person: ",self.face_names,"Dist",face_distances)
                if self.face_encodings and frame_count == 0:
                        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                            top *= 4
                            right *= 4
                            bottom *= 4
                            left *= 4
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    
                            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    
                        # Display the resulting image
                        #cv2.imshow('Video', frame)
                        cv2.imwrite("Frame"+str(count)+".png",frame)
                        count +=1
                        frame_count = 50
                        start_cooldown = time.time()
            process_this_frame = not process_this_frame


            

        video_capture.release()
        cv2.destroyAllWindows()
Nhan_dang()