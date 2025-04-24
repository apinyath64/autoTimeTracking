# pylint: disable=no-name-in-module
from win32gui import GetWindowText, GetForegroundWindow
import time
from pywinauto import Application
import tldextract
import json
from datetime import datetime
import os
from activity import Duration, Activity_list, Activity
import tkinter as tk
import threading


active_window_name = ""
activity = ""
start_time = datetime.now()
first_time = True
activity_list = Activity_list([])

activity_data = []
json_file = 'activity_data.json'


def get_active_window():
    new_window = GetForegroundWindow()
    new_window_title = GetWindowText(new_window)
    if "-" in new_window_title:
        app = new_window_title.split("-")[-1].strip()
    else:
        app = new_window_title.strip()
    
    return app


def get_active_url():
   try:
        app = Application(backend='uia')
        app.connect(title_re='.*Chrome.*')
        element_name = "Address and search bar"
        dlg = app.top_window()
        url = dlg.child_window(title=element_name, control_type='Edit').get_value()
        extracted_url = tldextract.extract(url)
        # domain = extracted_url.domain
        return f'{extracted_url.domain}.{extracted_url.suffix}'
   
   except Exception as e:
       print(f"Fail to get URL: {e}")
       return "Unknown URL"
   

def save_to_json(log):
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    existing_data.append(log)

    with open(json_file, "w") as f:
        json.dump(existing_data, f, sort_keys=True, indent=4, ensure_ascii=False)


def time_tracking_window():

    def data_from_json():
        if os.path.exists('activity_data.json'):
            try:
                with open('activity_data.json', 'r') as json_file:
                    data = json.load(json_file)
                    text_display.delete(1.0, tk.END)
                    for activity in data.get("activities", []):
                        name = activity.get("name")
                        duration = activity.get("duration")
                        text_display.insert(tk.END, f"{name}:\n")
                        for d in duration:
                            start_time = d.get("start_time", "")
                            end_time = d.get("end_time", "")
                            hours = d.get("hours", 0)
                            minutes = d.get("minutes", 0)
                            seconds = d.get("seconds", 0)
                            time_format = f"{hours:02}:{minutes:02}:{seconds:02}"
                            text_display.insert(tk.END, f"From {start_time} To {end_time} ({time_format})\n")
                        text_display.insert(tk.END, "-" * 70 + "\n\n")
                
            except json.JSONDecodeError:
                text_display.delete(1.0, tk.END)
                text_display.insert(tk.END, "Failed to parse json!")

        else:
            text_display.delete(1.0, tk.END)
            text_display.insert(tk.END, "No activity found!")

        root.after(1000, data_from_json)

    root = tk.Tk()
    root.title("Automatic Time Tracking")
    label = tk.Label(root, text="Time tracking started...")
    label.pack()
    text_display = tk.Text(root, width=80, height=30)
    text_display.pack()

    data_from_json()
    root.mainloop()



tk_window = threading.Thread(target=time_tracking_window, daemon=True)
tk_window.start()



try:
    while True:
        window_name = get_active_window()
        if 'Google Chrome' in window_name:
            active_activity = get_active_url()
        else:
            active_activity = window_name

        if active_window_name != active_activity:
            print(active_window_name)
            activity = active_window_name
            
            if not first_time:
                end_time = datetime.now()
                duration = Duration(start_time, end_time, 0, 0, 0, 0)
                duration.get_specific_times()

                exists = False
                for act in activity_list.activities:
                    if act.name == activity:
                        exists = True
                        act.duration.append(duration)

                if not exists:
                    act = Activity(activity, [duration])
                    activity_list.activities.append(act)
                with open('activity_data.json', 'w') as json_file:
                    json.dump(activity_list.serialize(), json_file, indent=4, sort_keys=True)
                    start_time = datetime.now()

            first_time = False
            active_window_name = active_activity


        time.sleep(1)

except KeyboardInterrupt:
    with open('activity_data.json', 'w') as json_file:
        json.dump(activity_list.serialize(), json_file, indent=4, sort_keys=True)

