"""CL script to track the time remaining on duration based tasks. provide --help argument for more information."""

# IMPORT
import argparse
import csv
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.table import Table

# from rich.live import Live
from rich import box

# GLOBAL VARIABLES
DATABASE_FILEPATH = "task_timer_database.csv"


# DATABASE MANAGEMENT
def db_read(filepath=DATABASE_FILEPATH):
    """print full database"""
    # TODO convert string entries into proper types (start, end = date and duration = int)
    # TODO return a list of tuples of all entries
    # NOTE provide arguement to return only (1) entry
    csv.reader
    file = open(filepath)
    reader = csv.reader(file)
    db_list = []
    for row in reader:
        # typecast row, then append to list
        name, start, end, duration = row
        row = str(name), valid_date(start), valid_date(end), int(duration)
        db_list.append(row)
    return db_list


def db_write(
    entry: tuple,
    filepath=DATABASE_FILEPATH,
    mode="a",
    write_header=False,
    disable_write_row=False,
):
    """write an entry to database. Supports 1 entry"""
    # NOTE ValueError provided for programmatic error - not user error.
    # NOTE write_header arguement may not be required, unless needed for when an entry is deleted.
    # BUG the below indented ValueError check doesn't work when calling db_delete() due to it's empty string
    # if len(entry) != 4 or len(entry) != 0:
    #     raise ValueError(f"Recieved tuple of {len(entry)} length. Expected 4.")
    with open(filepath, mode, newline="") as csv_file:
        writer = csv.writer(csv_file)
        if disable_write_row:
            return
        if write_header:
            writer.writerow(("name", " start", " end", " duration"))
        writer.writerow(entry)


def db_delete(name, filepath=DATABASE_FILEPATH):
    """delete entry from database"""
    # fetch current list
    db_list_current = db_read()
    # FIXME turn into list comprehension
    db_list_new = []
    for item in db_list_current:
        if item[0] != name:
            db_list_new.append(item)
    # FIXME change from length equality to list equality
    if len(db_list_current) == len(db_list_new):
        raise ValueError("Name does not match any existing entry name. Try again.")
    # call write function to update datebase with new list
    # NOTE purpose of fist db_write() is to purge the file contents.
    db_write("", mode="w", disable_write_row=True)
    # FIXME instead of using a for loop, function should accept list of tuples, not a tuple.
    for item in db_list_new:
        db_write(item, mode="a")


def check_if_duplicate_entry(new_entry_name):
    """check if new entry has duplicate name with prior entries"""
    current_entries = db_read()
    current_names = [entry[0] for entry in current_entries]
    is_duplicate = new_entry_name in current_names
    if is_duplicate:
        raise ValueError(
            f'name: "{new_entry_name}" already in use. New entry must have unique name.'
        )


def calculate_duration(start: date, end: date) -> int:
    """Calculate duration between two dates"""
    # NOTE function is called by other functiosn - be aware
    # check args for valid type
    if not isinstance(start, date) or not isinstance(end, date):
        raise ValueError("Both --start and --end must be date objects")
    # check start is before end
    # if start >= end:
    #     raise ValueError("--start date must be earlier than or equal to --end date")
    # calculate duration in days
    duration = (end - start).days
    return duration


