import csv
import os


# Базовый класс Check
class Check:
    def __init__(self, number, date_time, amount, item_name):
        self.number = number
        self.date_time = date_time
        self.amount = amount
        self.item_name = item_name

    def __repr__(self):
        """Перегрузка метода repr для красивого отображения"""
        return f"Check(№{self.number}, {self.date_time}, {self.amount}, '{self.item_name}')"

    def __str__(self):
        """Перегрузка метода str для строкового представления объекта"""
        return f"Чек №{self.number}, Дата и время: {self.date_time}, Сумма: {self.amount}, Товар: {self.item_name}"

    # Модифицируем __setattr__ в классе Check
    def __setattr__(self, name, value):
        """Запись значений в свойства только через __setattr__"""
        if name == "amount":
            if isinstance(value, str):  # Проверяем, если значение - строка
                try:
                    value = float(value.replace(',', '.'))  # Преобразуем строку в число с плавающей точкой
                except ValueError:
                    raise ValueError("Сумма должна быть числом или строкой, представляющей число.")
            elif isinstance(value, (int, float)):
                value = float(value)  # Преобразуем int в float для единообразия
            else:
                raise ValueError("Сумма должна быть числом или строкой, представляющей число.")
        super().__setattr__(name, value)


# Наследуемся от Check и создаем класс RefundCheck для чеков с возвратом
class RefundCheck(Check):
    def __init__(self, number, date_time, amount, item_name, reason_for_return):
        super().__init__(number, date_time, amount, item_name)
        self.reason_for_return = reason_for_return

    def __repr__(self):
        """Переопределение для отображения возврата"""
        return f"RefundCheck(№{self.number}, {self.date_time}, {self.amount}, '{self.item_name}', '{self.reason_for_return}')"

    def __str__(self):
        """Переопределение для строки"""
        return f"Чек с возвратом №{self.number}, Дата и время: {self.date_time}, Сумма: {self.amount}, Товар: {self.item_name}, Причина возврата: {self.reason_for_return}"


# Коллекция чеков
class CheckCollection:
    def __init__(self):
        self._checks = []

    def __repr__(self):
        """Перегрузка метода repr для представления коллекции чеков"""
        return f"CheckCollection({len(self._checks)} items)"

    def __getitem__(self, index):
        """Доступ к элементам коллекции по индексу"""
        return self._checks[index]

    def __iter__(self):
        """Итератор для перебора чеков"""
        self._index = 0
        return self

    def __next__(self):
        """Реализация итератора для CheckCollection"""
        if self._index < len(self._checks):
            result = self._checks[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

    def sort_by_item_name(self):
        """Сортировка чеков по наименованию товара"""
        self._checks.sort(key=lambda check: check.item_name)

    def sort_by_amount(self):
        """Сортировка чеков по сумме"""
        self._checks.sort(key=lambda check: check.amount)

    def filter_by_amount(self, min_amount):
        """Фильтрация чеков по минимальной сумме"""
        return [check for check in self._checks if check.amount >= min_amount]

    @staticmethod
    def from_csv(filename):
        """Статический метод для создания коллекции чеков из CSV файла"""
        collection = CheckCollection()
        try:
            with open(filename, newline='', encoding='windows-1251') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    # Если в поле "наименование 1 товарной позиции" есть слово "возврат", создаем RefundCheck
                    if "возврат" in row['наименование 1 товарной позиции'].lower():
                        check = RefundCheck(row['№'], row['дата и время'], row['сумма'],
                                            row['наименование 1 товарной позиции'],
                                            row.get('причина возврата', 'Не указана'))
                    else:
                        check = Check(row['№'], row['дата и время'], row['сумма'],
                                      row['наименование 1 товарной позиции'])
                    collection._checks.append(check)
        except FileNotFoundError:
            print(f"Ошибка: Файл {filename} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при чтении файла {filename}: {e}")
        return collection

    def save_to_csv(self, filename):
        """Сохранение коллекции чеков в CSV файл"""
        with open(filename, mode='w', newline='', encoding='windows-1251') as csvfile:
            fieldnames = ['№', 'дата и время', 'сумма', 'наименование 1 товарной позиции', 'причина возврата']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for check in self._checks:
                row = {
                    '№': check.number,
                    'дата и время': check.date_time,
                    'сумма': check.amount,
                    'наименование 1 товарной позиции': check.item_name,
                }
                if isinstance(check, RefundCheck):
                    row['причина возврата'] = check.reason_for_return
                writer.writerow(row)

    def __iter__(self):
        """Генератор, который позволяет получать чек по одному"""
        for check in self._checks:
            yield check

    def __len__(self):
        """Метод для получения длины коллекции"""
        return len(self._checks)


class DirectoryAnalyzer:
    """Класс для анализа содержимого директории"""

    def __init__(self, directory_path):
        self.directory_path = directory_path

    def count_files_and_folders(self):
        """Подсчитывает количество файлов и папок в директории"""
        try:
            items = os.listdir(self.directory_path)
            file_count = sum(1 for item in items if os.path.isfile(os.path.join(self.directory_path, item)))
            folder_count = sum(1 for item in items if os.path.isdir(os.path.join(self.directory_path, item)))
            return file_count, folder_count
        except FileNotFoundError:
            print("Ошибка: Указанная директория не найдена.")
            return 0, 0
        except PermissionError:
            print("Ошибка: Недостаточно прав для доступа к директории.")
            return 0, 0

    def get_directory_size(self):
        """Возвращает общий размер всех файлов в директории в байтах"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.directory_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except (FileNotFoundError, PermissionError):
                    continue
        return total_size

    def nothing(self):
        return 0;

    def doconflict(self):
        return 0;


# Пример использования:
if __name__ == "__main__":
    # Создаем коллекцию чеков, загружая данные из файла
    collection = CheckCollection.from_csv("data.csv")

    # Пример перегрузки repr
    print(repr(collection))

    # Пример доступа через индекс
    print(collection[1])  # Вывод второго чека

    # Пример сортировки по наименованию товара
    collection.sort_by_item_name()
    print("\nЧеки после сортировки по наименованию товара:")
    for check in collection:
        print(check)

    # Пример сортировки по сумме
    collection.sort_by_amount()
    print("\nЧеки после сортировки по сумме:")
    for check in collection:
        print(check)

    # Пример фильтрации по минимальной сумме
    filtered_checks = collection.filter_by_amount(150)
    print("\nЧеки с суммой больше 150:")
    for check in filtered_checks:
        print(check)

    # Сохранение в новый CSV файл
    collection.save_to_csv("output.csv")
    print("\nЧеки сохранены в файл output.csv.")

    # Работа с файлами и папками
    directory = input("\nВведите путь к директории для подсчета файлов и папок: ")
    analyzer = DirectoryAnalyzer(directory)  # Создаем экземпляр DirectoryAnalyzer
    file_count, folder_count = analyzer.count_files_and_folders()  # Вызываем метод экземпляра
    print(f"Количество файлов: {file_count}")
    print(f"Количество папок: {folder_count}")  # comment
