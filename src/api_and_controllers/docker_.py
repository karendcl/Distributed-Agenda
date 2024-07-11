import docker
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

cwd = os.getcwd()
client = docker.from_env()

def create_network(net_name):
    return client.networks.create(net_name)

def remove_dangling():
    client.images.prune(filters={'dangling': True})
    for container in client.containers.list(all=True):
        if len(container.image.tags) == 0:
            remove_container(container)

def build_image(path_to_dockerfile, image_name):
    image_names = [image.tags[0] for image in client.images.list(
        all=True) if image.tags]
    image = client.images.build(path=path_to_dockerfile, tag=image_name)

    if f'{image_name}:latest' in image_names:
        client.images.prune(filters={'dangling': True})
        for container in client.containers.list(all=True):
            if len(container.image.tags) == 0 or container.image.tags[0] == f'{image_name}:latest':
                remove_container(container)
    return image


def create_container(image_name, params=[]):
    container = client.containers.run(
        image_name, command=params, network='my-network', detach=True)

    if len(params) > 0:
        container.wait()
        lines = container.logs().decode().split('\n')
        logs = lines
        if 'set' in params:
            logs = [line for line in lines if 'DEBUG' in line or 'INFO' in line]
        last_line = logs[-2] if len(logs) > 1 else logs[0]
        container.stop()
        container.remove()
        return last_line

    return container

def remove_container(container):
    container.stop()
    container.remove()
