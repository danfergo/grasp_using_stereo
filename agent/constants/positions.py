from math import pi


class Positions:

    @staticmethod
    def start():
        return [0.52, 0, 0.30, pi, 0, pi/2]

    @staticmethod
    def down():
        return [0.52, 0.0, 0.037, pi, 0, 0]

    @staticmethod
    def pre_down():
        return [0.52, 0.0, 0.08, pi, 0, 0]

    @staticmethod
    def detect():
        return [0.4, 0, 0.4, pi, 0, 0]

    @staticmethod
    def gate_high():
        return [0.15, -0.18, 0.46, pi - pi / 6, pi / 5, 0]

    @staticmethod
    def gate_low():
        return [0.07, -0.18, 0.34, pi - pi / 6, pi / 6, 0]

    @staticmethod
    def drop_entrance():
        return [0.17, -0.27, 0.67, pi - pi / 3, 0, 0]

    @staticmethod
    def drop_final():
        return [0.09, -0.30, 0.70, pi - pi / 3, 0, 0]
