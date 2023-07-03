from re import search
from pathlib import Path
from classes import AddressBook, Record, Phone, Birthday, Name, Email
from classes import NoteBook, RECORD_HEADER, LINE, NOTE_HEADER
from clean import sort_files

TEXT_FORMAT = "%d %b %Y"
SELECT_CONTACT = "Press Enter or type a row number to select a contact: "
SELECT_NOTE = "Press Enter or type a row number to select a note: "
ENTER_BIRTHDAY = "Enter birthday (format is 'yyyy-mm-dd', e.g. '1999-10-22'): "
ENTER_EMAIL = "Enter e-mail: "
ENTER_PHONE = (
    "Enter a list of 12-digit phone numbers separated by ' '"
    + ", e.g. 380501234567: "
)
BACK = "-"
A_MAIN = 0
A_CONTACTS_BY_NAME = 65
A_CONTACTS_BY_BIRTHDAY = 66
A_NOTE_BY_TEXT = 97
A_NOTE_BY_TAG = 98
A_SORT_FOLDER = 99
A_ADD = 4
A_ADD_BD = 5
A_ADD_EM = 6
A_ADD_PH = 7
A_EDIT = 8
A_EDIT_ADD_PH = 9
A_EDIT_DEL_PH = 10
A_EDIT_UPD_EM = 11
A_EDIT_UPD_BD = 12
A_EDIT_DELETE = 13
A_ADD_NOTE = 17
A_ADD_NOTE_TAGS = 18
A_EDIT_NOTE = 33
A_EDIT_NOTE_TEXT = 34
A_EDIT_NOTE_ADD_TAG = 35
A_EDIT_NOTE_DEL_TAG = 36
A_EDIT_NOTE_DELETE = 37
MESSAGE = {
    A_MAIN: (
        "1 = Add new contact\n"
        + "2 = Add new note\n"
        + "3 = Show all contacts\n"
        + "4 = Search contacts by birthday\n"
        + "5 = Search contacts using name and/or phone\n"
        + "6 = Show all notes\n"
        + "7 = Search notes using text\n"
        + "8 = Search notes using hashtag\n"
        + "9 = Sort files\n"
        + "0 = Exit (Ctrl+C)\n"
        + LINE
        + "\nNB: Options from 3 to 7 allow to select one item for update\n"
        + LINE
        + "\nSelect an option or type some symbols to search for: "
    ),
    A_ADD: (
        "\n\nYou are about to add new contact.\n"
        + LINE
        + "\nYou may leave the birthday/email/phone fields blank (Enter),"
        + "\nEnter '-' command to go back to the previous value"
        + "\nCtrl+Z and Enter (or F6 and Enter) to finish"
        + "\nCtrl+C to exit/main menu\n"
        + LINE
        + "\nEnter a name (required): "
    ),
    A_ADD_BD: ENTER_BIRTHDAY,
    A_ADD_EM: ENTER_EMAIL,
    A_ADD_PH: ENTER_PHONE,
    A_CONTACTS_BY_NAME: "Enter a pattern to search contacts: ",
    A_CONTACTS_BY_BIRTHDAY: "Enter days to birthday: ",
    A_NOTE_BY_TEXT: "Enter a text pattern to search notes: ",
    A_NOTE_BY_TAG: "Enter a text pattern to search tags: ",
    A_SORT_FOLDER: (
        "\n\nYou are about to start sorting files.\n"
        + LINE
        + "\nPlease specify folder name or leave it blank and press Enter"
        + f"\nto use the current folder ({Path('.').parent.resolve()})\n"
        + LINE
        + "\nEnter folder name: "
    ),
    A_EDIT: (
        "1 = Add new phone(s)\n"
        + "2 = Delete existing phone\n"
        + "3 = Update e-mail\n"
        + "4 = Update birthday\n"
        + "5 = Delete e-mail\n"
        + "6 = Delete birthday\n"
        + "7 = Delete contact\n"
        + "0 = Main menu (Ctrl+C)\n"
        + LINE
        + "\nSelect an option: "
    ),
    A_EDIT_ADD_PH: "\n" + ENTER_PHONE,
    A_EDIT_DEL_PH: "Enter a row number for the phone to delete: ",
    A_EDIT_UPD_EM: "\n" + ENTER_EMAIL,
    A_EDIT_UPD_BD: "\n" + ENTER_BIRTHDAY,
    A_EDIT_DELETE: (
        "\nAre you sure you want to delete the selected contact (Y)?"
    ),
    A_ADD_NOTE: (
        "\n\nYou are about to add new note.\n"
        + LINE
        + "\nYou may leave the tags blank (press Enter),"
        + "\nCtrl+Z and Enter (or F6 and Enter) to finish"
        + "\nCtrl+C to exit/main menu\n"
        + LINE
        + "\nEnter a note text (required): "
    ),
    A_ADD_NOTE_TAGS: (
        "Enter list of tags separated by ' ' (e.g. #world #bus): "
    ),
    A_EDIT_NOTE: (
        "1 = Update text\n"
        + "2 = Delete existing hashtag\n"
        + "3 = Add new hashtag\n"
        + "4 = Delete note\n"
        + "0 = Main menu (Ctrl+C)\n"
        + LINE
        + "\nSelect an option: "
    ),
    A_EDIT_NOTE_TEXT: "Enter new text: ",
    A_EDIT_NOTE_ADD_TAG: "Enter hashtag (e.g. #world): ",
    A_EDIT_NOTE_DEL_TAG: LINE + "\nEnter row number for the tag to delete: ",
    A_EDIT_NOTE_DELETE: (
        "\nAre you sure you want to delete the selected note (Y)?"
    )
}
CTRL_C = "{~"
F6 = "}~"

