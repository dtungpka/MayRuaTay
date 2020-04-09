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
class Person:
    Ten = ""
    Lop = ""
    IMG = ""
    STT = ""
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


    
    
class Nhan_dang():
    def __init__(self):
        Console.Log("Starting")
        self.face_locations = []
        self.face_encodings = []
        self.face_STTs = []
        self.Running = True
        self.Bat_dau()
        
    def Bat_dau(self):
        
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        count = 0
        frame_count = 0
        start_cooldown = 0.0
        while self.Running:
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # BGR -> RGB
            rgb_small_frame = small_frame[:, :, ::-1]

           
            if process_this_frame:
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                if not frame_count == 0 :
                    frame_count = 0 if time.time() - start_cooldown > 3 else frame_count - 1
                
                self.face_STTs = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(DataBase.Face_encodings, face_encoding)
                    STT = "Unknown"
                    face_distances = face_recognition.face_distance(DataBase.Face_encodings, face_encoding)
                    print("Dist",face_distances)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        STT = DataBase.Face_STTs[best_match_index]
                        if DataBase.Thong_tin_hs[best_match_index] not in DataBase.Co_mat:
                            DataBase.Co_mat.append(DataBase.Thong_tin_hs[best_match_index])
                    self.face_STTs.append(STT)
                    Console.Log("ID hoc sinh: ",best_match_index,"Thong tin: ",DataBase.Thong_tin_hs[best_match_index].Ten,DataBase.Thong_tin_hs[best_match_index].Lop)
                if self.face_encodings and frame_count == 0 and STT == "Unknown":
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


           

        video_capture.release()
        

class React(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
     if author_id != self.uid and  (str( message_object.text)[0] == "1" or message_object.text == "Toàn trường") :
        thong_bao = ""
        # We can only kick people from group chats, so no need to try if it's a user chat
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




            super(React, self).onMessage(
                author_id=author_id,
                message_object=message_object,
                thread_id=thread_id,
                thread_type=thread_type,
                **kwargs
            )
           else:
                DataBase.client.send(Message(text="Lớp không tồn tại !"), thread_id=thread_id, thread_type=thread_type)


        

def Start_FB():
    DataBase.client = React('duongdoantung2k3@gmail.com', 'tung2003')
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