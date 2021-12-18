from app import db
from random import randint

# flask db init
# flask db migrate -m "user and proposal tables"
# flask db upgrade
# db.create_all()

def generate_nonce(length=8):
    return ''.join([str(randint(0, 9)) for i in range(length)])

class User(db.Model):
    public_address = db.Column(db.String(80), primary_key=True, nullable=False, unique=True)
    nonce = db.Column(db.Integer(), nullable=False, default=generate_nonce)

    def __repr__(self):
        return '<User {}>'.format(self.public_address)

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal = db.Column(db.String(2048), nullable=False)
    unixtime_start = db.Column(db.Integer)
    start_time = db.Column(db.String(64))
    unixtime_end = db.Column(db.Integer)
    end_time = db.Column(db.String(64))
    voting_period = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String, db.ForeignKey('user.public_address'))
    option_a_votes = db.Column(db.Float, default=0, nullable=False)
    option_a_tag = db.Column(db.String(128), default="ACCEPT", nullable=False)
    option_b_votes = db.Column(db.Float)
    option_b_tag = db.Column(db.String(128))
    option_c_votes = db.Column(db.Float)
    option_c_tag = db.Column(db.String(128))
    reject_votes = db.Column(db.Float, default=0, nullable=False)
    reject_option = db.Column(db.String(1))
    open = db.Column(db.Boolean, default=True, nullable=False)
    admin_approved = db.Column(db.Boolean, default=False, nullable=False)
    result = db.Column(db.String(128))

    def __repr__(self):
        return '<Proposal {}>'.format(self.id)
