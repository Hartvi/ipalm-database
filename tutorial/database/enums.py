from enum import Enum


class ChoiceEnum(Enum):
    """
    General enum wrapper. E.g. inside a class definition
    # Encapsulation, we meet again.
    class Colors(ChoiceEnum):
        RED = 'red'
        WHITE = 'white'
        BLUE = 'blue'
    """
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


class DataFormats(ChoiceEnum):
    """
    Unused
    """
    # ["rgb", "bw", "depth", "json", "csv", "npy", "npz"]
    RGB = 'rgb'  # rgb_w_h, i.e. rgb_1280_720
    BW = 'bw'  # rgb_w_h, i.e. rgb_1280_720
    DEPTH = 'depth'  # rgb_w_h, i.e. rgb_1280_720
    JSON = 'json'
    CSV = 'csv'
    NPY = 'npy'
    NPZ = 'npz'


class PhysicalQuantities(ChoiceEnum):
    MASS = 'mass'
    VOLUME = 'volume'
    DENSITY = 'density'
    STIFFNESS = 'stiffness'  # hooke's coefficient
    XDIM = 'xdim'
    YDIM = 'ydim'
    ZDIM = 'zdim'
    TABLEFRICTION = 'tablefriction'
    MATERIAL = 'material'


class Units(ChoiceEnum):
    G = 'g'
    KG = 'kg'
    M3 = 'm^3'
    DM3 = 'dm^3'
    CM3 = 'cm^3'
    MM3 = 'mm^3'
    GCM_3 = 'g cm^-3'
    KGM_3 = 'kg m^-3'
    M = 'm'
    DM = 'dm'
    CM = 'cm'
    MM = 'mm'

