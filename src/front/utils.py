import datetime
import random
import json
import hashlib

class AgendaItem:
    def __init__(self, name, description, time, date = datetime.datetime.today(), id = 0):
        self.name = name
        self.description = description
        self.time = time
        self.date = date
        self.id = id

def create_group(group_name, selected_users, hierarchical):
    path = '../data/groups.json'
    try:
        with open(path, 'r') as f:
            groups = json.load(f)
    except FileNotFoundError:
        groups = {}

    if group_name in groups:
        return False

    groups[group_name] = {'users': selected_users, 'hierarchical': hierarchical}
    with open(path, 'w') as f:
        json.dump(groups, f)
    return True

def get_groups_of_user(username):
    path = '../data/groups.json'
    try:
        with open(path, 'r') as f:
            groups : dict = json.load(f)
    except FileNotFoundError:
        return []

    return [key for key,value in groups.items() if username in value['users']]


def get_Selected_users(list_widget):
    selected_users = []
    for i in range(list_widget.count()):
        if list_widget.item(i).checkState():
            selected_users.append(list_widget.item(i).text())
    return selected_users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    path = '../data/users.json'
    try:
        with open(path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        return False
    if username in users and users[username] == hash_password(password):
        return True
    return False

def signup(username, password):
    path = '../data/users.json'
    try:
        with open(path, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    if username in users:
        return False
    users[username] = hash_password(password)
    with open(path, 'w') as f:
        json.dump(users, f)
    return True

def get_meeting(username,path):
    try:
        with open(path, 'r') as f:
            meetings = json.load(f)
    except FileNotFoundError:
        return []
    return [AgendaItem(meeting['name'], meeting['description'], meeting['time'], meeting['date'], ind)
            for ind, meeting in enumerate(meetings.values()) if username in meeting['participants']]
def get_meetings(username):
    path = '../data/meetings.json'
    return get_meeting(username,path)

def get_pending_meetings(username):
    path = '../data/pending_meetings.json'
    return get_meeting(username,path)

def create_meeting(name, description, time, date, participants, groups, username):
    path = '../data/pending_meetings.json'
    meeting = {'name': name, 'description': description, 'time': time, 'date': date,
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
        return False

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

def identify_conflicts(accepted_meetings: list[AgendaItem], pending_meetings: list[AgendaItem] = None) -> list[int]:
    conflicts = []
    for i in range(len(accepted_meetings)):
        for j in range(i+1, len(accepted_meetings)):
            if accepted_meetings[i].date == accepted_meetings[j].date and accepted_meetings[i].time == accepted_meetings[j].time:
                conflicts.append(accepted_meetings[i].id)
                conflicts.append(accepted_meetings[j].id)
    if pending_meetings:
        for i in range(len(accepted_meetings)):
            for j in range(len(pending_meetings)):
                if accepted_meetings[i].date == pending_meetings[j].date and accepted_meetings[i].time == pending_meetings[j].time:
                    conflicts.append(accepted_meetings[i].id)
                    conflicts.append(pending_meetings[j].id)
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