import contextlib
import io
import random
from field import GameField
from base import Base
from units import Assault, Sniper, Tracker, Stalker, Medic, Engineer
from enemies import Zombie, zombie_turn
from objects import Medkit, Supplies, Trap, Armor
from territory import Road, Forest, Radiation
from game_text import messages
from instance_counter import InstanceCounter


class Game:
    def __init__(self):
        'создание игры'
        # создание поля
        self.field = GameField(20, 20)
        self.field.generate_territory()

        # создание убежища
        self.base = Base(3, 3)
        self.field.add_object(3, 3, self.base)

        # доступные типы юнитов
        self.unit_classes = [
            Assault, Sniper, Tracker, Stalker, Medic, Engineer
        ]

        # начальный отряд
        with contextlib.redirect_stdout(io.StringIO()):
            self.base.create_unit(Assault, self.field, 2, 3)
            self.base.create_unit(Sniper, self.field, 4, 3)
            self.base.create_unit(Tracker, self.field, 3, 2)
            self.base.create_unit(Stalker, self.field, 3, 4)
            self.base.create_unit(Medic, self.field, 2, 2)
            self.base.create_unit(Engineer, self.field, 4, 4)

        # случайное размещение предметов
        self.field.generate_items({
            Medkit: 6,
            Supplies: 8,
            Trap: 5,
            Armor: 5
        })

        # случайное размещение зомби
        self.total_zombies = 8
        self.spawn_zombies(self.total_zombies)

        # Клетки, которые выжившие уже исследовали
        self.explored_cells = set()

        # Предметы, распознанные сканером
        self.identified_items = set()

        # Счётчик ходов
        self.turn_count = 0

        # Запоминание расстояний до зомби
        self.zombie_proximity = {}


    def reveal_area(self, unit, radius):
        'открытие территории вокруг юннита'
        cells = set()

        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.distance(unit.x, unit.y, x, y) <= radius:
                    cells.add((x, y))

        self.explored_cells.update(cells)
        return cells

    def visible_cells(self):
        'территория, которую видно прямо сейчас'
        visible = set()

        # Обзор вокруг убежища
        visible.update(self.reveal_area(self.base, 2))

        for unit in self.base.units:
            # У разведчиков обзор больше
            if isinstance(unit, (Tracker, Stalker)):
                radius = 4 
            else: 
                radius =2
            visible.update(self.reveal_area(unit, radius))

        return visible

    def get_statistics(self):
        'сбор статистики'
        zombies_left = 0

        for row in self.field.grid:
            for obj in row:
                if isinstance(obj, Zombie):
                    zombies_left += 1

        total_cells = self.field.width * self.field.height

        explored_percent = round(
            len(self.explored_cells) / total_cells * 100
        )

        return {
            "turns": self.turn_count,
            "zombies_left": zombies_left,
            "zombies_killed": self.total_zombies - zombies_left,
            "zombie_instances": InstanceCounter.instances,
            "survivors": len(self.base.units),
            "resources": self.base.resources,
            "base_health": self.base.health,
            "explored_percent": explored_percent
        }


    def distance(self, x1, y1, x2, y2):
        'расстояние между клетками'
        return abs(x1 - x2) + abs(y1 - y2)

    def valid_coordinates(self, x, y):
        'проверка координат'
        return 0 <= x < self.field.width and 0 <= y < self.field.height

    def get_object(self, x, y):
        'объект по координатам'
        if not self.valid_coordinates(x, y):
            return None

        return self.field.grid[y][x]


    def spawn_zombies(self, count):
        'спавн зомби'
        available_cells = []

        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.distance(x, y, self.base.x, self.base.y) < 6:
                    continue

                if self.get_object(x, y) is not None:
                    continue

                if self.field.items[y][x] is not None:
                    continue

                available_cells.append((x, y))

        random.shuffle(available_cells)

        for x, y in available_cells[:count]:
            self.field.add_object(x, y, Zombie())


    def set_zombie_count(self, count):
        'изменение количества зомби'

        if count > self.field.max_objects:
            print("Ошибка! Слишком большое количество зомби.")
            return False

        # Текущее количество зомби
        current_count = self.get_statistics()["zombies_left"]

        # Если нужно добавить зомби
        if count > current_count:
            difference = count - current_count
            self.spawn_zombies(difference)

        # Если нужно убрать зомби
        elif count < current_count:
            difference = current_count - count

            for y in range(self.field.height):
                for x in range(self.field.width):
                    obj = self.field.grid[y][x]

                    if isinstance(obj, Zombie):
                        self.field.remove_object(x, y)
                        difference -= 1

                        if difference == 0:
                            break

                if difference == 0:
                    break

        # Пересчитываем количество зомби
        new_count = self.get_statistics()["zombies_left"]

        # Сохраняем статистику уничтоженных зомби
        killed = self.total_zombies - current_count
        self.total_zombies = killed + new_count

        print("Теперь на карте зомби:", new_count)

        if new_count != count:
            print("Не удалось разместить всех зомби: недостаточно свободных клеток.")

        return new_count == count
            


    def check_death(self, unit):
        'проверка смерти'
        if unit.health > 0:
            return False

        print(unit.name, "погиб!")

        self.field.remove_object(unit.x, unit.y)

        if unit.base is not None:
            unit.base.remove_unit(unit)

        return True


    def move_unit(self, unit, x, y):
        'перемещение выжившего'
        if unit not in self.base.units:
            print("Юнит недоступен!")
            return False

        if not self.valid_coordinates(x, y):
            print("Координаты за пределами карты!")
            return False

        steps = self.distance(unit.x, unit.y, x, y)
        if isinstance(unit, Tracker):
            max_steps = 2
        else:
            max_steps = 1

        if steps < 1 or steps > max_steps:
            print("Недопустимая дальность перемещения!")
            return False

        if self.get_object(x, y) is not None:
            print("Конечная клетка занята!")
            return False

        # 2 шага только для разведчика по прямой
        if steps == 2:
            if unit.x != x and unit.y != y:
                print("Можно сделать два шага только по прямой!")
                return False

            dx = (x > unit.x) - (x < unit.x)
            dy = (y > unit.y) - (y < unit.y)

            middle_x = unit.x + dx
            middle_y = unit.y + dy

            if self.get_object(middle_x, middle_y) is not None:
                print("Путь перекрыт другим персонажем!")
                return False

            # Первый шаг
            self.field.move_object(
                unit.x, unit.y, middle_x, middle_y, self.base
            )

            # Если юнит погиб, действие уже было совершено
            if unit.health <= 0:
                return True

        # Обычное движение или второй шаг разведчика
        moved = self.field.move_object(
            unit.x, unit.y, x, y, self.base
        )

        if unit.health <= 0:
            return True

        if not moved:
            return False

        print()
        messages.event(
            f"{unit.name} переместился на клетку ({x}, {y}).",
            "info"
        )

        self.describe_surroundings(unit)
        messages.character(unit, "move")

        return True


    def attack_enemy(self, unit, x, y):
        'обычная атака'
        # Нельзя атаковать невидимую цель
        if (x, y) not in self.visible_cells():
            print("Цель находится вне зоны видимости!")
            return False
        
        target = self.get_object(x, y)

        if not isinstance(target, Zombie):
            print("На выбранной клетке нет зомби!")
            return False

        if isinstance(unit, Sniper):
            attack_range = 3
        else:
            attack_range = 1

        if self.distance(unit.x, unit.y, x, y) > attack_range:
            print("Противник слишком далеко!")
            return False

        unit.attack_target(target)
        messages.character(unit, "attack")
        self.check_death(target)
        return True


    def use_ability(self, unit, x=None, y=None):
        'использование абилок'
        # Сканирование предметов Разведчиком
        if isinstance(unit, Tracker):
            found_items = unit.use_ability(field=self.field)
            messages.character(unit, "ability")

            self.identified_items.update(found_items)
            return True

        # Разведка территории Дозорным
        if isinstance(unit, Stalker):
            result = unit.use_ability(field=self.field)
            if result:
                messages.character(unit, "ability")

            if result:
                self.reveal_area(unit, 6)
                self.describe_surroundings(unit, 6)

            return result


        if isinstance(unit, Engineer):
            if self.distance(unit.x, unit.y, self.base.x, self.base.y) > 1:
                print("Инженер слишком далеко от убежища!")
                return False

            result = unit.use_ability(target=self.base)
            if result:
                messages.character(unit, "ability")

            return result

        # цель для прочих персонажей
        if x is None or y is None:
            print("Не выбрана цель способности!")
            return False

        target = self.get_object(x, y)

        if target is None:
            print("На выбранной клетке нет подходящей цели!")
            return False

        # Усиленная атака бойцов
        if isinstance(unit, (Assault, Sniper)):
            if (x, y) not in self.visible_cells():
                    print("Цель находится вне зоны видимости!")
                    return False
            
            if not isinstance(target, Zombie):
                print("Атаковать можно только зомби!")
                return False

            if isinstance(unit, Sniper):
                attack_range = 3 
            else:
                attack_range = 1

            if self.distance(unit.x, unit.y, x, y) > attack_range:
                print("Противник слишком далеко!")
                return False

            # Стоимость усиленной атаки
            ability_cost = 5

            if self.base.resources < ability_cost:
                print("Недостаточно ресурсов для усиленной атаки!")
                return False

            result = unit.use_ability(target=target)
            if result:
                messages.character(unit, "attack")

            if result:
                self.base.resources -= ability_cost
                print("Потрачено ресурсов:", ability_cost)
                self.check_death(target)

            return result

        # Хил медика
        if isinstance(unit, Medic):
            if target not in self.base.units:
                print("Лечить можно только союзников!")
                return False

            if self.distance(unit.x, unit.y, x, y) > 1:
                print("Союзник слишком далеко!")
                return False

            result = unit.use_ability(target=target)
            if result:
                messages.character(unit, "ability")

            return result

        return False


