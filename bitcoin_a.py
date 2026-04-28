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

    if price_change_24h <= -10:  # 下跌超过 10%
        send_email(current_price, price_change_24h)

def send_email(price, change):
    msg = MIMEText(f"警报：{SYMBOL} 24小时内下跌了 {change}%，当前价格 ${price}。")
    msg['Subject'] = f"【币价预警】{SYMBOL} 跌幅超过 10%!"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # 以 QQ 邮箱 SMTP 为例 (smtp.qq.com, 端口 465)
    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("邮件已发送")

if __name__ == "__main__":
    check_and_notify()
