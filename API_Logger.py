import os
import json
from datetime import datetime
import logging


class ApiLogger:

    
    def __init__(self):
       
        self.base_dir = "log_API_Call"
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def format_response(self):
        try:
            formatted = {
                "id": self.response.get("id", "unknown"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": self.response.get("model", "unknown"),
                "question": self.question,
                "content": None,
                "duration": self.durations,
                "system": self.system,
                "tokens": {
                    "prompt": self.response.get("usage", {}).get("prompt_tokens", 0),
                    "completion": self.response.get("usage", {}).get("completion_tokens", 0),
                    "total": self.response.get("usage", {}).get("total_tokens", 0),
                    # 1M tokens cost 0.04 euros
                    "average_price": self.response.get("usage", {}).get("total_tokens", 0) * 0.04 / 1000000
                }
            }
            
            choices = self.response.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                formatted["content"] = message.get("content")
                
                if message.get("tool_calls"):
                    formatted["tool_calls"] = message.get("tool_calls")
            
            return formatted
        except Exception as e:
            self.logger.error(f"Error formatting response: {e}")
            return self.response 
    
    def save(self,question ,response, api_type, name,duration,system):
        """
        Save the formatted response to a JSONL file in the appropriate directory.
        log_API_Call/[type]/[name]/[date].jsonl
        """
        self.response = response
        self.question = question
        self.api_type = api_type
        self.name = name
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.durations = duration
        self.system = system
        
        try:
            log_dir = os.path.join(self.base_dir, self.api_type, self.name)
            os.makedirs(log_dir, exist_ok=True)
            
            file_path = os.path.join(log_dir, f"{self.today}.jsonl")
            
            formatted_response = self.format_response()
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(formatted_response, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Logged API response to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving log: {e}")
            return False


if __name__ == "__main__":
    sample_response = {
        'id': '65fe72fe5eb74220bfd4ad90580856e9',
        'object': 'chat.completion',
        'created': 1741923304,
        'model': 'ministral-3b-latest',
        'choices': [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'tool_calls': None,
                    'content': 'Hello world'
                },
                'finish_reason': 'stop'
            }
        ],
        'usage': {
            'prompt_tokens': 9,
            'total_tokens': 11,
            'completion_tokens': 2
        }
    }

    logger = ApiLogger()
    logger.save(sample_response, "chat", "test_user")