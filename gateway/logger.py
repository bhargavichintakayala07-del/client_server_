from datetime import datetime


def save_log(domain, decision):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log = f"{current_time} | {domain} | {decision}\n"

    with open("logs/gateway.log", "a") as file:
        file.write(log)