import requests
import smtplib
import os
from email.mime.text import MIMEText

# 配置参数
SYMBOL = "bitcoin"  # CoinGecko 中的币种 ID
THRESHOLD = 0.1     # 10% 跌幅
EMAIL_SENDER = os.environ['EMAIL_SENDER']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_RECEIVER = os.environ['EMAIL_RECEIVER']



def check_and_notify():
    # 获取当前价格和 24 小时变化百分比
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={SYMBOL}"
    data = requests.get(url).json()[0]
    
    current_price = data['current_price']
    price_change_24h = data['price_change_percentage_24h']  # 返回值如 -10.5

    print(f"当前 {SYMBOL} 价格: {current_price}, 24h 变化: {price_change_24h}%")

    if current_price > 0:  # 下跌超过 10%
        send_email(current_price, price_change_24h)

def send_email(price, change):
    import base64
    
    sender = os.environ.get('EMAIL_SENDER', '').strip()
    password = os.environ.get('EMAIL_PASSWORD', '').strip()
    receiver = os.environ.get('EMAIL_RECEIVER', '').strip()

    # 构造极简邮件头
    mail_msg = (
        f"From: {sender}\r\n"
        f"To: {receiver}\r\n"
        f"Subject: Crypto Alert\r\n\r\n"
        f"{SYMBOL} dropped {change}%, price: {price}"
    )

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        # 不使用 server.login，改用更原始的 docmd (如果 login 持续报错)
        server.ehlo()
        server.login(sender, password) 
        server.sendmail(sender, [receiver], mail_msg.encode('utf-8'))
        server.quit()
        print("邮件已发送成功！")
    except Exception as e:
        print(f"致命错误排查: {e}")



if __name__ == "__main__":
    check_and_notify()
