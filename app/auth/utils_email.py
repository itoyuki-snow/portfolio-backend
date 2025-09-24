import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_order_confirmation_email(to_email: str, username: str):
    sender_email = "amaironohi@example.com"
    sender_name = "天色の日-AmaironoHi-"
    subject = "ご注文いただきありがとうございました!"
    body = f"""
{username} 様

この度は天色の日-AmaironoHi-オンラインショップをご利用いただき、誠にありがとうございます。
ご注文が完了しました。商品の発送まで今しばらくお待ちください。

またのご利用を心よりお待ちしております。

天色の日-AmaironoHi-
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login("amaironohi@example.com", "yourpassword")
            server.send_message(msg)
    except Exception as e:
        print("メール送信エラー:", e)
