import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from entities.event import Event
from abc import abstractmethod, ABC

from abc import abstractmethod, ABC

class Request(ABC):
    """
    Clase abstracta para representar solicitudes en el sistema de agenda.

    Define los atributos y métodos comunes a todos los tipos de solicitudes.
    """
    def __init__(self, group_id, from_user_id, max_users, id=None, count=0):
        """
        Inicializa una nueva solicitud.

        Args:
            group_id (str): El ID del grupo al que se refiere la solicitud.
            from_user_id (str): El alias del usuario que envió la solicitud.
            max_users (int): El número máximo de usuarios que deben aprobar la solicitud.
            id (str, optional): El ID único de la solicitud. Si no se proporciona, se genera uno. Defaults to None.
            count (int, optional): El número actual de usuarios que han aprobado la solicitud. Defaults to 0.
        """
        self.group_id = group_id
        self.from_user_id = from_user_id
        self.max_users = max_users
        self.status = 'sent'
        self.count = count
        

    def __eq__(self, other: object) -> bool:
        """
        Compara dos solicitudes por su ID.

        Args:
            other (Request): La otra solicitud para comparar.

        Returns:
            bool: True si los IDs de las solicitudes son iguales, False en caso contrario.
        """
        if isinstance(other,Request):
            return self.request_id == other.request_id
        return False
    
    @abstractmethod
    def get_type(self):
        """
        Devuelve el tipo de solicitud.
        """
        pass

    @abstractmethod
    def dicc(self):
        """
        Devuelve un diccionario que representa la solicitud.
        """
        pass
    
    def __repr__(self) -> str:
        return f"Type: {self.get_type}\n User: {self.from_user_id}\n Group: {self.group_id}"
    
    def __str__(self) -> str:
        return f"Request"

class JoinRequest(Request):
    """
    Representa una solicitud para unirse a un grupo.
    """

    def __init__(self, group_id, from_user_id, max_users, to_user, id=None, count=0):
        """
        Inicializa una nueva solicitud de unión.

        Args:
            group_id (str): El ID del grupo al que se solicita unirse.
            from_user_id (str): El alias del usuario que envía la solicitud.
            max_users (int): El número máximo de usuarios que deben aprobar la solicitud.
            to_user (str): El alias del usuario al que se le envía la solicitud.
            id (str, optional): El ID único de la solicitud. Si no se proporciona, se genera uno. Defaults to None.
            count (int, optional): El número actual de usuarios que han aprobado la solicitud. Defaults to 0.
        """
        super().__init__(group_id, from_user_id, max_users, id, count)
        self.to_user = to_user
        self.request_id = id or self.group_id + self.from_user_id + self.to_user
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other,Request):
            return self.request_id == other.request_id
        return False
    

    def get_type(self):
        """
        Devuelve el tipo de solicitud.
        """
        return 'join'
    
    def dicc(self):
        """
        Devuelve un diccionario que representa la solicitud.
        """

        return {'class':'request',
                'id':self.request_id,
                'type':self.get_type(),
                'group_id':self.group_id,
                'from_user_alias':self.from_user_id,
                'to_user':self.to_user,
                'max':self.max_users,
                'status': self.status,
                'count':self.count}
    
    def __repr__(self) -> str:
        return f"Type: {self.get_type()}\n User: {self.from_user_id}\n Group: {self.group_id}"
    
    def __str__(self) -> str:
        return f"[{self.request_id}] Invitacion del usuario: {self.from_user_id} para unirse al grupo: {self.group_id}"
    
class EventRequest(Request):
    """
    Representa una solicitud para crear un evento en un grupo.
    """

    def __init__(self, group_id, from_user_id,max_users, event_id, id=None, count=0):
        """
        Inicializa una nueva solicitud de evento.

        Args:
            group_id (str): El ID del grupo donde se creará el evento.
            from_user_id (str): El alias del usuario que envía la solicitud.
            max_users (int): El número máximo de usuarios que deben aprobar la solicitud.
            event_id (str): El ID del evento que se solicita crear.
            id (str, optional): El ID único de la solicitud. Si no se proporciona, se genera uno. Defaults to None.
            count (int, optional): El número actual de usuarios que han aprobado la solicitud. Defaults to 0.
        """
        super().__init__(group_id, from_user_id, max_users,id,count)
        self.event_id = event_id
        self.request_id = id or self.group_id + self.from_user_id + self.event_id

    def __str__(self) -> str:
        return f"[{self.request_id}] Request del usuario: {self.from_user_id} para crear el evento: {self.event_id} on group {self.group_id}"

    def get_type(self):
        return 'event'
    
    def dicc(self):
        return {'class':'request',
                'id':self.request_id,
                'type':self.get_type(),
                'group_id':self.group_id,
                'from_user_alias':self.from_user_id,
                'max':self.max_users,
                'count':self.count,
                'status':self.status,
                'event':self.event_id}


