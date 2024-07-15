from entities.group import Group, IndependentGroup, HierarchicalGroup
from entities.event import Event
from entities.group import Request
from kademlia.utils import digest

class User:
    """
    Representa un usuario de la agenda distribuida.
    """

    def __init__(self, alias, password):
        """
        Inicializa un nuevo usuario.

        Args:
            alias (str): El alias del usuario.
            full_name (str): El nombre completo del usuario.
            password (str): La contraseña del usuario.
        """
        self.alias = alias
        self.password = password
        self.groups = []  # Lista de IDs de grupos a los que pertenece el usuario
        self.active = False  # Indica si el usuario está conectado
        self.confirmed_events = []  # Lista de IDs de eventos confirmados por el usuario
        self.pending_events = []  # Lista de IDs de eventos pendientes de confirmación por el usuario

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.alias == other.alias
        return False
        
    def logged(self):
        """
        Establece el estado del usuario como conectado.
        """
        self.active = True

    def create_event(self, event):
        """
        Crea un nuevo evento.

        Args:
            event (Event): El evento a crear.

        Returns:
            Event: El evento creado.
        """
        self.confirmed_events.append(event.event_id)
        print(f"Event {event.title} created and added to user {self.alias} confirmed events")

    def add_pending_event(self, event):
        """
        Agrega un evento pendiente de confirmación.

        Args:
            event (Event): El evento a agregar.
        """
        self.pending_events.append(event.event_id)
        print(f"Event {event.title} added to user {self.alias} pending events")

    
    def create_group(self, group_name, group_type,id=None):
        """
        Crea un nuevo grupo.

        Args:
            group_name (str): El nombre del grupo.
            group_type (str): El tipo de grupo (flat o hierarchical).
            id (str, optional): El ID único del grupo. Si no se proporciona, se genera uno. Defaults to None.

        Returns:
            Group: El nuevo grupo creado.
        """
        new_group = None

        if group_type == 'independent':
            new_group = IndependentGroup(group_name,id)
            new_group.users.append(self.alias)
            self.groups.append(new_group.group_id)
        else:
            new_group = HierarchicalGroup(group_name,id)
            new_group.users.append(self.alias)
            new_group.admins.append(self.alias)
            self.groups.append(new_group.group_id)
            
        
        return new_group
    
    def add_to_group(self,group_id):
        """
        Agrega el usuario a un grupo.

        Args:
            group_id (str): El ID del grupo al que se va a agregar el usuario.
        """
        if group_id not in self.groups:
            self.groups.append(group_id)

    def exit_group(self,group):
        """
        Elimina el usuario de un grupo.

        Args:
            group (Group): El grupo del que se va a eliminar el usuario.
        """
        if group.group_id in self.groups:
            self.groups.remove(group.group_id)
            group.exit_group(self.alias)


    def remove_from_group(self,group_id):
        """
        Elimina el usuario de un grupo por ID.

        Args:
            group_id (str): El ID del grupo del que se va a eliminar el usuario.
        """
        if group_id in self.groups:
            self.groups.remove(group_id)
            

    def remove_event(self, group: Group, event: Event):
        """
        Elimina un evento de un grupo.

        Args:
            group (Group): El grupo del que se va a eliminar el evento.
            event (Event): El evento a eliminar.

        Returns:
            Event: El evento eliminado.
        """
        event = group.remove_event(self.alias, event)

        return event

        
    def set_event(self, event, group, **fields):
        """
        Modifica un evento existente.

        Args:
            event (Event): El evento a modificar.
            group (Group): El grupo al que pertenece el evento.
            **fields: Atributos del evento a modificar (por ejemplo, título, fecha, etc.).

        Returns:
            Event: El evento modificado.
        """
        return group.set_event(event, user=self.alias, **fields)

    def set_request(self, request_id):
        """
        Agrega una solicitud a la bandeja de entrada del usuario.

        Args:
            request_id (str): El ID de la solicitud.
        """
        self.requests.append(request_id)       

    def accept_request(self, request, group):
        """
        Acepta una solicitud.

        Args:
            request (Request): La solicitud a aceptar.
            group (Group): El grupo al que pertenece la solicitud.

        Returns:
            Group: El nuevo grupo, si la solicitud es para cambiar el tipo de grupo, None en caso contrario.
        """
        if request.request_id in self.requests:
            new = group.accepted_request(request)
            if request.get_type() == 'join':
                self.groups.append(group.group_id)
            self.requests.remove(request.request_id)
            return new
        
        return None
    
    def reject_request(self, request, group):
        """
        Rechaza una solicitud.

        Args:
            request (Request): La solicitud a rechazar.
            group (Group): El grupo al que pertenece la solicitud.

        Returns:
            Request: La solicitud rechazada.
        """
        if request.request_id in self.requests:
            request = group.rejected_request(request)
            self.requests.remove(request.request_id)
            return request
        
        return None
    
    def change_group_type(self, group, admins, users):
        """
        Cambia el tipo de un grupo.

        Args:
            group (Group): El grupo al que se va a cambiar el tipo.
            admins (list): Una lista de alias de los nuevos administradores.
            users (list): Una lista de usuarios en el grupo.

        Returns:
            tuple: Una tupla que contiene la solicitud creada y el nuevo grupo, si es necesario.
        """
        if group.group_id not in self.groups:
            print(f"You do not belong to group {group.name}")
            return None, None
        
        if admins != None:
            not_in_group = []

            for adm in admins:
                if adm not in group.users:
                    not_in_group.append(adm)

            if len(not_in_group) > 0:
                print(f"Users {not_in_group} do not belong to group {group.group_id}")
                return None, None
        
        request, new_group = group.change_group_type(self.alias, admins, users)

        if request != None:
            self.requests.append(request.request_id)

        return request, new_group

    
    def dicc(self):
        return {'class': 'user',
                'alias':self.alias,
                'password':self.password,
                'logged':self.active, 
                # 'inbox':self.requests, 
                'groups':self.groups}


    def __repr__(self) -> str:
        return self.alias
    
    def __str__(self) -> str:
        return self.alias



        




        
        
            