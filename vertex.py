from dataclasses import dataclass, fields

@dataclass
class Vertex():
    id: int
    barcode: int
    x: float
    y: float
    z: float
    t: float
    numIncomingParticles: int
    numOutgoingParticles: int

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))