class GroupRequest(Request):
    """
    Representa una solicitud para cambiar el tipo de un grupo.
    """
    def __init__(self, group_id, from_user_id, max_users, admins, id=None, count=0):
        """
        Inicializa una nueva solicitud de cambio de tipo de grupo.

        Args:
            group_id (str): El ID del grupo al que se va a cambiar el tipo.
            from_user_id (str): El alias del usuario que envía la solicitud.
            max_users (int): El número máximo de usuarios que deben aprobar la solicitud.
            admins (list): Una lista de alias de los administradores del grupo.
            id (str, optional): El ID único de la solicitud. Si no se proporciona, se genera uno. Defaults to None.
            count (int, optional): El número actual de usuarios que han aprobado la solicitud. Defaults to 0.
        """
        super().__init__(group_id, from_user_id, max_users, id, count)
        self.admins = admins
        admins_str = ''
        for adm in self.admins:
            admins_str+=adm
        self.request_id = id or self.group_id + self.from_user_id + admins_str
        

        

    def __str__(self) -> str:
        return f"[{self.request_id}] Request del usuario: {self.from_user_id} para cambiar el tipo del grupo: {self.group_id}."

    def get_type(self):
        return 'group'
    
    def dicc(self):
        return {'class':'request',
                'id':self.request_id,
                'type':self.get_type(),
                'group_id':self.group_id,
                'from_user_alias':self.from_user_id,
                'max':self.max_users,
                'status':self.status,
                'count':self.count,
                'admins':self.admins}






class Group(ABC):
    """
    Clase abstracta para grupos en una agenda.

    Define los atributos y métodos comunes a todos los tipos de grupos.
    """
    def __init__(self, group_name, id=None) -> None:        
        """
        Inicializa un nuevo grupo.

        Args:
            group_name (str): El nombre del grupo.
            id (str, optional): El ID único del grupo. Si no se proporciona, se usa el nombre del grupo. Defaults to None.
        """
        self.group_name = group_name
        self.events = []
        self.users = []    
        self.group_id = id or self.group_name
    
    @abstractmethod
    def get_type(self):
        """
        Devuelve el tipo de grupo.
        """
        pass    

    @abstractmethod
    def add_event(self,event):
        """
        Agrega un evento al grupo.
        """
        pass                

    @abstractmethod
    def remove_event(self, time,date,start_time,end_time, users):
        """
        Elimina un evento del grupo.
        """
        pass

    @abstractmethod
    def add_user(self, from_user, user_to_add):
        """
        Agrega un usuario al grupo.
        """
        pass

    
    def add_users(self,from_user, users_list_to_add):
        """
        Agrega una lista de usuarios al grupo.
        """
        for user in users_list_to_add:
            self.add_user

    @abstractmethod
    def remove_user(self, user):
        """
        Elimina un usuario del grupo.
        """
        pass

    @abstractmethod
    def change_group_type(self):
        """
        Cambia el tipo de grupo.
        """
        pass
    
    @abstractmethod
    def dicc(self):
        """
        Devuelve un diccionario que representa el grupo.
        """
        pass


    def exit_group(self, user_alias):
        """
        Elimina un usuario del grupo.
        """
        if user_alias in self.users:
            self.users.remove(user_alias)

    def send_request(self, request, user):
        """
        Envía una solicitud a un usuario.
        """
        user.set_request(request) 


    def __repr__(self) -> str:
        """
        Devuelve una representación de cadena del grupo.
        """
        return self.group_name
    
    def __str__(self) -> str:
        """
        Devuelve una representación de cadena del grupo.
        """
        return self.group_name
    


