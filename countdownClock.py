#GOAL
#Create a program that allows the user to choose a time and date, and then prints out a message at given intervals (such as every second)
# that tells the user how much longer there is until the selected time.

#SUBGOALS
#If the selected time has already passed, have the program tell the user to start over.
#If your program asks for the year, month, day, hour, etc. separately, allow the user to be able to type in either the month name or its number.
#TIP: Making use of built in modules such as time and datetime can change this project from a nightmare into a much simpler task.

import time
import datetime

print("Enter year,month,day,hour,minutes,seconds in separate lines:")
year = input()
month = input()
day = input()
hour = input()
minutes = input()
seconds = input()
futureTime = year+" "+month+" "+day+" "+hour+" "+minutes+" "+seconds

if len(month)>2:
    eventTime = datetime.datetime.strptime(futureTime, "%Y %B %d %H %M %S")

else:
    eventTime = datetime.datetime.strptime(futureTime, "%Y %m %d %H %M %S")

while True:
    currentTime = datetime.datetime.now()
    if eventTime < currentTime :
        print("Countdown Over")
        exit()
    difference = eventTime-currentTime
    print(difference)
    time.sleep(1)



