import requests
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from html import unescape

def clean_html(raw_html):
    # 정규식을 사용하여 HTML 태그 제거
    clean_text = re.sub(r'<[^>]*>', '', raw_html)  # HTML 태그 제거
    clean_text = unescape(clean_text)  # HTML 엔티티(&gt;, &lt;, etc.)를 실제 문자로 변환
    return clean_text.strip()

def get_current_data():
    # API에 요청
    url = 'A도서관 A/S 게시판 목록 조회 API'
    response = requests.get(url)

    # 응답 JSON 데이터 파싱
    data = json.loads(response.text)
    return data

def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except:
        data = []
    return data

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

def check_new_data(current_data, previous_data):
    new_data = []
    for item in current_data['data']:
        if item not in previous_data:
            new_data.append(item)
    return new_data

def send_email(new_data):
    # 이메일 정보 입력
    host_email = '보내는 메일 아이디'
    host_password = '보내는 메일 비밀번호'

    # 이메일 수신자 목록
    to_email = ['팀원1', '팀원2', '팀원3']
    
    # 데이터 가공
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = f"{now} A도서관 신규 A/S 접수\n\n"

    for item in new_data:
        result += f"============================================================\n"
        result += f"[제목] : {item['title']}\n\n"
        result += f"[작성일] : {item['inputDate']}\n\n"
        result += f"[중요도] : {item['importance']}\n"
        result += f"[상태] : {item['status']}\n"
        result += f"[도서관 구분] : {item['manageCode']}\n\n"
        
        # HTML 태그 및 엔티티 처리
        cleaned_content = clean_html(item['content'])
        result += f"[내용] : {cleaned_content}\n"
        result += f"[바로가기] : {item['link']}\n"
        result += f"============================================================\n\n"

    # 메일 구성
    subject = f"{now} A도서관 신규 A/S접수"

    msg = MIMEMultipart()
    msg['From'] = host_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    # 메일 본문 추가
    text = MIMEText(result)
    msg.attach(text)

    # SMTP 서버 연결
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(host_email, host_password)

    # 메일 보내기
    smtp_server.sendmail(host_email, to_email, msg.as_string())
    smtp_server.quit()

# data.json 파일에서 이전 데이터 불러오기
previous_data = load_data('data_A.json')

# 현재 데이터 가져오기
current_data = get_current_data()

# 새로운 데이터가 있는지 확인하기
new_data = check_new_data(current_data, previous_data)

if new_data:
    # 메일 보내기
    send_email(new_data)

    # data.json 파일에 현재 데이터 저장하기
    save_data('data_A.json', current_data['data'])