class IndependentGroup(Group):
    """
    Representa un grupo no jerarquico.
    """

    def __init__(self, name, id=None) -> None:
        """
        Inicializa un nuevo grupo independiente.
        """
        super().__init__(name,id)  
        self.requests = []      
        self.waiting_events = []
        self.waiting_users = []

    def __str__(self) -> str:
        """
        Devuelve una representación de cadena del grupo.
        """
        return f"""{self.group_name}:\n ID: {self.group_id}\n Users: {self.users}\n Events:{self.events}"""

    def get_type(self):
        """
        Devuelve el tipo de grupo.
        """
        return 'independent'


    def user_needs_to_confirm_event(self, event, user):
        """
        Verifica si un usuario necesita confirmar un evento.
        """
        return event in self.waiting_events and user in self.waiting_users[self.waiting_events.index(event)]
    def add_event(self, event: Event, user):
        """
        Agrega un evento al grupo.
        """
        self.waiting_events.append(event.event_id)
        self.waiting_users.append([x for x in self.users if x != user])
        print(f"Evento {event.event_id} agregado correctamente al grupo {self.group_id}")

    def confirm_event(self, event, user):
        """
        Remove pending user from pending event
        if all users have confirmed it, then accept it

        :param event:
        :param user:
        :return:
        """

        index = self.waiting_events.index(event)
        if user in self.waiting_users[index]:
            self.waiting_users[index].remove(user)
            if len(self.waiting_users[index]) == 0:
                self.waiting_events.remove(event)
                self.waiting_users.remove([])
                self.events.append(event)
                print(f"Evento {event} confirmado por todos los usuarios.")
                return True
        else:
            print(f"El usuario {user} no está en la lista de usuarios pendientes del evento {event}")
        return False

    def reject_event(self, event, user):
        """
        Remove pending user from pending event

        :param event:
        :param user:
        :return:
        """
        index = self.waiting_events.index(event)
        if user in self.waiting_users[index]:
            self.waiting_users[index].remove(user)
            self.waiting_events.remove(event)
            print(f"Evento {event} rechazado por el usuario {user}")
            return True
        else:
            print(f"El usuario {user} no está en la lista de usuarios pendientes del evento {event}")
        return False

    def set_event(self, event, **fields):
        """
        Modifica un evento existente.
        """
        if fields['user'] != event.from_user:
            print(f"El usuario {fields['user']} no puede modificar el evento {event.event_id}")
            return None
        return Event(
            from_user=fields['user'] or event.from_user,
            title=fields['title'] or event.title,
            date=fields['date'] or event.date,
            place=fields['place'] or event.place,
            start_time=fields['start_time'] or event.start_time,
            end_time=fields['end_time'] or event.end_time,
            group_id=self.group_id,
            id=event.event_id
        )


    def remove_event(self, event):
        """
        Elimina un evento del grupo.
        """
        if event.event_id in self.events:
            self.events.remove(event.event_id)
            print(f"Evento {event.event_id} eliminado correctamente del grupo {self.group_id}")

        if event.event_id in self.waiting_events:
            index = self.waiting_events.index(event.event_id)
            self.waiting_events.remove(event.event_id)
            self.waiting_users.remove(self.waiting_users[index])
            print(f"Evento {event.event_id} eliminado correctamente del grupo {self.group_id}")



    
    def add_user(self, from_user_alias, user_to_add):
        """
        Agrega un usuario al grupo.
        """
        self.users.append(user_to_add)
        
    
    def remove_user(self, from_user, user_to_remove):
        """
        Elimina un usuario del grupo.
        """
        try:
            self.users.remove(user_to_remove.alias)
            user_to_remove.remove_from_group(self.group_id)  
            print(f"Usuario {user_to_remove.alias} eliminado correctamente del grupo {self.group_id}")        
            return True
        except:
            print(f"El usuario {user_to_remove.alias} no se puede eliminar del grupo {self} porque no pertenece a él.")

        return False

    
    def accepted_request(self, request):
        """
        Procesa una solicitud aceptada.
        """
        if request.request_id in self.requests:
            request_type = request.get_type()
            request.count += 1
            
            if request.count == request.max_users:
                
                if request_type == 'join':
                    user_alias = request.to_user
                    self.users.append(user_alias)
                    self.waiting_users.remove(user_alias)
    
                elif request_type == 'event':
                    event_id = request.event_id
                    self.events.append(event_id)
                    self.waiting_events.remove(event_id) 
                
                else:
                    new_group = HierarchicalGroup(self.group_name,self.group_id)

                    new_group.events = self.events
                    new_group.users = self.users
                    new_group.admins = request.admins

                    return new_group
                
                request.status = 'accepted'

        return self


    def rejected_request(self, request):
        """
        Procesa una solicitud rechazada.
        """
        if request.request_id in self.requests:
            request_type = request.get_type()
                        
            if request_type == 'join':
                user_alias = request.to_user
                self.waiting_users.remove(user_alias)
    
            elif request_type == 'event':
                event_id = request.event_id
                self.waiting_events.remove(event_id) 

            request.status = 'rejected'

            return request

        return None
        

    def change_group_type(self, author_id, admins, users):
        """
        Cambia el tipo de grupo de independiente a jerárquico.
        """
        if admins == None:
            print(f"Para cambiar el tipo del grupo {self.group_id} a jerárquico, se necesita una lista de administradores del grupo.")
            return None, None
        
        if len(self.users) == 1 and author_id in self.users:
            new_group = HierarchicalGroup(self.group_name,self.group_id)

            new_group.events = self.events
            new_group.users = self.users
            new_group.admins = admins
            
            return None,new_group

        request = GroupRequest(self.group_id, author_id, len(self.users)-1,admins)

        for user in users:
            if user.alias == author_id:
                continue
            self.send_request(request.request_id,user)

        self.requests.append(request.request_id)

        return request, None

    def dicc(self):
        """
        Devuelve un diccionario que representa el grupo.
        """
        return {'class':'group',
                'id':self.group_id,
                'type':self.get_type(), 
                "name":self.group_name,
                'events':self.events,                
                'users':self.users, 
                'requests':self.requests, 
                'waiting_events':self.waiting_events, 
                'waiting_users': self.waiting_users}

    

