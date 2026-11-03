from units import Tracker, Stalker, Engineer
from game_text import messages
import os
from instance_counter import save_count, load_count

class GameMenu:
    def __init__(self, game):
        self.game = game


    def clear_screen(self):
        'очистка терминала'
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="", flush=True)

    def get_coordinates(self):
        'ввод координат'
        coordinates = input("Введи координаты X Y через пробел: ")

        coordinates = coordinates.split()

        if len(coordinates) != 2:
            print("Ошибка! Нужно ввести две координаты.")
            return None

        try:
            x = int(coordinates[0])
            y = int(coordinates[1])

            return x, y

        except ValueError:
            print("Ошибка! Координаты должны быть числами.")
            return None

    def show_game(self):
        'вывод карты и игровой статистики'
        print("========== ТЕНИ ПУСТОШЕЙ ==========")
        print()

        # Вывод карты
        self.game.field.display(
            self.game.visible_cells(),
            self.game.explored_cells,
            self.game.identified_items
        )

        # Вывод статистики
        print()
        stats = self.game.get_statistics()

        print(
            f"Ход: {stats['turns']} | "
            f"Зомби: {stats['zombies_left']}/{self.game.total_zombies} | "
            f"Выжившие: {stats['survivors']}/{self.game.base.max_units}"
        )

        print(
            f"Убежище: {stats['base_health']}/500 HP | "
            f"Ресурсы: {stats['resources']} | "
            f"Исследовано: {stats['explored_percent']}%"
        )
        print("Экземпляров зомби:", stats["zombie_instances"])


