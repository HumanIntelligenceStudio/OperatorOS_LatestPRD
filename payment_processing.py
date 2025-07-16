import os
import logging
import stripe
from datetime import datetime
from typing import Dict, Any, Optional
from app import db
from models import Payment, User

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentProcessingSystem:
    def __init__(self):
        self.stripe = stripe
        self.your_domain = self._get_domain()
    
    def _get_domain(self) -> str:
        """Get the current domain for redirects"""
        replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if replit_domain:
            return f"https://{replit_domain}"
        
        domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
        if domains and domains[0]:
            return f"https://{domains[0]}"
        
        return "https://localhost:5000"
    
    def create_checkout_session(self, user_id: str, service_type: str, 
                              amount: float, currency: str = "USD") -> Dict[str, Any]:
        """Create Stripe checkout session"""
        try:
            if not stripe.api_key:
                return {"error": "Stripe not configured"}
            
            # Create payment record
            payment = Payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                service_type=service_type,
                status="pending"
            )
            db.session.add(payment)
            db.session.commit()
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': service_type,
                            'description': f'OperatorOS - {service_type}',
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{self.your_domain}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{self.your_domain}/payment/cancel',
                metadata={
                    'payment_id': str(payment.id),
                    'user_id': user_id
                }
            )
            
            # Update payment with Stripe session ID
            payment.stripe_payment_id = checkout_session.id
            db.session.commit()
            
            return {
                "success": True,
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "payment_id": payment.id
            }
            
        except Exception as e:
            logging.error(f"Checkout session creation failed: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}
    
    def handle_payment_success(self, session_id: str) -> Dict[str, Any]:
        """Handle successful payment"""
        try:
            if not stripe.api_key:
                return {"error": "Stripe not configured"}
            
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Find the payment record
                payment = Payment.query.filter_by(stripe_payment_id=session_id).first()
                
                if payment:
                    payment.status = 'completed'
                    payment.updated_at = datetime.now()
                    db.session.commit()
                    
                    # Upgrade user subscription if applicable
                    self._upgrade_user_subscription(payment.user_id, payment.service_type)
                    
                    return {
                        "success": True,
                        "payment": payment,
                        "message": "Payment processed successfully"
                    }
                else:
                    return {"error": "Payment record not found"}
            else:
                return {"error": "Payment not completed"}
            
        except Exception as e:
            logging.error(f"Payment success handling failed: {str(e)}")
            return {"error": str(e)}
    
    def _upgrade_user_subscription(self, user_id: str, service_type: str):
        """Upgrade user subscription based on payment"""
        try:
            user = User.query.get(user_id)
            if not user:
                return
            
            # Map service types to subscription tiers
            subscription_mapping = {
                "Premium Access": "premium",
                "Professional Package": "professional",
                "Enterprise Solution": "enterprise"
            }
            
            new_tier = subscription_mapping.get(service_type, "premium")
            user.subscription_tier = new_tier
            db.session.commit()
            
            logging.info(f"User {user_id} upgraded to {new_tier}")
            
        except Exception as e:
            logging.error(f"Subscription upgrade failed: {str(e)}")
    
    def get_payment_history(self, user_id: str) -> Dict[str, Any]:
        """Get payment history for a user"""
        try:
            payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
            
            total_paid = sum(p.amount for p in payments if p.status == 'completed')
            
            return {
                "payments": payments,
                "total_paid": round(total_paid, 2),
                "payment_count": len(payments)
            }
            
        except Exception as e:
            logging.error(f"Payment history retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    def create_subscription(self, user_id: str, price_id: str) -> Dict[str, Any]:
        """Create a Stripe subscription"""
        try:
            if not stripe.api_key:
                return {"error": "Stripe not configured"}
            
            user = User.query.get(user_id)
            if not user or not user.email:
                return {"error": "User not found or no email"}
            
            # Create or retrieve Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={'user_id': user_id}
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "customer_id": customer.id
            }
            
        except Exception as e:
            logging.error(f"Subscription creation failed: {str(e)}")
            return {"error": str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        try:
            if not stripe.api_key:
                return {"error": "Stripe not configured"}
            
            subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                "success": True,
                "subscription": subscription,
                "message": "Subscription cancelled successfully"
            }
            
        except Exception as e:
            logging.error(f"Subscription cancellation failed: {str(e)}")
            return {"error": str(e)}
    
    def get_pricing_tiers(self) -> Dict[str, Any]:
        """Get available pricing tiers"""
        return {
            "free": {
                "name": "Free",
                "price": 0,
                "features": [
                    "Basic AI assistance",
                    "5 goals per month",
                    "Standard templates",
                    "Basic analytics"
                ]
            },
            "premium": {
                "name": "Premium",
                "price": 29.99,
                "features": [
                    "Multi-AI provider access",
                    "Unlimited goals",
                    "Advanced templates",
                    "Financial analysis",
                    "Priority support"
                ]
            },
            "professional": {
                "name": "Professional",
                "price": 79.99,
                "features": [
                    "All Premium features",
                    "Business automation",
                    "Custom templates",
                    "Advanced analytics",
                    "API access",
                    "White-label options"
                ]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 199.99,
                "features": [
                    "All Professional features",
                    "Custom integrations",
                    "Dedicated support",
                    "Advanced security",
                    "Custom deployment",
                    "Training sessions"
                ]
            }
        }

# Global payment processing system
payment_system = PaymentProcessingSystem()
