# Python
import logging
# Django
from django.db import transaction
# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
# Core APP
from core.utils import execute_raw_query, execute_raw_query_with_columns
# Delivery APP
from delivery.utils import *
from delivery.sqls import get_delivery_list_query
from delivery.serializers import UpdateBulkDeliverySerializer

# Set up logger
logger = logging.getLogger("delivery")

# API View's Starts Here

class DeliveryListView(APIView):
    def get(self, request):
        """
        Fetches delivery list for a given DA code and type (Done or Not Done)
        """
        try:
            da_code = request.query_params.get('da_code', None)
            delivery_type = request.query_params.get('type', None)
            
            # Validate query parameters
            if da_code is None:
                return Response(
                    {"success": False, "message": "DA code is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            da_code = da_code.zfill(8)
            
            delivery_type_query = "AND di.delivery_status = 1" if delivery_type == "Done" else "AND (di.delivery_status != 1 OR di.delivery_status IS NULL)"
            delivery_list_query = get_delivery_list_query(delivery_type_query)
            
            # Execute query.
            data, error = execute_raw_query_with_columns(delivery_list_query, [da_code])
            if error:
                logger.error(f"Error while fetching delivery list for DA code: {da_code} and type: {delivery_type}: {error}")
                return Response(
                    {"success": False, "message": str(error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Process data
            response_data = []
            for item in data:
                response_data.append(
                    {
                        "partner": item['partner'],
                        "invoices": item['invoices'],
                        "sales_amount": item['sales_amount'],
                        "delivery_amount": item['delivery_amount'],
                        "partner_name": item['partner_name'],
                        "partner_address": item['partner_address'],
                        "partner_mobile": item['partner_mobile'],
                        "previous_due": item['previous_due']
                    }
                )
            logger.info(f"Successfully fetched delivery list for DA code: {da_code} and type: {delivery_type}")
            return Response(
                {"success": True, "message": "Successfully fetched delivery list", "data": response_data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.critical(f"Internal Server Error while fetching delivery list for DA code: {da_code} and type: {delivery_type}: {str(e)}")
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
