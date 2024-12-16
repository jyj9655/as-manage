# 도서관 A/S 관리 자동화 프로젝트

## 프로젝트 개요

### 배경
유지보수 업무를 위해 직원들은 도서관별로 A/S 게시판에 수시로 접속해야 했습니다.  
신규 등록된 A/S가 있는지 직접 확인하고, 데이터를 공유 드라이브에 업로드하는 번거로운 작업이 반복되었습니다.  
이 과정에서 비효율성을 느꼈고, 이를 해결하기 위해 자동화 시스템을 기획하게 되었습니다.  

Python 파일을 `exe`로 빌드한 후 작업 스케줄러에 등록하여 1시간마다 실행되도록 설정했습니다.  
첫 실행 시 게시판 데이터를 가져와 `data_도서관명.json` 파일로 저장하며, 두 번째 실행부터는 기존 JSON 데이터와 비교합니다.  
비교 결과 **신규 등록** 또는 **처리 완료**와 같은 차이점이 발견되면 해당 내용을 이메일로 발송하여 알림을 제공합니다.  
이를 통해 반복 작업을 제거하고 업무 효율성을 크게 향상시켰습니다.  

---

## 발전 과정

### **v0: 초기 버전**
초기에는 각 도서관마다 **별도의 Python 파일**을 작성하여, 이를 각각 `exe` 파일로 빌드하고 작업 스케줄러에 등록하는 방식으로 자동화를 구현했습니다.

#### 초기 구조
- 도서관별로 독립된 Python 파일 존재.
- 신규 데이터를 감지하고 이메일로 발송.
- 스케줄러에서 1시간마다 실행.

#### 문제점
- 도서관이 **2~3개일 때는 쉽게 관리 가능**했지만, 도서관이 늘어날수록 Python 파일과 빌드 관리가 번거로워짐.
- 이메일 수신자를 수정하려면 각각의 Python 파일을 수정 후 재빌드해야 함.

#### `초기 Python 코드` 예시 (A도서관)
```python
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
    msg['From'] = my_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    # 메일 본문 추가
    text = MIMEText(result)
    msg.attach(text)

    # SMTP 서버 연결
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(my_email, my_password)

    # 메일 보내기
    smtp_server.sendmail(my_email, to_email, msg.as_string())
    smtp_server.quit()

# data.json 파일에서 이전 데이터 불러오기
previous_data = load_data('data_gangseo.json')

# 현재 데이터 가져오기
current_data = get_current_data()

# 새로운 데이터가 있는지 확인하기
new_data = check_new_data(current_data, previous_data)

if new_data:
    # 메일 보내기
    send_email(new_data)

    # data.json 파일에 현재 데이터 저장하기
    save_data('data_A.json', current_data['data'])
```
---

### **v1: 중간 버전**
도서관이 **2개 이상**으로 늘어나면서 각각의 파일을 관리하는 번거로움을 줄이기 위해, 도서관별로 **Python 파일을 통합**했습니다.

#### 중간 구조
- 모든 도서관 정보를 한 파일에서 관리.
- 도서관별 데이터를 처리하는 로직을 추가.
- 통합된 Python 파일을 `exe`로 빌드 후 작업 스케줄러에 등록.

#### 문제점
- 도서관별 이메일 수신자 수정 시, 여전히 Python 파일을 수정 후 재빌드 필요.

#### `중간 Python 코드` 예시
```python
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
    msg['From'] = my_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(result))

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(my_email, my_password)
        smtp_server.sendmail(my_email, to_email, msg.as_string())
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
```
---

### **v2: 최종 버전**
이메일 수신자 목록이 변경될 때마다 **Python 파일을 수정하고 재빌드해야 하는 불편함**을 해결하기 위해, **수신자 목록과 이메일 설정을 별도의 JSON 파일로 분리**했습니다. 이제 JSON 파일만 수정하면 즉시 반영됩니다.

#### 최종 구조
- `config.json` 파일에서 이메일 및 도서관별 수신자 관리.
- Python 코드에서는 `config.json`을 읽어 이메일 발송.

#### `config.json` 예시
```json
{
    "host_email": "보내는 메일 아이디",
    "host_password": "보내는 메일 비밀번호",
    "default_recipients": ["기본 메일"],
    "libraries": {
        "A도서관": ["팀원1", "팀원2", "팀원3"],
        "B도서관": ["팀원1", "팀원2"],
        "C도서관": ["팀원1", "팀원2", "팀원3"],
        "D도서관": ["팀원1", "팀원2"]
    }
}
```
#### `최종 Python 코드` 예시
```python
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
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load data from {file_path}: {e}")
        data = []
    return data

# 설정 파일 로드
def load_config(config_file):
    try:
        with open(config_file, 'r', encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}

# 데이터 저장
def save_data(file_path, data):
    try:
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to save data to {file_path}: {e}")

# 새로운 데이터 확인
def check_new_data(current_data, previous_data, key_field):
    new_data = []
    previous_keys = {item[key_field] for item in previous_data}

    for item in current_data:
        if item[key_field] not in previous_keys:
            new_data.append(item)

    return new_data

# 이메일 보내기
def send_email(library_name, new_data, config):
    host_email = config.get('host_email')
    host_password = config.get('host_password')
    to_email = config['libraries'].get(library_name, config.get('default_recipients', []))

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
            link = f"url/as/{item['recKey']}"
        else:
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
config = load_config("config.json")  # 설정 파일 로드

if not config:
    print("Configuration could not be loaded. Exiting...")
else:
    for library in libraries:
        print(f"Processing {library['name']}...")
        previous_data = load_data(library['data_file'])
        current_data = get_library_data(library)

        if current_data:
            new_data = check_new_data(current_data, previous_data, library['key_field'])
            if new_data:
                send_email(library['name'], new_data, config)  # 도서관별 이메일 발송
                save_data(library['data_file'], current_data)  # 데이터 저장

```
---

## 주요 성과
1. **업무 시간 절약**:  
   - 직원들이 수작업으로 게시판을 확인하던 시간을 줄이고, 중요한 업무에 집중할 수 있게 되었습니다.

2. **유지보수 효율성 개선**:  
   - 도서관별 Python 파일을 통합하고, 이메일 수신자를 JSON 파일로 관리함으로써 수정 및 확장이 용이해졌습니다.

3. **확장성 강화**:  
   - 새로운 도서관이 추가될 때, JSON 파일에 해당 도서관 정보를 추가하기만 하면 됩니다.
   - 수신자 변경을 할 경우 config.json 수정으로 쉽게 변경이 가능합니다.
