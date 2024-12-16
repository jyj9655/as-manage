import requests
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from html import unescape
import os

# HTML 태그와 엔티티 제거
def clean_html(raw_html):
    clean_text = re.sub(r'<[^>]*>', '', raw_html)
    clean_text = unescape(clean_text)
    return clean_text.strip()

# 데이터 로드
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except:
        data = []
    return data

# 데이터 저장
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# 새로운 데이터 확인
def check_new_data(current_data, previous_data, key_field):
    new_data = []
    previous_keys = {item[key_field] for item in previous_data}

    for item in current_data:
        if item[key_field] not in previous_keys:
            new_data.append(item)

    return new_data

# 이메일 보내기
def send_email(library_name, new_data):
    # 이메일 정보 입력
    host_email = '보내는 메일 아이디'
    host_password = '보내는 메일 비밀번호'

    # 이메일 수신자 목록
    to_email = ['팀원1', '팀원2', '팀원3']

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = f"{now} {library_name} 신규 A/S 접수\n\n"

    for item in new_data:
        result += f"============================================================\n"
        result += f"[제목]: {item.get('title', 'N/A')}\n"
        result += f"[작성일]: {item.get('inputDate', 'N/A')}\n"
        result += f"[중요도]: {item.get('importance', 'N/A')}\n"
        result += f"[상태]: {item.get('status', 'N/A')}\n"
        result += f"[도서관 구분]: {item.get('manageCode', 'N/A')}\n"
        result += f"[내용]: {clean_html(item.get('content', ''))}\n"

        # 링크 처리
        if library_name == "A도서관":
            # A도서관의 경우 recKey로 링크 생성
            link = f"url/as/{item['recKey']}"
        else:
            # 다른 도서관은 JSON에 있는 link 필드 사용
            link = item.get('link', 'N/A')
        
        result += f"[바로가기]: {link}\n"
        result += f"============================================================\n\n"

    subject = f"{now} {library_name} 신규 A/S 접수"
    msg = MIMEMultipart()
    msg['From'] = host_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(result))

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(host_email, host_password)
        smtp_server.sendmail(host_email, to_email, msg.as_string())
        smtp_server.quit()
        print(f"Email sent successfully for {library_name}")
    except Exception as e:
        print(f"Failed to send email for {library_name}: {e}")

# 도서관별 데이터 처리 로직
def get_library_data(library):
    url = library['url']
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        data = json.loads(response.text)
        if library['name'] == "A도서관":
            return data['data']['data']  # A 데이터 구조
        elif library['name'] == "B도서관":
            return data['data']  # B 데이터 구조
        elif library['name'] == "C도서관":
            return data['data']  # C 데이터 구조
        elif library['name'] == "D도서관":
            return data['data']  # D 데이터 구조
    else:
        print(f"Failed to fetch data for {library['name']}: {response.status_code}")
        return []

# 도서관 정보 설정
libraries = [
    {
        "name": "A도서관",
        "url": "A도서관 A/S 게시판 목록 조회 API",
        "data_file": "data_A.json",
        "key_field": "recKey"  # 데이터 고유 필드
    },
    {
        "name": "B도서관",
        "url": "B도서관 A/S 게시판 목록 조회 API",
        "data_file": "data_B.json",
        "key_field": "recKey"
    },
    {
        "name": "C도서관",
        "url": "C도서관 A/S 게시판 목록 조회 API",
        "data_file": "data_C.json",
        "key_field": "recKey"
    },
    {
        "name": "D도서관",
        "url": "D도서관 A/S 게시판 목록 조회 API",
        "data_file": "data_D.json",
        "key_field": "recKey"
    }
]

# 메인 실행
for library in libraries:
    print(f"Processing {library['name']}...")
    previous_data = load_data(library['data_file'])
    current_data = get_library_data(library)

    if current_data:
        new_data = check_new_data(current_data, previous_data, library['key_field'])
        if new_data:
            send_email(library['name'], new_data)  # 도서관별 메일 전송
            save_data(library['data_file'], current_data)  # 데이터 저장