from firebase import firebase
import time, threading
from google.cloud import firestore
import os
import argparse
import datetime

parser = argparse.ArgumentParser(description='Run printer simulator.')
parser.add_argument('UUID', metavar='U', type=str,
                    help='UUID of the printer to simulate')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\jrmuy\Documents\Code\Inertia\inertia-printers-project-1af0a447d855.json"


args = parser.parse_args()
print(args.UUID)

db = firestore.Client()

uuid = args.UUID;


database_url = "https://inertia-printers-project-default-rtdb.firebaseio.com"

timer_progress = 0
firebase = firebase.FirebaseApplication(database_url, None)
data =  { 'Name': 'John Doe',
          'RollNo': 3,
          'Percentage': 70.02
          }
result = firebase.post('/python-example-f6d0b/Students/',data)
print(firebase.get(database_url, uuid))
print(result)

StartTime=time.time()
counter = 0
def action(startTime) :
   global counter
   if (state == "printing"):
      global timer_progress
      timer_progress = (round(counter))
      print('action ! -> time : {:.1f}s'.format(counter))
      firebase.put( database_url,uuid + '/print/timeRemaining', '{:}s'.format(round(8.0 -( counter))))
      firebase.put( database_url, uuid + "/print/percentCompletion", round(((counter)/8.0) * 100.0) )
      counter += 0.2
    
state = "idle"

def after() :
   global state
   if (state == "printing"):
      print("Print complete")
      firebase.put(database_url, uuid+ "/status", "Idle")
      firebase.put(database_url, uuid+ "/print/printStatus", "Complete")
      firebase.put( database_url,uuid + '/print/timeRemaining', '0s')
      firebase.put( database_url, uuid + "/print/percentCompletion", 100 )
      state = "idle"
      fileID = firebase.get(database_url, uuid+"/print/fileID")
      print("FILE ID: " ,fileID)
      file_ref=db.collection('files').where('fileID', '==', fileID).get()
      for doc in file_ref:
         print(doc.to_dict())
      print(db.collection('files').where('fileID', "==", fileID).get()[0].reference)
      db.collection('files').where('fileID', "==", fileID).get()[0].reference.update({
         'hasPrint': True,
         'pastPrintTime': '8s',
         'pastPrintDate': datetime.datetime.now()
      })


class setInterval :
    def __init__(self,interval,action,after) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        self.startTime = time.time()
        self.after=after
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action(self.startTime)

    def cancel(self) :
      print("Canceling thread")
      self.stopEvent.set()
      self.after()

t= None

import signal
import atexit

def exit_handler():
    print( 'My application is ending!')
    t.cancel()

atexit.register(exit_handler)

def main():
   global t
   global state
   global timer_progress
   try:
      while(True):
         
         command = firebase.get(database_url, uuid + "/print/command")
         if (command == ""):
            firebase.put(database_url,uuid + "/print/ack", 0)
         elif (command == "print"):
            if (state == "idle"):
               counter = 0
               firebase.put(database_url,uuid + "/print/ack", 1)
               firebase.put(database_url,uuid + "/print/printStatus", "Printing")
               firebase.put(database_url, uuid+ "/status", "Printing")
               # global t
               print("T:" , t)
               state = "printing"
               inter=setInterval(0.2,action, after)

               t = threading.Timer(8,inter.cancel)
               
               t.start()               
               
               state = "printing";
         elif (command == "stop"):
            if (state == "printing"):
               firebase.put(database_url,uuid + "/print/ack", 1)

               firebase.put(database_url, uuid+ "/status", "Idle")
               firebase.put(database_url, uuid+ "/print/printStatus", "Canceled")
               firebase.put( database_url,uuid + '/print/timeRemaining', '0s')
               state = "idle"
               counter = 0
               inter.cancel()


         elif (command == "pause"):
            if (state == "printing"):
               
               firebase.put(database_url,uuid + "/print/ack", 1)

               firebase.put(database_url, uuid+ "/status", "Printing")
               firebase.put(database_url, uuid+ "/print/printStatus", "Paused")
               state = "paused"
               inter.cancel()

         elif (command == "resume"):
            if (state == "paused"):
               firebase.put(database_url,uuid + "/print/ack", 1)

               firebase.put(database_url, uuid+ "/status", "Printing")
               firebase.put(database_url, uuid+ "/print/printStatus", "Printing")
               state = "printing"
               # global t
               inter=setInterval(0.2,action, after)

               t=threading.Timer(8-timer_progress,inter.cancel)
               t.start()
   finally:
      print("Exiting Program")
      # global t
      t.cancel

if __name__ == '__main__':
   main()

# # start action every 0.6s
# inter=setInterval(0.5,action)
# print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# # will stop interval in 5s
# t=threading.Timer(5,inter.cancel)
# t.start()