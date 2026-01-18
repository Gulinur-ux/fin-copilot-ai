import frappe

def get_financial_schema(doctype=None):
    """
    Extracts schema information for financial analysis, filtering for specific field types.
    
    Args:
        doctype (str, optional): Specific DocType to extract schema for. 
                                 If None, defaults to ["GL Entry", "Account"].
    
    Returns:
        dict: A dictionary where keys are DocType names and values are lists of field metadata.
    """
    target_doctypes = ["GL Entry", "Account"]
    if doctype:
        target_doctypes = [doctype]
        
    schema = {}
    
    for dt in target_doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
            
        meta = frappe.get_meta(dt)
        fields = meta.fields
        
        dt_schema = []
        for field in fields:
            # Filter for specific field types relevant to financial analysis
            if field.fieldtype in ["Float", "Currency", "Link", "Int", "Data"]: 
                # Added Int and Data as they might be useful (e.g., account_number is Data/Int usually)
                # But strict requirement was Float, Currency, Link. Let's stick to requirements mostly
                # but "Account Number" is often Data. Let's re-read requirements carefully.
                # Requirement: "Float, Currency va Link tiplarini ajratib olsin."
                # Strict adherence to requirements:
                if field.fieldtype in ["Float", "Currency", "Link"]:
                    field_data = {
                        "fieldname": field.fieldname,
                        "label": field.label,
                        "fieldtype": field.fieldtype
                    }
                    if field.fieldtype == "Link":
                        field_data["options"] = field.options
                    
                    dt_schema.append(field_data)
        
        schema[dt] = dt_schema
        
    return schema
