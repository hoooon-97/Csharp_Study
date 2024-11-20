import os
from datetime import datetime
from collections import defaultdict

def get_device_info(filename):
    """로그 파일에서 PID와 hostname 추출"""
    model = "Unknown Model"
    hostname = "Unknown Host"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reading_inventory = False
            for line in f:
                # Hostname 찾기 - hostname 명령어 출력 확인
                if "hostname" in line.lower():
                    hostname = line.split()[1]
                    continue
                
                # PID 찾기
                if "show inventory" in line:
                    reading_inventory = True
                    continue
                if reading_inventory and "PID:" in line:
                    potential_pid = line.split("PID:")[1].split(",")[0].strip()
                    if potential_pid and len(potential_pid) > 1:
                        model = potential_pid
                        reading_inventory = False
                
                # 둘 다 찾았으면 종료
                if model != "Unknown Model" and hostname != "Unknown Host":
                    break
                    
    except Exception as e:
        print(f"장비 정보 추출 중 오류 발생 ({filename}): {e}")
    
    return model, hostname


def filter_logs(file_path, start_month='Oct', start_day=15):
    error_keywords = [
        "limited space"
    ]
    
    current_year = datetime.now().year
    start_date = datetime.strptime(f'{start_month} {start_day} {current_year}', '%b %d %Y')
    
    message_counts = defaultdict(lambda: defaultdict(lambda: [None, 0]))
    has_errors = False
    
    def process_file(file_obj):
        nonlocal has_errors
        for line in file_obj:
            try:
                original_line = line.strip()
                date_part = line[:6].replace("  ", " ").strip()
                if not date_part:
                    continue
                
                time_part = line[7:18].strip()
                log_date = datetime.strptime(f'{date_part} {current_year}', '%b %d %Y')
                
                if log_date >= start_date:
                    if any(keyword.lower() in line.lower() for keyword in error_keywords):
                        has_errors = True
                        message_body = original_line[19:].strip()
                        
                        if message_counts[date_part][message_body][0] is None:
                            message_counts[date_part][message_body][0] = time_part
                        
                        message_counts[date_part][message_body][1] += 1
                        
            except ValueError:
                continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            process_file(f)
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp949') as f:
                process_file(f)
        except Exception as e:
            print(f"파일 처리 중 오류 발생: {e}")
            return {}, False

    return message_counts, has_errors

def process_directory(directory_path, output_file='filtered_errors.log'):
    device_logs = {}
    device_info = {}  # {device_ip: (model, hostname)}
    has_any_errors = False
    all_devices = set()
    error_devices = set()
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.log') and filename != output_file:
            device_ip = filename.split('_')[0]
            all_devices.add(device_ip)
            
            file_path = os.path.join(directory_path, filename)
            print(f"처리 중: {filename}")
            
            # 장비 정보 저장
            model, hostname = get_device_info(file_path)
            device_info[device_ip] = (model, hostname)
            
            file_counts, has_errors = filter_logs(file_path)
            
            if has_errors:
                has_any_errors = True
                error_devices.add(device_ip)
                if device_ip not in device_logs:
                    device_logs[device_ip] = defaultdict(lambda: defaultdict(lambda: [None, 0]))
                
                for date, messages in file_counts.items():
                    for message, (time, count) in messages.items():
                        if device_logs[device_ip][date][message][0] is None:
                            device_logs[device_ip][date][message][0] = time
                        device_logs[device_ip][date][message][1] += count
    
    if has_any_errors:
        with open(output_file, 'w', encoding='utf-8') as f:
            for device in sorted(device_logs.keys()):
                if device_logs[device]:
                    model, hostname = device_info[device]
                    f.write(f"{device}, {model}, {hostname}:\n")
                    
                    sorted_dates = sorted(device_logs[device].keys(), 
                                       key=lambda x: int(x.split()[1]))
                    
                    for date in sorted_dates:
                        for message, (time, count) in sorted(device_logs[device][date].items()):
                            f.write(f"  === {date} === {time} {message} (발생횟수: {count}회)\n")
                    f.write("\n")
            
            f.write("\n=== 통계 정보 ===\n")
            f.write(f"전체 장비 수: {len(all_devices)}대\n")
            f.write(f"장애 발생 장비 수: {len(error_devices)}대\n")
            f.write(f"장애 발생률: {(len(error_devices)/len(all_devices)*100):.1f}%\n")
                
        print(f"\n결과가 {output_file}에 저장되었습니다.")
        print(f"\n통계 정보:")
        print(f"전체 장비 수: {len(all_devices)}대")
        print(f"장애 발생 장비 수: {len(error_devices)}대")
        print(f"장애 발생률: {(len(error_devices)/len(all_devices)*100):.1f}%")
    else:
        print("에러/장애 관련 로그가 없습니다.")
        print(f"\n통계 정보:")
        print(f"전체 장비 수: {len(all_devices)}대")
        print(f"장애 발생 장비 수: 0대")
        print(f"장애 발생률: 0.0%")

if __name__ == "__main__":
    directory_path = "/Users/parksanghun/Library/CloudStorage/OneDrive-Ringnet/2. Coupang/8. FC_CAMP Maintainance/2024-11/FC/L2"
    output_file = "L2_error.txt"
    
    if not os.path.exists(directory_path):
        print(f"경로를 찾을 수 없습니다: {directory_path}")
    else:
        process_directory(directory_path, output_file)