class HierarchicalGroup(Group):
    """
    Representa un grupo jerárquico.
    """
    def __init__(self, name, id=None) -> None:
        """
        Inicializa un nuevo grupo jerárquico.
        """
        super().__init__(name,id)
        self.requests = []
        self.waiting_events = []
        self.waiting_users = []
        self.admins = [] 

    def __str__(self) -> str:
        """
        Devuelve una representación de cadena del grupo.
        """
        return f"""{self.group_name}:\n ID: {self.group_id}\n Users: {self.users}\n Events:{self.events}\n Admins: {self.admins}"""


    def user_needs_to_confirm_event(self, event, user):
        """
        Verifica si un usuario necesita confirmar un evento.
        """
        return event in self.waiting_events and user in self.admins
    def get_type(self):
        """
        Devuelve el tipo de grupo.
        """
        return 'hierarchical'
    
    def change_role(self, from_user_alias, user_to_change):
        """
        Cambia el rol de un usuario en el grupo.
        """
        if from_user_alias not in self.admins:
            print(f"El usuario {from_user_alias} no puede cambiar el rol del usuario {user_to_change} porque no es administrador del grupo.")
            return
        if user_to_change in self.users:
            if user_to_change in self.admins:
                self.admins.remove(user_to_change)
                print(f"El rol del usuario {user_to_change} se cambió a no administrador.")
            else:
                self.admins.append(user_to_change)
                print(f"El rol del usuario {user_to_change} se cambió a administrador.")

            return
        
        print(f"El usuario {user_to_change} no está en el grupo {self.group_id}")
        

    def add_event(self, event, user):
        """
        Agrega un evento al grupo.
        """
        self.waiting_events.append(event.event_id)
        print(f"Evento {event.event_id} agregado correctamente al grupo {self.group_id}")

    def confirm_event(self, event, user):
        if user not in self.admins:
            print(f"El usuario {user} no puede confirmar eventos en el grupo {self.group_id} porque no es administrador.")
            return False

        if event in self.waiting_events:
            self.waiting_events.remove(event)
            self.events.append(event)
            print(f"Evento {event} confirmado por el usuario {user}")
            return True

        print(f"El evento {event} no está en la lista de eventos pendientes del grupo {self.group_id}")
        return False

    def reject_event(self, event, user):
        if user not in self.admins:
            print(f"El usuario {user} no puede rechazar eventos en el grupo {self.group_id} porque no es administrador.")
            return False

        if event in self.waiting_events:
            self.waiting_events.remove(event)
            print(f"Evento {event} rechazado por el usuario {user}")
            return True

        print(f"El evento {event} no está en la lista de eventos pendientes del grupo {self.group_id}")
        return False
    def set_event(self, event, **fields):
        """
        Modifica un evento existente.
        """
        if not fields['user'] in self.admins:
            print(f"El usuario {fields['user']} no puede modificar el evento {event.event_id}")
            return None
        if event.event_id not in self.events:
            print(f"El evento {event.event_id} no existe.")
            return None
        return Event(
            from_user=fields['user'] or event.from_user,
            title=fields['title'] or event.title,
            date=fields['date'] or event.date,
            place=fields['place'] or event.place,
            start_time=fields['start_time'] or event.start_time,
            end_time=fields['end_time'] or event.end_time,
            group_id=self.group_id,
            id=event.event_id
        )


    def remove_event(self, event):
        """
        Elimina un evento del grupo.
        """
        if event.event_id in self.events:
            self.events.remove(event.event_id)
            print(f"Evento {event.event_id} eliminado correctamente del grupo {self.group_id}")

        if event.event_id in self.waiting_events:
            self.waiting_events.remove(event.event_id)
            print(f"Evento {event.event_id} eliminado correctamente del grupo {self.group_id}")
    
    def add_user(self, from_user_alias, user_to_add):
        """
        Agrega un usuario al grupo.
        """
        self.users.append(user_to_add)
        print(f"Usuario {user_to_add} agregado correctamente al grupo {self.group_id}")
    

    def remove_user(self, from_user_alias, user_to_remove):
        """
        Elimina un usuario del grupo.
        """

        if from_user_alias in self.admins and user_to_remove.alias in self.users:
            self.users.remove(user_to_remove.alias)
            user_to_remove.remove_from_group(self.group_id)
            print(f"Usuario {user_to_remove.alias} eliminado correctamente del grupo {self.group_id}") 

            if user_to_remove.alias in self.admins:
                self.admins.remove(user_to_remove.alias)
                
            return True
        
        print(f"El usuario {from_user_alias} no puede eliminar usuarios porque no es administrador del grupo {self.group_id}")
        
        return False
    
    def accepted_request(self, request):
        """
        Procesa una solicitud aceptada.
        """
        if request.request_id in self.requests:
            request_type = request.get_type()
            request.count += 1
            
            if request.count == request.max_users:                          
                user_alias = request.to_user
                self.users.append(user_alias)
                self.waiting_users.remove(user_alias)
                request.status = 'accepted'

        return None
    
    def rejected_request(self, request):
        """
        Procesa una solicitud rechazada.
        """
        if request.request_id in self.requests:
            user_alias = request.to_user
            self.waiting_users.remove(user_alias)
            request.status = 'rejected'
            return request
        
        
    
    def change_group_type(self, author_id, admins, users):
        """
        Procesa una solicitud rechazada.
        """
        if author_id not in self.admins:
            print(f"No puedes cambiar el tipo del grupo {self.group_id} porque no eres administrador.")
            return None, None
        
        new_group = IndependentGroup(self.group_name, self.group_id)

        new_group.events = self.events
        new_group.users = self.users

        return None, new_group
    
    def dicc(self):
        """
        Devuelve un diccionario que representa el grupo.
        """
        return {'class':'group',
                'id':self.group_id,
                'type':self.get_type(), 
                "name":self.group_name,
                'events':self.events,                
                'users':self.users,
                'requests': self.requests,
                'waiting_users':self.waiting_users,
                'admins':self.admins}

