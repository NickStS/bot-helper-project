from collections import UserDict
import datetime
from typing import Optional
import re
import pickle


class Field:
    def __init__(self, value=None):
        self.value = self.process_input(value)

    def process_input(self, value):
        return value


class Name(Field):
    pass


class Phone(Field):
    def process_input(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise ValueError("Invalid phone number")
        return value


class Birthday(Field):
    def process_input(self, value: Optional[datetime.date]):
        if value is not None and not isinstance(value, datetime.date):
            raise ValueError("Invalid date")
        return value


class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in (phones or [])]
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday.value is None:
            return None
        today = datetime.date.today()
        next_birthday = datetime.date(
            today.year, self.birthday.value.month, self.birthday.value.day)
        if today > next_birthday:
            next_birthday = datetime.date(
                today.year + 1, self.birthday.value.month, self.birthday.value.day)
        return (next_birthday - today).days

    def __str__(self):
        phones = ', '.join([phone.value for phone in self.phones])
        birthday = self.birthday.value if self.birthday.value else "Not set"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def __iter__(self, n):
        records = list(self.data.values())
        while records:
            yield records[:n]
            records = records[n:]

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        with open(filename, 'rb') as file:
            self.data = pickle.load(file)

    def search(self, query):
        result = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                result.append(record)
            else:
                for phone in record.phones:
                    if query in phone.value:
                        result.append(record)
                        break
        return result
