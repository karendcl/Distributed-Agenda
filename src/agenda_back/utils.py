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
                        'request': lambda obj: self._create_request(obj),
                        'group': lambda obj: self._create_group(obj)}

    def create(self, object):

        if object == None:
            return None

        class_name = object['class']

        return self.classes[class_name](object)

    def _create_event(self, object):

        title = object['title']
        description = object['description']
        date = object['date']
        start_time = object['start_time']
        end_time = object['end_time']
        participants = object['participants']
        groups = object['groups']

        event = Event(title, description, date, start_time, end_time, participants, groups)

        return event


    def _create_user(self, object):

        user = User(object['alias'], object['password'])

        try:
            user.active = object['logged']
            user.requests = object['inbox']
            user.groups = object['groups']
        except:
            ...

        return user

    def _create_request(self, object):

        id = object['id']
        type = object['type']
        group_id = object['group_id']
        from_user_alias = object['from_user_alias']
        max = object['max']
        count = object['count']
        status = object['status']

        if type == 'join':
            to_user_alias = object['to_user']
            request = JoinRequest(group_id, from_user_alias, max, to_user_alias, id, count)
        elif type == 'event':
            event = object['event']
            request = EventRequest(group_id, from_user_alias, max, event, id, count)
        else:
            admins = object['admins']
            request = GroupRequest(group_id, from_user_alias, max, admins, id, count)

        request.status = status

        return request

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



