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
            new_group = self.factory.create({
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
        data = self.api.get_value(key)[1]

        if data == None or data is None:
            return

        try:
            data = eval(eval(data)[1])
        except:
            data = eval(data)

        return self.back.create(data)

    def set(self, key, value):
        self.api.set_value(key, value)
        time.sleep(5)


    def login(self, username, password):

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
    
    #Por ahora simplemente imprime los usuarios del grupo global, adaptalo para que lo devuelva
    def get_all_users(self):
        global_group_id = "global"
        global_group = self.get(global_group_id)
        if global_group:
            print(f"Users:")
            for u in global_group.users:
                print(f"- {u}")
        else:
            return []

    def groups_of_user(self):

        user = self.get(self.logged_user)

        ans = []

        if len(user.groups) > 0:
            for w in user.groups:
                ans.append(self.get(w))

        print(ans)
        return ans

    def create_group(self, name, users, hierarchical):

        if hierarchical:
            type = 'hierarchical'
        else:
            type = 'independent'

        user = self.get(self.logged_user)

        new_group = user.create_group(name, type, name)
        self.set(user.alias, user.dicc())
        self.set(new_group.group_id, new_group.dicc())

        if users:
            for us in users:
                user_ = self.get(us)
                user_.add_to_group(name)

    # NOT DONE ------------------------
    def logout(self, username):
        user = self.get(self.logged_user)
        user.active = False
        self.set(user.alias, user.dicc())
        self.logged_user = None

    def inbox(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        handle_request = args.handle
        req_id = args.id

        user = self.get(self.logged_user)
        requests = {}

        if req_id != None and req_id not in user.requests:
            print("Wrong request id.")
            return

        for req in user.requests:
            requests[req] = self.get(req)

        if handle_request == None and req_id == None:
            if len(requests.values()) > 0:
                print(f"Inbox:")
                for r in requests.values():
                    print(f"- {r}")
            else:
                print("You have no notifications")
                return

        elif handle_request == None and req_id != None:
            print(f"{requests[req_id]}")

        elif handle_request != None and req_id != None:

            group = self.get(requests[req_id].group_id)

            if handle_request == 'accept':
                new = user.accept_request(requests[req_id], group)
                if requests[req_id].get_type() == 'group' and new:
                    group = new
                print(f"Request successfully accepted.")
            else:
                new = user.reject_request(requests[req_id], group)
                print(f"Request successfully rejected.")

            self.set(user.alias, user.dicc())
            self.set(group.group_id, group.dicc())
            self.set(req_id, requests[req_id].dicc())






        # pending

    def add_user_to_group(self, group_id, user_alias):
        user = self.get(self.logged_user)
        user_to_add = self.get(user_alias)
        group = self.get(group_id)

        request = group.add_user(user.alias, user_to_add)

        if request:
            self.set(request.request_id, request.dicc())

        self.set(user.alias, user.dicc())
        self.set(user_to_add.alias, user_to_add.dicc())
        self.set(group_id, group.dicc())
    def change_role(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        user_alias = args.user_alias
        group_id = args.group_id

        user = self.get(self.logged_user)

        if group_id not in user.groups:
            print(
                f"User {user.alias} does not belong to group {group_id}")
            return

        user_to_change = self.get(user_alias)
        group = self.get(group_id)

        if group.get_type() == 'flat':
            print(f"group {group_id} does not have roles")
            return

        group.change_role(user.alias, user_alias)

        self.set(user.alias, user.dicc())
        self.set(user_to_change.alias, user_to_change.dicc())
        self.set(group.group_id, group.dicc())

    def create_event(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        group_id = args.group_id
        title = args.title
        date = args.date
        place = args.place
        start_time = args.start_time
        end_time = args.end_time
        id_event = args.id

        user_get = self.get(self.logged_user)

        if group_id not in user_get.groups:
            print(f"User {user_get.alias} does not belong to group {group_id}")
            return

        group_get = self.get(group_id)
        users = []

        for u in group_get.users:
            users.append(self.get(u))

        users_collision = set()
        you = False

        for user in users:
            for group_id in user.groups:
                group = self.get(group_id)
                for event_id in group.events:

                    event = self.get(event_id)
                    min_start_time, max_start_time, min_end_time = 0, 0, 0

                    if start_time > event.start_time:
                        min_start_time = event.start_time
                        max_start_time = start_time
                        min_end_time = event.end_time

                    else:
                        max_start_time = event.start_time
                        min_start_time = start_time
                        min_end_time = end_time

                    if date == event.date and (min_start_time <= max_start_time and min_end_time > max_start_time):
                        if user.alias == self.logged_user:
                            you = True
                        else:
                            users_collision.add(user.alias)

        if users_collision != set() or you:
            if you:
                print(f"WARNING: Users {users_collision} and you have an event that collides with the new event.")
            else:
                print(f"WARNING: Users {users_collision} have an event that collides with the new event.")

            while True:
                confirmation = input("Do you want to continue? (y/n): ")
                if confirmation.lower() == 'y':
                    break
                if confirmation.lower() == 'n':
                    return

        event, request = user_get.create_event(group_get, title, date, place, start_time, end_time, users, id_event)

        if event != None:
            self.set(event.event_id, event.dicc())

        if request != None:
            self.set(request.request_id, request.dicc())

        self.set(user_get.alias, user_get.dicc())

        for u in users:
            self.set(u.alias, u.dicc())

        self.set(group_get.group_id, group_get.dicc())

    def remove_event(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        event_id = args.event_id

        user = self.get(self.logged_user)
        event = self.get(event_id)
        group = self.get(event.group_id)

        user.remove_event(group, event)

        self.set(user.alias, user.dicc())
        self.set(group.group_id, group.dicc())

    def events(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        group_id = args.group_id

        user = self.get(self.logged_user)

        if group_id not in user.groups:
            print(
                f"User {user.alias} does not belong to group {group_id}")
            return

        group = self.get(group_id)

        if len(group.events) > 0:
            print(f"Events of group {group_id}:")
            for i, e in enumerate(group.events):
                print(f"{i + 1}. {self.get(e)}")
        else:
            print(f"group {group_id} does not have any events")
            return

    def set_event(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        event_id = args.id
        title = args.title
        date = args.date
        place = args.place
        start_time = args.start_time
        end_time = args.end_time

        user = self.get(self.logged_user)

        event = self.get(event_id)

        group = self.get(event.group_id)

        new_event = user.set_event(
            event=event,
            group=group,
            title=title,
            date=date,
            place=place,
            end_time=end_time,
            start_time=start_time
        )

        if new_event != None:
            self.set(new_event.event_id, new_event.dicc())
            print("Event successfully modified")

    # def change_group_type(self, args):
    #
    #     if not self._already_logged():
    #         print("There is no user logged")
    #         return
    #
    #     group_id = args.group_id
    #     admins = args.admins
    #
    #     group = self.get(group_id)
    #
    #     if group == None:
    #         print(f"group {group_id} does not exist")
    #         return
    #
    #     user = self.get(self.logged_user)
    #
    #     users = []
    #
    #     for u in group.users:
    #         users.append(self.get(u))
    #
    #     request, new_group = user.change_group_type(
    #         group, admins, users)
    #
    #     if request != None:
    #         self.set(request.request_id, request.dicc())
    #         print(f"Request to change type of group {group_id} sent")
    #     if new_group != None:
    #         self.set(new_group.group_id, new_group.dicc())
    #         print(f"Type of group {group_id} was changed successfully")
    #     else:
    #         self.set(group.group_id, group.dicc())
    #
    #     for u in users:
    #         self.set(u.alias, u.dicc())

    def request_status(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        group_id = args.group_id

        group = self.get(group_id)

        if self.logged_user not in group.users:
            print(f"You do not belong to group {group_id}")
            return

        print(f"Request from group {group_id}:")

        for r in group.requests:
            request = self.get(r)
            print(f"{request} - {request.status}")

    # def exit_group(self, args):
    #
    #     if not self._already_logged():
    #         print("There is no user logged")
    #         return
    #
    #     group_id = args.group_id
    #
    #     user = self.get(self.logged_user)
    #     group = self.get(group_id)
    #
    #     user.exit_group(group)
    #
    #     self.set(user.alias, user.dicc())
    #     self.set(group.group_id, group.dicc())
    #
    #     print(f"You have successfull exited group {group_id}")

    def check_availability(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        group_id = args.group_id
        date = args.date
        start_time = args.start_time
        end_time = args.end_time

        group = self.get(group_id)

        events = []

        for event_id in group.events:
            event = self.get(event_id)
            if event.date == date:
                if start_time and end_time:

                    min_start_time, max_start_time, min_end_time = 0, 0, 0

                    if start_time > event.start_time:

                        min_start_time = event.start_time
                        max_start_time = start_time
                        min_end_time = event.end_time
                    else:

                        max_start_time = event.start_time
                        min_start_time = start_time
                        min_end_time = end_time

                    if min_start_time <= max_start_time and min_end_time > max_start_time:
                        events.append(event)
                elif start_time and start_time <= event.end_time:

                    events.append(event)
                elif end_time and end_time <= events.start_time:

                    events.append(event)

        if len(events) > 0:
            print("The following events collide with the given date and time:")
            for e in events:
                print(f"- {e}")
        else:
            print("The given date and time is available for any event")


    # PENDING
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


        