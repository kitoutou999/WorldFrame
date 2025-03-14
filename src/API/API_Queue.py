import queue
import threading
from collections import deque
import time
import uuid

class API_Queue():
        
        def __init__(self, rate_limit=1.0):
            self.queue = deque()
            self.rate_limit = rate_limit
            self.last_request_time = 0
            self.lock = threading.Lock()
            self.processing = False
            self.processing_thread = None
            
            self.resulats = {}
            
        def add_to_queue(self, function, *args):
            request_id = str(uuid.uuid4())
            result_queue = queue.Queue()
            with self.lock:
                self.resulats[request_id] = result_queue
                self.queue.append((function, args[0], request_id))
                if not self.processing:
                    self.processing = True
                    self.processing_thread = threading.Thread(target=self.process_queue)
                    self.processing_thread.daemon = True
                    self.processing_thread.start()
            return Future(result_queue)
            
        def get_next_item(self):
            if len(self.queue) > 0:
                return self.queue.popleft()
            else:
                return None
            
        def get_queue_size(self):
            with self.lock:
                return len(self.queue)
            
        def clear_queue(self):
            with self.lock:
                self.queue.clear()
                for result_queue in self.resulats.values():
                    result_queue.put((None, Exception("Requête annulée")))
                self.resulats.clear()
                
        def process_queue(self):
            while True:
                item_to_process = None 
                
                with self.lock:
                    if not self.queue:
                        self.processing = False
                        break
                    
                    current_time = time.time()
                    time_since_last_request = current_time - self.last_request_time
                    time_to_wait = max(0, (1.0 / self.rate_limit) - time_since_last_request)
                    
                    if time_to_wait <= 0:
                        item_to_process = self.get_next_item()
                        self.last_request_time = current_time
                        
                if item_to_process:
                    function, args, request_id = item_to_process
                    try:
                        result = function(args)  # Exécuter la fonction
                        with self.lock:
                            self.resulats[request_id].put((result, None))
                            del self.resulats[request_id]
                    except Exception as e:
                        with self.lock:
                            if request_id in self.resulats:
                                self.resulats[request_id].put((None, e))
                                del self.resulats[request_id]
                
                # Ajouter un délai APRÈS le traitement
                time.sleep(1.0 / self.rate_limit)
                    
        def _execute_api_call(self, function, *args):
            try:
                result = function(*args)
                print(f"Résultat: {result}")
                return result
            except Exception as e:
                print(f"Erreur lors de l'appel API: {e}")
                return None

class Future:
    def __init__(self, result_queue):
        self.result_queue = result_queue
        self.done = False
        self.result = None
        self.exception = None
    
    def get_result(self, timeout=None):
    
        if not self.done:
            try:
                self.result, self.exception = self.result_queue.get(timeout=timeout)
                self.done = True
            except queue.Empty:
                raise TimeoutError("L'opération a expiré")
        
        if self.exception:
            raise self.exception
        return self.result
    
    def is_done(self):
        """Vérifie si le résultat est disponible sans bloquer."""
        if not self.done and not self.result_queue.empty():
            self.result, self.exception = self.result_queue.get_nowait()
            self.done = True
        return self.done

