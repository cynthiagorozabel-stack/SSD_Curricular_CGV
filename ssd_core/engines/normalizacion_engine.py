# NOTA: Este motor no se usa en el pipeline principal. Puede eliminarse si no se requiere para otros procesos.

class NormalizacionEngine:
    def __init__(self, *args, **kwargs):
        pass
    def normalize(self, *args, **kwargs):
        raise NotImplementedError('NormalizacionEngine no implementado.')