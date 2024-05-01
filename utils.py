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