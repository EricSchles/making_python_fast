from app import db
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Integer)
    
    def __init__(self,datum):
        self.datum = datum
        
