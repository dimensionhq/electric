######################################################################
#                          DOWNLOAD LIMITER                          #
######################################################################

import threading
import time
from progress.bar import Bar

class TokenBucket:
    def __init__(self, tokens, fill_rate) -> None:
        self.capacity = float(tokens)
        self._tokens = float(tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()
        self.lock = threading.RLock()

    def consume(self, tokens):
        self.lock.acquire()

        tokens = max(tokens, self.tokens)

        expected_time = (tokens - self.tokens) / self.fill_rate

        if expected_time <= 0:
            self._tokens -= tokens
        
        self.lock.release()

        return max(0, expected_time)
    
    @property
    def tokens(self):
        self.lock.acquire()

        if self._tokens < self.capacity:
            now = time.time()

            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)

            self.timestamp = now

        value = self._tokens

        self.lock.release()

        return value
    

class Limiter:
    """
    Download speed limiter
    """    
    def __init__(self, bucket, filename) -> None:
        self.bucket = bucket
        self.last_update = 0
        self.last_downloaded_kb = 0

        self.filename = filename
        self.avg_rate = None
        self.bar = Bar('')

    def __call__(self, block_count, block_size, total_size):
        total_kb = total_size / 1024
        self.bar.max = total_kb / 8.00008

        downloaded_kb = (block_count * block_size) / 1024.
        just_downloaded = downloaded_kb - self.last_downloaded_kb
        
        self.last_downloaded_kb = downloaded_kb

        self.bar.next()

        predicted_size = block_size/1024.

        wait_time = self.bucket.consume(predicted_size)

        while wait_time > 0:
            time.sleep(wait_time)
            wait_time = self.bucket.consume(predicted_size)

        now = time.time()
        delta = now - self.last_update
        
        if self.last_update != 0:
            if delta > 0:
                rate = just_downloaded / delta
                
                if self.avg_rate is not None:
                    rate = 0.9 * self.avg_rate + 0.1 * rate
                
                self.avg_rate = rate
            
            else:
                rate = self.avg_rate or 0.

        self.last_update = now
