from app.models import Data
from app import db
import random

for _ in range(10000):
    data = Data(random.randint(0,100000))
    db.session.add(data)
    db.session.commit()
