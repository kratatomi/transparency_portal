from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class ProposalForm(FlaskForm):
    proposal = TextAreaField('Proposal description', validators=[DataRequired()])
    voting_period = IntegerField('Voting period', validators=[DataRequired()], default=7)
    choice_a = StringField('Choice A', validators=[DataRequired()], default='ACCEPT')
    choice_b = StringField('Choice B')
    choice_c = StringField('Choice C')
    submit = SubmitField('Submit proposal')

class VoteForm(FlaskForm):
    choice = SelectField(u'Choice')