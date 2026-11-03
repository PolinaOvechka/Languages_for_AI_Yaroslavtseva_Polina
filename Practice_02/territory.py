
from units import Stalker
from game_text import GameText

class Territory:
    def __init__(self, name, symbol):
        'Характеристики ландшафта'
        self.name = name
        self.symbol = symbol

    def on_enter(self, unit):
        pass

    def on_leave(self, unit):
        pass


class Road(Territory):
    'Дорога'
    def __init__(self):
        super().__init__("Дорога", "▪")


class Forest(Territory):
    'Лес'
    def __init__(self):
        super().__init__("Лес", "▲")

    # Получение бонуса брони
    def on_enter(self, unit):
        if not getattr(unit, "forest_bonus", False):
            unit.armor += 10
            unit.forest_bonus = True
            GameText.event(f"{unit.name} получает +10 брони в лесу!", "success")

    # Удаление бонуса при выходе
    def on_leave(self, unit):
        if getattr(unit, "forest_bonus", False):
            unit.armor -= 10
            unit.forest_bonus = False


class Radiation(Territory):
    'Радиация'
    def __init__(self):
        super().__init__("Радиация", "!")

    def on_enter(self, unit):
        # сталкеры получают меньше урона от радиации
        damage = 5 if isinstance(unit, Stalker) else 10

        unit.health = max(0, unit.health - damage)

        GameText.event(
            f"{unit.name} получает {damage} урона от радиации!",
            "danger"
        )
