def get_delivery_list_query(delivery_type_condition=""):
    DELIVERY_LIST_QUERY = f"""
    SELECT
        di.partner,
        COUNT(di.billing_doc_no) AS invoices,
        SUM(di.sales_amount) AS sales_amount,
        SUM(di.delivery_amount) AS delivery_amount,
        CONCAT(c.name1,' ',c.name2) AS partner_name,
        CONCAT(c.street,' ',c.street1,' ',c.street2,' ',c.street3,' ',c.post_code,' ',c.upazilla,' ',c.district) AS partner_address,
        c.mobile_no AS partner_mobile,
        c.previous_due
    FROM rdl_delivery_info di 
    INNER JOIN rpl_customer c ON di.partner=c.partner
    WHERE di.billing_date=CURRENT_DATE AND di.da_code=%s AND di.sales_type!='04' {delivery_type_condition} 
    GROUP BY di.partner;
    """
    return DELIVERY_LIST_QUERY