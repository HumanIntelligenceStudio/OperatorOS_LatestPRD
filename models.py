from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

# User model for Replit Auth
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String, default='free')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# OAuth model for Replit Auth
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)
    __table_args__ = (UniqueConstraint('user_id', 'browser_session_key', 'provider', name='uq_user_browser_session_key_provider'),)

# Goal tracking model
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')
    priority = db.Column(db.String(20), default='medium')
    target_date = db.Column(db.DateTime)
    completion_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user = db.relationship(User, backref='goals')

# Task breakdown model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey(Goal.id), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.String(20), default='medium')
    estimated_hours = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    goal = db.relationship(Goal, backref='tasks')

# AI conversations model
class AIConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # openai, anthropic, grok
    model = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer)
    cost = db.Column(db.Float)
    clarity_rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship(User, backref='conversations')

# Business automation model
class BusinessProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    automation_type = db.Column(db.String(100), nullable=False)  # client_acquisition, fulfillment, etc.
    status = db.Column(db.String(50), default='active')
    success_rate = db.Column(db.Float, default=0.0)
    revenue_generated = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Financial analysis model
class FinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # bank_statement, expense, revenue
    category = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500))
    analysis_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship(User, backref='financial_data')

# Service templates model
class ServiceTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float)
    automation_level = db.Column(db.String(50), default='manual')
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Payment tracking model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    service_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')
    stripe_payment_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship(User, backref='payments')

# System metrics model
class SystemMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    additional_data = db.Column(db.Text)
