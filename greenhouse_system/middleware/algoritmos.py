class ControladorPID:
    def __init__(self, kp=1.0, ki=0.1, kd=0.05):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._prev_error = 0
        self._integral = 0

    def calcular_ajuste(self, valor_actual, valor_deseado):
        error = valor_deseado - valor_actual
        self._integral += error
        derivada = error - self._prev_error
        self._prev_error = error
        ajuste = self.kp*error + self.ki*self._integral + self.kd*derivada
        return ajuste


class OptimizadorGeneticoSimple:
    def __init__(self, poblacion=10, generaciones=5):
        self.poblacion = poblacion
        self.generaciones = generaciones

    def optimizar_parametros(self, datos_sensores):
        media = sum(datos_sensores.values()) / len(datos_sensores)
        return {"param1": media, "param2": media*0.8}