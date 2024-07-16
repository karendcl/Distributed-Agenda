import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from agenda_back.utils import Back

import hashlib
import time
import dictdatabase as DDB
import getpass



def digest(string):
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).hexdigest()


file_name = 'data'


def database():
    DDB.config.storage_directory = "./database"
    database = DDB.at(f"{file_name}")
    if not database.exists():
        database.create({})


class Agenda:

    def __init__(self, api) -> None:
        self.back = Back()
        self.logged_user = None
        self.api = api

        self.create_global_group() 

    def create_global_group(self):
        global_group_name = "GlobalGroup"
        global_group_id = "global"  # Un ID único para el group global

        # Verifica si el group global ya existe
        global_group = self.get(global_group_id)
        if global_group is None:
            print("Creating global_group")
            # Crea el group global
            new_group = self.back.create({
                'class': 'group',
                'id': global_group_id,
                'type': 'global',
                'users': [], 
                'name': global_group_name
            })
            self.set(global_group_id, new_group.dicc())
        else:
            print(f"El group global {global_group_name} ya existe.")

    def _already_logged(self):
        return self.logged_user is not None

    def get(self, key):
        print(f"Key: {key}")
        data = self.api.get_value(key)[1]

        if "kademlia.network" in data:
            # Find the index of the opening square bracket '['
            start_index = data.find("{") + 1
            
            # Find the index of the closing square bracket ']'
            end_index = data.rfind("}") - 1
            
            data = data[start_index:end_index]
            print("Clean")

        print(f"Data: {data}")
        if data == None or data is None:
            return

        try:
            print(f"In Try: {eval(data)}")
            data = eval(eval(data)[1])
        except Exception as e:
            print(f"Error in Eval: {e}")
            data = eval(data)

        print(f"Struct data: {data}")
        return self.back.create(data)

    def set(self, key, value):
        self.api.set_value(key, value)
        time.sleep(5)


    def login(self, username, password):

        print(f"Trying to log in: {username}")
        user = self.get(username)

        if user is None or user == None:
            return False

        # if alias and password match with user's, logged
        if user.alias == username and user.password == password:
            user.logged()
            self.set(user.alias, user.dicc())
            self.logged_user = user.alias
            return True

        return False

    def register(self, username, password):

        user = self.get(username)

        if user != None or user is not None:
            return False

        new_user = self.back.create({
            'class': 'user',
            'alias': username,
            'password': password}
        )

        new_user.logged()

        self.logged_user = new_user.alias

        self.set(new_user.alias, new_user.dicc())

        global_group_id = "global"
        global_group = self.get(global_group_id)
        if global_group:
            global_group.add_user(self.logged_user, new_user) 
            self.set(global_group_id, global_group.dicc()) 

        return True


    def get_users_from_group(self, group_name, user):

        if not self._already_logged():
            return []

        user = self.get(self.logged_user)

        ans = []
        if group_name in user.groups:
            group = self.get(group_name)
            for u in group.users:
                ans.append(u)

        print(ans)
        return ans
    
    def get_all_users(self):
        global_group_id = "global"
        global_group = self.get(global_group_id)
        ans = []
        if global_group:
            for u in global_group.users:
                ans.append(u)
        return ans

    def groups_of_user(self):
        user = self.get(self.logged_user)
        ans = []
        for g in user.groups:
            ans.append(g)
        return ans


    def create_group(self, name, users, hierarchical):

        if hierarchical:
            type = 'hierarchical'
        else:
            type = 'independent'

        user = self.get(self.logged_user)

        new_group = user.create_group(name, type, name)
        print(f"Set user: {user.dicc()}")
        self.set(user.alias, user.dicc())
        self.set(new_group.group_id, new_group.dicc())

        if users != []:
            for us in users:
                user_ = self.get(us)
                user_.add_to_group(name)
                print(f"User added to group: {user_.dicc()}")
                self.set(user_.alias, user_.dicc())

                new_group = self.get(name)
                new_group.add_user(user.alias, us)
                print(f"Group added user: {new_group.dicc()}")
                self.set(new_group.group_id, new_group.dicc())


    def logout(self, username):
        user = self.get(self.logged_user)
        user.active = False
        self.set(user.alias, user.dicc())
        self.logged_user = None

    def create_pending_meeting(self, title, description, date, start_time, end_time, groups, participants):
        event = self.back.create({
            'class': 'event',
            'title': title,
            'description': description,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'participants': [self.logged_user] + participants,
            'groups': groups
        })

        self.set(event.event_id, event.dicc())
        event = self.get(event.event_id)

        user = self.get(self.logged_user)
        user.create_event(event)
        self.set(user.alias, user.dicc())

        for p in participants:
            user = self.get(p)
            user.add_pending_event(event)
            self.set(user.alias, user.dicc())

        for g in groups:
            group = self.get(g)
            confirmed = group.add_event(event, self.logged_user)
            self.set(group.group_id, group.dicc())

            if confirmed:
                event.group_confirm(g)
                self.set(event.event_id, event.dicc())

    def get_pending_meetings(self):
        user = self.get(self.logged_user)
        ans = []
        for e in user.pending_events:
            event = self.get(e)
            ans.append(event)
        return ans

    def get_confirmed_meetings(self, username):
        user = self.get(username)
        ans = []
        for e in user.confirmed_events:
            event = self.get(e)
            print(f"Event: {event}")
            if event.confirmed:
                print("Event is confirmed")
                ans.append(event)
        return ans

    def get_pending_group_meetings(self):
        user = self.get(self.logged_user)
        print(f"G User: {user}")
        ans = []
        for group_id in user.groups:
            group = self.get(group_id)

            if group.get_type() == 'independent':
                for e in group.waiting_events:
                    event = self.get(e)
                    print(f"Group Event: {event}")
                    if group.user_needs_to_confirm_event(event.event_id, user.alias):
                        ans.append(event)
                    # if not event.confirmed and not event.rejected:
                    #     ans.append(event)

            elif group.get_type() == 'hierarchical':
                if user.alias in group.admins:
                    for e in group.waiting_events:
                        event = self.get(e)
                        print(f"Group Event: {event}")
                        if group.user_needs_to_confirm_event(event.event_id, user.alias):
                            ans.append(event)
                        # if not event.confirmed and not event.rejected:
                        #     ans.append(event)

        print(f'Pending group meetings: {ans}')
        return ans

    def get_confirmed_group_meetings(self, username):
        user = self.get(username)

        ans = []
        for group_id in user.groups:
            group = self.get(group_id)
            for e in group.events:
                event = self.get(e)
                if event.confirmed:
                    ans.append(event)
        print(f'Confirmed group meetings: {ans}')
        return ans


    def accept_meeting(self, event_id):
        user = self.get(self.logged_user)
        print(f'Event_id: {event_id}')
        event = self.get(event_id)
        was_in_group = False
        was_in_self = False

        if user.alias in event.pending_confirmations_people:
            event.user_confirm(user.alias)
            user.confirm_event(event)
            self.set(event.event_id, event.dicc())
            self.set(user.alias, user.dicc())
            was_in_self = True

        else:
            for group_id in event.pending_confirmations_groups:
                if group_id in user.groups:
                        was_in_group = True
                        group = self.get(group_id)
                        if group.get_type() == 'hierarchical' and user.alias in group.admins:
                            confirmed = group.confirm_event(event.event_id, user.alias)
                            if confirmed:
                                event.group_confirm(group_id)
                                self.set(event.event_id, event.dicc())
                            self.set(group.group_id, group.dicc())
                        elif group.get_type() == 'independent':
                            confirmed = group.confirm_event(event.event_id, user.alias)
                            if confirmed:
                                event.group_confirm(group_id)
                                self.set(event.event_id, event.dicc())
                            self.set(group.group_id, group.dicc())

        return was_in_group or was_in_self

    def reject_meeting(self, event_id):
        user = self.get(self.logged_user)
        event = self.get(event_id)
        was_in_group = False
        was_in_self = False

        if user.alias in event.pending_confirmations_people:
            event.user_reject(user.alias)
            user.reject_event(event.event_id)
            self.set(event.event_id, event.dicc())
            self.set(user.alias, user.dicc())
            was_in_self = True

        else:
            for group_id in event.pending_confirmations_groups:
                if group_id in user.groups:
                    group = self.get(group_id)
                    if group.get_type() == 'hierarchical' and user.alias in group.admins:
                        rejected = group.reject_event(event.event_id, user.alias)
                        if rejected:
                            event.group_reject(group_id)
                            self.set(event.event_id, event.dicc())
                        self.set(group.group_id, group.dicc())
                    elif group.get_type() == 'independent':
                        rejected = group.reject_event(event.event_id, user.alias)
                        if rejected:
                            event.group_reject(group_id)
                            self.set(event.event_id, event.dicc())
                        self.set(group.group_id, group.dicc())


        return was_in_group or was_in_self

    def events_created(self):
        try:
            user = self.get(self.logged_user)
            ans = []
            for e in user.created_events:
                event = self.get(e)
                ans.append(event)
            return ans
        except Exception as e:
            print(e)
            return []

    def remove_meeting(self, event_id):
        try:
            event = self.get(event_id)

            for p in event.participants:
                user = self.get(p)
                user.remove_event(event)
                self.set(user.alias, user.dicc())

            for g in event.groups:
                group = self.get(g)
                group.remove_event(event)
                self.set(group.group_id, group.dicc())

            return True
        except Exception as e:
            print(e)
            return False


    def sudo(self, action, n_s):

        if action == 'create':
            if n_s:
                self.api.create_servers(n_s)
                print(f'{n_s} server(s) added')
            else:
                self.api.create_servers()
                print(f'3 server(s) added')
        else:
            if not n_s:
                self.api.remove_servers()
            else:
                print('This command removes a random number of servers')


        