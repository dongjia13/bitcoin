import requests
import os

def check():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin"
    try:
        response = requests.get(url)
        data = response.json()[0]
        price = data['current_price']
        change = data['price_change_percentage_24h']
        
        info = f"BTC当前价格: ${price}, 24h变化: {change}%"
        print(info)

        # 只要运行就通知（测试用），后期可以改回 change <= -10
        should_notify = "true" 
        
        # 将结果传递给 GitHub Actions 的环境变量
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"should_notify={should_notify}\n")
            f.write(f"price_info={info}\n")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    check()
