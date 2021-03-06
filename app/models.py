from app import db, login
from random import randint
from flask_login import UserMixin

# Steps to initialize the SQL database:
# flask db init
# flask db migrate -m "users and proposal tables"
# flask db upgrade



def generate_nonce(length=8):
    return ''.join([str(randint(0, 9)) for i in range(length)])

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

#Class User is deprecated, use Users instead
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
    proposal_author = db.Column(db.String(80))
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

#Association table
#flask db migrate -m "votes"
#flask db upgrade
votes = db.Table('votes', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('proposal_id', db.Integer, db.ForeignKey('proposal.id'))
)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_address = db.Column(db.String(80), nullable=False, unique=True)
    nonce = db.Column(db.Integer(), nullable=False, default=generate_nonce)
    votes = db.relationship("Proposal", secondary=votes, lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.public_address)

    def has_voted(self, proposal):
        return self.votes.filter(
            votes.c.proposal_id == proposal.id).count() > 0
