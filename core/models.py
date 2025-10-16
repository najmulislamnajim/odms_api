from django.db import models

# Create your models here.
class DeliveryInfo(models.Model):
    billing_doc_no = models.CharField(max_length=10, primary_key=True)
    gate_pass_no = models.CharField(max_length=10, null=True)
    billing_date = models.DateField()
    billing_type = models.CharField(max_length=4, null=True)
    sales_type = models.CharField(max_length=2, null=True)
    partner = models.CharField(max_length=10, null=True)
    da_code = models.CharField(max_length=10, null=True)
    route_code = models.CharField(max_length=6, null=True)
    sales_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    last_status = models.CharField(max_length=255, null=True)
    sales_org = models.CharField(max_length=4, null=True)
    delv_no = models.CharField(max_length=10, null=True)
    vehicle_no = models.CharField(max_length=25, null=True)
    company_code = models.CharField(max_length=4, null=True)
    assignment = models.CharField(max_length=10, null=True)
    plant = models.CharField(max_length=4, null=True)
    reference = models.CharField(max_length=16, null=True)
    order_type = models.CharField(max_length=5, null=True)
    item_category = models.CharField(max_length=4, null=True)
    territory_code = models.CharField(max_length=5, null=True)
    team = models.CharField(max_length=3, null=True)
    mio_name = models.CharField(max_length=55, null=True)
    mio_mobile_no = models.CharField(max_length=15, null=True)
    delivery_status = models.BooleanField(default=False, null=True)
    delivery_time = models.DateTimeField(null=True)
    cash_collection_status = models.BooleanField(default=False, null=True)
    cash_collection_time = models.DateTimeField(null=True)
    return_status = models.BooleanField(default=False, null=True)
    delivery_returned = models.BooleanField(default=False, null=True)
    collection_returned = models.BooleanField(default=False, null=True)
    due_status = models.BooleanField(default=False, null=True)
    delivery_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cash_collection_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    return_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    due_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    delivery_latitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    delivery_longitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    cash_collection_latitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    cash_collection_longitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    is_cache = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.billing_doc_no} - {self.billing_date}"
    
    class Meta:
        db_table = 'rdl_delivery_info'
        verbose_name = 'Delivery Info'
        verbose_name_plural = 'Delivery Infos'
        indexes = [
            # Composite indexes for common queries
            models.Index(fields=['billing_date', 'da_code', 'sales_type']),
            models.Index(fields=['billing_date', 'partner', 'sales_type']),
        ]
    
class DeliveryProductList(models.Model):
    billing_doc_no = models.ForeignKey(
        DeliveryInfo,
        on_delete=models.CASCADE,
        null=False,
        db_column="billing_doc_no",
        related_name="sales_products",
    )
    mtnr = models.CharField(max_length=40, null=False)
    batch = models.CharField(max_length=10, null=True)
    tp = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vat = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    sales_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    sales_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cancel = models.CharField(max_length=1, null=True)
    delivery_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    delivery_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    return_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    return_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    is_cache = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.BigAutoField(primary_key=True)
    def __str__(self):
        return f"{self.billing_doc_no} - {self.mtnr}"
    
    class Meta:
        db_table = 'rdl_delivery_product_list'
        verbose_name = 'Delivery Product List'
        verbose_name_plural = 'Delivery Product Lists'
        constraints = [
            models.UniqueConstraint(
                fields=['billing_doc_no', 'mtnr', 'batch'],
                name='unique_key'
            )
        ]