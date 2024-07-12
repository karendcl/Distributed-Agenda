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

    def _already_logged(self):
        return self.logged_user != None

    def login(self, args):

        if self._already_logged():
            print(f"There is a user logged already.")
            return

        alias = args.alias
        password = digest(args.password)

        user = self.get(alias)

        # if user not in DB, register
        if user == None:
            print('You are not register into the app.')
            return

        # if alias and password match with user's, logged
        if user.alias == alias and user.password == password:
            user.logged()
            self.set(user.alias, user.dicc())
            self.logged_user = user.alias

            print(f"Welcome to Monica Scheduler {user.alias}!")

        else:
            print(f"Incorrect username or password. Try again.")

        return

    def register(self, args):

        if self._already_logged():
            print(f"There is a user logged. You cannot register.")
            return

        alias = args.alias
        full_name = args.full_name
        password = digest(args.password)
        confirmation = digest(args.confirmation)

        # Password and confirmation not matching
        if password != confirmation:
            print("Wrong password.")
            return

        user = self.get(alias)

        if user != None:
            print(f"User with alias {alias} already exists")
            return

        new_user = self.factory.create({
            'class': 'user',
            'alias': alias,
            'full_name': full_name,
            'password': password}
        )

        new_user.logged()

        self.logged_user = new_user.alias

        self.set(new_user.alias, new_user.dicc())

        print("Successfully registered")
        print(f"Welcome to Monica Scheduler {new_user.alias}!")

    def logout(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        user = self.get(self.logged_user)
        user.active = False
        self.set(user.alias, user.dicc())
        print(f"Bye {self.logged_user}!")
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

            workspace = self.get(requests[req_id].workspace_id)

            if handle_request == 'accept':
                new = user.accept_request(requests[req_id], workspace)
                if requests[req_id].get_type() == 'workspace' and new:
                    workspace = new
                print(f"Request successfully accepted.")
            else:
                new = user.reject_request(requests[req_id], workspace)
                print(f"Request successfully rejected.")

            self.set(user.alias, user.dicc())
            self.set(workspace.workspace_id, workspace.dicc())
            self.set(req_id, requests[req_id].dicc())

    def workspaces(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        user = self.get(self.logged_user)

        if len(user.workspaces) > 0:

            workspaces = []

            for w in user.workspaces:
                workspaces.append(self.get(w))

            print(f"Workspaces:")
            for i, w in enumerate(workspaces):
                print(f"{i + 1}. {w}")

        else:
            print("You do not belong to any workspace")
            return

    def user_profile(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        name = args.name
        change_password = args.change_password

        user = self.get(self.logged_user)

        if name == None and not change_password:
            print(f'Profile:\n Alias: {user.alias}\n Name: {user.full_name}')
            return

        new_password = None
        if change_password:
            while True:
                confirmation = getpass.getpass(
                    "Please type your current password:")
                if digest(confirmation) != user.password:
                    print("Incorrect password")
                else:
                    while True:
                        new_password = digest(
                            getpass.getpass("Type the new password:"))
                        new_password_confirmation = digest(
                            getpass.getpass("New password confirmation:"))
                        if new_password_confirmation == new_password:
                            break
                        else:
                            print('Incorrect password')
                    break

        new_user = self.factory.create(
            {'class': 'user',
             'alias': user.alias,
             'full_name': name or user.full_name,
             'password': new_password or user.password,
             'logged': user.active,
             'inbox': user.requests,
             'workspaces': user.workspaces}
        )

        self.set(new_user.alias, new_user.dicc())

        self.logged_user = new_user.alias

        print(f'Profile edited.')

    def create_workspace(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        title = args.title
        type = args.type
        id = args.id

        if type == 'f':
            type = 'flat'
        else:
            type = 'hierarchical'

        user = self.get(self.logged_user)

        new_workspace = user.create_workspace(title, type, id)
        self.set(user.alias, user.dicc())
        self.set(new_workspace.workspace_id, new_workspace.dicc())

        print(f"Workspace {new_workspace.workspace_id} was created.")

    def add_user(self, args):

        if not self._already_logged():
            print("There is no user logged")
            return

        workspace_id = args.workspace_id
        user_alias = args.user_alias

        user = self.get(self.logged_user)
        user_to_add = self.get(user_alias)
        workspace = self.get(workspace_id)

        if user_to_add == None:
            print(f"User {user_alias} is not register into the app")
            return
        if workspace == None or workspace_id not in user.workspaces:
            print(
                f"User {user.alias} does not belong to workspace {workspace_id}")
            return

        request = workspace.add_user(user.alias, user_to_add)

        if request:
            self.set(request.request_id, request.dicc())

        self.set(user.alias, user.dicc())
        self.set(user_to_add.alias, user_to_add.dicc())
        self.set(workspace_id, workspace.dicc())
