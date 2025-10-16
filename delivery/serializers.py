# Python
from decimal import Decimal, ROUND_HALF_UP
# Django
from django.db import transaction
from django.utils import timezone
# DRF
from rest_framework import serializers
# Local
from core.models import DeliveryInfo, DeliveryProductList
from core.utils import calculate_net_value

class UpdateProductListSerializer(serializers.Serializer):
    """
    Serializer for updating DeliveryProductList.
    """
    mtnr = serializers.CharField(max_length=40)
    batch = serializers.CharField(max_length=10, allow_null=True)
    delivery_quantity = serializers.DecimalField(
        max_digits=18, 
        decimal_places=0, 
        required=False, 
        allow_null=True,
        default=0
    )
    return_quantity = serializers.DecimalField(
        max_digits=18, 
        decimal_places=0, 
        required=False, 
        allow_null=True,
        default=0
    )

    def validate(self, data):
        """
        Validate that delivery_quantity + return_quantity <= sales_quantity
        This will be checked against the existing product data
        """
        delivery_qty = data.get('delivery_quantity')
        return_qty = data.get('return_quantity')
        
        if delivery_qty == None or delivery_qty < 0:
            raise serializers.ValidationError("Delivery quantity cannot be negative or null")
        if return_qty == None or return_qty < 0:
            raise serializers.ValidationError("Return quantity cannot be negative or null")
            
        return data


class UpdateDeliverySerializer(serializers.Serializer):
    """Serializer for updating DeliveryInfo and DeliveryProductList."""
    billing_doc_no = serializers.CharField(max_length=10)
    delivery_products = UpdateProductListSerializer(many=True)

    def validate_billing_doc_no(self, value):
        """Validate that the delivery exists"""
        try:
            DeliveryInfo.objects.get(billing_doc_no=value)
        except DeliveryInfo.DoesNotExist:
            raise serializers.ValidationError(f"Delivery with billing_doc_no '{value}' does not exist")
        return value

class UpdateBulkDeliverySerializer(serializers.Serializer):
    """
    Handles atomic bulk updates of deliveries and their products.
    Validates input, recalculates delivery/return amounts, and updates coordinates.
    """
    delivery_latitude = serializers.DecimalField(
        max_digits=27, 
        decimal_places=16, 
        required=False, 
        allow_null=True
    )
    delivery_longitude = serializers.DecimalField(
        max_digits=27, 
        decimal_places=16, 
        required=False, 
        allow_null=True
    )
    deliveries = UpdateDeliverySerializer(many=True)

    def validate_deliveries(self, value):
        """Validate that all deliveries have unique billing_doc_no"""
        billing_docs = [delivery['billing_doc_no'] for delivery in value]
        if len(billing_docs) != len(set(billing_docs)):
            raise serializers.ValidationError("Duplicate billing_doc_no found in deliveries")
        return value

    def validate_and_update_product(self, product_data, billing_doc_no):
        """
        Validate and update a single product
        Returns the updated product instance
        """
        try:
            # Get the existing product
            product = DeliveryProductList.objects.get(
                billing_doc_no=billing_doc_no,
                mtnr=product_data['mtnr'],
                batch=product_data.get('batch')
            )
        except DeliveryProductList.DoesNotExist:
            raise serializers.ValidationError(
                f"Product {product_data['mtnr']} with batch {product_data.get('batch')} "
                f"not found for delivery {billing_doc_no}"
            )

        # Get quantities
        # Convert numeric inputs to Decimal for accurate arithmetic
        delivery_qty = Decimal(product_data.get('delivery_quantity'))
        return_qty = Decimal(product_data.get('return_quantity'))
        sales_qty = product.sales_quantity
        sales_net_val = product.sales_net_val
        vat = product.vat or 0
        # validate sales quantity and sales net value
        if not sales_qty or not sales_net_val:
            raise serializers.ValidationError("Sales quantity and sales net value must be provided")
        # Validate quantities
        total_qty = delivery_qty + return_qty
        if total_qty != sales_qty:
            raise serializers.ValidationError(
                f"Product {product.mtnr}: delivery + return quantity ({total_qty}) "
                f"does not match sales quantity ({sales_qty})"
            )

        # Calculate net values
        delivery_net_val, return_net_val = calculate_net_value(vat, sales_qty, sales_net_val, delivery_qty, return_qty)

        # Update product
        product.delivery_quantity = delivery_qty
        product.return_quantity = return_qty
        product.delivery_net_val = delivery_net_val
        product.return_net_val = return_net_val
        product.updated_at = timezone.now()

        return product

    @transaction.atomic
    def update_deliveries(self):
        """Perform all delivery updates within a single transaction to ensure consistency."""
        if not self.is_valid():
            raise serializers.ValidationError(self.errors)

        validated_data = self.validated_data
        latitude = validated_data.get('delivery_latitude')
        longitude = validated_data.get('delivery_longitude')
        deliveries_data = validated_data['deliveries']

        updated_deliveries = []
        
        for delivery_data in deliveries_data:
            billing_doc_no = delivery_data['billing_doc_no']
            # Fetch and lock delivery record for update
            try:
                delivery_info = DeliveryInfo.objects.select_for_update().get(
                    billing_doc_no=billing_doc_no
                )
            except DeliveryInfo.DoesNotExist:
                raise serializers.ValidationError(
                    f"Delivery {billing_doc_no} not found"
                )

            # Update products and collect amounts
            total_delivery_amount = Decimal('0.00')
            total_return_amount = Decimal('0.00')
            has_returns = False
            
            updated_products = []
            for product_data in delivery_data['delivery_products']:
                # Validate and prepare updated product entry
                product = self.validate_and_update_product(
                    product_data, 
                    billing_doc_no
                )
                
                total_delivery_amount += product.delivery_net_val
                total_return_amount += product.return_net_val
                
                if product.return_quantity and product.return_quantity > 0:
                    has_returns = True
                
                updated_products.append(product)

            # Bulk update products
            DeliveryProductList.objects.bulk_update(
                updated_products,
                [
                    'delivery_quantity', 
                    'return_quantity', 
                    'delivery_net_val', 
                    'return_net_val', 
                    'updated_at'
                ]
            )

            # Update delivery info
            current_time = timezone.now()
            
            delivery_info.delivery_status = True
            delivery_info.delivery_time = current_time
            delivery_info.last_status = 'delivery done'
            delivery_info.delivery_amount = total_delivery_amount
            delivery_info.return_amount = total_return_amount
            delivery_info.return_status = has_returns
            delivery_info.updated_at = current_time
            delivery_info.delivery_returned = has_returns
            
            # Update coordinates if provided
            if latitude is not None:
                delivery_info.delivery_latitude = latitude
            if longitude is not None:
                delivery_info.delivery_longitude = longitude

            delivery_info.save(update_fields=[
                'delivery_status',
                'delivery_time', 
                'last_status',
                'delivery_amount',
                'return_amount', 
                'return_status',
                'delivery_latitude',
                'delivery_longitude',
                'updated_at'
            ])

            updated_deliveries.append({
                'billing_doc_no': billing_doc_no,
                'delivery_amount': total_delivery_amount,
                'return_amount': total_return_amount,
                'return_status': has_returns,
                'products_updated': len(updated_products)
            })

        return updated_deliveries