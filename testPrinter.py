from firebase import firebase
import time, threading

uuid = "1";

database_url = "https://inertia-printers-project-default-rtdb.firebaseio.com"

firebase = firebase.FirebaseApplication(database_url, None)
data =  { 'Name': 'John Doe',
          'RollNo': 3,
          'Percentage': 70.02
          }
result = firebase.post('/python-example-f6d0b/Students/',data)
print(firebase.get(database_url, '1'))
print(result)

StartTime=time.time()

def action(startTime) :
   print('action ! -> time : {:.1f}s'.format(time.time()-startTime))
   firebase.put( database_url,uuid + '/print/timeRemaining', '{:}s'.format(round(8.0 -( time.time()-startTime))))
   firebase.put( database_url, uuid + "/print/percentCompletion", round(((time.time()-startTime)/8.0) * 100.0) )
    
state = "Idle"

def after() :
   print("Print complete")
   firebase.put(database_url, uuid+ "/status", "Idle")
   firebase.put(database_url, uuid+ "/print/printStatus", "Complete")
   firebase.put( database_url,uuid + '/print/timeRemaining', '0s')
   firebase.put( database_url, uuid + "/print/percentCompletion", 100 )
   global state
   state = "idle"


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
      self.stopEvent.set()
      self.after()


while(True):
   command = firebase.get(database_url, uuid + "/print/command")
   if (command == ""):
      firebase.put(database_url,uuid + "/print/ack", 0)
   elif (command == "print"):
      if (state != "printing"):
         time.sleep(2)
         firebase.put(database_url,uuid + "/print/ack", 1)
         firebase.put(database_url,uuid + "/print/printStatus", "Printing")
         firebase.put(database_url, uuid+ "/status", "Printing")
         inter=setInterval(0.2,action, after)
         t=threading.Timer(8,inter.cancel)
         t.start()
         state = "printing";

# start action every 0.6s
inter=setInterval(0.5,action)
print('just after setInterval -> time : {:.1f}s'.format(time.time()-StartTime))

# will stop interval in 5s
t=threading.Timer(5,inter.cancel)
t.start()