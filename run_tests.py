#!/usr/bin/env python
"""
Test runner script for Finance Tracker project.
This script sets up the Django environment and runs the tests.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    """Run the Django test suite."""
    # Add the project directory to the Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_tracker.test_settings')
    
    # Setup Django
    django.setup()
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run the tests
    failures = test_runner.run_tests([
        'finance_tracker.tests',
        'finance_tracker.test_mixins',
        'accounts.tests',
        'categories.tests',
        'expenses.tests',
        'income.tests',
        'subscriptions.tests',
        'work.tests',
        'dashboard.tests',
    ])
    
    return failures

if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures))
