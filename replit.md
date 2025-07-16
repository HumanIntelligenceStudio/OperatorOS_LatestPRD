# OperatorOS - Universal Goal Achievement Platform

## Overview

OperatorOS is a comprehensive AI-powered goal achievement platform that combines multi-AI provider integration with business automation, financial analysis, and service template generation. The system leverages OpenAI, Anthropic, and Grok AI models to provide intelligent routing and specialized assistance across various domains.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM
- **Database**: PostgreSQL with Flask-SQLAlchemy integration
- **Authentication**: Replit Auth with OAuth2 flow and Flask-Login session management
- **AI Integration**: Multi-provider AI system with intelligent routing based on task types

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 (Replit Dark Theme)
- **UI Framework**: Bootstrap with Font Awesome icons and Chart.js for visualizations
- **JavaScript**: Vanilla JavaScript for interactive features and real-time updates
- **Styling**: Custom CSS with dark theme support and responsive design

### Data Layer
- **ORM**: SQLAlchemy with declarative base model
- **Models**: User, Goal, Task, AIConversation, BusinessProcess, FinancialData, ServiceTemplate, Payment, SystemMetrics
- **Migrations**: Automatic table creation on app initialization

## Key Components

### AI Provider Management (`ai_providers.py`)
- Multi-AI provider integration (OpenAI, Anthropic, Grok)
- Intelligent routing based on task type (analysis→Anthropic, creative→OpenAI, reasoning→Grok)
- Centralized API key management through environment variables
- Fallback mechanisms for provider availability

### Goal Achievement System (`goal_achievement.py`)
- AI-powered goal breakdown into actionable tasks
- Progress tracking and completion percentage calculation
- Task prioritization and timeline management
- Integration with AI providers for intelligent suggestions

### Business Automation (`business_automation.py`)
- Automated business process templates (client acquisition, service fulfillment, revenue optimization)
- AI-generated automation workflows
- Process monitoring and metrics collection
- Revenue tracking and optimization suggestions

### Financial Analysis (`financial_analysis.py`)
- Bank statement CSV processing and analysis
- CFO-level insights generation through AI
- Income/expense categorization and tracking
- Financial trend analysis and recommendations

### Service Templates (`service_templates.py`)
- AI-generated professional service templates
- Category-based template organization
- Usage tracking and analytics
- Automated proposal generation

### Payment Processing (`payment_processing.py`)
- Stripe integration for subscription and service payments
- Multiple pricing tiers (Free, Basic, Premium, Enterprise)
- Automatic domain detection for Replit deployment
- Payment status tracking and management

### Admin Dashboard (`admin_dashboard.py`)
- System-wide analytics and user management
- AI usage statistics and provider performance
- Business metrics and revenue tracking
- System health monitoring

## Data Flow

1. **User Authentication**: Replit Auth OAuth2 flow → User session management
2. **Goal Creation**: User input → AI task breakdown → Database storage
3. **AI Interactions**: User queries → Provider routing → AI processing → Response storage
4. **Financial Processing**: CSV upload → Data parsing → AI analysis → Insights generation
5. **Business Automation**: Process selection → AI workflow generation → Execution tracking
6. **Payment Flow**: Service selection → Stripe checkout → Payment confirmation → Access granted

## External Dependencies

### AI Providers
- **OpenAI**: GPT-4o model for creative tasks and general assistance
- **Anthropic**: Claude-sonnet-4-20250514 for analysis and reasoning
- **Grok (xAI)**: Specialized reasoning and problem-solving tasks

### Payment Processing
- **Stripe**: Complete payment processing with checkout sessions
- **Webhooks**: Real-time payment status updates

### Authentication
- **Replit Auth**: OAuth2 authentication with user profile management
- **Flask-Login**: Session management and user state persistence

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for enhanced UX
- **Chart.js**: Data visualization for analytics dashboards

## Deployment Strategy

### Environment Configuration
- **Database**: PostgreSQL connection via `DATABASE_URL` environment variable
- **API Keys**: Secure storage of AI provider and payment processor credentials
- **Session Management**: Secure session key configuration
- **Domain Handling**: Automatic Replit domain detection for callbacks

### Database Management
- **Auto-migration**: Automatic table creation on application startup
- **Connection Pooling**: Optimized database connections with pre-ping health checks
- **Transaction Management**: Proper rollback handling for data integrity

### Security Measures
- **OAuth2 Flow**: Secure authentication with token-based sessions
- **API Key Protection**: Environment-based credential management
- **Input Validation**: Form validation and SQL injection prevention
- **HTTPS Enforcement**: Secure communication protocols

### Scalability Considerations
- **Modular Architecture**: Separate systems for different functionalities
- **Database Optimization**: Efficient queries and proper indexing
- **AI Provider Load Balancing**: Intelligent routing to distribute AI workload
- **Caching Strategy**: Session-based caching for improved performance

The system is designed for easy deployment on Replit with automatic environment detection and configuration, supporting both development and production environments through environment variable management.