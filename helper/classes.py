import json
from collections import UserDict
from pathlib import Path
from datetime import datetime
from re import search

DATE_FORMAT = "%Y-%m-%d"
TEXT_FORMAT = "%d %b %Y"
FILE_ADDRESSBOOK = "ab.json"
FILE_NOTEBOOK = "nb.json"
MIN_YEAR = 1812
RECORD_HEADER = (
    "Row {:^20} {:^27} {:^30} {:^20}".format(
        "User", "Birthday", "e-mail", "Phone number(s)"
    )
    + "\n--- " + "-" * 20 + " " + "-" * 27 + " " + "-" * 30 + " " + "-" * 20
)
NOTE_HEADER = (
    " Row     Date     Note" + " " * 56 + "[Hashtags]\n"
    + "-" * 5 + " " + "-" * 10 + " " + "-" * 60
)
LINE = "-" * 60


class Field:
    def __init__(self, value=None):
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self) -> str:
        return self.value


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if len(value := str(value)) == 12 and value.isdigit():
            Field.value.fset(self, value)
        else:
            raise ValueError(f"'{value}' is not a valid phone number")


class Email(Field):
    @Field.value.setter
    def value(self, value):
        if search(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", value):
            Field.value.fset(self, value)
        else:
            raise ValueError(f"'{value}' is not a valid e-mail")


class Name(Field):
    ...


class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT)
        except ValueError:
            raise ValueError(
                f"'{value}' does not match the expected format ('yyyy-mm-dd')"
            )
        if not datetime.today().year > birthday.year >= MIN_YEAR:
            raise ValueError(f"'{value}' is not a valid date")
        Field.value.fset(self, birthday)

    def replace_year(self, year: int) -> datetime:
        try:
            return self.value.replace(year=year)
        except ValueError:
            return datetime(year=year, month=2, day=28)

    def days_to_birthday(self) -> int:
        todays_date = datetime.today()
        birthday = self.replace_year(todays_date.year)
        if todays_date > birthday:
            birthday = self.replace_year(todays_date.year + 1)
        return (birthday - todays_date).days

    def __str__(self) -> str:
        return (
            f"{self.value.strftime(TEXT_FORMAT)}"
            + f" ({self.days_to_birthday()} days left)"
        )

    def __contains__(self, days):
        return self.days_to_birthday() == days


class Record:
    def __init__(self, name: Name, birthday=None, email=None, phone=None):
        self.name = name
        self.phone: list[Phone] = []
        if phone:
            self.add_phone(phone)
        self.birthday = birthday
        self.email = email

    def is_phone(self, phone) -> bool:
        if self.phone:
            if phone.value in set(p.value for p in self.phone):
                return True
        return False

    def add_phone(self, phone):
        add_counter = 0
        if isinstance(phone, list):
            for p in phone:
                if not self.is_phone(p):
                    self.phone.append(p)
                    add_counter += 1
        elif not self.is_phone(phone):
            self.phone.append(phone)
            add_counter = 1
        return add_counter

    def del_phone(self, phone):
        if self.is_phone(phone):
            self.phone.remove(phone)
            return True

    def __str__(self) -> str:
        phones = ", ".join(str(p) for p in self.phone)
        return (
            f"{str(self.name):<20} {str(self.birthday):<27}"
            + f" {str(self.email):<30} {phones:<20}"
        )

    def __contains__(self, search_str: str):
        if search_str.lower() in self.name.value.lower():
            return True
        if search_str.isdigit():
            if search_str in "!".join(p.value for p in self.phone):
                return True
        return False


class AddressBook(UserDict):
    def __init__(self, filename=FILE_ADDRESSBOOK):
        super().__init__()
        self.file_path = Path(filename)
        self.read_from_file()

    def add_record(self, record: Record, print_msg=True):
        if record.name.value in self.data:
            raise KeyError(f"ERROR: cannot duplicate '{record.name.value}'")
        self.data[record.name.value] = record
        self.save_changes = True
        if print_msg:
            print(f"\nContact '{record.name.value}' successfully added.\n")

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            self.save_changes = True

    def __str__(self) -> str:
        return RECORD_HEADER + "\n".join(str(v) for v in self.values())

    def search_birthday(self, days: int):
        while days < 0:
            days += 365
        return sorted(
            name for name, record in self.data.items()
            if record.birthday and days in record.birthday
        )

    def search_all(self, search_str):
        if search_str:
            return sorted(
                name for name, record in self.data.items()
                if search_str in record
            )
        else:
            return sorted(self.data.keys())

    def search_name(self, search_str):
        return sorted(name for name in self.data.keys() if search_str in name)

    def search_phone(self, search_str):
        if search_str.isdigit():
            return sorted(
                name for name, record in self.data.items()
                if search_str in "!".join(p.value for p in record.phone)
            )
        else:
            return []

    def from_dict(self, source_dict: dict):
        for k, v in source_dict.items():
            self.data[k] = Record(
                Name(v["name"]),
                birthday=Birthday(v["birthday"]) if v["birthday"] else None,
                email=Email(v["email"]) if v["email"] else None,
                phone=[Phone(x) for x in v["phone"]],
            )

    def read_from_file(self):
        self.save_changes = False
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.from_dict(json.load(f))

    def to_dict(self) -> dict:
        return {
            k: {
                "name": v.name.value,
                "birthday": v.birthday.value.strftime(DATE_FORMAT)
                if v.birthday else None,
                "email": v.email.value if v.email else None,
                "phone": [p.value for p in v.phone],
            }
            for k, v in self.data.items()
        }

    def write_to_file(self):
        if self.save_changes:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f)
                self.save_changes = False


