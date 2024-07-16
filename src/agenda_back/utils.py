import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.event import Event
from entities.user import User
from entities.group import GlobalGroup, IndependentGroup, HierarchicalGroup, GroupRequest, JoinRequest, EventRequest


# Function to convert date string to datetime object
def parse_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')


# Function to convert time string to datetime.time object
def parse_time(time_string):
    return datetime.strptime(time_string, '%H:%M').time()

class Back:
    def __init__(self) -> None:

        self.classes = {'event': lambda obj: self._create_event(obj),
                        'user': lambda obj: self._create_user(obj),
                        'group': lambda obj: self._create_group(obj)}

    def create(self, object):

        if object == None or object is None:
            return None

        class_name = object['class']

        return self.classes[class_name](object)

    def _create_event(self, object):

        print("Re-Creating Event")
        title = object['title']
        description = object['description']
        date = object['date']
        start_time = object['start_time']
        end_time = object['end_time']
        participants = object['participants']
        groups = object['groups']

        event = Event(title, description, date, start_time, end_time, participants, groups)

        try:
            event.event_id = object['event_id']
            event.confirmed = object['confirmed']
            event.rejected = object['rejected']
            event.pending_confirmations_people = object['pending_confirmations_people']
            event.pending_confirmations_groups = object['pending_confirmations_groups']
        except Exception as e:
            print("Exception in ReCreating Event")
            print(e)

        return event


    def _create_user(self, object):

        user = User(object['alias'], object['password'])

        try:
            user.active = object['logged']
            user.groups = object['groups']
            user.confirmed_events = object['confirmed_events']
            user.pending_events = object['pending_events']
            user.created_events = object['created_events']
        except Exception as e:
            print(e)

        return user


    def _create_group(self, object):
        group = None
        if object['type'] == 'independent':
            group = IndependentGroup(object['name'], object['id'])
            group.events = object['events']
            group.users = object['users']
            group.requests = object['requests']
            group.waiting_events = object['waiting_events']
            group.waiting_users = object['waiting_users']
        elif object['type'] == 'global':  
            group = GlobalGroup(object['name'], object['id'])
            group.users = object['users']
        else:
            group = HierarchicalGroup(object['name'], object['id'])
            group.events = object['events']
            group.users = object['users']
            group.requests = object['requests']
            group.waiting_users = object['waiting_users']
            group.admins = object['admins']

        return group



