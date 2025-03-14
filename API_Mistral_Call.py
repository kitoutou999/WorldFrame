import uuid
from dotenv import load_dotenv
import os
import requests
import time


from API_Logger import ApiLogger

class Mistral_Call:
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('MISTRAL_APIKEY')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.modelList = ["ministral-3b-latest", "codestral-latest"]
        self.model = self.modelList[0]
        self.max_tokens = 100
        self.temperature = 0.7
        self.logger = ApiLogger()

        
    def send_request(self, prompt):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()  
            response_data = response.json()
            

            return response_data
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête: {e}")
            if e.response:
                print(f"Réponse d'erreur: {e.response.text}")
            self.last_usage = None
            return None
    
    def get_response(self, prompt):
        response_data = self.send_request(prompt)
        
        if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
            self.last_response = response_data
            return response_data['choices'][0]['message']['content']
        else:
            return "Erreur: Impossible d'obtenir une réponse valide du modèle."
        
        
        
        
    
    def chat(self, prompt, type="Default", name=uuid.uuid4().hex):
        """
        Envoie une requête à l'API Mistral et retourne la réponse.
        
        Args:
            prompt (str): La question à poser au modèle.
            type (str): Le type de l'entité qui fait la requetes. (e.g System,Default)
            name (str): Le nom de l'entité qui fait la requetes. (e.g Charlie, Tom)
        """
        start = time.time()
        response = self.get_response(prompt) 
        end = time.time()
        print(f"Prompt: {prompt}")
        print(f"Réponse: {response}")
        
        self.logger.save(prompt,self.last_response, type, name,end-start,os.getenv('COMPUTERNAME')) #Crée des logs des call API
        
    
        return response
    
        

if __name__ == "__main__": 
    mistral = Mistral_Call()

    response = mistral.chat("Say only 'hello world'", "System")
    

