import datetime
import random

class AgendaItem:
    def __init__(self, name, description, time, date = datetime.datetime.today()):
        self.name = name
        self.description = description
        self.time = time
        self.date = date

def create_group(group_name, selected_users, hierarchical):
    print(f'group_name: {group_name}, selected_users: {selected_users}, hierarchical: {hierarchical}')
    return True

def get_Selected_users(list_widget):
    selected_users = []
    for i in range(list_widget.count()):
        if list_widget.item(i).checkState():
            selected_users.append(list_widget.item(i).text())
    return selected_users

def login(username, password):
    print(f'username: {username}, password: {password}')
    return True

def signup(username, password):
    print(f'username: {username}, password: {password}')
    return True

def get_meetings(username):
    meetings = []
    for i in range(5):
        meeting = AgendaItem(f'Meeting {i}', f'Description {i}', f'{i}:00', datetime.datetime.today())
        meetings.append(meeting)
    return meetings

def get_pending_meetings(username):
    meetings = []
    for i in range(5):
        ind = random.randint(0, 5)
        meeting = AgendaItem(f'Meeting {ind}', f'Description {ind}', f'{ind}:00', datetime.datetime.today())
        meetings.append(meeting)
    return meetings

def create_meeting():
    print('create_meeting')
    return True

def accept_meeting(username, id):
    print('accept_meeting')
    return True

def decline_meeting(username, id):
    print('decline_meeting')
    return True

def identify_conflicts(accepted_meetings: list[AgendaItem], pending_meetings: list[AgendaItem] = None) -> list[int]:
    conflicts = []
    for i in range(len(accepted_meetings)):
        for j in range(i+1, len(accepted_meetings)):
            if accepted_meetings[i].date == accepted_meetings[j].date and accepted_meetings[i].time == accepted_meetings[j].time:
                #todo append the id of the conflicting meetings not the index
                conflicts.append(i)
                conflicts.append(j)
    if pending_meetings:
        for i in range(len(accepted_meetings)):
            for j in range(len(pending_meetings)):
                if accepted_meetings[i].date == pending_meetings[j].date and accepted_meetings[i].time == pending_meetings[j].time:
                    #todo append the id of the conflicting meetings not the index
                    conflicts.append(i)
                    conflicts.append(j)
    return conflicts


def get_all_users(username):
    return ['user1', 'user2', 'user3', 'user4', 'user5']

def get_all_groups():
    return ['group1', 'group2', 'group3', 'group4', 'group5']