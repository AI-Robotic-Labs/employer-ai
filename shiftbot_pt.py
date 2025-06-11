import datetime
import os

# Current date (February 25, 2025, a Tuesday)
TODAY = datetime.date(2025, 2, 25)
WEEKDAY_MAP = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday"
}

# In-memory data structure
employees = {}

# Days of the week in English
DAYS_OF_WEEK = {
    "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
    "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday", "sunday": "Sunday"
}

# Helper function to calculate hours
def calculate_hours(start, end):
    start = start.replace("h", ":")
    end = end.replace("h", ":")
    start_h, start_m = map(int, start.split(":"))
    end_h, end_m = map(int, end.split(":"))
    start_mins = start_h * 60 + start_m
    end_mins = end_h * 60 + end_m
    if end_mins < start_mins:  # Overnight shift
        end_mins += 24 * 60
    return (end_mins - start_mins) / 60

# Helper function to validate and parse DD-MM-YYYY date
def valid_date(date_str):
    try:
        day, month, year = map(int, date_str.split("-"))
        date = datetime.date(year, month, day)
        return date <= TODAY
    except:
        return False

# Convert DD-MM-YYYY to YYYY-MM-DD
def convert_date(date_str):
    day, month, year = map(int, date_str.split("-"))
    return f"{year}-{month:02d}-{day:02d}"

# Load saved data
def load_data():
    try:
        with open("shiftbot_data.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                emp_id = parts[0]
                if emp_id not in employees:
                    employees[emp_id] = {"name": parts[1], "schedule": {}, "shifts": {}}
                if parts[2] == "schedule":
                    employees[emp_id]["schedule"][parts[3]] = parts[4]
                elif parts[2] == "shift":
                    employees[emp_id]["shifts"][parts[3]] = {
                        "start": parts[4], "end": parts[5], "hours": float(parts[6])
                    }
    except FileNotFoundError:
        pass

# Load initial employees from a batch file
def load_batch_data():
    try:
        with open("employees.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3 and parts[0] == "employee":
                    emp_id, name = parts[1], parts[2]
                    if emp_id not in employees:
                        employees[emp_id] = {"name": name, "schedule": {}, "shifts": {}}
                        print(f"Employee imported: {name} ({emp_id})")
                elif len(parts) == 4 and parts[0] == "schedule":
                    emp_id, day, time = parts[1], parts[2].capitalize(), parts[3]
                    if emp_id in employees:
                        employees[emp_id]["schedule"][day] = time
                        print(f"Schedule imported for {emp_id}: {day} {time}")
    except FileNotFoundError:
        print("File employees.txt not found. Continuing without importing.")

# Save data to file
def save_data():
    with open("shiftbot_data.txt", "w") as f:
        for emp_id, data in employees.items():
            f.write(f"{emp_id}|{data['name']}|name\n")
            for day, time in data["schedule"].items():
                f.write(f"{emp_id}|{data['name']}|schedule|{day}|{time}\n")
            for date, shift in data["shifts"].items():
                f.write(f"{emp_id}|{data['name']}|shift|{date}|{shift['start']}|{shift['end']}|{shift['hours']}\n")

# Auto-log shifts based on today's schedule with conflict detection
def auto_log_shifts():
    today_str = TODAY.strftime("%Y-%m-%d")
    today_day = WEEKDAY_MAP[TODAY.weekday()]
    for emp_id, data in employees.items():
        if today_day in data["schedule"]:
            if today_str in data["shifts"]:
                print(f"Conflict detected for {data['name']} on {today_str}: Existing shift {data['shifts'][today_str]['start']}-{data['shifts'][today_str]['end']}. Use 'edit' to modify.")
            else:
                start, end = data["schedule"][today_day].split("-")
                hours = calculate_hours(start, end)
                employees[emp_id]["shifts"][today_str] = {"start": start, "end": end, "hours": hours}
                print(f"Automatic shift logged for {data['name']} on {today_str}: {start}-{end} ({hours} hours)")

# Generate weekly report
def generate_weekly_report():
    start_date = TODAY - datetime.timedelta(days=6)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = TODAY.strftime("%Y-%m-%d")
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(f"Weekly Report: {start_date.strftime('%d-%m-%Y')} to {TODAY.strftime('%d-%m-%Y')}\n")
        f.write("-" * 50 + "\n")
        for emp_id, data in employees.items():
            total = sum(shift["hours"] for date, shift in data["shifts"].items() if start_str <= date <= end_str)
            f.write(f"{data['name']} ({emp_id}): {total} hours\n")
    print("Weekly report generated in report.txt")

# Main command loop
def main():
    load_data()
    load_batch_data()
    auto_log_shifts()
    print("Welcome to ShiftBot - Employee Manager")
    print("Type 'help' to see available commands.")

    while True:
        cmd = input("> ").strip().lower()
        parts = cmd.split()

        if not parts:
            continue

        if parts[0] == "help":
            print("""
Commands:
- add <name> <id> : Add an employee (e.g.: add "John Smith" E001)
- schedule <id> <day> <start-end> : Set weekly schedule (e.g.: schedule E001 Monday 9:00-17:00)
- shift <id> <date> <start> <end> : Register shift (e.g.: shift E001 25-02-2025 9:00 17:00)
- hours <id> <start_date> <end_date> : Show total hours (e.g.: hours E001 20-02-2025 25-02-2025)
- edit <id> <date> <start> <end> : Edit shift (e.g.: edit E001 25-02-2025 9:30 17:00)
- list : Show all employees
- auto : Run automatic shift logging for today
- exit : Exit, save data and generate report
            """)

        elif parts[0] == "add" and len(parts) >= 3:
            emp_id = parts[-1]
            name = " ".join(parts[1:-1]).strip('"')
            if emp_id in employees:
                print(f"Error: Employee {emp_id} already exists.")
            else:
                employees[emp_id] = {"name": name, "schedule": {}, "shifts": {}}
                print(f"Employee added: {name} ({emp_id})")

        elif parts[0] == "schedule" and len(parts) == 4:
            emp_id, day, time = parts[1], parts[2].capitalize(), parts[3]
            if emp_id not in employees:
                print(f"Error: Employee {emp_id} not found.")
            elif day not in DAYS_OF_WEEK.values():
                print("Error: Invalid day. Use Monday, Tuesday, etc.")
            elif "-" not in time:
                print("Error: Time format must be start-end (e.g.: 9:00-17:00)")
            else:
                employees[emp_id]["schedule"][day] = time
                print(f"Schedule for {day} set for {employees[emp_id]['name']}: {time}")

        elif parts[0] == "shift" and len(parts) == 5:
            emp_id, date, start, end = parts[1], parts[2], parts[3], parts[4]
            if emp_id not in employees:
                print(f"Error: Employee {emp_id} not found.")
            elif not valid_date(date):
                print("Error: Invalid or future date (25-02-2025 is the limit).")
            else:
                internal_date = convert_date(date)
                if internal_date in employees[emp_id]["shifts"]:
                    print(f"Conflict: Existing shift on {date}: {employees[emp_id]['shifts'][internal_date]['start']}-{employees[emp_id]['shifts'][internal_date]['end']}. Use 'edit' to modify.")
                else:
                    try:
                        hours = calculate_hours(start, end)
                        if hours <= 0:
                            print("Error: End time must be after start time.")
                        else:
                            employees[emp_id]["shifts"][internal_date] = {"start": start, "end": end, "hours": hours}
                            print
