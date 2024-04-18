from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number")

class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, '%d.%m.%Y').date()
            if date > datetime.now().date():
                raise ValueError("Invalid date. Birthday cannot be in the future.")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        else:
            return None

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if str(phone) != phone_number]

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record
    @input_error
    def find(self, name):
        return self.data.get(name)
    @input_error
    def delete(self, name):
        del self.data[name]

    @input_error
    def birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value
                birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() >= 5:
                        delta = (7 - birthday_this_year.weekday())
                        birthday_this_year += timedelta(days=delta)

                    congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')
                    upcoming_birthdays.append({"name": name, "congratulation_date": congratulation_date_str})

        return f" birthdays nearest 7 days: {upcoming_birthdays}"

@input_error
def add_contact(args):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def add_birthday(args):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."
@input_error
def show_birthday(args):
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name}: {record.birthday.value}"
        else:
            return f"No birthday set for {name}."
    else:
        return f"Contact '{name}' not found."
@input_error
def all_contact():
    lines = []
    for name, record in book.data.items():
        phones = '; '.join(str(phone) for phone in record.phones)
        if record.birthday:
            birthday = record.birthday.value
        else:
            birthday = ""
        lines.append(f"| {name:<20} | {phones:<50} | {birthday:<20} |")
    header = "| {:<20} | {:<50} | {:<20} |".format("Name", "Phones", "Birthday")
    separator = "-" * len(header)
    return "\n".join([separator, header, separator] + lines + [separator])
@input_error
def edit_phone(args):
    name, phone_number, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found")
    phone = record.find_phone(phone_number)
    if phone:
        record.remove_phone(phone_number)
        record.add_phone(new_phone)
        return "Phone number updated."
    else:
        return "Phone number not found for this contact."

def phone_username(args):
    name, *_ = args
    record = book.find(name)
    if record:
        phone = record.find_phone(name)
        if phone:
            return phone.value
        else:
            return "Phone number not found for this contact."
    else:
        return "Contact not found."


# Створення нової адресної книги

if __name__ == "__main__":
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args))
        elif command == "change":
            name, phone_number, new_phone, *_ = args
            print(edit_phone(args))
        elif command == "phone":
            # user phone number
            name, *_ = args
            print(phone_username(name))
        elif command == "all":
            print(all_contact())
        elif command == "add-birthday":
            print(add_birthday(args))
        elif command == "show-birthday":
            print(show_birthday(args))
        elif command == "birthdays":
            print(book.birthdays())
        else:
            print("Invalid command.")