# ИНТРО И ПРАВИЛА
    def show_intro(self):
        'сюжетное вступление'
        self.clear_screen()

        print("========== ТЕНИ ПУСТОШЕЙ ==========")
        print()
        print("После катастрофы мир превратился в пустошь.")
        print("Города разрушены, земли заражены радиацией,")
        print("а среди руин бродят ожившие мертвецы.")
        print()
        print("Ты возглавляешь последнее Убежище.")
        print("Твоим выжившим предстоит исследовать земли,")
        print("собирать ресурсы и сражаться с заражёнными.")
        print()
        print("ЦЕЛЬ: уничтожить всех зомби и сохранить Убежище.")
        print()
        print("Пока живы выжившие — надежда не угасла.")
        print("===================================")
        print()

        input("Нажми Enter, чтобы продолжить...")

    def show_rules(self):
        'правила игры'
        self.clear_screen()

        print("========== КАК ИГРАТЬ ==========")
        print()
        print("1. Выбирай юнитов и управляй ими через меню.")
        print("2. Вводи координаты в формате X Y (например, 5 3).")
        print("3. Исследуй карту, собирай предметы и сражайся.")
        print("4. Используй уникальные способности выживших.")
        print("5. После твоего действия ходят зомби.")
        print()
        print("Победа: все зомби уничтожены.")
        print("Поражение: убежище разрушено или отряд погиб.")
        print("================================")
        print()

        input("Нажми Enter, чтобы начать игру...")

    def show_results(self, result):
        'экран результатов'
        self.clear_screen()
        stats = self.game.get_statistics()

        print("======================================")

        if result == "victory":
            messages.event("              ПОБЕДА", "success")
            print()
            print("Последний заражённый повержен.")
            print("Пустошь впервые за долгое время молчит.")
            print("Убежище выстояло.")

        elif result == "base_destroyed":
            messages.event("             ПОРАЖЕНИЕ", "danger")
            print()
            print("Стены убежища не выдержали натиска.")
            print("Последний безопасный огонь погас.")

        elif result == "squad_destroyed":
            messages.event("             ПОРАЖЕНИЕ", "danger")
            print()
            print("Последний выживший пал.")
            print("Защищать убежище больше некому.")

        print()
        print("========== ИТОГИ ЭКСПЕДИЦИИ ==========")
        print()
        print("Количество ходов:", stats["turns"])
        print("Уничтожено зомби:", stats["zombies_killed"])
        print("Осталось выживших:", stats["survivors"])
        print("Прочность убежища:", stats["base_health"], "/ 500")
        print("Оставшиеся ресурсы:", stats["resources"])
        print("Исследовано карты:", str(stats["explored_percent"]) + "%")

        print()
        print("======================================")

        if result == "victory":
            messages.event(
                "Пока горит свет в убежище — надежда жива.",
                "success"
            )
        else:
            messages.event(
                "Но даже в пустоши история ещё не закончена.",
                "warning"
            )

        print()
        input("Нажми Enter, чтобы завершить игру...")


    def run(self):
        'главное меню'
        # Сюжетное вступление и правила
        self.show_intro()
        self.show_rules()

        while True:
            self.clear_screen()
            self.show_game()

            print()
            print("1 - Управление убежищем")
            print("2 - Управление юнитами")
            print("3 - Обозначения")
            print("4 - Сохранить количество экземпляров зомби")
            print("5 - Загрузить количество экземпляров зомби")
            print("0 - Выход")

            choice = input("Выбери действие: ")

            if choice == "1":
                self.base_menu()

            elif choice == "2":
                self.unit_menu()

            elif choice == "3":
                self.show_legend()

            elif choice == "4":
                count = self.game.get_statistics()["zombies_left"]
                save_count(count)

            elif choice == "5":
                count = load_count()

                if count is not None:
                    self.game.set_zombie_count(count)

            elif choice == "0":
                print("Игра завершена.")
                break

            else:
                print("Неизвестная команда!")

            # Проверка победы или поражения
            result = self.game.check_game_end()

            if result is not None:
                self.show_results(result)
                break

            input("\nНажми Enter, чтобы обновить карту...")

    def base_menu(self):
        'меню убежища'
        base = self.game.base

        print()
        print("========== УБЕЖИЩЕ ==========")
        print("1 - Состояние убежища")
        print("2 - Создать юнита")
        print("3 - Расформировать юнита")
        print("0 - Назад")

        choice = input("Выбор: ")

        if choice == "1":
            base.show_info()

        elif choice == "2":
            print()
            print("Доступные юниты:")

            for i, unit_class in enumerate(self.game.unit_classes, 1):
                cost = base.unit_costs[unit_class.__name__]

                print(
                    i, "-", unit_class().name,
                    "| Цена:", cost
                )
                print("   " + unit_class.ability_description.replace("\n", "\n   "))

            try:
                number = int(input("Выбери юнита (0 - назад): "))
            except ValueError:
                print("Ошибка ввода!")
                return

            if number == 0:
                return

            if not (1 <= number <= len(self.game.unit_classes)):
                print("Неверный номер!")
                return

            print("Укажи свободную клетку рядом с убежищем:")
            coords = self.get_coordinates()

            if coords is None:
                return

            x, y = coords

            result = self.game.create_unit(
                self.game.unit_classes[number - 1], x, y
            )

            self.game.finish_turn(result)

        elif choice == "3":
            if not base.units:
                print("В убежище нет юнитов!")
                return

            print()
            print("========== РАСФОРМИРОВАНИЕ ==========")

            # Вывод существующих юнитов
            for i, unit in enumerate(base.units, 1):
                print(
                    i, "-", unit.name,
                    "| HP:", str(unit.health) + "/" + str(unit.max_health),
                    "| Координаты:", unit.x, unit.y
                )

            try:
                number = int(input("Выбери юнита (0 - назад): "))
            except ValueError:
                print("Ошибка ввода!")
                return

            if number == 0:
                return

            if not (1 <= number <= len(base.units)):
                print("Неверный номер!")
                return

            # Удаление выбранного юнита
            unit = base.units[number - 1]
            result = self.game.remove_unit(unit)

            self.game.finish_turn(result)

    def show_units(self):
        'список союзников'
        print()
        print("========== ЮНИТЫ ==========")

        for i, unit in enumerate(self.game.base.units, 1):
            print()
            print(
                i, "-", unit.name,
                "| HP:", str(unit.health) + "/" + str(unit.max_health),
                "| Броня:", unit.armor,
                "| Снижение урона:", unit.damage_reduction,
                "| Урон:", unit.attack,
                "| Координаты:", unit.x, unit.y
            )
            print("   " + unit.ability_description.replace("\n", "\n   "))


    def unit_menu(self):
        'меню персонажей'
        units = self.game.base.units

        if not units:
            print("У тебя нет юнитов!")
            return

        self.show_units()

        try:
            number = int(input("Выбери юнита (0 - назад): "))
        except ValueError:
            print("Ошибка ввода!")
            return

        if number == 0:
            return

        if not (1 <= number <= len(units)):
            print("Неверный номер!")
            return

        unit = units[number - 1]

        print()
        unit.show_info()

        print()
        print("1 - Перемещение")
        print("2 - Атака")
        print("3 - Способность")
        print("0 - Назад")

        choice = input("Выбор действия: ")
        result = False

        if choice == "1":
            coords = self.get_coordinates()

            if coords is None:
                return

            x, y = coords
            result = self.game.move_unit(unit, x, y)

        elif choice == "2":
            coords = self.get_coordinates()

            if coords is None:
                return

            x, y = coords
            result = self.game.attack_enemy(unit, x, y)

        elif choice == "3":
            # Разведка и ремонт не требуют ввода координат
            if isinstance(unit, (Tracker, Stalker, Engineer)):
                result = self.game.use_ability(unit)

            else:
                print("Выбери цель способности:")
                coords = self.get_coordinates()

                if coords is None:
                    return

                x, y = coords
                result = self.game.use_ability(unit, x, y)

        elif choice == "0":
            return

        else:
            print("Неизвестная команда!")
            return

        self.game.finish_turn(result)


    def show_legend(self):
        'легенда (обозначения)'
        print()
        print("========== ОБОЗНАЧЕНИЯ ==========")
        print("Ш - Штурмовик     С - Снайпер")
        print("Р - Разведчик     Д - Дозорный")
        print("М - Медик         И - Инженер")
        print("⌂ - Убежище       З - Зомби")
        print()
        print("▲ - Лес           ▪ - Дорога")
        print("! - Радиация")
        print()
        print("? - Неизвестный предмет")
        print("+ - Аптечка       $ - Припасы")
        print("X - Ловушка       # - Бронежилет")
        print()
        print("· - Неисследованная территория")
        print("Серые символы - территория вне обзора")
        print("=================================")
        print()
        print("Типы предметов становятся известны")
        print("после сканирования Разведчиком.")
        print()
        print("Броня снижает урон от обычных атак.")
        print("Каждые 5 единиц брони уменьшают урон на 1.")
        print("Минимальный урон от атаки — 1 HP.")
        print("Радиация и ловушки игнорируют броню.")

