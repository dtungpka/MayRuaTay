import face_recognition
import cv2
import numpy as np
import logging
from datetime import datetime
import os
import time
import openpyxl
from fbchat import log, Client
from  fbchat.models import *
from threading import Thread
import RPi.GPIO as GPIO
from time import sleep
from collections import Counter
try:
    os.mkdir("LogFiles/")
except :
    pass
format = "%(asctime)s: %(message)s"
logname =  "./LogFiles/Log_"+str(datetime.now().month) +"_"+ str(datetime.now().day)+"_"+ str(datetime.now().hour)+"_"+ str(datetime.now().minute)+".log"
logging.basicConfig(filename=logname,format=format, level=logging.INFO,datefmt="%H:%M:%S")
class Console():
    def Log(*arg):
        msg = ""
        for inf in arg:
            msg += str(inf) + " "
        logging.info("INFO "+msg)
        print("INFO "+msg)
    def Warning(*arg):
        msg = ""
        for inf in arg:
            msg += str(inf) + " "
        logging.warning("WARNING "+msg)
        print("WARNING "+msg)
    def Error(*arg):
        msg = ""
        for inf in arg:
            msg += str(inf) + " "
        logging.error("ERROR "+msg)
        print("ERROR "+msg)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.output(13, False)
GPIO.output(11, False)
GPIO.output(15, False)
GPIO.output(16, False)
class Person:
    Ten = ""
    Lop = ""
    IMG = ""
    STT = ""
    Muon = ""
    def __init__(self,STT, Lop,IMG,Ten):
        self.STT = STT
        self.Ten = Ten
        self.Lop = Lop
        self.IMG = IMG

class DataBase:
    client = None
    Face_encodings = []
    Face_STTs = []
    Thong_tin_hs = []
    Co_mat = []
    FB_ready = False


class Time:
    def CheckTime(Realtime = True,*arg):
        tg_chot_s = [7,15]
        tg_het_chot_s = [11,30]
        H = time.localtime().tm_hour
        M = time.localtime().tm_min
        if not Realtime:
            H = arg[0]
            M = arg[1]
        return (False if (  H < tg_het_chot_s[0] and M < tg_het_chot_s[1] and H >= tg_chot_s[0] and M >= tg_chot_s[1]) else True)
    def GetTime():
        return [time.localtime().tm_hour,time.localtime().tm_min]
class Timer:
    def __init__(self):
        self.Start = time.time()
    def Check(self,End):
        if (self.Start + End < time.time()):
            self.Start = time.time()
        return (self.Start + End < time.time())
class Blink:
    def __init__(self,pin,delay,times):
        for i in range(times): 
            GPIO.output(pin,True)
            sleep(delay)
            GPIO.output(pin,False)
class Nhan_dang():
    def __init__(self):
        Console.Log("Starting")
        self.face_locations = []
        self.face_encodings = []
        self.face_STTs = []
        self.Running = True
        self.Bat_dau()
        
    def Bat_dau(self):
        timer1 = None
        timer2 = time.time()
        if DataBase.FB_ready == False:
            timer1 = Timer()
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        count = 0
        frame_count = 0
        start_cooldown = 0.0
        while self.Running:
          if timer1.Check(10) and DataBase.FB_ready == False:
              Blink(16,0.25,4)
          else:
            sleep(0.5)
          index_time = []
          GPIO.output(11,False)
          GPIO.output(15,False)
          GPIO.output(13,False)
          while True:
            
            Last_Per = ""
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            #small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # BGR -> RGB
            rgb_small_frame = small_frame[:, :, ::-1]

            if len(index_time) >= 3 or timer2.Check(2):
                break
            if process_this_frame:
                
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                if not frame_count == 0 :
                    frame_count = 0 if time.time() - start_cooldown > 3 else frame_count - 1
                
                self.face_STTs = []
                for face_encoding in self.face_encodings:
                    GPIO.output(11,True)
                    matches = face_recognition.compare_faces(DataBase.Face_encodings, face_encoding)
                    STT = "Unknown"
                    face_distances = face_recognition.face_distance(DataBase.Face_encodings, face_encoding)
                    print("Dist",face_distances)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        STT = DataBase.Face_STTs[best_match_index]
                        index_time.append(best_match_index)
                    if STT == "Unknown":
                        GPIO.output(15,True)
                        GPIO.output(13,False)
                    else:
                        GPIO.output(11,True)
                        GPIO.output(13,False)
                        self.face_STTs.append(STT)
                    Console.Log("ID hoc sinh: ",best_match_index,"Thong tin: ",STT)
                if self.face_encodings and frame_count == 0 and STT != Last_Per:
                        Last_Per = STT
                        for (top, right, bottom, left), STT in zip(self.face_locations, self.face_STTs):
                            top *= 4
                            right *= 4
                            bottom *= 4
                            left *= 4
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    
                            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, STT, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                   
                        #cv2.imshow('Video', frame)
                        cv2.imwrite("./Capture/"+STT+str(count)+".png",frame)
                        count +=1
                        frame_count = 50
                        start_cooldown = time.time()
            process_this_frame = not process_this_frame
            GPIO.output(11,False)
          if len(index_time) > 0:
            count_o = Counter(index_time).most_common()[0][0]
            print(count_o)
            GPIO.output(13,True)
            sleep(2)
            GPIO.output(13,False)
            if DataBase.Thong_tin_hs[count_o] not in DataBase.Co_mat:
               if Time.CheckTime() == False:
                   DataBase.Thong_tin_hs[count_o].Muon = str( Time.GetTime()[0])+ ":"+  str( Time.GetTime()[1])
               DataBase.Co_mat.append(DataBase.Thong_tin_hs[count_o])
               
               GPIO.output(13,True)
               sleep(1)
          else:
              GPIO.output(13,True)
              sleep(1)
              GPIO.output(13,False)
           

        video_capture.release()
        

