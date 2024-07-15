from abc import ABC, abstractmethod

class CalendarEvent(ABC):
    """
    Clase abstracta para eventos en una agenda.

    Define los atributos y métodos comunes a todos los tipos de eventos.
    """

    @abstractmethod
    def __init__(self, title, description, date, start_time, end_time, participants, groups):
        """
        Inicializa un nuevo evento.

        Args:
               title (str): El título del evento.
                description (str): La descripción del evento.
                date (date): La fecha del evento.
                start_time (time): La hora de inicio del evento.
                end_time (time): La hora de finalización del evento.
                participants (list): Una lista de usuarios que participarán en el evento.
                groups (list): Una lista de grupos a los que pertenece el evento
        """
        pass

    @abstractmethod
    def __eq__(self, other_event) -> bool:
        """
        Compara dos eventos por su ID.

        Args:
            other_event (CalendarEvent): El otro evento para comparar.

        Returns:
            bool: True si los IDs de los eventos son iguales, False en caso contrario.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Devuelve una representación de cadena del evento.

        Returns:
            str: Una cadena que representa el evento.
        """
        pass

    @abstractmethod
    def dicc(self):
        """
        Devuelve un diccionario que representa el evento.

        Returns:
            dict: Un diccionario con los atributos del evento.
        """
        pass

class Event(CalendarEvent):

    def __init__(self, title, description, date, start_time, end_time, participants, groups):
        """
        Inicializa un nuevo evento.

        Args:
               title (str): El título del evento.
                description (str): La descripción del evento.
                date (date): La fecha del evento.
                start_time (time): La hora de inicio del evento.
                end_time (time): La hora de finalización del evento.
                participants (list): Una lista de usuarios que participarán en el evento.
                groups (list): Una lista de grupos a los que pertenece el evento
        """
        self.title = title
        self.description = description
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.participants = participants
        self.groups = groups
        self.event_id = str(hash(title+str(date)+str(start_time)+str(end_time)+str(participants)+str(groups)))
        self.confirmed = False
        self.rejected = False
        self.pending_confirmations_people = participants.copy()
        self.pending_confirmations_groups = groups.copy()


    def user_confirm(self, user):
        """
        Confirma la asistencia de un usuario al evento.

        Args:
            user (str): El alias del usuario que confirma asistencia.
        """
        if user in self.pending_confirmations_people:
            self.pending_confirmations_people.remove(user)
            print(f"User {user} confirmed attendance to event {self.title}")
        else:
            print(f"User {user} is not pending confirmation for event {self.title}")

        self.confirm()
    def user_reject(self, user):
        """
        Rechaza la asistencia de un usuario al evento.

        Args:
            user (str): El alias del usuario que rechaza asistencia.
        """
        if user in self.pending_confirmations_people:
            self.pending_confirmations_people.remove(user)
            self.rejected = True
            print(f"User {user} rejected attendance to event {self.title}")
        else:
            print(f"User {user} is not pending confirmation for event {self.title}")

    def group_confirm(self, group):
        """
        Confirma la asistencia de un grupo al evento.

        Args:
            group (str): El nombre del grupo que confirma asistencia.
        """
        if group in self.pending_confirmations_groups:
            self.pending_confirmations_groups.remove(group)
            print(f"Group {group} confirmed attendance to event {self.title}")
        else:
            print(f"Group {group} is not pending confirmation for event {self.title}")

        self.confirm()

    def group_reject(self, group):
        """
        Rechaza la asistencia de un grupo al evento.

        Args:
            group (str): El nombre del grupo que rechaza asistencia.
        """
        if group in self.pending_confirmations_groups:
            self.pending_confirmations_groups.remove(group)
            self.rejected = True
            print(f"Group {group} rejected attendance to event {self.title}")
        else:
            print(f"Group {group} is not pending confirmation for event {self.title}")

    def confirm(self):
        """
        Confirma la asistencia de todos los participantes al evento.
        """
        if len(self.pending_confirmations_people) == 0 and len(self.pending_confirmations_groups) == 0 and not self.rejected:
            self.confirmed = True
            print(f"All participants confirmed attendance to event {self.title}")
        else:
            print(f"Not all participants have confirmed attendance to event {self.title}")


    def __eq__(self, other_event) -> bool:
        """
        Compara dos eventos por su ID.

        Args:
            other_event (CalendarEvent): El otro evento para comparar.

        Returns:
            bool: True si los IDs de los eventos son iguales, False en caso contrario.
        """
        if isinstance(other_event, Event):
            return self.event_id == other_event.event_id
        return False
    
    def __str__(self) -> str:
        """
        Devuelve una representación de cadena del evento.

        Returns:
            str: Una cadena que representa el evento.
        """
        return f"{self.title}\n Date:{str(self.date)[:10]}\n Time: {str(self.start_time)[:5]}-{str(self.end_time)[:5]}\n"


    def dicc(self):
        """
        Devuelve un diccionario que representa el evento.

        Returns:
            dict: Un diccionario con los atributos del evento.
        """
        return {'class':'event',
                'title':self.title,
                'description':self.description,
                'date':str(self.date),
                'start_time':str(self.start_time),
                'end_time':str(self.end_time),
                'participants':self.participants,
                'groups':self.groups,
                'id':self.event_id,
                'confirmed':self.confirmed,
                'rejected':self.rejected,
                'pending_confirmations_people':self.pending_confirmations_people,
                'pending_confirmations_groups':self.pending_confirmations_groups
        }
        

    
