import pyautogui
import time
from datetime import datetime

target_hour = int(input("Enter the target hour "))
target_minute = int(input("Enter the target minute "))
print(f"The program will work till {target_hour}:{target_minute}.")
while True:
    datetime.now()
    if datetime.now().hour == target_hour and datetime.now().minute == target_minute:
        print("Run out of time")
        break
    pyautogui.hotkey('alt', 'tab')
    pyautogui.click(100,200)
    time.sleep(10)
    pyautogui.click(500,600)
    time.sleep(30)