# USER INTERFACE - INPUT
def process_args(args):
    """
    Calculate remaining variable.

    :param args: argparse.parse_args() object
    :return: tuple = (name, start, end, duration)
    """
    # TODO Determine altnerate way to unpack namespace object

    name = args.name
    start = args.start
    end = args.end
    duration = args.duration

    def calculate_date_from_duration(initial_date: date, duration: int) -> date:
        """
        Calculate a new date based on a date and a duration in days.

        :param initial_date: The starting date (datetime.date object)
        :param duration: The number of days to add (or subtract if negative)
        :return: A new date object
        """
        return initial_date + timedelta(days=duration)

    if start and end and duration:
        # Notify user to provide 2 of 3 arguements
        raise ValueError("Provide (2) of (3)) arguments only.")

    elif start and duration:
        # calcuate end date and point to args.end
        end = calculate_date_from_duration(start, duration)

    elif end and duration:
        # calcuate start date and point to args.start
        # NOTE duration arg below is set to negative to find start.
        start = calculate_date_from_duration(end, -(duration))

    elif start and end:
        # calcuate duration and point to args.duration
        duration = calculate_duration(start, end)

    else:
        raise ValueError(
            "Provide at least 2 of 3 arguements. Argument options follow: --start, --end, --duration"
        )
        pass
        # return error (TypeError?) clarifying more than (1) argument is require
    return (name, start, end, duration)


def valid_date(date_string):
    """convert argparse arguement from string to date. includes value error."""
    try:
        return date.fromisoformat(date_string)
    except ValueError:
        msg = f"Invalid date format: '{date_string}'. It should be YYYY-MM-DD."
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser(description="script that tracks task countdowns")
parser.add_argument(
    "--name",
    help="name of task, multi-word names are allowed by wrapping with quotes",
)
parser.add_argument("--duration", help="duration of task in days", type=int)
parser.add_argument(
    "--start",
    help="Day which task starts, follow a YYY-MM-DD format",
    type=valid_date,
)
parser.add_argument(
    "--end",
    help="Day which task ends, follow a YYY-MM-DD format",
    type=valid_date,
)
parser.add_argument(
    "--taskboard",
    help="Show entries of program",
    action="store_true",
)
parser.add_argument(
    "--read",
    help="read databse, print to screen",
    action="store_true",
)
parser.add_argument(
    "--delete",
    help="Remove task from task_timer.py",
)

args = parser.parse_args()


# USER INTERFACE - OUTPUT
def print_args(args):
    # FIXME This was a function used during build, Consider removing (or making useful in CLI)
    """prrint args in a fancy way"""
    print()
    print("### Args")
    print("==========")
    print(f"{args.name = }")
    print()
    print(f"{args.duration = }")
    print()
    print(f"{args.start = }")
    print()
    print(f"{args.end = }")
    print("==========")
    print()


def db_print(filepath=DATABASE_FILEPATH):
    """print full database"""
    csv.reader
    file = open(filepath)
    reader = csv.reader(file)
    for row in reader:
        print(row)


def render_table(entries):
    table = Table("name", "start", "end", "duration")
    for row in entries:
        name, start, end, duration = row
        table.add_row(
            f"{name}",
            f"{start}",
            f"{end}",
            f"{duration}",
        )
    Console().print(table)


def create_taskboard(entries, sort):
    # TODO new feature!, get this done.
    # Sort entries
    list.sort()
    if sort == "name":
        pass
    elif sort == "target date":
        pass
    elif sort == "progress":
        pass
    else:
        pass

    # Create table
    table = Table(box=box.ROUNDED)
    table.add_column("name", justify="right")
    table.add_column("target date")
    table.add_column("complete/duration", justify="center")
    table.add_column("progress", justify="center", width=None)
    # Add rows
    for entry in entries:
        item, start, end, duration = entry
        completed = calculate_duration(start=start, end=date.today())
        progress_bar = Progress(
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            expand=False,
        )
        progress_bar.add_task(
            description="",
            total=duration,
            completed=completed,
        )
        table.add_row(
            str(item),
            str(end),
            str(f"[{completed}/{duration}]"),
            progress_bar,
        )
    Console().print(table)


# LOGISTICS CODE
if __name__ == "__main__":
    # CLI logistics code
    if args.start or args.end or args.duration:
        new_entry = process_args(args)
        check_if_duplicate_entry(new_entry[0])
        db_write(new_entry)
    if args.taskboard:
        # render_table(db_read())
        create_taskboard(db_read())
    # FIXME - in process code below
    if args.read:
        db_read()
    if args.delete:
        db_delete(args.delete)
