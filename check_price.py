import requests
import os

def check():
    # 1. 定义要监控的币种 ID (对应 CoinGecko 的 API ID)
    coin_ids = ["bitcoin", "ethereum", "binancecoin", "solana"]
    ids_str = ",".join(coin_ids)
    
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids_str}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        triggered_list = []  # 存放达到告警条件的币种信息
        all_info = []        # 存放所有币种的当前状态（用于日志查看）

        for coin in data:
            name = coin['name']
            symbol = coin['symbol'].upper()
            price = coin['current_price']
            change = coin['price_change_percentage_24h']
            
            status = f"{name}({symbol}): ${price}, 24h变化: {change:.2f}%"
            all_info.append(status)
            
            # 2. 判断逻辑：如果跌幅 <= -10% 则加入告警列表
            # 测试阶段你可以先改为 -0.1 (只要跌了就报) 来确认多币种是否生效
            if change <= -10:
                triggered_list.append(status)

        # 打印到 GitHub Actions 日志，方便调试
        print("当前市场状态:\n" + "\n".join(all_info))

        should_notify = "false"
        price_info = ""

        # 3. 如果有币种触发了告警
        if len(triggered_list) > 0:
            should_notify = "true"
            # 邮件内容：列出所有达到告警线的币
            price_info = "【币价告警】以下币种跌幅超过 10%：\n\n" + "\n".join(triggered_list)

        # 4. 将结果传递给 GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"should_notify={should_notify}\n")
            # 注意：如果字符串有换行，需要处理。这里简单处理为一行，或者使用环境变量
            # 为了保证邮件格式，我们把换行符替换为 Action 识别的格式
            f.write(f"price_info={price_info.replace('', '')}\n")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    check()
