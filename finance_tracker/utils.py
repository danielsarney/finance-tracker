from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

def get_years_list(start_year=2020):
    """
    Generate a list of years for filtering.
    
    Args:
        start_year (int): The starting year for the list
        
    Returns:
        list: List of years from start_year to current year
    """
    current_year = timezone.now().year
    return list(range(start_year, current_year + 1))

def format_currency(amount, currency='GBP'):
    """
    Format a decimal amount as currency.
    
    Args:
        amount (Decimal): The amount to format
        currency (str): The currency code
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return f"£0.00"
    
    # Convert to Decimal if it's not already
    amount = Decimal(str(amount))
    
    if currency == 'GBP':
        return f"£{amount:.2f}"
    elif currency == 'USD':
        return f"${amount:.2f}"
    elif currency == 'EUR':
        return f"€{amount:.2f}"
    else:
        return f"{amount:.2f}"

def format_date(date, format_type='short'):
    """
    Format a date object.
    
    Args:
        date: Date object or string
        format_type (str): 'short', 'long', or 'iso'
        
    Returns:
        str: Formatted date string
    """
    if not date:
        return ""
    
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return date
    
    if format_type == 'short':
        return date.strftime('%d/%m/%Y')
    elif format_type == 'long':
        return date.strftime('%d %B %Y')
    elif format_type == 'iso':
        return date.isoformat()
    else:
        return date.strftime('%d/%m/%Y')

def calculate_monthly_cost(amount, billing_cycle):
    """
    Calculate monthly cost for a subscription.
    
    Args:
        amount (Decimal): The subscription amount
        billing_cycle (str): The billing cycle (DAILY, WEEKLY, MONTHLY, etc.)
        
    Returns:
        Decimal: Monthly cost
    """
    amount = Decimal(str(amount))
    
    if billing_cycle == 'DAILY':
        return amount * Decimal('30')
    elif billing_cycle == 'WEEKLY':
        return amount * Decimal('4.33')  # Average weeks per month
    elif billing_cycle == 'MONTHLY':
        return amount
    elif billing_cycle == 'QUARTERLY':
        return amount / Decimal('3')
    elif billing_cycle == 'YEARLY':
        return amount / Decimal('12')
    else:
        return amount

def get_upcoming_dates(start_date, billing_cycle, count=12):
    """
    Get upcoming billing dates for a subscription.
    
    Args:
        start_date: The start date of the subscription
        billing_cycle (str): The billing cycle
        count (int): Number of upcoming dates to generate
        
    Returns:
        list: List of upcoming billing dates
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    dates = []
    current_date = start_date
    
    for _ in range(count):
        dates.append(current_date)
        
        if billing_cycle == 'DAILY':
            current_date += timedelta(days=1)
        elif billing_cycle == 'WEEKLY':
            current_date += timedelta(weeks=1)
        elif billing_cycle == 'MONTHLY':
            # Simple month addition (not perfect for all months)
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        elif billing_cycle == 'QUARTERLY':
            if current_date.month >= 10:
                current_date = current_date.replace(year=current_date.year + 1, month=current_date.month - 9)
            else:
                current_date = current_date.replace(month=current_date.month + 3)
        elif billing_cycle == 'YEARLY':
            current_date = current_date.replace(year=current_date.year + 1)
    
    return dates

def get_status_color(status):
    """
    Get Bootstrap color class for a status.
    
    Args:
        status (str): The status string
        
    Returns:
        str: Bootstrap color class
    """
    status_colors = {
        'PENDING': 'warning',
        'INVOICED': 'info',
        'PAID': 'success',
        'ACTIVE': 'success',
        'INACTIVE': 'secondary',
        'CANCELLED': 'danger',
    }
    
    return status_colors.get(status.upper(), 'secondary')

def paginate_queryset(queryset, page_number, per_page=20):
    """
    Paginate a queryset.
    
    Args:
        queryset: The queryset to paginate
        page_number: The current page number
        per_page (int): Number of items per page
        
    Returns:
        tuple: (paginator, page_obj)
    """
    from django.core.paginator import Paginator
    
    # Ensure queryset is ordered for consistent pagination
    if not queryset.ordered:
        queryset = queryset.order_by('-date', '-created_at')
    
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    
    return paginator, page_obj
