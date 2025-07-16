from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from app import app, db
from replit_auth import make_replit_blueprint, require_login
from models import User, Goal, Task, AIConversation, BusinessProcess, FinancialData, ServiceTemplate, Payment
from goal_achievement import goal_system
from business_automation import business_automation
from financial_analysis import financial_system
from service_templates import service_templates
from admin_dashboard import admin_dashboard
from payment_processing import payment_system
from ai_providers import ai_manager
import json
import logging

# Register Replit Auth blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """User dashboard"""
    try:
        dashboard_data = goal_system.get_user_dashboard_data(current_user.id)
        return render_template('dashboard.html', **dashboard_data)
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return render_template('dashboard.html', error=str(e))

@app.route('/goals')
@require_login
def goals():
    """Goals page"""
    try:
        user_goals = Goal.query.filter_by(user_id=current_user.id).all()
        return render_template('goal_achievement.html', goals=user_goals)
    except Exception as e:
        logging.error(f"Goals page error: {str(e)}")
        flash('Error loading goals', 'danger')
        return render_template('goal_achievement.html', goals=[])

@app.route('/create_goal', methods=['POST'])
@require_login
def create_goal():
    """Create a new goal"""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        
        if not title or not description:
            flash('Title and description are required', 'warning')
            return redirect(url_for('goals'))
        
        goal = goal_system.create_goal(current_user.id, title, description, priority=priority)
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goals'))
        
    except Exception as e:
        logging.error(f"Goal creation error: {str(e)}")
        flash('Error creating goal', 'danger')
        return redirect(url_for('goals'))

@app.route('/complete_task/<int:task_id>')
@require_login
def complete_task(task_id):
    """Complete a task"""
    try:
        result = goal_system.complete_task(task_id, current_user.id)
        if result.get('success'):
            flash(result['message'], 'success')
        else:
            flash(result.get('error', 'Error completing task'), 'danger')
    except Exception as e:
        logging.error(f"Task completion error: {str(e)}")
        flash('Error completing task', 'danger')
    
    return redirect(url_for('goals'))

