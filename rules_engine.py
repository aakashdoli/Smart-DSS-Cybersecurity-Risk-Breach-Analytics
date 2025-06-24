def apply_rules(row):
    actions = []
    if row['risk_category'] == 'Critical':
        actions.append("Isolate Vendor")
    if row['num_incidents'] >= 2:
        actions.append("Force Patch Verification")
    if row['compliance_score'] < 0.5:
        actions.append("Mandatory Audit")
    return ', '.join(actions)