def calculate_risk_score(row):
    return round(
        (1 - row['compliance_score']) * 0.5 +
        (row['num_incidents'] / 5) * 0.3 +
        (row['critical_assets_linked'] / 5) * 0.2,
        2
    )
