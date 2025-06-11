# 🕒 ShiftBot – Employee Shift Manager

> ShiftBot is a simple, in-memory Python tool to manage employee schedules and shifts, supporting weekly planning, shift registration, auto-logging based on weekly schedule, conflict detection, and report generation.

**Idea and design by Rsync**

## 📦 Features

* Add and list employees.
* Define weekly work schedules per employee.
* Log and edit specific shifts with date and time.
* Automatically register today’s shift based on the weekday schedule.
* Detect shift conflicts to prevent duplicate entries.
* Generate weekly total hours worked per employee in a report file.
* Load initial data from batch files.
* Save and persist employee data between runs.
* Works offiline

---

## 📁 File Structure

```
.
├── shiftbot.py             # Main Python script
├── shiftbot_data.txt       # Persistent storage of shift and schedule data
├── employees.txt           # Batch file to pre-load employees and schedules
└── report.txt           # Generated weekly report
```

---

## ⚙️ Setup

### Requirements

* Python 3.6 or higher
* No external dependencies

### Run the program

```bash
python shiftbot.py
```

---

## 🧑‍💻 Commands

### 📌 General

```text
help                 - Show available commands
exit                 - Save data and generate weekly report
list                 - List all registered employees
auto                 - Automatically register today’s shifts
```

### 👷 Employee Management

```text
add <name> <id>      - Add a new employee (e.g., add "John Doe" E001)
schedule <id> <day> <start-end> 
                     - Set weekly schedule (e.g., schedule E001 Monday 09:00-17:00)
```

### 🕒 Shift Management

```text
shift <id> <dd-mm-yyyy> <start> <end>
                     - Register a manual shift (e.g., shift E001 25-02-2025 09:00 17:00)

edit <id> <dd-mm-yyyy> <start> <end>
                     - Edit an existing shift (e.g., edit E001 25-02-2025 09:30 17:00)

hours <id> <start_date> <end_date>
                     - Show total hours worked in date range (e.g., hours E001 20-02-2025 25-02-2025)
```

---

## 📂 Batch File Format

You can pre-load employees and their weekly schedules using the `employees.txt` file.

Example format:

```txt
employee|E001|John Doe
schedule|E001|Monday|09:00-17:00
schedule|E001|Tuesday|09:00-17:00
```

---

## 📊 Weekly Report

When you exit (`exit` command), a weekly report will be saved in `relatorio.txt`:

```
Weekly Report: 19-02-2025 to 25-02-2025
--------------------------------------------------
John Doe (E001): 16.0 hours
```

---

## 🧠 Notes

* Days must be written in English: `Monday`, `Tuesday`, ..., `Sunday`.
* Time must be formatted as `HH:MM` or `HHhMM` (e.g., `9:00`, `09h00`).
* Overnight shifts (e.g., 22:00–06:00) are supported.
* Dates must follow `DD-MM-YYYY`.

---

## ✅ Example Session

```text
> add "Alice Smith" E002
Employee added: Alice Smith (E002)

> schedule E002 Monday 09:00-17:00
Monday schedule set for Alice Smith: 09:00-17:00

> auto
Auto shift registered for Alice Smith on 2025-02-25: 09:00-17:00 (8.0 hours)

> hours E002 20-02-2025 25-02-2025
Alice Smith worked 8.0 hours from 20-02-2025 to 25-02-2025

> exit
Weekly report generated in relatorio.txt
```

---

## 📖 License

This project is licensed under the MIT License.

---
