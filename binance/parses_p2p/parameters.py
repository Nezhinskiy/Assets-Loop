from datetime import datetime
from time import sleep

start_time = datetime.now()
sleep(3)
duration = datetime.now() - start_time
print(f'{type(duration)}, {duration}')

