from datetime import datetime, timezone

a = datetime.now(timezone.utc).time().hour
print(a)