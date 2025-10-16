from django.db import connection
from rest_framework.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP


def execute_raw_query(query, params=None):
    """
    Executes a raw SQL query and returns the results.

    Args:
        query (str): SQL query to execute.
        params (list): Parameters to pass to the query.

    Returns:
        list: List of tuples containing the query results.
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

def execute_raw_query_with_columns(query, params=None):
    """
    Executes a raw SQL query and returns the results as a list of dictionaries.

    The returned dictionaries will have column names as keys and row values as values.

    Args:
        query (str): SQL query to execute.
        params (list): Parameters to pass to the query.

    Returns:
        list: List of dictionaries containing the query results.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def execute_update_query(query, params=None):
    """Executes an UPDATE/INSERT/DELETE and returns affected rows count."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount


def calculate_net_value(vat, sales_quantity , sales_net_val, delivery_quantity, return_quantity):
        """
        Calculate net value with proper rounding 
        """
        try:
            if vat == None:
                raise ValidationError(f"VAT must be provided for net value calculation")
            if  not sales_quantity or not sales_net_val:
                raise ValidationError(f"Sales quantity and sales net value must be provided for net value calculation")

            if sales_quantity == 0:
                raise ValidationError(f"Sales quantity must be greater than 0")
            
            # calculate per unit price
            net_val = Decimal(sales_net_val) + Decimal(vat)
            per_unit = (Decimal(net_val)/Decimal(sales_quantity)).quantize(Decimal('0.0001'))
            
            # calculate delivery net value 
            delivery_net_val = (per_unit * Decimal(delivery_quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # calculate return net value
            return_net_val = (per_unit * Decimal(return_quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            # Adjust for rounding differences
            total_now = delivery_net_val + return_net_val
            difference = net_val - total_now
            if difference != 0:
                if return_quantity > 0:
                    return_net_val += difference
                else:
                    delivery_net_val += difference
            
            return (delivery_net_val, return_net_val)
        except Exception as e:
            raise ValidationError(f"Error calculating net value: {str(e)}")
