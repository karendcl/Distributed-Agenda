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

def build_image(path_to_dckrfile, image_name):
    # Verifica si la imagen ya existe
    image_names = [image.tags[0] for image in client.images.list(
        all=True) if image.tags]
    
    print(image_names)
    print(image_name)
    if f'{image_name}:latest' in image_names:
        # Imagen ya existe, no la construyas
        print(f"Imagen {image_name}:latest ya existe.")
        return client.images.get(f"{image_name}:latest")  # Obtén la imagen existente
    else:
        # Construye la imagen solo si no existe
        image = client.images.build(path=path_to_dckrfile, tag=image_name)
        print(f"Imagen {image_name}:latest construida.")
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
