# Finance Tracker

Finance Tracker is a full-featured personal finance management application built with Django. It provides an intuitive interface for users to monitor their financial health by tracking various aspects of their financial life including daily expenses, income sources, subscription costs, and work time logging. The app features a clean dashboard with visual summaries and comprehensive reporting capabilities.

## Features

- **User Authentication**: Secure login/registration system with user-specific data isolation
- **Expense Management**: Track daily expenses with categories, dates, and amounts
- **Income Tracking**: Record and monitor various income sources
- **Subscription Monitoring**: Keep track of recurring subscription costs and renewal dates
- **Work Time Logging**: Log work hours and track productivity
- **Category Management**: Organize transactions with customizable categories
- **Dashboard Overview**: Visual summary of financial data with charts and statistics
- **Responsive Design**: Mobile-friendly interface for on-the-go financial tracking
- **Data Export**: Export financial data for external analysis
- **Search & Filtering**: Advanced search and filtering capabilities for transactions

## Tech Stack

- **Backend**: Django 4.2.23 (Python web framework)
- **Database**: PostgreSQL with psycopg2 adapter
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django's built-in authentication system
- **Styling**: Custom CSS with responsive design
- **Environment Management**: python-dotenv for configuration
- **Testing**: Factory Boy and Faker for test data generation
- **Date Handling**: python-dateutil for advanced date operations

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielsarney/finance-tracker.git
   cd finance-tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the `.env.example` file and fill in your database details:
   ```bash
   cp .env.example .env
   ```

5. **Set up PostgreSQL database**
   - Create a new PostgreSQL database
   - Update the `.env` file with your database credentials

6. **Run database migrations**
   ```bash
   python3 manage.py migrate
   ```

7. **Run the development server**
   ```bash
   python3 manage.py runserver
   ```

8. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

9. **Run Tests**
   ```
   python3 manage.py test
   ```

### Default URLs
- **Main Dashboard**: `/`
- **Login**: `/accounts/login/`
- **Register**: `/accounts/register/`
- **Expenses**: `/expenses/`
- **Income**: `/income/`
- **Subscriptions**: `/subscriptions/`
- **Work Logs**: `/work/`
- **Categories**: `/categories/`