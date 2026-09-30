import requests
import json
from requests.exceptions import RequestException

# 配置日志（根据你的项目结构调整）
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnythingLLMClient:
    def __init__(self, config):
        """
        初始化 AnythingLLM 客户端
        :param config: 配置字典，包含以下键：
            - api_base: AnythingLLM 服务地址 (e.g. "http://localhost:3000")
            - workspace_id: 工作区 ID (e.g. "gdufs")
            - api_key: 认证令牌 (可选)
        """
        self.api_base = config["api_base"].rstrip('/')
        self.workspace_id = config["workspace_id"]
        self.api_key = config.get("api_key")
        
        # 构建完整 API 端点
        self.chat_endpoint = f"{self.api_base}/api/v1/workspace/{self.workspace_id}/chat"
        
        # 配置请求头
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def chat(self, message, mode="query", retries=3):
        """
        执行对话请求
        :param message: 用户消息内容
        :param mode: 对话模式 ("query" 或 "conversation")
        :param retries: 失败重试次数
        :return: 响应文本 (str)
        """
        payload = {
            "message": message,
            "mode": mode
        }

        for attempt in range(retries):
            try:
                response = requests.post(
                    self.chat_endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=30  # 增加超时防止 Ollama 长响应中断
                )
                response.raise_for_status()  # 自动处理 4xx/5xx 错误
                
                # 解析响应
                result = response.json()
                if "textResponse" in result:
                    return result["textResponse"]
                elif "response" in result:  # 兼容不同版本
                    return result["response"]
                else:
                    logger.error(f"未知响应格式: {json.dumps(result, indent=2)}")
                    return "【响应解析错误】"

            except RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt+1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    return f"【服务不可用: {str(e)}】"
                
            except json.JSONDecodeError:
                logger.error("响应非 JSON 格式，原始响应: %s", response.text)
                return "【响应格式错误】"

        return "【请求失败】"

# 使用示例
if __name__ == "__main__":
    # 配置参数（根据实际情况修改）
    config = {
        "api_base": "http://47.92.167.25:3316",  # AnythingLLM 服务地址
        "workspace_id": "gdufs",                # 工作区 ID
        "api_key": "DN92HW9-HCVMZSM-PDQGE71-DY57VV6"  # 可选认证
    }
    
    client = AnythingLLMClient(config)
    
    # 执行对话
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        response = client.chat(
            message=user_input,
            mode="query"  # 或 "conversation"（需工作区支持）
        )
        print(f"Bot: {response}")