from address_book import AddressBook, Record, Phone, Birthday, Name
import datetime


def input_error(handler):
    def inner(*args):
        try:
            return handler(*args)
        except (KeyError, ValueError, IndexError) as error:
            return str(error)
    return inner


@input_error
def add_contact(contacts, name, phone, birthday=None):
    if birthday:
        birthday = datetime.datetime.strptime(birthday, "%d-%m-%Y").date()
    record = Record(Name(name), [Phone(phone)], Birthday(birthday))
    contacts.add_record(record)
    return f"Contact {name} added."


@input_error
def change_contact(contacts, name, phone, birthday=None):
    if name.lower() in contacts.data:
        record = contacts.data[name.lower()]
        if phone:
            record.phones[0].value = phone
        if birthday:
            record.birthday.value = datetime.datetime.strptime(
                birthday, "%d-%m-%Y").date()
        return f"Contact {name} updated."
    else:
        raise KeyError("Contact not found.")


@input_error
def find_contact(contacts, name):
    return contacts.data[name.lower()].phones[0].value


@input_error
def days_to_birthday(contacts, name):
    if name.lower() in contacts.data:
        record = contacts.data[name.lower()]
        return record.days_to_birthday()


@input_error
def show_all(contacts):
    result = ["Contacts:"]
    for name, record in contacts.data.items():
        result.append(f"{name}: {record.phones[0].value}")
    return "\n".join(result)


def main():
    contacts = AddressBook()
    print("Welcome to the assistant!")

    handlers = {
        "add": add_contact,
        "change": change_contact,
        "phone": find_contact,
        "birthday": days_to_birthday,
        "show all": show_all
    }

    while True:
        user_input = input("\nEnter your command: ").strip().lower()
        command, *data = user_input.split(' ', 1)

        if user_input in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        elif user_input == "hello":
            print("How can I help you?")
        elif command in handlers:
            data = data[0].split(',') if data else []
            print(handlers[command](contacts, *data))
        else:
            print("Command not recognized. Try again.")


if __name__ == "__main__":
    main()
