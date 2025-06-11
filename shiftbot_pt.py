import datetime
import os

# Current date (February 25, 2025, a Tuesday)
TODAY = datetime.date(2025, 2, 25)
WEEKDAY_MAP = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira",
    4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
}

# In-memory data structure
employees = {}

# Days of the week in Portuguese
DAYS_OF_WEEK = {
    "segunda-feira": "Segunda-feira", "terça-feira": "Terça-feira", "quarta-feira": "Quarta-feira",
    "quinta-feira": "Quinta-feira", "sexta-feira": "Sexta-feira", "sábado": "Sábado", "domingo": "Domingo"
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
                if len(parts) == 3 and parts[0] == "funcionário":
                    emp_id, name = parts[1], parts[2]
                    if emp_id not in employees:
                        employees[emp_id] = {"name": name, "schedule": {}, "shifts": {}}
                        print(f"Funcionário importado: {name} ({emp_id})")
                elif len(parts) == 4 and parts[0] == "horário":
                    emp_id, day, time = parts[1], parts[2].capitalize(), parts[3]
                    if emp_id in employees:
                        employees[emp_id]["schedule"][day] = time
                        print(f"Horário importado para {emp_id}: {day} {time}")
    except FileNotFoundError:
        print("Arquivo employees.txt não encontrado. Continuando sem importação.")

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
                print(f"Conflito detectado para {data['name']} em {today_str}: Turno existente {data['shifts'][today_str]['start']}-{data['shifts'][today_str]['end']}. Use 'editar' para alterar.")
            else:
                start, end = data["schedule"][today_day].split("-")
                hours = calculate_hours(start, end)
                employees[emp_id]["shifts"][today_str] = {"start": start, "end": end, "hours": hours}
                print(f"Turno automático registrado para {data['name']} em {today_str}: {start}-{end} ({hours} horas)")

# Generate weekly report
def generate_weekly_report():
    start_date = TODAY - datetime.timedelta(days=6)  # 7-day range
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = TODAY.strftime("%Y-%m-%d")
    with open("relatorio.txt", "w", encoding="utf-8") as f:
        f.write(f"Relatório Semanal: {start_date.strftime('%d-%m-%Y')} a {TODAY.strftime('%d-%m-%Y')}\n")
        f.write("-" * 50 + "\n")
        for emp_id, data in employees.items():
            total = sum(shift["hours"] for date, shift in data["shifts"].items() if start_str <= date <= end_str)
            f.write(f"{data['name']} ({emp_id}): {total} horas\n")
    print("Relatório semanal gerado em relatorio.txt")

# Main command loop
def main():
    load_data()
    load_batch_data()
    auto_log_shifts()
    print("Bem-vindo ao ShiftBot - Gerenciador de Funcionários")
    print("Digite 'ajuda' para ver os comandos.")

    while True:
        cmd = input("> ").strip().lower()
        parts = cmd.split()

        if not parts:
            continue

        if parts[0] == "ajuda":
            print("""
Comandos:
- adicionar <nome> <id> : Adicionar um funcionário (ex.: adicionar "João Silva" E001)
- horário <id> <dia> <início-fim> : Definir horário semanal (ex.: horário E001 Segunda-feira 9:00-17:00)
- turno <id> <data> <início> <fim> : Registrar turno (ex.: turno E001 25-02-2025 9:00 17:00)
- horas <id> <data_início> <data_fim> : Mostrar horas totais (ex.: horas E001 20-02-2025 25-02-2025)
- editar <id> <data> <início> <fim> : Editar turno (ex.: editar E001 25-02-2025 9:30 17:00)
- listar : Mostrar todos os funcionários
- auto : Executar registro automático de turnos para hoje
- sair : Sair, salvar dados e gerar relatório
            """)

        elif parts[0] == "adicionar" and len(parts) >= 3:
            emp_id = parts[-1]
            name = " ".join(parts[1:-1]).strip('"')
            if emp_id in employees:
                print(f"Erro: Funcionário {emp_id} já existe.")
            else:
                employees[emp_id] = {"name": name, "schedule": {}, "shifts": {}}
                print(f"Funcionário adicionado: {name} ({emp_id})")

        elif parts[0] == "horário" and len(parts) == 4:
            emp_id, day, time = parts[1], parts[2].capitalize(), parts[3]
            if emp_id not in employees:
                print(f"Erro: Funcionário {emp_id} não encontrado.")
            elif day not in DAYS_OF_WEEK.values():
                print("Erro: Dia da semana inválido. Use Segunda-feira, Terça-feira, etc.")
            elif "-" not in time:
                print("Erro: Formato de horário deve ser início-fim (ex.: 9:00-17:00)")
            else:
                employees[emp_id]["schedule"][day] = time
                print(f"Horário de {day} definido para {employees[emp_id]['name']}: {time}")

        elif parts[0] == "turno" and len(parts) == 5:
            emp_id, date, start, end = parts[1], parts[2], parts[3], parts[4]
            if emp_id not in employees:
                print(f"Erro: Funcionário {emp_id} não encontrado.")
            elif not valid_date(date):
                print("Erro: Data inválida ou posterior a hoje (25-02-2025).")
            else:
                internal_date = convert_date(date)
                if internal_date in employees[emp_id]["shifts"]:
                    print(f"Conflito detectado: Turno existente em {date}: {employees[emp_id]['shifts'][internal_date]['start']}-{employees[emp_id]['shifts'][internal_date]['end']}. Use 'editar' para alterar.")
                else:
                    try:
                        hours = calculate_hours(start, end)
                        if hours <= 0:
                            print("Erro: Horário de fim deve ser após o início.")
                        else:
                            employees[emp_id]["shifts"][internal_date] = {"start": start, "end": end, "hours": hours}
                            print(f"Turno registrado para {employees[emp_id]['name']} em {date}: {start}-{end} ({hours} horas)")
                    except:
                        print("Erro: Formato de horário inválido (use HH:MM ou HHhMM, ex.: 9:00).")

        elif parts[0] == "horas" and len(parts) == 4:
            emp_id, start_date, end_date = parts[1], parts[2], parts[3]
            if emp_id not in employees:
                print(f"Erro: Funcionário {emp_id} não encontrado.")
            elif not (valid_date(start_date) and valid_date(end_date)):
                print("Erro: Intervalo de datas inválido.")
            else:
                start_internal = convert_date(start_date)
                end_internal = convert_date(end_date)
                total = sum(shift["hours"] for date, shift in employees[emp_id]["shifts"].items()
                            if start_internal <= date <= end_internal)
                print(f"{employees[emp_id]['name']} trabalhou {total} horas de {start_date} a {end_date}")

        elif parts[0] == "editar" and len(parts) == 5:
            emp_id, date, start, end = parts[1], parts[2], parts[3], parts[4]
            if emp_id not in employees:
                print(f"Erro: Funcionário {emp_id} não encontrado.")
            else:
                internal_date = convert_date(date)
                if internal_date not in employees[emp_id]["shifts"]:
                    print(f"Erro: Nenhum turno encontrado para {date}.")
                else:
                    try:
                        hours = calculate_hours(start, end)
                        if hours <= 0:
                            print("Erro: Horário de fim deve ser após o início.")
                        else:
                            employees[emp_id]["shifts"][internal_date] = {"start": start, "end": end, "hours": hours}
                            print(f"Turno atualizado para {employees[emp_id]['name']} em {date}: {start}-{end} ({hours} horas)")
                    except:
                        print("Erro: Formato de horário inválido (use HH:MM ou HHhMM, ex.: 9:00).")

        elif parts[0] == "listar":
            if not employees:
                print("Nenhum funcionário registrado.")
            else:
                print("Funcionários:")
                for emp_id, data in employees.items():
                    print(f"- {emp_id}: {data['name']}")

        elif parts[0] == "auto":
            auto_log_shifts()

        elif parts[0] == "sair":
            save_data()
            generate_weekly_report()
            print("Dados salvos. Relatório gerado. Até logo!")
            break

        else:
            print("Comando desconhecido. Digite 'ajuda' para assistência.")

if __name__ == "__main__":
    main()