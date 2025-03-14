from API_Mistral_Call import Mistral_Call
from API_Queue import API_Queue
import time



mistral = Mistral_Call()
queue = API_Queue(rate_limit=1.0)
    

future1 = queue.add_to_queue(mistral.chat, "Hello 1")
future2 = queue.add_to_queue(mistral.chat, "Hello 2")
future3 = queue.add_to_queue(mistral.chat, "Hello 3")

print("Attente des résultats...")
    
result1 = future1.get_result()
print(f"Résultat 1 reçu à {time.strftime('%H:%M:%S')}: {result1}\n")

result2 = future2.get_result()
print(f"Résultat 2 reçu à {time.strftime('%H:%M:%S')}: {result2}\n")

result3 = future3.get_result()
print(f"Résultat 3 reçu à {time.strftime('%H:%M:%S')}: {result3}\n")

print("Tous les résultats ont été reçus!")