import datetime
import random
import json
import hashlib
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agenda_back.back as back_
from api_and_controllers.api import *

api = API()
back = back_.Agenda(api)

class AgendaItem:
    def __init__(self, name, description, time, time_end, date = datetime.datetime.today(), id = 0):
        self.name = name
        self.description = description
        self.time_start = time
        self.time_end = time_end
        self.date = date
        self.id = id

def create_group(group_name, selected_users, hierarchical, username):
    try:
        selected_users = [] if not selected_users else selected_users
        back.create_group(group_name,selected_users,hierarchical)
        return True
    except Exception as e:
        print(e)
        return False

def get_groups_of_user(username):
    return back.group_of_user()

def hash_password(password):
    return '0o' + hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    return back.login(username,hash_password(password))

def logout_(username):
    back.logout(username)

def signup(username, password):
    pass_ = hash_password(password)
    return back.register(username,pass_)


def parse_event_to_AgendaItem(events):
    ans = []
    for event in events:
        ans.append(AgendaItem(event.title, event.description, event.start_time, event.end_time, event.date, event.event_id))
    return ans

def get_meetings(username):
    ans = back.get_confirmed_meetings()
    ans.sort(key=lambda x: (x.date, x.start_time))
    return ans

def get_pending_meetings(username):
    ans = back.get_pending_meetings()
    ans.sort(key=lambda x: (x.date, x.start_time))
    return ans

def create_meeting(name, description, time,endtime, date, participants, groups, username):
    try:
        back.create_pending_meeting(name, description, date, time, endtime, groups, participants)
        return True
    except Exception as e:
        print(e)
        return False

def remove_meeting(path, id):
    try:
        with open(path, 'r') as f:
            meetings = json.load(f)
    except FileNotFoundError:
        return False
    meeting = meetings.pop(str(id))
    with open(path, 'w') as f:
        json.dump(meetings, f)
    return meeting

def add_meeting(path, meet):
    try:
        with open(path, 'r') as f:
            meetings = json.load(f)
    except FileNotFoundError:
        meetings = {}

    id = len(meetings)
    meetings[id] = meet

    with open(path, 'w') as f:
        json.dump(meetings, f)
    return True

def accept_meeting(username, id):
    path = '../data/pending_meetings.json'

    meet = remove_meeting(path, id)
    if not meet:
        return False

    path = '../data/meetings.json'
    return add_meeting(path, meet)


def decline_meeting(username, id):
    path = '../data/pending_meetings.json'
    meeting = remove_meeting(path, id)
    return False if not meeting else True

def get_all_users(username):
    users = back.get_all_users()
    ans = [x for x in users if x != username]
    return ans

def get_all_groups():
    return back.groups_of_user()

# todo once a leader accepts it, all group participants get it






def get_Selected_users(list_widget):
    """
    Get the selected users from a list widget.

    Args:
        list_widget (QListWidget): The list widget containing the users.

    Returns:
        list: A list of the selected users.
    """
    selected_users = []
    for i in range(list_widget.count()):
        if list_widget.item(i).checkState():
            selected_users.append(list_widget.item(i).text())
    return selected_users

def identify_conflicts(accepted_meetings: list[AgendaItem], pending_meetings: list[AgendaItem] = None) -> list[int]:
    """
    Identify conflicts between meetings.

    Args:
        accepted_meetings (list[AgendaItem]): A list of accepted meetings.
        pending_meetings (list[AgendaItem]): A list of pending meetings. Defaults to None.

    Returns:
        list[int]: A list of IDs of conflicting meetings
    """
    conflicts = []
    if pending_meetings:
        for i in range(len(accepted_meetings)):
            for j in range(len(pending_meetings)):
                if times_clash(accepted_meetings[i].time_start, accepted_meetings[i].time_end, pending_meetings[j].time_start,
                               pending_meetings[j].time_end, accepted_meetings[i].date, pending_meetings[j].date):
                    conflicts.append(accepted_meetings[i].id)
                    conflicts.append(pending_meetings[j].id)
    else:
        for i in range(len(accepted_meetings)):
            for j in range(i+1, len(accepted_meetings)):
                if times_clash(accepted_meetings[i].time_start, accepted_meetings[i].time_end, accepted_meetings[j].time_start,
                               accepted_meetings[j].time_end, accepted_meetings[i].date, accepted_meetings[j].date):
                    conflicts.append(accepted_meetings[i].id)
                    conflicts.append(accepted_meetings[j].id)

    return conflicts

def times_clash(start1, end1, start2, end2, date1, date2):
    """
    Check if two events clash in time.

    Args:
        start1 (datetime): The start time of the first event.
        end1 (datetime): The end time of the first event.
        start2 (datetime): The start time of the second event.
        end2 (datetime): The end time of the second event.
        date1 (datetime): The date of the first event.
        date2 (datetime): The date of the second event.

    """
    return start1 <= end2 and start2 <= end1 and date1 == date2


