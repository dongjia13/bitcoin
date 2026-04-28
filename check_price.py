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
    content = f"警报：{SYMBOL} 24小时内变化了 {change}%，当前价格 ${price}。"
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = f"【币价预警】{SYMBOL} 状态更新"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.ehlo()
        
        # 核心修复：先构造认证字节流，避开 f-string 语法限制
        auth_str = f"\0{EMAIL_SENDER}\0{EMAIL_PASSWORD}"
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        # 发送认证指令
        server.docmd("AUTH", f"PLAIN {auth_base64}")
        
        server.send_message(msg)
        server.quit()
        print("邮件已发送成功！")
    except Exception as e:
        print(f"高级认证模式失败: {e}，尝试保底模式...")
        try:
            # 如果上面的特殊认证不行，退回到最标准的模式
            server_fallback = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server_fallback.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server_fallback.send_message(msg)
            server_fallback.quit()
            print("保底模式发送成功！")
        except Exception as e2:
            print(f"所有模式均失败，请检查授权码。错误信息: {e2}")

if __name__ == "__main__":
    check_and_notify()