@app.route('/goal_insights/<int:goal_id>')
@require_login
def goal_insights(goal_id):
    """Get AI insights for a goal"""
    try:
        insights = goal_system.get_goal_insights(goal_id)
        return jsonify(insights)
    except Exception as e:
        logging.error(f"Goal insights error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/ai_chat', methods=['POST'])
@require_login
def ai_chat():
    """AI chat interface"""
    try:
        prompt = request.form.get('prompt')
        provider = request.form.get('provider', 'auto')
        task_type = request.form.get('task_type', 'general')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"})
        
        # Generate AI response
        if provider == 'auto':
            response = ai_manager.generate_response(prompt, task_type=task_type)
        else:
            response = ai_manager.generate_response(prompt, provider=provider, task_type=task_type)
        
        if response.get('success'):
            # Store conversation
            conversation = AIConversation(
                user_id=current_user.id,
                provider=response['provider'],
                model=response['model'],
                prompt=prompt,
                response=response['content'],
                tokens_used=response.get('tokens_used', 0),
                cost=response.get('cost', 0)
            )
            db.session.add(conversation)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "response": response['content'],
                "provider": response['provider'],
                "model": response['model'],
                "conversation_id": conversation.id
            })
        else:
            return jsonify({"error": response.get('error', 'AI generation failed')})
            
    except Exception as e:
        logging.error(f"AI chat error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/rate_response', methods=['POST'])
@require_login
def rate_response():
    """Rate AI response clarity"""
    try:
        conversation_id = request.form.get('conversation_id')
        rating = int(request.form.get('rating'))
        
        conversation = AIConversation.query.get(conversation_id)
        if conversation and conversation.user_id == current_user.id:
            conversation.clarity_rating = rating
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Conversation not found"})
            
    except Exception as e:
        logging.error(f"Rating error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/financial_analysis')
@require_login
def financial_analysis():
    """Financial analysis page"""
    try:
        dashboard_data = financial_system.get_financial_dashboard(current_user.id)
        return render_template('financial_analysis.html', **dashboard_data)
    except Exception as e:
        logging.error(f"Financial analysis error: {str(e)}")
        flash('Error loading financial analysis', 'danger')
        return render_template('financial_analysis.html', error=str(e))

@app.route('/upload_bank_data', methods=['POST'])
@require_login
def upload_bank_data():
    """Upload bank statement data"""
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'warning')
            return redirect(url_for('financial_analysis'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'warning')
            return redirect(url_for('financial_analysis'))
        
        if file and file.filename.endswith('.csv'):
            csv_content = file.read().decode('utf-8')
            result = financial_system.process_bank_data(current_user.id, csv_content)
            
            if result.get('success'):
                flash(f'Successfully processed {result["processed_entries"]} entries', 'success')
            else:
                flash(result.get('error', 'Error processing bank data'), 'danger')
        else:
            flash('Please upload a CSV file', 'warning')
        
        return redirect(url_for('financial_analysis'))
        
    except Exception as e:
        logging.error(f"Bank data upload error: {str(e)}")
        flash('Error uploading bank data', 'danger')
        return redirect(url_for('financial_analysis'))

@app.route('/investment_recommendations')
@require_login
def investment_recommendations():
    """Get investment recommendations"""
    try:
        recommendations = financial_system.generate_investment_recommendations(current_user.id)
        return jsonify(recommendations)
    except Exception as e:
        logging.error(f"Investment recommendations error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/service_templates')
@require_login
def service_templates_page():
    """Service templates page"""
    try:
        catalog = service_templates.get_service_catalog()
        return render_template('service_templates.html', **catalog)
    except Exception as e:
        logging.error(f"Service templates error: {str(e)}")
        flash('Error loading service templates', 'danger')
        return render_template('service_templates.html', error=str(e))

@app.route('/generate_proposal', methods=['POST'])
@require_login
def generate_proposal():
    """Generate a service proposal"""
    try:
        template_id = request.form.get('template_id')
        client_name = request.form.get('client_name')
        project_details = request.form.get('project_details')
        budget_range = request.form.get('budget_range')
        
        if not all([template_id, client_name, project_details]):
            return jsonify({"error": "Missing required fields"})
        
        result = service_templates.generate_proposal(
            int(template_id), client_name, project_details, budget_range
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Proposal generation error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/business_automation')
@require_login
def business_automation_page():
    """Business automation page"""
    try:
        dashboard_data = business_automation.get_automation_dashboard()
        return render_template('dashboard.html', automation_data=dashboard_data)
    except Exception as e:
        logging.error(f"Business automation error: {str(e)}")
        flash('Error loading business automation', 'danger')
        return render_template('dashboard.html', error=str(e))

@app.route('/run_automation', methods=['POST'])
@require_login
def run_automation():
    """Run business automation process"""
    try:
        automation_type = request.form.get('automation_type')
        
        if automation_type == 'client_acquisition':
            # Create or get existing process
            process = business_automation.create_automation_process('client_acquisition')
            result = business_automation.run_client_acquisition_automation(process.id)
        elif automation_type == 'service_fulfillment':
            service_type = request.form.get('service_type', 'general')
            process = business_automation.create_automation_process('service_fulfillment')
            result = business_automation.run_service_fulfillment_automation(process.id, service_type)
        elif automation_type == 'revenue_optimization':
            process = business_automation.create_automation_process('revenue_optimization')
            result = business_automation.run_revenue_optimization(process.id)
        else:
            return jsonify({"error": "Invalid automation type"})
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Automation execution error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/admin')
@require_login
def admin_dashboard_page():
    """Admin dashboard (restricted)"""
    try:
        if not current_user.is_admin:
            return render_template('403.html'), 403
        
        dashboard_data = admin_dashboard.get_dashboard_overview()
        return render_template('admin.html', **dashboard_data)
        
    except Exception as e:
        logging.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading admin dashboard', 'danger')
        return render_template('admin.html', error=str(e))

@app.route('/admin/report')
@require_login
def admin_report():
    """Generate admin report"""
    try:
        if not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403
        
        report = admin_dashboard.generate_admin_report()
        return jsonify(report)
        
    except Exception as e:
        logging.error(f"Admin report error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/payment/create', methods=['POST'])
@require_login
def create_payment():
    """Create payment checkout session"""
    try:
        service_type = request.form.get('service_type')
        amount = float(request.form.get('amount'))
        
        if not service_type or amount <= 0:
            return jsonify({"error": "Invalid payment details"})
        
        result = payment_system.create_checkout_session(
            current_user.id, service_type, amount
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Payment creation error: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/payment/success')
@require_login
def payment_success():
    """Handle successful payment"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            flash('Invalid payment session', 'danger')
            return redirect(url_for('dashboard'))
        
        result = payment_system.handle_payment_success(session_id)
        
        if result.get('success'):
            flash('Payment successful! Thank you for your purchase.', 'success')
        else:
            flash(result.get('error', 'Payment verification failed'), 'danger')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Payment success handling error: {str(e)}")
        flash('Error processing payment', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/payment/cancel')
@require_login
def payment_cancel():
    """Handle cancelled payment"""
    flash('Payment cancelled', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/pricing')
def pricing():
    """Pricing page"""
    try:
        pricing_tiers = payment_system.get_pricing_tiers()
        return render_template('pricing.html', pricing_tiers=pricing_tiers)
    except Exception as e:
        logging.error(f"Pricing page error: {str(e)}")
        return render_template('pricing.html', error=str(e))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Initialize default data
_initialized = False

@app.before_request
def initialize_default_data():
    """Initialize default service templates"""
    global _initialized
    if not _initialized:
        try:
            service_templates.create_default_templates()
            _initialized = True
        except Exception as e:
            logging.error(f"Default data initialization error: {str(e)}")
