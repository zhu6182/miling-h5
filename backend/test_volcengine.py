"""
火山方舟 API 测试脚本
使用方法：在下面填入你的 API Key 和模型名称，然后运行 python test_volcengine.py
"""

import sys

API_KEY = ""  # 你的火山方舟 API Key
MODEL = "doubao-pro-32k"  # 模型名称，根据你的接入点调整
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 默认地址，如果是自定义接入点可以改

TEST_MESSAGE = "你好，请用一句话介绍你自己"


def test_volcengine():
    if not API_KEY:
        print("请先在脚本里填入你的 API_KEY")
        return False

    try:
        from openai import OpenAI
    except ImportError:
        print("缺少 openai 包，正在安装...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
        from openai import OpenAI

    print(f"正在测试火山方舟 API...")
    print(f"模型: {MODEL}")
    print(f"Base URL: {BASE_URL}")
    print()

    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个助手"},
                {"role": "user", "content": TEST_MESSAGE}
            ],
            temperature=0.7,
        )
        result = response.choices[0].message.content
        print("✅ 调用成功！")
        print()
        print("返回内容：")
        print(result)
        return True
    except Exception as e:
        print(f"❌ 调用失败: {e}")
        return False


if __name__ == "__main__":
    test_volcengine()