class GlobalGroup(Group):
    def __init__(self, name, id=None) -> None:
        super().__init__(name, id)
        self.users = []  # Inicializa la lista de usuarios

    def get_type(self):
        return "global"

    def add_user(self, from_user_alias, user_to_add):
        """
        Agrega un usuario al group global. No se requiere autorización.
        """
        if user_to_add.alias not in self.users:
            self.users.append(user_to_add.alias)
            print(f"User {user_to_add.alias} successfully added to global group.")
            print(self.users)
        else:
            print(f"User {user_to_add.alias} already exists in the global group.")
        return None

    def remove_user(self, from_user_alias, user_to_remove):
        """
        Elimina un usuario del group global. No se requiere autorización.
        """
        if user_to_remove.alias in self.users:
            self.users.remove(user_to_remove.alias)
            print(f"User {user_to_remove.alias} successfully removed from global group.")
        else:
            print(f"User {user_to_remove.alias} does not exist in the global group.")
        return None

    def dicc(self):
        return {'class': 'group',
                'id': self.group_id,
                'type': self.get_type(),
                'name': self.group_name,
                'users': self.users}

    def add_event(self,event):
        pass                

    def remove_event(self, time,date,start_time,end_time, users):
        pass

    def change_group_type(self):
        pass

    def change_group_type(self):
        pass

    def __repr__(self) -> str:
        return self.users
    
    def __str__(self) -> str:
        return self.users
    



