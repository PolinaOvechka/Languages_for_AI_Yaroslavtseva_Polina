class Base:
    def __init__(self, x, y, health=500, max_units=6):
        'характеристики убежища'
        self.name = "Убежище"
        self.symbol = "⌂"
        self.x = x
        self.y = y
        self.health = health
        self.max_units = max_units
        self.resources = 250

        # Стоимость создания юнитов
        self.unit_costs = {
            "Assault": 40,
            "Sniper": 50,
            "Tracker": 25,
            "Stalker": 30,
            "Medic": 35,
            "Engineer": 35
        }       

        # Список созданных юнитов
        self.units = []


    def create_unit(self, unit_class, field, x, y, silent=False):
        'создание юнитов'
        if len(self.units) >= self.max_units:
            print("Ошибка: достигнут лимит юнитов!")
            return False

        # Определение стоимости юнита
        cost = self.unit_costs.get(unit_class.__name__, 0)

        # Проверка ресурсов
        if self.resources < cost:
            print("Ошибка: недостаточно ресурсов!")
            return False

        # Создание юнита
        unit = unit_class()

        if field.add_object(x, y, unit):
            unit.base = self
            self.units.append(unit)
            self.resources -= cost

            # Применение ландшафта при появлении юнита
            field.territory[y][x].on_enter(unit)

            if not silent:
                print("Создан юнит:", unit.name)

            # Проверка гибели от радиации
            if unit.health <= 0:
                field.remove_object(x, y)
                self.remove_unit(unit)

            return True

        return False


    def remove_unit(self, unit):
        ' Удаление юнита из списка базы '
        if unit in self.units:
            self.units.remove(unit)
            print("Юнит удалён из базы:", unit.name)
            return True

        return False
    

    def add_resources(self, amount):
        'Пополнение ресурсов убежища'
        self.resources += amount
        print("Ресурсы убежища пополнены на", amount)
        

    def show_info(self):
        'Вывод состояния убежища'
        print("Название:", self.name)
        print("Здоровье:", self.health)
        print("Количество юнитов:", len(self.units))
        print("Максимум юнитов:", self.max_units)
        print("Ресурсы:", self.resources)
