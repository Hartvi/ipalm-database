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
    MASS = 'mass'  # mean, std, unit
    VOLUME = 'volume'  # mean, std, unit
    DENSITY = 'density'  # mean, std, unit
    STIFFNESS = 'stiffness'  # hooke's coefficient - mean, std, unit
    YOUNGS_MODULUS = 'youngs_modulus'  # mean, std, unit
    XDIM = 'xdim'  # mean, std, unit
    YDIM = 'ydim'  # mean, std, unit
    ZDIM = 'zdim'  # mean, std, unit
    TABLEFRICTION = 'tablefriction'  # mean, std, unit, other material
    MATERIAL = 'material'  # {mat1: {mean, std, unit}, mat2: {mean, std, unit}, ... }
    MODEL = 'model'  # point-like: 3d mesh, texture


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

