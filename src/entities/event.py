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
        self.pending_confirmations = participants.copy()


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
                'id':self.event_id
        }
        

    