contacts = AddressBook()
notes = NoteBook()


def input_str(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        return F6
    except KeyboardInterrupt:
        print()
        return CTRL_C


def add_sequence(user_input: str, selected: Record, action: int):
    if user_input == CTRL_C:
        return A_MAIN, None
    if user_input == F6:
        if selected:
            contacts.add_record(selected)
        return A_MAIN, None
    if user_input == BACK:
        if action == A_ADD_PH:
            return A_ADD_EM, selected
        elif action == A_ADD_EM:
            return A_ADD_BD, selected
        return A_ADD, selected
    if user_input:
        if action == A_ADD:
            if user_input in contacts:
                print(f"\n'{user_input}' is already in Contact list")
                return action, selected
            if selected:
                selected.name.value = user_input
                return A_ADD_BD, selected
            return A_ADD_BD, Record(Name(user_input))
        if action == A_ADD_BD:
            try:
                birthday = Birthday(user_input)
            except ValueError as e:
                print(e)
                return action, selected
            else:
                selected.birthday = birthday
                return A_ADD_EM, selected
        if action == A_ADD_EM:
            try:
                email = Email(user_input)
            except ValueError as e:
                print(e)
                return action, selected
            else:
                selected.email = email
                return A_ADD_PH, selected
        if action == A_ADD_PH:
            for phone_str in user_input.split():
                try:
                    phone = Phone(phone_str)
                except ValueError as e:
                    print(e)
                else:
                    selected.add_phone(phone)
                    print(f"Phone '{phone}' added.")
            contacts.add_record(selected)
            return A_MAIN, None
    elif action == A_ADD_BD:
        return A_ADD_EM, selected
    elif action == A_ADD_EM:
        return A_ADD_PH, selected
    elif action == A_ADD_PH:
        contacts.add_record(selected)
        return A_MAIN, None
    elif action == A_ADD:
        print("\nName cannot be skipped\n")
    return action, selected


def edit_sequence(user_input: str, selected: Record, action: int):
    if action == A_EDIT:
        if user_input == CTRL_C or user_input == "0":  # = Main menu (Ctrl+C)
            return A_MAIN, None
        if user_input == "1":              # = Add new phone(s)
            return A_EDIT_ADD_PH, selected
        if user_input == "2":              # = Delete existing phone
            if selected.phone:
                print()
                for i, phone in enumerate(selected.phone):
                    print(f"{i} = {phone.value}")
                print(LINE)
                return A_EDIT_DEL_PH, selected
            else:
                print("\nPhone list is empty\n")
            return A_EDIT, selected
        if user_input == "3":              # = Update e-mail
            return A_EDIT_UPD_EM, selected
        if user_input == "4":              # = Update birthday
            return A_EDIT_UPD_BD, selected
        if user_input == "5":              # = Delete e-mail
            if selected.email:
                email = selected.email.value
                print(f"\nE-mail '{email}' has been deleted.\n")
                contacts[selected.name.value].email = None
                contacts.save_changes = True
            else:
                print('\nNothing to delete\n')
            return A_EDIT, selected
        if user_input == "6":              # = Delete birthday
            if selected.birthday:
                birthday = selected.birthday.value.strftime(TEXT_FORMAT)
                print(f"\nBirthday '{birthday}' has been deleted.\n")
                contacts[selected.name.value].birthday = None
                contacts.save_changes = True
            else:
                print('\nNothing to delete\n')
            return A_EDIT, selected
        if user_input == "7":              # = Delete contact
            return A_EDIT_DELETE, selected
        print("\nUnrecognized command\n")
        return A_EDIT, selected
    if user_input in (CTRL_C, F6):
        return A_EDIT, selected
    if action == A_EDIT_ADD_PH:
        print()
        for value in user_input.split():
            try:
                phone = Phone(value)
            except ValueError as e:
                print(e)
            else:
                if contacts[selected.name.value].add_phone(phone):
                    print(f"Phone '{phone}' added.")
                    contacts.save_changes = True
                else:
                    print(f"Phone '{phone}' already exists.")
        return A_EDIT, selected
    if action == A_EDIT_DEL_PH:
        try:
            phone = selected.phone[int(user_input)]
        except (ValueError, KeyError):
            print(
                "\nA number between 0 and {len(selected.phone)} is expected\n"
            )
            return action, selected
        contacts[selected.name.value].del_phone(phone)
        print(f"\nPhone '{phone.value}' has been deleted.\n")
        contacts.save_changes = True
        return A_EDIT, selected
    if action == A_EDIT_UPD_EM:
        try:
            email = Email(user_input)
        except ValueError as e:
            print(f"\n{str(e)}")
            return action, selected
        else:
            contacts[selected.name.value].email = email
            contacts.save_changes = True
        return A_EDIT, selected
    if action == A_EDIT_UPD_BD:
        try:
            birthday = Birthday(user_input)
        except ValueError as e:
            print(f"\n{str(e)}")
            return action, selected
        else:
            value = birthday.value.strftime(TEXT_FORMAT)
            print(f"\nBirthday '{value}' added.\n")
            contacts[selected.name.value].birthday = birthday
            contacts.save_changes = True
        return A_EDIT, selected
    if action == A_EDIT_DELETE and user_input.upper() == "Y":
        print(f"\nContact '{selected.name.value}' has been deleted\n")
        contacts.delete_record(selected.name.value)
        return A_MAIN, None
    return A_EDIT, selected


def add_note(user_input: str, selected: dict, action: int):
    if user_input == CTRL_C:
        return A_MAIN, None
    elif user_input == F6:
        if selected.get("text"):
            notes.add_note(selected['text'])
        return A_MAIN, None
    elif action == A_ADD_NOTE:
        if len(user_input) > 0:
            selected['text'] = user_input
            return A_ADD_NOTE_TAGS, selected
        else:
            print("\nCan not add empty note\n")
            return action, selected
    elif action == A_ADD_NOTE_TAGS:
        tag_list = []
        if user_input:
            for tag in user_input.split():
                if search(r"^#\w+$", tag):
                    if tag in tag_list:
                        print(f"Duplicate tag '{tag}'")
                    else:
                        print(f"Hashtag '{tag}' added")
                        tag_list.append(tag)
                else:
                    print(f"'{tag}' is not a hashtag")
        notes.add_note(selected['text'], tag_list)
        print()
        return A_MAIN, None
    return A_MAIN, None


def edit_note(user_input: str, selected: int, action: int):
    if user_input == CTRL_C:
        return A_MAIN, None
    elif action == A_EDIT_NOTE:
        if user_input == '1':      # = Update text
            return A_EDIT_NOTE_TEXT, selected
        elif user_input == '2':    # = Delete existing hashtag
            if notes[selected]['tags']:
                print()
                for i, tag in enumerate(notes[selected]['tags']):
                    print(f"{i} = {tag}")
                return A_EDIT_NOTE_DEL_TAG, selected
            else:
                print("\nThere are 0 hashtags in the selected note\n")
        elif user_input == '3':    # = Add new hashtag
            return A_EDIT_NOTE_ADD_TAG, selected
        elif user_input == '4':    # = Delete note
            return A_EDIT_NOTE_DELETE, selected
        elif user_input == '0':    # = Main menu (Ctrl+C)
            return A_MAIN, None
    elif action == A_EDIT_NOTE_TEXT:
        if user_input:
            notes.update(selected, user_input)
            return A_EDIT_NOTE, selected
        else:
            print("\nPlease enter text to update note\n")
            return action, selected
    elif action == A_EDIT_NOTE_ADD_TAG:
        if user_input:
            try:
                notes.add_tag(selected, user_input)
            except (ValueError, KeyError) as e:
                print(e)
                return action, selected
            else:
                print(f"Hashtag '{user_input}' added\n")
        else:
            print("\nCannot add empty hashtag\n")
        return A_EDIT_NOTE, selected
    elif action == A_EDIT_NOTE_DEL_TAG:
        if user_input.isdigit():
            tag_id = int(user_input)
            tag_count = len(notes[selected]['tags'])
            if 0 <= tag_id < tag_count:
                tag = notes[selected]['tags'][tag_id]
                notes.delete_tag(selected, tag)
                print(f"\nHashtag '{tag}' has been deleted.\n")
                return A_EDIT_NOTE, selected
        print("\nA number between 0 and {tag_count} is expected\n")
        return action, selected
    elif action == A_EDIT_NOTE_DELETE:
        if user_input.upper() == "Y":
            notes.delete_note(selected)
            print(f"\nNote {selected} has been deleted\n")
            return A_MAIN, None
    else:
        print("\nUnrecognized command\n")
    return A_EDIT_NOTE, selected


def show_contacts(name_list):
    if name_list:
        print(f"\n{RECORD_HEADER}")
        for i, name in enumerate(name_list):
            print(f"{i:>3} {str(contacts[name])}")
        print(LINE)
        try:
            row_number = int(input_str(SELECT_CONTACT))
        except ValueError:
            print("\nNo contacts selected\n")
            return A_MAIN, None
        else:
            if 0 <= row_number < len(name_list):
                print(f"\nContact '{name_list[row_number]}' selected\n")
                return A_EDIT, contacts[name_list[row_number]]
    else:
        print("\n0 contacts found\n")
    return A_MAIN, None


def search_contacts(user_input: str, selected, action: int):
    if user_input in (F6, CTRL_C, ""):
        return A_MAIN, None
    name_list = []
    if action == A_CONTACTS_BY_BIRTHDAY:
        try:
            days = int(user_input)
        except ValueError:
            print("An integer number is expected")
            return action, selected
        else:
            name_list = contacts.search_birthday(days)
    elif action == A_CONTACTS_BY_NAME:
        name_list = contacts.search_all(user_input)
    return show_contacts(name_list)


def show_notes(note_id_list, action=A_MAIN):
    if note_id_list:
        print(f"\n{NOTE_HEADER}")
        for i in note_id_list:
            notes.show_note(i)
        print(LINE)
        try:
            row_number = int(input_str(SELECT_NOTE))
        except ValueError:
            print("\nNo notes selected\n")
            return action, None
        else:
            if row_number in note_id_list:
                print(f"\nNote {row_number} selected\n")
                return A_EDIT_NOTE, row_number
    else:
        print("\n0 notes found\n")
    return A_MAIN, None


def search_notes(user_input: str, selected, action: int):
    if user_input in (F6, CTRL_C):
        return A_MAIN, None
    if action == A_NOTE_BY_TEXT:
        return show_notes(notes.search_text(user_input))
    if action == A_NOTE_BY_TAG:
        return show_notes(notes.search_tag(user_input))
    return A_MAIN, None


def sort_folder(user_input: str, selected, action: int):
    path = Path(user_input) if user_input else Path(".")
    try:
        sort_files(path)
    except ValueError as e:
        print(f"\n{str(e)}\n")
    return A_MAIN, None


def main_menu(user_input: str, selected, action: int):
    if user_input == "0" or user_input == CTRL_C:  # = Exit (Ctrl+C)
        contacts.write_to_file()
        notes.write_to_file()
        print("Good bye!")
        exit()
    if user_input == "1":            # = Add new contact
        return A_ADD, None
    if user_input == "2":            # = Add new note
        return A_ADD_NOTE, {}
    if user_input == "3":            # = Show all contacts
        return show_contacts(sorted(contacts.data.keys()))
    if user_input == "4":            # = Search contacts by birthday
        return A_CONTACTS_BY_BIRTHDAY, None
    if user_input == "5":            # = Search contacts using name & phone
        return A_CONTACTS_BY_NAME, None
    if user_input == "6":            # = Show all notes
        return show_notes(sorted(notes.data.keys()))
    if user_input == "7":            # = Search notes using text
        return A_NOTE_BY_TEXT, None
    if user_input == "8":            # = Search notes using hashtag
        return A_NOTE_BY_TAG, None
    if user_input == "9":            # = Sort folder
        return A_SORT_FOLDER, None
    else:
        print("\nUnrecognized command\n")
    return A_MAIN, None


menu_functions = {
    A_MAIN: main_menu,
    A_CONTACTS_BY_BIRTHDAY: search_contacts,
    A_CONTACTS_BY_NAME: search_contacts,
    A_NOTE_BY_TEXT: search_notes,
    A_NOTE_BY_TAG: search_notes,
    A_SORT_FOLDER: sort_folder,
    A_ADD: add_sequence,
    A_ADD_BD: add_sequence,
    A_ADD_EM: add_sequence,
    A_ADD_PH: add_sequence,
    A_EDIT: edit_sequence,
    A_EDIT_ADD_PH: edit_sequence,
    A_EDIT_DEL_PH: edit_sequence,
    A_EDIT_UPD_EM: edit_sequence,
    A_EDIT_UPD_BD: edit_sequence,
    A_EDIT_DELETE: edit_sequence,
    A_ADD_NOTE: add_note,
    A_ADD_NOTE_TAGS: add_note,
    A_EDIT_NOTE: edit_note,
    A_EDIT_NOTE_TEXT: edit_note,
    A_EDIT_NOTE_ADD_TAG: edit_note,
    A_EDIT_NOTE_DEL_TAG: edit_note,
    A_EDIT_NOTE_DELETE: edit_note
}


def bot_helper():
    action = A_MAIN
    selected = None
    while True:
        if action == A_MAIN:
            cnt = f"\n[{len(contacts)} contacts] [{len(notes)} notes]"
            print(cnt + "\n" + LINE)
        action, selected = menu_functions[action](
            input_str(MESSAGE[action]),
            selected,
            action
        )


if __name__ == "__main__":
    bot_helper()
