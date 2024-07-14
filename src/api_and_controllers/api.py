import time
import random
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_and_controllers.docker_ import build_image, create_container, remove_dangling, remove_container, cwd

class API:
    def __init__(self):
        print("\U0001F6A7 \U0001F6E0  Building app, please wait...")
        self.image_name = 'script'
        self.image = build_image(cwd, self.image_name)
        remove_dangling()
        self.containers = []

        self.create_servers()
        print("      \U00002705 Done building")

    def create_servers(self, number_of_servers=3):
        for i in range(number_of_servers):
            self.containers.append(create_container(self.image_name))
            time.sleep(10)
            remove_dangling()

    def remove_servers(self, cont_id=None):
        to_remove = []
        if cont_id:
            to_remove = [self.containers[i] for i in range(len(self.containers)) if self.containers[i].id == cont_id]
        else:
            to_remove = random.choices(
                self.containers, k=random.randint(1, len(self.containers)-1))
            to_remove = list(set(to_remove))
        print(to_remove)
        if len(to_remove) == len(self.containers):
            print("BE AWARE: All servers are going down")
        # print(to_remove)
        for container in to_remove:
            remove_container(container)
            remove_dangling()
            self.containers.remove(container)
        print(f'{len(to_remove)} container(s) removed')

    def set_value(self, key, value):
        result = create_container(
            self.image_name, ["-o", "set", "-k", str(key), "-v", str(value)])
        remove_dangling()
        return (True, 'Success!!') if result.find('True') != -1 else (False, 'Setting value failed!')

    def get_value(self, key):
        result = create_container(
            self.image_name, ["-o", "get", "-k", str(key)])
        remove_dangling()
        return (True, result) if result != 'None' else (False, None)