class React(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
     GPIO.output(16, True)
     Console.Log("Nhan duoc tin nhan")
     if author_id != self.uid and  (str( message_object.text)[0] == "1" or message_object.text == "Toàn trường") :
        thong_bao = ""
        self.reactToMessage(message_object.uid, MessageReaction.HEART)
        DataBase.client.setTypingStatus(TypingStatus.TYPING , thread_id=thread_id, thread_type=thread_type)
        
        if message_object.text == "Toàn trường" and thread_type == ThreadType.GROUP :
            self.reactToMessage(message_object.uid, MessageReaction.HEART)
            Si_so_lop_co_mat = []
            Si_so_lop = []
            Si_so_truong = len(DataBase.Thong_tin_hs)
            Si_so_truong_dd = len(DataBase.Co_mat)
            print(DataBase.Co_mat)
            for Hs in DataBase.Thong_tin_hs:
               Si_so_lop.append(Hs.Lop)
            for Hs_co_mat in DataBase.Co_mat:
                Si_so_lop_co_mat.append(Hs_co_mat.Lop)
            cac_lop = [ [l, Si_so_lop.count(l)] for l in set(Si_so_lop)]
            cac_lop_da_dd = [ [l, Si_so_lop_co_mat.count(l)] for l in set(Si_so_lop_co_mat)]
            thong_bao = "Sĩ số toàn trường: "
            thong_bao += str(Si_so_truong_dd)+"/"+ str(Si_so_truong)+ "\n Theo từng lớp: \n"
            print(cac_lop)
            for Lop in cac_lop :
                for Lop_da_dd in cac_lop_da_dd:
                    if Lop_da_dd[0] == Lop[0]:
                        thong_bao += "Lớp "+ str(Lop[0])+": " +str(Lop_da_dd[1])+"/"+str(Lop[1])+"\n"
                        break
                    
            Console.Log(thong_bao)
            DataBase.client.setTypingStatus(TypingStatus.STOPPED , thread_id=thread_id, thread_type=thread_type)
            DataBase.client.send(Message(text=thong_bao), thread_id=thread_id, thread_type=thread_type)
        
        else:
          if str( message_object.text)[0] == "1":
           Si_so_lop =[]
           for Hs in DataBase.Thong_tin_hs:
              Si_so_lop.append(Hs.Lop)
           if  str( message_object.text) in Si_so_lop:
            # Sends the data to the inherited onMessage, so that we can still see when a message is recieved
            Lop = str( message_object.text)
            
            Lop_vang = []
            Lop_tong = []
            for Hs in DataBase.Thong_tin_hs:
                if Hs.Lop == Lop:
                    Lop_tong.append(Hs)
                    if Hs not in DataBase.Co_mat:
                        Lop_vang.append(Hs)
            thong_bao = "Sĩ số lớp "+Lop+": "+str(len(Lop_tong) - len(Lop_vang))+"/"+str(len(Lop_tong))+"\n"
            thong_bao += "Vắng:\n" if len(Lop_vang) > 0 else "Lớp đủ"
            for i in Lop_vang:
                thong_bao +=i.STT + " " + i.Ten +"\n"
            Console.Log(thong_bao)
            DataBase.client.setTypingStatus(TypingStatus.STOPPED , thread_id=thread_id, thread_type=thread_type)
            DataBase.client.send(Message(text=thong_bao), thread_id=thread_id, thread_type=thread_type)
            muon = "Điểm danh muộn lớp "+ Lop + ": \n"
            ds_muon = []
            for hs in DataBase.Thong_tin_hs:
                if hs.Muon != "":
                    ds_muon.append(hs)
                    muon += hs.Ten + " " + hs.Muon + "\n"
            if len(ds_muon) > 0:
                DataBase.client.send(Message(text=muon), thread_id=thread_id, thread_type=thread_type)
                



            super(React, self).onMessage(
                author_id=author_id,
                message_object=message_object,
                thread_id=thread_id,
                thread_type=thread_type,
                **kwargs
            )
           else:
                DataBase.client.send(Message(text="Lớp không tồn tại !"), thread_id=thread_id, thread_type=thread_type)
     sleep(0.25)
     GPIO.output(16, False)

        

def Start_FB():
    Blink(16,0.25,15)


    GPIO.output(16, True)
    DataBase.client = React('duongdoantung2k3@gmail.com', 'tung2003')
    Console.Log("Dang nhap FB thanh cong")
    DataBase.FB_ready = True
    DataBase.client.listen()
class Main():
     def __init__(self):
        self.files =  os.listdir("./IMG_DataBase/")
        self.en_file = os.listdir("./Face_data/")
        self.ReadExcel()
        FB = Thread(target=Start_FB)
        FB.start()
        Nhan_dang()

     def New_entry(self,Thong_tin_hs,Face_path):

        if (Thong_tin_hs.Lop+"_"+Thong_tin_hs.STT+".data") in self.en_file:
            face_encoding = self.Read_en(Thong_tin_hs.Lop+"_"+Thong_tin_hs.STT)
        else:
            image = face_recognition.load_image_file(Face_path)
            face_encoding = face_recognition.face_encodings(image)[0]
            self.Write_en(face_encoding,Thong_tin_hs.Lop+"_"+Thong_tin_hs.STT)
        print(face_encoding)
        print(type(face_encoding[0]),len(face_encoding))
        DataBase.Face_STTs.append(Thong_tin_hs.Ten)
        DataBase.Face_encodings.append(face_encoding)
        DataBase.Thong_tin_hs.append(Thong_tin_hs)
        Console.Log("New entry: ",Thong_tin_hs.Ten," ",Face_path)
     def Read_en(self,file_name):
          with open("./Face_data/"+file_name+".data","r") as File:
             data_str = File.read().split(" ")
             data_list = []
             for i in data_str:
                 data_list.append(float(i))
             data = np.array(data_list,np.float64)
             File.close()
             Console.Log("Read complete")
             return data
     def Write_en(self,data,file_name):
         
         with open("./Face_data/"+file_name+".data","w+") as File:
             string = ""
             for x in data:
                string += str(x) + " "
             string = string[:-1]
             File.write(string)
             File.close()
             Console.Log("Write complete")
     def ReadExcel(self):
        wb = openpyxl.load_workbook('Thong_tin_hs.xlsx')
        self.missing_data = []
        for ws in wb:
            Console.Log("Lop",ws.title)
            Colunm = ws['A3':'B100']
            Console.Log("Main: ",self.files)
            for Row in Colunm:
                if Row[0].value != None:
                    
                    if (ws.title+"_"+str(Row[0].value)+".png" in self.files) or  (ws.title+"_"+str(Row[0].value)+".jpg" in self.files ):
                        Hoc_sinh = Person(str(Row[0].value),ws.title,"./IMG_DataBase/"+((ws.title+"_"+str(Row[0].value)+".png") if ws.title+"_"+str(Row[0].value)+".png" in self.files else ws.title+"_"+str(Row[0].value)+".jpg" ) ,str(Row[1].value))
                        self.New_entry(Hoc_sinh,Hoc_sinh.IMG)
                    else:
                        self.missing_data.append(Person(str(Row[0].value),ws.title,"",str(Row[1].value)))
                        Console.Warning("Missing data: ",str(Row[1].value),ws.title)
                else:
                   del Row
            Console.Log("DataBase: ",len(DataBase.Thong_tin_hs))
Main()