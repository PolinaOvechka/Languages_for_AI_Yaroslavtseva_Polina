from game_text import GameText

class NeutralObject:
    'класс нейтральных объектов'
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def interact(self, unit):
        # Взаимодействие с юнитом
        pass


class Medkit(NeutralObject):
    'аптечка'
    def __init__(self):
        super().__init__("Аптечка", "+")

    def interact(self, unit):
        'Восстановление здоровья без превышения максимума'
        old_health = unit.health
        unit.health = min(unit.max_health, unit.health + 30)

        restored = unit.health - old_health
        GameText.event(f"{unit.name} восстанавливает {restored} HP!", "success")



class Supplies(NeutralObject):
    'припасы'
    def __init__(self):
        super().__init__("Припасы", "$")

    def interact(self, unit):
        GameText.event(f"{unit.name} нашёл 20 ресурсов!", "success")
        return 20


class Trap(NeutralObject):
    'ресурсы'
    def __init__(self):
        super().__init__("Ловушка", "X")

    def interact(self, unit):
        unit.health = max(0, unit.health - 20)
        GameText.event(f"{unit.name} попал в ловушку! -20 HP", "danger")


class Armor(NeutralObject):
    'броня'
    def __init__(self):
        super().__init__("Бронежилет", "#")

    def interact(self, unit):
        unit.armor += 15
        GameText.event(f"{unit.name} получает +15 брони!", "success")
