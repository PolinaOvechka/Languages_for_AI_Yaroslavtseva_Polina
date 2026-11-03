import json

class InstanceCounter:
    instances = 0

    def __init__(self):
        InstanceCounter.instances += 1

    def __del__(self):
        InstanceCounter.instances -= 1

def save_count(count):
    data = {"instances": count}

    with open ("instances.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Количество зомби сохранено!")

def load_count():
    try:
        with open("instances.json", "r") as file:
            data = json.load(file)

        count = data["instances"]

        if type(count) != int or count < 0:
            print("Ошибка! Количество зомби должно быть целым неотрицательным числом.")
            return None
        
        return count
    
    except FileNotFoundError:
        print("Файл не найден!")
        return None
    except(ValueError, KeyError, TypeError):
        print("Ошибка чтения файла сохранения!")
