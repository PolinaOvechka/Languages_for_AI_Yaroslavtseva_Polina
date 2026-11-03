from units import Unit
import random
from game_text import messages
from instance_counter import InstanceCounter


class Enemy(Unit):
    'враги'
    def __init__(self, name, health, armor, attack, x=0, y=0):
        super().__init__(name, health, armor, attack, x, y)


class Zombie(Enemy):
    'зомби'
    def __init__(self, x=0, y=0):
        super().__init__("Зомби", 70, 0, 15, x, y)
        self.counter = InstanceCounter()
        self.symbol = "З"
        self.detection_radius = 7

    def distance_to(self, target):
        'расстояние до объекта'
        return abs(self.x - target.x) + abs(self.y - target.y)

    def find_target(self, base):
        'поиск ближайшей цели'
        targets = [base]

        for unit in base.units:
            if unit.health > 0:
                targets.append(unit)

        nearest = targets[0]
        min_distance = self.distance_to(nearest)

        for target in targets:
            distance = self.distance_to(target)

            if distance < min_distance:
                min_distance = distance
                nearest = target

        if self.distance_to(nearest) <= self.detection_radius:
            return nearest

        return None

    def move_randomly(self, field, target=None):
        'перемещение зомби'
        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        random.shuffle(directions)
        available = []

        for dx, dy in directions:
            x = self.x + dx
            y = self.y + dy

            if not (0 <= x < field.width and 0 <= y < field.height):
                continue

            if field.grid[y][x] is not None:
                continue

            available.append((x, y))

        if not available:
            return False

        if target is not None:
            # При обнаружении цели зомби приближается к ней
            old_distance = self.distance_to(target)

            closer = [
                (x, y) for x, y in available
                if abs(x - target.x) + abs(y - target.y) < old_distance
            ]

            if closer:
                available = closer
            else:
                # Не уходим от цели, если путь перекрыт
                return False

        x, y = random.choice(available)
        return field.move_object(self.x, self.y, x, y)

    def find_survivors(self, field):
        'поиск соседних выживших'
        survivors = []

        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        for dx, dy in directions:
            x = self.x + dx
            y = self.y + dy

            if not (0 <= x < field.width and 0 <= y < field.height):
                continue

            obj = field.grid[y][x]

            if obj is not None and getattr(obj, "base", None) is not None:
                if obj.health > 0:
                    survivors.append(obj)

        return survivors

    def attack_survivor(self, field, base):
        'атака выжившего или убежища'
        survivors = self.find_survivors(field)

        if survivors:
            target = survivors[0]

            for unit in survivors:
                if unit.health < target.health:
                    target = unit

            print()
            messages.event("Из темноты вырывается заражённый!", "warning")
            self.attack_target(target)

            if target.health <= 0:
                print(target.name, "погиб!")
                field.remove_object(target.x, target.y)
                base.remove_unit(target)

            return True

        # Если выживших рядом нет, атакуем убежище
        if self.distance_to(base) == 1:
            base.health = max(0, base.health - self.attack)

            print()
            messages.event("Зомби вцепился в укрепления убежища!", "danger")
            messages.event(f"Прочность убежища: {base.health}/500", "danger")
            return True

        return False

    def take_turn(self, field, base):
        'полный ход зомби'
        if self.health <= 0:
            return

        target = self.find_target(base)

        # Если цель уже рядом, зомби сразу атакует
        if not self.find_survivors(field) and self.distance_to(base) != 1:
            self.move_randomly(field, target)

        self.attack_survivor(field, base)

def zombie_turn(field, base):
    'ход всех зомби'
    zombies = []

    for row in field.grid:
        for obj in row:
            if isinstance(obj, Zombie):
                zombies.append(obj)

    for zombie in zombies:
        if zombie.health > 0 and base.health > 0:
            zombie.take_turn(field, base)