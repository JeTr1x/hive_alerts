import requests
import psutil
import subprocess
import json
import time

# Настройки
TELEGRAM_TOKEN = '8134307090:AAFnr9lBPnYH0HW9EKsIaXsJVW_n_jlhMw8'
CHAT_ID = '-1002282433697'
SERVER_NAME = '7900x'        # <--- Имя сервера
TEMP_THRESHOLD = 75
CPU_LOAD_THRESHOLD = 90
RAM_USAGE_THRESHOLD = 90
DISK_USAGE_THRESHOLD = 90

def send_telegram_alert(message):
    full_message = f'📡 *{SERVER_NAME}*: {message}'
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': full_message, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def get_gpu_temps():
    try:
        result = subprocess.run(['hive', 'stats'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stats = json.loads(result.stdout)
        return [(gpu['index'], gpu['temp']) for gpu in stats.get('gpus', []) if gpu.get('temp')]
    except Exception as e:
        send_telegram_alert(f'Ошибка при получении температуры GPU: {e}')
        return []

def check_system():
    alerts = []

    for idx, temp in get_gpu_temps():
        if temp > TEMP_THRESHOLD:
            alerts.append(f'🔥 *GPU {idx}* перегревается: {temp}°C')

    cpu_load = psutil.cpu_percent(interval=1)
    if cpu_load > CPU_LOAD_THRESHOLD:
        alerts.append(f'⚠️ Высокая загрузка CPU: {cpu_load:.1f}%')

    mem = psutil.virtual_memory()
    if mem.percent > RAM_USAGE_THRESHOLD:
        alerts.append(f'⚠️ ОЗУ почти заполнена: {mem.percent:.1f}%')

    disk = psutil.disk_usage('/')
    if disk.percent > DISK_USAGE_THRESHOLD:
        alerts.append(f'⚠️ Диск почти заполнен: {disk.percent:.1f}%')

    for alert in alerts:
        send_telegram_alert(alert)

def main():
    while True:
        check_system()
        time.sleep(60)

if __name__ == "__main__":
    main()
