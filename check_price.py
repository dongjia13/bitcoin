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

import requests
import smtplib
import os
import base64
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

        # 测试阶段强制发送，测通后请改回 if price_change_24h <= -10:
        if True: 
            send_email(current_price, price_change_24h)
    except Exception as e:
        print(f"获取数据或逻辑执行失败: {e}")

def send_email(price, change):
    # 构造邮件内容
    content = f"警报：{SYMBOL} 24小时内变化了 {change}%，当前价格 ${price}。"
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = f"【币价预警】{SYMBOL} 状态更新"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        # 使用 SSL 连接 QQ 邮箱
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.ehlo()
        
        # --- 核心修复：手动处理 Base64 认证，规避 smtplib 内部拼接错误 ---
        user_b64 = base64.b64encode(EMAIL_SENDER.encode('utf-8')).decode('utf-8')
        pass_b64 = base64.b64encode(EMAIL_PASSWORD.encode('utf-8')).decode('utf-8')
        
        # 手动发送认证指令
        server.docmd("AUTH", f"PLAIN {base64.b64encode(f'\0{EMAIL_SENDER}\0{EMAIL_PASSWORD}'.encode('utf-8')).decode('utf-8')}")
        
        server.send_message(msg)
        server.quit()
        print("邮件已发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")
        # 如果手动认证也失败，尝试退回到标准模式作为保底
        print("尝试保底模式...")
        try:
            server_fallback = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server_fallback.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server_fallback.send_message(msg)
            server_fallback.quit()
            print("保底模式发送成功！")
        except Exception as e2:
            print(f"保底模式也失败: {e2}")



if __name__ == "__main__":
    check_and_notify()
