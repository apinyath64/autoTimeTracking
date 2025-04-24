import json
from dateutil import parser

class Activity:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def serialize(self):
        return {
            'name': self.name,
            'duration': self.save_time_to_json()
        }
    
    def save_time_to_json(self):
        time_list = []
        for time in self.duration:
            time_list.append(time.serialize())
        return time_list
    

class Duration:
    def __init__(self, start_time, end_time, days, hours, minutes, seconds):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def get_specific_times(self):
        self.days, self.seconds = self.duration.days, self.duration.seconds
        self.hours = self.days * 24 + self.seconds // 3600
        self.minutes = (self.seconds) % 3600 // 60
        self.seconds = self.seconds % 60
      

    def serialize(self):
        return {
            'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end_time': self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'days': self.days,
            'hours': self.hours,
            'minutes': self.minutes,
            'seconds': self.seconds
        }
    

class Activity_list:
    def __init__(self, activities):
        self.activities = activities

    def data_initialize(self):
        activity_list = Activity_list([])
        with open('activity_data.json', 'r') as f:
            data = json.load(f)
            activity_list = Activity_list(activities = self.get_activities_from_json(data))
        return activity_list
    
    def get_activities_from_json(self, data):
        return_data = []
        for activity in data['activities']:
            return_data.append(
                Activity(
                    name = activity['name'],
                    duration = self.get_time_from_json(activity),
                )
            )
        self.activities = return_data
        return return_data
    
    def get_time_from_json(self, data):
        time_list = []
        for time in data['duration']:
            time_list.append(
                Duration(
                    start_time = parser.parse(time['start_time']),
                    end_time = parser.parse(time['end_time']),
                    days = time['days'],
                    hours = time['hours'],
                    minutes = time['minutes'],
                    seconds = time['seconds']
                )
            )
        self.duration = time_list
        return time_list
    

    def serialize(self):
        return {
            'activities': self.save_to_json()
        }
    
    def save_to_json(self):
        activity_data = []
        for activity in self.activities:
            activity_data.append(activity.serialize())

        return activity_data



