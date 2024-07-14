import datetime
import random
import json
import hashlib
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agenda_back.back as back

class AgendaItem:
    def __init__(self, name, description, time, time_end, date = datetime.datetime.today(), id = 0):
        self.name = name
        self.description = description
        self.time_start = time
        self.time_end = time_end
        self.date = date
        self.id = id

def create_group(group_name, selected_users, hierarchical, username):
    path = '../data/groups.json'
    try:
        with open(path, 'r') as f:
            groups = json.load(f)
    except FileNotFoundError:
        groups = {}

    if group_name in groups:
        return False

    selected_users += [username]
    groups[group_name] = {'users': selected_users, 'hierarchical': hierarchical, 'admin': username}
    with open(path, 'w') as f:
        json.dump(groups, f)
    return True

def get_groups_of_user(username):
    return back.group_of_user()


def get_Selected_users(list_widget):
    selected_users = []
    for i in range(list_widget.count()):
        if list_widget.item(i).checkState():
            selected_users.append(list_widget.item(i).text())
    return selected_users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    return back.login(username,password)

def signup(username, password):
    pass_ = hash_password(password)
    return back.register(username,pass_)

def get_meeting(username,path):
    try:
        with open(path, 'r') as f:
            meetings = json.load(f)
    except FileNotFoundError:
        return []

    try:
        with open('../data/groups.json','r') as f:
            groups = json.load(f)
    except FileNotFoundError:
        groups = {}

    groups_admin = []
    for key,value in groups.items():
        if username == value['admin'] and value['hierarchical']:
            groups_admin.append(key)


    return [AgendaItem(meeting['name'], meeting['description'], meeting['time_start'], meeting['time_end'], meeting['date'], ind)
            for ind, meeting in enumerate(meetings.values())
            if username in meeting['participants']
            or [g for g in meeting['groups'] if g in groups_admin] != []]

def get_meetings(username):
    path = '../data/meetings.json'
    ans =  get_meeting(username,path)
    ans.sort(key=lambda x: (x.date, x.time_start))
    return ans

def get_pending_meetings(username):
    path = '../data/pending_meetings.json'
    ans =  get_meeting(username,path)
    ans.sort(key=lambda x: (x.date, x.time_start))
    return ans

def create_meeting(name, description, time,endtime, date, participants, groups, username):
    path = '../data/pending_meetings.json'
    meeting = {'name': name, 'description': description, 'time_start': time, 'time_end': endtime, 'date': date,
                    'participants': participants + [username], 'groups': groups}
    return add_meeting(path, meeting)

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

def times_clash(start1, end1, start2, end2, date1, date2):
    return start1 <= end2 and start2 <= end1 and date1 == date2

def identify_conflicts(accepted_meetings: list[AgendaItem], pending_meetings: list[AgendaItem] = None) -> list[int]:
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


def get_all_users(username):
    path = '../data/users.json'
    try:
        with open(path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        return []
    return [user for user in users.keys() if user != username]

def get_all_groups():
    path = '../data/groups.json'
    try:
        with open(path, 'r') as f:
            groups = json.load(f)
    except FileNotFoundError:
        return []
    return groups.keys()

# todo once a leader accepts it, all group participants get it






