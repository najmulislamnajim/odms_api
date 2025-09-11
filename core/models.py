from django.db import models

# Create your models here.
class DeliveryAssistant(models.Model):
    sap_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    mobile_number = models.CharField(max_length=15, null=True)
    type = models.CharField(max_length=55, null=True)
    designation = models.CharField(max_length=55, null=True)
    depot_code = models.ForeignKey(
        'Depot',
        on_delete=models.SET_NULL,
        null=True,
        db_column='depot_code',
        related_name='delivery_assistants'
    )
    job_location = models.CharField(max_length=155, null=True)
    password = models.CharField(max_length=55, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sap_id} - {self.name}"
    
    class Meta:
        db_table = 'rdl_users'
        verbose_name = 'Delivery Assistant'
        verbose_name_plural = 'Delivery Assistants'
    
    
class Depot(models.Model):
    depot_code = models.CharField(max_length=10, primary_key=True)
    depot_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.depot_code} - {self.depot_name}"

    class Meta:
        db_table = 'rdl_depots'
        verbose_name = 'Depot'
        verbose_name_plural = 'Depots'
    
class Route(models.Model):
    route_code = models.CharField(max_length=20, primary_key=True)
    route_name = models.CharField(max_length=255, null=True)
    depot_code = models.ForeignKey(
        Depot, 
        on_delete=models.SET_NULL,
        null=True, 
        db_column="depot_code", 
        related_name="routes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.route_code} - {self.route_name}"
    
    class Meta:
        db_table = 'rdl_routes'
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
    
class Customer(models.Model):
    partner = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    contact_person = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    post_code = models.CharField(max_length=10, null=True)
    upazila = models.CharField(max_length=155, null=True)
    district = models.CharField(max_length=155, null=True)
    mobile_number = models.CharField(max_length=15, null=True)
    email = models.CharField(max_length=155, null=True)
    drug_reg_no = models.CharField(max_length=55, null=True)
    group = models.CharField(max_length=15, null=True)
    transport_zone = models.CharField(max_length=25, null=True)
    create_on = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.partner} - {self.name}"
    
    class Meta:
        db_table = 'rpl_customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
class Material(models.Model):
    material_code = models.CharField(max_length=20, primary_key=True)
    material_name = models.CharField(max_length=255, null=True)
    producer_company = models.CharField(max_length=3, null=True)
    unit_tp = models.DecimalField(max_digits=10, decimal_places=2)
    unit_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mrp = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    brand_name = models.CharField(max_length=255, null=True)
    brand_description = models.CharField(max_length=255, null=True)
    plant = models.CharField(max_length=4, null=True)
    sales_org = models.CharField(max_length=4, null=True)
    dis_channel = models.CharField(max_length=2, null=True)
    team = models.CharField(max_length=3, null=True)
    pack_size = models.CharField(max_length=3, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material_code} - {self.material_name}"
    
    class Meta:
        db_table = 'rpl_materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
    
class SalesInfo(models.Model):
    billing_doc_no = models.CharField(max_length=10, primary_key=True)
    gate_pass_no = models.CharField(max_length=10, null=True)
    billing_date = models.DateField()
    billing_type = models.CharField(max_length=4, null=True)
    sales_type = models.CharField(max_length=2, null=True)
    partner = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL,
        null=True, 
        db_column="partner", 
        related_name="sales_infos"
    )
    da_code = models.ForeignKey(
        DeliveryAssistant,
        on_delete=models.SET_NULL,
        null=True,
        db_column="da_code",
        related_name="sales_infos"
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        db_column="route",
        related_name="sales_infos"
    )
    delivery_status = models.BooleanField(default=False)
    delivery_time = models.DateTimeField(null=True)
    cash_collection_status = models.BooleanField(default=False)
    cash_collection_time = models.DateTimeField(null=True)
    return_status = models.BooleanField(default=False)
    delivery_time_return = models.BooleanField(default=False)
    collection_time_return = models.BooleanField(default=False)
    due_status = models.BooleanField(default=False)
    sales_net_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    delivery_net_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cash_collection_net_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    return_net_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    due_net_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    last_status = models.CharField(max_length=255, null=True)
    delivery_latitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    delivery_longitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    cash_collection_latitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
    cash_collection_longitude = models.DecimalField(max_digits=27, decimal_places=16, null=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.billing_doc_no} - {self.billing_date}"
    
    class Meta:
        db_table = 'rpl_sales_info'
        verbose_name = 'Sales Info'
        verbose_name_plural = 'Sales Infos'
        indexes = [
            # Composite indexes for common queries
            models.Index(fields=['da_code', 'billing_date']),
            models.Index(fields=['partner', 'billing_date']),
            models.Index(fields=['gate_pass_no', 'billing_date', 'da_code']),

            # Single-column indexes for frequent filters
            models.Index(fields=['gate_pass_no']),
            models.Index(fields=['partner']),
            models.Index(fields=['da_code']),
            models.Index(fields=['sales_type']),
            models.Index(fields=['billing_date']),
        ]
    
class SalesProductList(models.Model):
    billing_doc_no = models.ForeignKey(
        SalesInfo,
        on_delete=models.SET_NULL,
        null=True,
        db_column="billing_doc_no",
        related_name="sales_products",
        primary_key=True
    )
    material_code = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        db_column="material_code",
        related_name="sales_products"
    )
    batch = models.CharField(max_length=10, null=True)
    tp = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vat = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    sales_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    sales_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    delivery_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    delivery_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    return_quantity = models.DecimalField(max_digits=18, decimal_places=0, null=True)
    return_net_val = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cancel = models.CharField(max_length=1, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.billing_doc_no} - {self.material_code}"
    
    class Meta:
        db_table = 'rpl_sales_products'
        verbose_name = 'Sales Product'
        verbose_name_plural = 'Sales Products'