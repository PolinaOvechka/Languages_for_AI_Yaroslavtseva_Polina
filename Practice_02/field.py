import random
import copy
from territory import Road, Forest, Radiation
from units import Fighter, Scout, Support
from enemies import Enemy
from objects import Medkit, Supplies, Trap, Armor

class GameField:
    def __init__(self, width, height):
        'размеры поля'
        self.width = width
        self.height = height

        # Максимальное количество объектов
        self.max_objects = width * height
        self.object_count = 0

        self.grid = []

        for y in range(height):
            row = []

            for x in range(width):
                row.append(None)

            self.grid.append(row)

        # Создание карты ландшафта
        self.territory = []
        for y in range(height):
            row = []

            for x in range(width):
                row.append(Road())

            self.territory.append(row)

    
        # Создание массива предметов
        self.items = []
        for y in range(height):
            row = []

            for x in range(width):
                row.append(None)

            self.items.append(row)

    
    def add_object(self, x, y, obj):
        'добавление юнита'
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            print("Ошибка: координаты за пределами поля!")
            return False

        if self.object_count >= self.max_objects:
            print("Ошибка: поле заполнено!")
            return False

        if self.grid[y][x] is not None:
            print("Ошибка: клетка уже занята!")
            return False

        # размещение объекта на поле
        self.grid[y][x] = obj
        self.object_count += 1

        # обновление координат юнита
        if hasattr(obj, "x") and hasattr(obj, "y"):
            obj.x = x
            obj.y = y

        return True

   
    def remove_object(self, x, y):
        'удаление юнита'
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            print("Ошибка: координаты за пределами поля!")
            return False
        
        if self.grid[y][x] is None:
            print("Ошибка: клетка пустая!")
            return False

        self.grid[y][x] = None
        self.object_count -= 1

        return True


    def move_object(self, old_x, old_y, new_x, new_y, base=None):
        'перемещение юнита'
        if not (0 <= old_x < self.width and 0 <= old_y < self.height):
            print("Ошибка: неверные начальные координаты!")
            return False

        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            print("Ошибка: нельзя выйти за пределы поля!")
            return False

        obj = self.grid[old_y][old_x]
        # Убежище нельзя перемещать
        if not hasattr(obj, "move"):
            print("Этот объект нельзя перемещать!")
            return False

        if obj is None:
            print("Ошибка: на клетке нет объекта!")
            return False

        if self.grid[new_y][new_x] is not None:
            print("Ошибка: новая клетка занята!")
            return False
        
        # Проверка перехода между лесными клетками
        forest_to_forest = (
            isinstance(self.territory[old_y][old_x], Forest)
            and isinstance(self.territory[new_y][new_x], Forest)
        )

        # удаление старого эффекта ландшафтра (эффекты ландшафта действуют только на выживших)
        if getattr(obj, "base", None) is not None:
            old_territory = self.territory[old_y][old_x]

            if not forest_to_forest:
                old_territory.on_leave(obj)

        # перемещение
        self.grid[new_y][new_x] = obj
        self.grid[old_y][old_x] = None

        # обновление координат юнита
        if hasattr(obj, "x") and hasattr(obj, "y"):
            obj.move(new_x, new_y)

        # применение эффекта нового ландшафта (эффекты ландшафта действуют только на выживших)
        if getattr(obj, "base", None) is not None:
            new_territory = self.territory[new_y][new_x]

            if forest_to_forest:
                print("Юнит переместился между лесными клетками.")
                print("Бонус леса сохраняется: +10 временной брони.")
            else:
                new_territory.on_enter(obj)

        # подбор предмета (только для выживших)
        if getattr(obj, "base", None) is not None:
            self.collect_item(new_x, new_y, obj, base)

        # Проверка гибели юнита
        if hasattr(obj, "health") and obj.health <= 0:
            print(obj.name, "погиб!")

            # Удаление с карты
            self.remove_object(new_x, new_y)

            # Удаление из списка убежища
            if obj.base is not None:
                obj.base.remove_unit(obj)

            return False

        return True


    def copy_field(self):
        ' создание независимой копии поля'
        return copy.deepcopy(self)


    def set_territory(self, x, y, territory):
        'изменение ландшафта'
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            print("Ошибка: координаты за пределами поля!")
            return False

        self.territory[y][x] = territory
        return True


    def generate_territory(self):
        'случайная генерация ландшафта'
        for y in range(self.height):
            for x in range(self.width):
                chance = random.randint(1, 100)

                if chance <= 30:
                    self.territory[y][x] = Forest()
                elif chance <= 34:
                    self.territory[y][x] = Radiation()
                else:
                    self.territory[y][x] = Road()
    

    def add_item(self, x, y, item):
        'добавление предмета'
        if not (0 <= x < self.width and 0 <= y < self.height):
            print("Ошибка: координаты за пределами поля!")
            return False

        if self.items[y][x] is not None:
            print("Ошибка: здесь уже есть предмет!")
            return False

        if self.grid[y][x] is not None:
            print("Ошибка: клетка занята объектом!")
            return False

        self.items[y][x] = item
        return True
    
    
    def generate_items(self, item_counts):
        'размещение предметов (случайное)'
        available_cells = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is None and self.items[y][x] is None:
                    available_cells.append((x, y))

        # Перемешивание свободных клеток
        random.shuffle(available_cells)

        # Размещение предметов
        for item_class, count in item_counts.items():
            for i in range(count):
                if not available_cells:
                    print("Недостаточно свободных клеток!")
                    return

                x, y = available_cells.pop()
                self.add_item(x, y, item_class())


    def collect_item(self, x, y, unit, base=None):
        'сбор предметов'
        item = self.items[y][x]

        if item is None:
            return None

        result = unit + item

        # Пополнение ресурсов базы
        if base is not None and isinstance(result, int):
            base.add_resources(result)

        # Удаление использованного предмета
        self.items[y][x] = None

        return result


    def display(self, visible_cells=None, explored_cells=None, identified_items=None):
        'вывод поля'
        if visible_cells is None:
            visible_cells = {
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
            }

        if explored_cells is None:
            explored_cells = visible_cells
        
        if identified_items is None:
            identified_items = set()

        # Цвета
        reset = "\033[0m"
        bold = "\033[1m"

        gray = "\033[38;2;137;142;153m"
        blue = "\033[38;2;98;182;255m"
        turquoise = "\033[38;2;49;199;179m"
        purple = "\033[38;2;205;141;255m"
        red = "\033[38;2;255;85;85m"
        yellow = "\033[38;2;255;214;90m"
        light_green = "\033[38;2;100;230;140m"
        orange = "\033[38;2;244;162;97m"
        beige = "\033[38;2;231;210;160m"
        green = "\033[38;2;22;139;85m"
        white = "\033[97m"

        cell_width = 4

        # Центрирование символа
        def format_cell(symbol, color, is_bold=False):
            width = len(symbol)
            spaces = max(0, cell_width - width)

            left = spaces // 2
            right = spaces - left

            style = bold if is_bold else ""

            return (
                " " * left
                + style + color + symbol + reset
                + " " * right
            )

         # Ширина карты
        inner_width = self.width * cell_width + 2

        # Верхняя строка с координатами X
        print("     ", end="")

        for x in range(self.width):
            number = str(x)
            spaces = cell_width - len(number)
            left = spaces // 2
            right = spaces - left

            print(" " * left + number + " " * right, end="")

        print()

        # Верхняя граница
        print("   " + gray + "┌" + "─" * inner_width + "┐" + reset)

        for y in range(self.height):
            # Номер строки Y
            line = f"{y:>2} " + gray + "│ " + reset

            for x in range(self.width):
                obj = self.grid[y][x]
                item = self.items[y][x]
                territory = self.territory[y][x]

                symbol = "·"
                color = gray
                is_bold = False

                # Неизвестная территория
                if (x, y) not in explored_cells:
                    symbol = "·"

                # Исследованная, но сейчас невидимая территория
                elif (x, y) not in visible_cells:
                    symbol = territory.symbol
                    color = gray

                # Объекты в зоне видимости
                elif obj is not None:
                    symbol = obj.symbol
                    is_bold = True

                    if isinstance(obj, Enemy):
                        color = red
                    elif isinstance(obj, Fighter):
                        color = blue
                    elif isinstance(obj, Scout):
                        color = turquoise
                    elif isinstance(obj, Support):
                        color = purple
                    else:
                        color = white

                # Отображение предметов
                elif item is not None:
                    is_bold = True

                    if (x, y) in identified_items:
                        symbol = item.symbol

                        if isinstance(item, Trap):
                            color = red
                        elif isinstance(item, Medkit):
                            color = light_green
                        elif isinstance(item, Armor):
                            color = orange
                        elif isinstance(item, Supplies):
                            color = beige
                    else:
                        symbol = "?"
                        color = beige

                # Видимый ландшафт
                else:
                    symbol = territory.symbol

                    if isinstance(territory, Forest):
                        color = green
                    elif isinstance(territory, Radiation):
                        color = yellow
                    else:
                        color = gray
                line += format_cell(symbol, color, is_bold)

            line += gray + " │" + reset
            print(line)

        # Нижняя граница
        print("   " + gray + "└" + "─" * inner_width + "┘" + reset)