class HashTag(Field):
    @Field.value.setter
    def value(self, value):
        if search(r"^#\w+$", value):
            Field.value.fset(self, value)
        else:
            raise ValueError(f"'{value}' is not a hashtag")


class NoteBook():
    def __init__(self, filename=FILE_NOTEBOOK):
        # super().__init__()
        self.file_path = Path(filename)
        self.read_from_file()

    def add_id_to_tags(self, note_id, tags):
        self.save_changes = True
        if tags:
            for tag in tags:
                self.tags.setdefault(tag, []).append(note_id)
        else:
            self.tags.setdefault("#", []).append(note_id)

    def delete_id_from_tags(self, note_id, tags):
        self.save_changes = True
        if tags:
            for tag in tags:
                self.tags.get(tag).remove(note_id)
        else:
            self.tags.get("#").remove(note_id)

    def delete_tag(self, note_id, tag):
        self.save_changes = True
        self.data[note_id]['tags'].remove(tag)
        if len(self.tags[tag]) == 1:
            del self.tags[tag]
        else:
            self.tags[tag].remove(note_id)
        if not self.data[note_id]['tags']:
            self.tags.setdefault("#", []).append(note_id)

    def tags_scan(self):
        self.tags = {}
        for note_id, note in self.data.items():
            self.add_id_to_tags(note_id, note['tags'])

    def from_dict(self, source_dict):
        for k, v in source_dict.items():
            self.data[int(k)] = {
                "text": v['text'],
                "created": v['created'],
                "tags": v['tags']
            }

    def read_from_file(self):
        self.data: dict = {}
        self.max_id = 0
        self.save_changes = False
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    self.from_dict(json.load(f))
                except json.decoder.JSONDecodeError:
                    print(f"ERROR: File {self.file_path} could not be decoded")
        if self.data:
            self.max_id = max(self.data.keys()) + 1
        self.tags_scan()

    def write_to_file(self):
        if self.save_changes:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f)
                self.save_changes = False

    def add_note(self, text, tags: list[str] = []):
        self.data[self.max_id] = {
            "text": text,
            "created": datetime.today().strftime(DATE_FORMAT),
            "tags": tags
        }
        self.add_id_to_tags(self.max_id, tags)
        self.max_id += 1
        self.save_changes = True

    def add_tag(self, note_id, tag):
        if search(r"^#\w+$", tag):
            if self.data[note_id]['tags']:
                if tag in self.data[note_id]['tags']:
                    raise KeyError(f"Cannot duplicate tag '{tag}'")
            else:
                self.tags["#"].remove(note_id)
            self.save_changes = True
            self.data[note_id]['tags'].append(tag)
            self.tags.setdefault(tag, []).append(note_id)
        else:
            raise ValueError(f"'{tag}' is not a valid hashtag")

    def delete_note(self, note_id):
        self.delete_id_from_tags(note_id, self.data[note_id]['tags'])
        del self.data[note_id]
        self.save_changes = True

    def update(self, note_id, text):
        self.save_changes = True
        self.data

    def search_text(self, search_str):
        return [
            note_id for note_id, note in self.data.items()
            if search_str.lower() in note['text'].lower()
        ]

    def search_tag(self, search_str):
        if search_str in ("", "#"):
            return self.tags.get("#")
        result_set = set()
        for tag, note_id_list in self.tags.items():
            if search_str.lower() in tag.lower():
                result_set.update(note_id_list)
        return sorted(result_set)

    def search_all(self, search_str):
        if not search_str or search_str.startswith("#"):
            return self.search_tag(search_str[1:])
        result_set = set()
        for tag, note_id_list in self.tags.items():
            if search_str.lower() in tag.lower():
                result_set.update(note_id_list)
        search_set = set(self.data.keys()) - result_set
        for note_id in search_set:
            if search_str.lower() in self.data[note_id]['text'].lower():
                result_set.add(note_id)
        return sorted(result_set)

    def show_note(self, note_id):
        print("{:>5} {} {:<60} {}".format(
            note_id,
            self.data[note_id]['created'],
            self.data[note_id]['text'],
            str(self.data[note_id]['tags'])
        ))

    def __str__(self):
        return NOTE_HEADER + "\n".join(
            f"{n_id:>5} {n['created']:>5} {n['text']:<60} " + str(n['tags'])
            for n_id, n in self.data.items()
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, note_id):
        return self.data[note_id]

    def __contains__(self, note_id):
        return note_id in self.data