# УДАЛЕНИЕ И ДОБАВЛЕНИЕ ЮНИТОВ
    def create_unit(self, unit_class, x, y):
        'создание юнита'
        if not self.valid_coordinates(x, y):
            print("Координаты за пределами карты!")
            return False

        if self.distance(x, y, self.base.x, self.base.y) != 1:
            print("Создавать юнитов можно только рядом с убежищем!")
            return False

        if self.field.items[y][x] is not None:
            print("Клетка занята предметом!")
            return False

        return self.base.create_unit(
            unit_class, self.field, x, y
        )

    def remove_unit(self, unit):
        'удаление юнита'
        if unit not in self.base.units:
            return False

        self.field.remove_object(unit.x, unit.y)
        return self.base.remove_unit(unit)


# КОНЕЦ ХОДА
    def finish_turn(self, success):
        'конец хода игрока'
        if success:
            self.turn_count += 1
            zombie_turn(self.field, self.base)

            if self.base.health > 0 and self.base.units:
                self.warn_zombies()

    def check_game_end(self):
            'проверка окончания игры'
            if self.base.health <= 0:
                return "base_destroyed"

            if not self.base.units:
                return "squad_destroyed"

            if self.get_statistics()["zombies_left"] == 0:
                return "victory"

            return None



# ОКРУЖАЮЩАЯ ОБСТАНОВКА ОПИСАНИЯ
    def get_direction(self, x1, y1, x2, y2):
        'определение направления'
        vertical = ""
        horizontal = ""

        if y2 < y1:
            vertical = "сверху"
        elif y2 > y1:
            vertical = "снизу"

        if x2 < x1:
            horizontal = "слева"
        elif x2 > x1:
            horizontal = "справа"

        if vertical and horizontal:
            return vertical + " и " + horizontal

        return vertical or horizontal or "рядом"

    def describe_surroundings(self, unit, radius=None):
        'описания'
        if radius is None:
            if isinstance(unit, (Tracker, Stalker)):
                radius = 4
            else:
                radius = 2

        territory = self.field.territory[unit.y][unit.x]

        # Описание ландшафта
        if isinstance(territory, Forest):
            descriptions = [
                "Лес встречает выжившего зловещей тишиной.",
                "Ветер шевелит ветви мёртвых деревьев.",
                "Сквозь густые заросли едва пробивается свет.",
                "Под ногами хрустят сухие ветви."
            ]

        elif isinstance(territory, Radiation):
            descriptions = [
                "Счётчик Гейгера отчаянно трещит.",
                "Воздух кажется тяжёлым и опасным.",
                "Здесь даже тишина кажется отравленной.",
                "Вокруг виднеются следы радиоактивного заражения."
            ]

        else:
            descriptions = [
                "Под ногами тянется потрескавшаяся дорога.",
                "Пустынная дорога уходит за горизонт.",
                "Ветер гонит пыль по разрушенному асфальту.",
                "Ничто не нарушает тишину заброшенной дороги."
            ]

        messages.event(random.choice(descriptions), "atmosphere")

        # Поиск ближайших объектов
        closest = {}

        for y in range(self.field.height):
            for x in range(self.field.width):
                dist = self.distance(unit.x, unit.y, x, y)

                if dist == 0 or dist > radius:
                    continue

                obj = self.field.grid[y][x]
                item = self.field.items[y][x]
                terrain = self.field.territory[y][x]

                kinds = []

                if isinstance(obj, Zombie):
                    kinds.append("zombie")

                if item is not None:
                    kinds.append("item")

                if isinstance(terrain, Radiation):
                    kinds.append("radiation")

                for kind in kinds:
                    if kind not in closest or dist < closest[kind][0]:
                        closest[kind] = (dist, x, y)

        nearby_messages = {
            "zombie": [
                "доносится хриплый рык заражённого.",
                "слышны тяжёлые, волочащиеся шаги.",
                "раздаётся нечеловеческий стон."
            ],
            "radiation": [
                "слышится треск радиоактивного заражения.",
                "заметны признаки радиационной опасности.",
                "воздух кажется подозрительно нездоровым."
            ],
            "item": [
                "замечен неизвестный предмет.",
                "среди обломков виднеется что-то необычное.",
                "на земле лежит что-то, что стоит проверить."
            ]
        }

        for kind in ["zombie", "radiation", "item"]:
            if kind in closest:
                dist, x, y = closest[kind]
                direction = self.get_direction(
                    unit.x, unit.y, x, y
                )

                message = (direction.capitalize() + " " + random.choice(nearby_messages[kind]))
                if kind != "item":
                    color = "warning"
                else:
                    color = "info"
                messages.event(message, color)

        if not closest:
            print("Поблизости ничего подозрительного не обнаружено.")


    def warn_zombies(self):
        'рык зомби (приближение врага)'
        current_proximity = {}

        for row in self.field.grid:
            for zombie in row:
                if not isinstance(zombie, Zombie):
                    continue

                if not self.base.units:
                    continue

                # Поиск ближайшего к зомби выжившего
                unit = self.base.units[0]

                min_distance = self.distance(
                    unit.x, unit.y, zombie.x, zombie.y
                )

                for survivor in self.base.units:
                    distance = self.distance(
                        survivor.x, survivor.y, zombie.x, zombie.y
                    )

                    if distance < min_distance:
                        min_distance = distance
                        unit = survivor

                dist = self.distance(
                    unit.x, unit.y, zombie.x, zombie.y
                )

                old_dist = self.zombie_proximity.get(zombie)
                current_proximity[zombie] = dist

                # Предупреждение при приближении
                if dist <= 3 and (old_dist is None or dist < old_dist):
                    direction = self.get_direction(
                        unit.x, unit.y, zombie.x, zombie.y
                    )

                    warnings = [
                        "слышится низкий утробный рык!",
                        "раздаются шаркающие шаги заражённого!",
                        "раздаётся зловещий хрип!"
                    ]

                    print()
                    print(
                        unit.name + " слышит:",
                        direction,
                        random.choice(warnings)
                    )

        self.zombie_proximity = current_proximity


# ЗАПУСК ИГРЫ
    def run(self):
        'запуск игры'
        from game_menu import GameMenu

        menu = GameMenu(self)
        menu.run()
