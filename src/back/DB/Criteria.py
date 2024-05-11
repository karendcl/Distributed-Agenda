from abc import ABC

class ICriteria(ABC):
    def __call__(self, registro):
        pass

class IDCriteria(ICriteria):
    def __init__(self, id_value):
        self.id_value = id_value

    def __call__(self, registro):
        # Comprueba si el registro tiene el ID especificado
        return registro.get('id') == self.id_value