import requests
import smtplib
import os
import ssl
from email.mime.text import MIMEText

# 配置参数
SYMBOL = "bitcoin"
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '').strip()
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '').strip()
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '').strip()

def check_and_notify():
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={SYMBOL}"
    try:
        response = requests.get(url)
        data = response.json()[0]
        current_price = data['current_price']
        price_change_24h = data['price_change_percentage_24h']
        
        print(f"当前 {SYMBOL} 价格: {current_price}, 24h 变化: {price_change_24h}%")

        # 强制测试，测通后改回 if price_change_24h <= -10:
        if True: 
            send_email(current_price, price_change_24h)
    except Exception as e:
        print(f"执行失败: {e}")

def send_email(price, change):
    msg = MIMEText(f"警报：{SYMBOL} 24h变化 {change}%，价格 ${price}。", 'plain', 'utf-8')
    msg['Subject'] = "Crypto Price Alert"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # 创建安全的 SSL 上下文
    context = ssl.create_default_context()

    try:
        # 使用 with 语句自动管理连接关闭
        with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context) as server:
            # 直接调用 login，不做任何手动编码
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("邮件已发送成功！")
    except Exception as e:
        print(f"发送彻底失败: {e}")
        print("排查建议：请检查 GitHub Secrets 中的 EMAIL_PASSWORD 是否为最新的 16 位授权码（无空格）。")

if __name__ == "__main__":
    check_and_notify()
