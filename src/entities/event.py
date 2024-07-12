from abc import ABC, abstractmethod

class CalendarEvent(ABC):
    """
    Clase abstracta para eventos en una agenda.

    Define los atributos y métodos comunes a todos los tipos de eventos.
    """

    @abstractmethod
    def __init__(self, from_user, title, date, place, start_time, end_time, workspace_id, id=None):
        """
        Inicializa un nuevo evento.

        Args:
            from_user (str): El alias del usuario que creó el evento.
            title (str): El título del evento.
            date (date): La fecha del evento.
            place (str): El lugar del evento.
            start_time (time): La hora de inicio del evento.
            end_time (time): La hora de finalización del evento.
            workspace_id (str): El ID del workspace al que pertenece el evento.
            id (str, optional): El ID único del evento. Si no se proporciona, se usa el título. Defaults to None.
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

    def __init__(self, creator, event_name, date, place, start_time, end_time, group_id, id=None):
        """
        Inicializa un nuevo evento.

        Args:
            creator (str): El alias del usuario que creó el evento.
            event_name (str): El nombre del evento.
            date (date): La fecha del evento.
            place (str): El lugar del evento.
            start_time (time): La hora de inicio del evento.
            end_time (time): La hora de finalización del evento.
            workspace_id (str): El ID del workspace al que pertenece el evento.
            id (str, optional): El ID único del evento. Si no se proporciona, se usa el título. Defaults to None.
        """
        self.creator = creator
        self.event_name = event_name
        self.date = date
        self.place = place
        self.start_time = start_time
        self.end_time = end_time
        self.group_id= group_id
        self.event_id = id or self.event_name

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
        return f"{self.title}\n ID:{self.event_id}\n Date:{str(self.date)[:10]}\n Place: {self.place}\n Time: {str(self.start_time)[:5]}-{str(self.end_time)[:5]}\n Group: {self.group_id}\n"
    
    def dicc(self):
        """
        Devuelve un diccionario que representa el evento.

        Returns:
            dict: Un diccionario con los atributos del evento.
        """
        return {'class':'event',
                'id':self.event_id,
                'from_user':self.from_user,
                'title':self.title,
                'date':str(self.date)[:10],
                'place':self.place,
                'start_time':str(self.start_time)[:5],
                'end_time':str(self.end_time)[:5],
                'group':self.group_id                
        }
        

    
