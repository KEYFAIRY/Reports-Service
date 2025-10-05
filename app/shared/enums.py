from enum import Enum

class Figure(Enum):
    BLANCA = 0.5
    NEGRA = 1
    CORCHEA = 2

    @classmethod
    def to_str(cls, value):
        mapping = {
            cls.BLANCA.value: "Blanca",
            cls.NEGRA.value: "Negra",
            cls.CORCHEA.value: "Corchea",
        }
        return mapping.get(value, "Desconocido")