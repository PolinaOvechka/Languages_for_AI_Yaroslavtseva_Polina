
from game_text import GameText

class Unit:
    def __init__(self, name, health, armor, attack, x=0, y=0):
        ' Основные характеристики юнита ' 
        self.name = name
        self.health = health
        self.max_health = health
        self.armor = armor
        self.attack = attack

        # Положение на игровом поле
        self.x = x
        self.y = y
        self.base = None


    def move(self, x, y):
        'Изменение координат юнита' 
        self.x = x
        self.y = y


    def take_damage(self, damage):
        " Получение урона с учетом брони"
        actual_damage = max(1, damage - self.armor // 5)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

   
    def attack_target(self, target, bonus=0):
        ' Атака другого юнита'
        damage = target.take_damage(self.attack + bonus)
        kind = "danger" if self.base is None else "attack"

        GameText.event(
            f"{self.name} атакует {target.name}! Урон: {damage}",
            kind
        )
        return damage
    
    
    def use_ability(self, target=None, field=None):
        'использование абилок'
        return False


    def __add__(self, obj):
        'Перегрузка оператора сложения'
        if hasattr(obj, "interact"):
            return obj.interact(self)

        return NotImplemented


    def show_info(self):
        ' Вывод характеристик юнита '
        print("Юнит:", self.name)
        print("Здоровье:", self.health, "/", self.max_health)
        print("Броня:", self.armor)
        print("Атака:", self.attack)
        print("Координаты:", self.x, self.y)


# БОЙЦЫ
class Fighter(Unit):
    ' Бойцы '
    def __init__(self, name, health, armor, attack, x=0, y=0):
        super().__init__(name, health, armor, attack, x, y)

    def use_ability(self, target=None, field=None):
        'усиленная атака (бойцы)'
        if target is None or target.health <= 0:
            return False

        self.attack_target(target, 15)
        return True

class Assault(Fighter):
    ' Штурмовик '
    ability_description = (
    "Пассивно: обзор 2 клетки, передвижение на 1 клетку.\n"
    "Способность: усиленная атака по соседнему зомби.\n"
    "Урон: 55 вместо 40. Стоимость: 5 ресурсов."
)

    def __init__(self, x=0, y=0):
        super().__init__("Штурмовик", 120, 30, 40, x, y)
        self.symbol = "Ш"

class Sniper(Fighter):
    ' снайпер '
    ability_description = (
    "Пассивно: обзор 2 клетки, дальность атаки 3 клетки.\n"
    "Способность: усиленный выстрел на расстоянии до 3 клеток.\n"
    "Урон: 75 вместо 60. Стоимость: 5 ресурсов."
)

    def __init__(self, x=0, y=0):
        super().__init__("Снайпер", 80, 10, 60, x, y)
        self.symbol = "С"


# САППОРТЫ
class Support(Unit):
    ' саппорты '
    def __init__(self, name, health, armor, attack, x=0, y=0):
        super().__init__(name, health, armor, attack, x, y)

class Medic(Support):
    ' медик '
    ability_description = (
    "Пассивно: обзор 2 клетки, передвижение на 1 клетку.\n"
    "Способность: лечение союзника на соседней клетке.\n"
    "Восстанавливает до 10 HP, не превышая максимум.\n"
    "Лечение бесплатно, но расходует ход."
)

    def __init__(self, x=0, y=0):
        super().__init__("Медик", 80, 10, 15, x, y)
        self.symbol = "М"
            
    def heal(self, target):
        'хилящий спелл'
        old_health = target.health
        target.health = min(target.max_health, target.health + 10)

        restored = target.health - old_health
        GameText.event(
            f"{self.name} лечит {target.name}. "
            f"Восстановлено здоровья: {restored}",
            "success"
        )
    def use_ability(self, target=None, field=None):
        'вызов хила'
        if target is None or target.health <= 0:
            return False

        if target.health >= target.max_health:
            print("Союзник не нуждается в лечении.")
            return False

        self.heal(target)
        return True

class Engineer(Support):
    ' инженер '
    ability_description = (
    "Пассивно: обзор 2 клетки, передвижение на 1 клетку.\n"
    "Способность: ремонт убежища с соседней клетки.\n"
    "Восстанавливает до 10 HP прочности убежища.\n"
    "Ремонт бесплатный, но расходует ход."
)

    def __init__(self, x=0, y=0):
        super().__init__("Инженер", 100, 20, 20, x, y)
        self.symbol = "И"

    def repair(self, base):
        'ремонт базы'
        old_health = base.health
        base.health = min(500, base.health + 10)

        restored = base.health - old_health
        GameText.event(
            f"Инженер ремонтирует убежище! "
            f"Восстановлено прочности: {restored}",
            "success"
        )

    def use_ability(self, target=None, field=None):
        'вызов ремонта'
        if target is None:
            return False

        if target.health >= 500:
            print("Убежище не нуждается в ремонте.")
            return False

        self.repair(target)
        return True


# РАЗВЕДЧИКИ
class Scout(Unit):
    ' разведчики '
    def __init__(self, name, health, armor, attack, x=0, y=0):
        super().__init__(name, health, armor, attack, x, y)

    def use_ability(self, target=None, field=None):
        'разведка территории (разведчики)'
        if field is None:
            return False
        
        print()
        print(self.name, "внимательно осматривает пустошь...")
        return True

class Tracker(Scout):
    ' разведчик '
    ability_description = (
    "Пассивно: обзор 4 клетки, передвижение до 2 клеток по прямой.\n"
    "Способность: сканирование предметов в радиусе 3 клеток.\n"
    "Раскрывает их типы (аптечка, припасы, ловушка, броня).\n"
    "Стоимость: бесплатно, но расходует ход."
)

    def __init__(self, x=0, y=0):
        super().__init__("Разведчик", 90, 15, 25, x, y)
        self.symbol = "Р"
    
    def use_ability(self, target=None, field=None):
        'сканирование неизвестных предметов'
        if field is None:
            return set()

        found_items = set()

        for y in range(field.height):
            for x in range(field.width):
                distance = abs(self.x - x) + abs(self.y - y)

                if distance <= 3 and field.items[y][x] is not None:
                    found_items.add((x, y))

        print()
        print("Разведчик активирует сканер...")

        if found_items:
            for x, y in sorted(found_items):
                item = field.items[y][x]
                print(item.name, "- координаты:", x, y)
        else:
            print("Поблизости не обнаружено предметов.")

        return found_items

class Stalker(Scout):
    ' дозорный '
    ability_description = (
    "Пассивно: обзор 4 клетки, передвижение на 1 клетку.\n"
    "Получает 5 урона от радиации вместо 10.\n"
    "Способность: разведка территории в радиусе 6 клеток.\n"
    "Открывает местность, но не определяет типы предметов."
)

    def __init__(self, x=0, y=0):
        super().__init__("Дозорный", 100, 20, 30, x, y)
        self.symbol = "Д"

