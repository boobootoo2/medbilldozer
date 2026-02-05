"""Simulated Healthcare Portal Templates

This module generates HTML templates for fictional insurance and provider portals.
ALL data is simulated and clearly marked as DEMO ONLY.

These templates are designed to be rendered in iframes to demonstrate
a Plaid-like connection experience without connecting to real systems.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict


# ==============================================================================
# Utility Functions
# ==============================================================================


def generate_fake_claim_number() -> str:
    """Generate a fake claim number."""
    return f"CLM-{random.randint(100000, 999999)}"


def generate_fake_date(days_ago: int = 0) -> str:
    """Generate a fake date in the past."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%m/%d/%Y")


def generate_fake_cpt_code() -> str:
    """Generate a fake CPT procedure code."""
    codes = [
        "99213",  # Office visit
        "99214",  # Office visit, detailed
        "80053",  # Comprehensive metabolic panel
        "85025",  # Complete blood count
        "36415",  # Venipuncture
        "45378",  # Colonoscopy
        "93000",  # Electrocardiogram
        "73610",  # X-ray ankle
        "70450",  # CT head
        "71020",  # Chest X-ray
    ]
    return random.choice(codes)


def generate_fake_amount() -> float:
    """Generate a fake dollar amount."""
    return round(random.uniform(50.00, 2500.00), 2)


# ==============================================================================
# Insurance Portal Template
# ==============================================================================


def generate_insurance_portal_html(
    company_name: str = "Demo Insurance Co.",
    member_id: str = "DEMO123456",
    plan_name: str = "Gold PPO Plan"
) -> str:
    """Generate a simulated insurance company portal.

    Args:
        company_name: Name of the fictional insurance company
        member_id: Fake member ID
        plan_name: Fake plan name

    Returns:
        HTML string for insurance portal
    """

    # Generate fake claims data
    claims = []
    for i in range(5):
        days_ago = random.randint(30, 180)
        billed = generate_fake_amount()
        allowed = round(billed * random.uniform(0.6, 0.9), 2)
        paid = round(allowed * random.uniform(0.7, 0.95), 2)
        patient_resp = round(allowed - paid, 2)

        claims.append({
            "claim_number": generate_fake_claim_number(),
            "service_date": generate_fake_date(days_ago),
            "processed_date": generate_fake_date(days_ago - 14),
            "provider": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis'])} (DEMO)",
            "service": random.choice([
                "Office Visit",
                "Laboratory Services",
                "Diagnostic Imaging",
                "Preventive Care",
                "Specialist Consultation"
            ]),
            "cpt_code": generate_fake_cpt_code(),
            "billed_amount": billed,
            "allowed_amount": allowed,
            "paid_amount": paid,
            "patient_responsibility": patient_resp,
            "status": random.choice(["Processed", "Paid", "Pending"])
        })

    # Build claims table HTML
    claims_html = ""
    for claim in claims:
        claims_html += f"""
        <tr>
            <td>{claim['claim_number']}</td>
            <td>{claim['service_date']}</td>
            <td>{claim['provider']}</td>
            <td>{claim['service']}<br/><small>CPT: {claim['cpt_code']}</small></td>
            <td>${claim['billed_amount']:,.2f}</td>
            <td>${claim['allowed_amount']:,.2f}</td>
            <td>${claim['paid_amount']:,.2f}</td>
            <td><strong>${claim['patient_responsibility']:,.2f}</strong></td>
            <td><span class="status status-{claim['status'].lower()}">{claim['status']}</span></td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Member Portal (DEMO)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .demo-banner {{
            background: #ff6b6b;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .portal-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(to right, #4e54c8, #8f94fb);
            color: white;
            padding: 30px;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .member-info {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .info-item {{
            display: flex;
            flex-direction: column;
        }}

        .info-label {{
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 5px;
        }}

        .info-value {{
            font-size: 16px;
            font-weight: 600;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            color: #4e54c8;
            font-size: 22px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4e54c8;
        }}

        .summary-card-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}

        .summary-card-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}

        thead {{
            background: #f8f9fa;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #4e54c8;
            border-bottom: 2px solid #e0e0e0;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}

        .status-processed {{
            background: #d4edda;
            color: #155724;
        }}

        .status-paid {{
            background: #cce5ff;
            color: #004085;
        }}

        .status-pending {{
            background: #fff3cd;
            color: #856404;
        }}

        .disclaimer {{
            background: #fff3cd;
            border: 2px dashed #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            text-align: center;
        }}

        .disclaimer-title {{
            font-weight: bold;
            font-size: 18px;
            color: #856404;
            margin-bottom: 10px;
        }}

        .disclaimer-text {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        ⚠️ SIMULATED SAMPLE PORTAL — FICTIONAL DATA FOR DEMONSTRATION PURPOSES ONLY
    </div>

    <div class="portal-container">
        <div class="header">
            <h1>🛡️ {company_name}</h1>
            <p>Member Portal Dashboard</p>

            <div class="member-info">
                <div class="info-item">
                    <div class="info-label">Member ID</div>
                    <div class="info-value">{member_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Plan</div>
                    <div class="info-value">{plan_name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Coverage Period</div>
                    <div class="info-value">01/01/2026 - 12/31/2026</div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>Plan Summary (YTD 2026)</h2>
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="summary-card-label">Deductible Progress</div>
                        <div class="summary-card-value">$850 / $1,500</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-card-label">Out-of-Pocket Max</div>
                        <div class="summary-card-value">$1,240 / $5,000</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-card-label">Total Claims (YTD)</div>
                        <div class="summary-card-value">12</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Recent Claims & Explanation of Benefits (EOB)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Claim #</th>
                            <th>Service Date</th>
                            <th>Provider</th>
                            <th>Service</th>
                            <th>Billed</th>
                            <th>Allowed</th>
                            <th>Paid</th>
                            <th>You Owe</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {claims_html}
                    </tbody>
                </table>
            </div>

            <div class="disclaimer">
                <div class="disclaimer-title">⚠️ DEMO DISCLAIMER</div>
                <div class="disclaimer-text">
                    This is a <strong>simulated insurance portal</strong> displaying <strong>fictional data only</strong>.<br/>
                    All claim numbers, dates, amounts, and provider names are completely fabricated for demonstration purposes.<br/>
                    <strong>No real insurance data or PHI is displayed or transmitted.</strong><br/>
                    For educational and demo use only.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """


# ==============================================================================
# Provider Portal Template
# ==============================================================================


def generate_provider_portal_html(
    provider_name: str = "Memorial Medical Center",
    patient_name: str = "DEMO PATIENT",
    account_number: str = "ACCT-789012"
) -> str:
    """Generate a simulated healthcare provider portal.

    Args:
        provider_name: Name of the fictional provider
        patient_name: Fake patient name
        account_number: Fake account number

    Returns:
        HTML string for provider portal
    """

    # Generate fake statements
    statements = []
    for i in range(4):
        days_ago = random.randint(30, 120)
        statement_date = generate_fake_date(days_ago)

        # Generate line items for this statement
        line_items = []
        total_charges = 0
        for j in range(random.randint(1, 3)):
            charge = generate_fake_amount()
            total_charges += charge
            line_items.append({
                "date": generate_fake_date(days_ago + random.randint(0, 5)),
                "description": random.choice([
                    "Office Visit - New Patient",
                    "Laboratory - Blood Work",
                    "Diagnostic Imaging - X-Ray",
                    "Preventive Care Screening",
                    "Follow-up Consultation",
                    "Immunization Administration"
                ]),
                "cpt_code": generate_fake_cpt_code(),
                "charge": charge
            })

        insurance_paid = round(total_charges * random.uniform(0.6, 0.8), 2)
        patient_balance = round(total_charges - insurance_paid, 2)

        statements.append({
            "statement_date": statement_date,
            "account_number": account_number,
            "total_charges": total_charges,
            "insurance_paid": insurance_paid,
            "patient_balance": patient_balance,
            "line_items": line_items,
            "status": random.choice(["Current", "Paid", "Payment Plan"])
        })

    # Build statements HTML
    statements_html = ""
    for idx, stmt in enumerate(statements):
        line_items_html = ""
        for item in stmt['line_items']:
            line_items_html += f"""
            <tr>
                <td>{item['date']}</td>
                <td>{item['description']}<br/><small>CPT: {item['cpt_code']}</small></td>
                <td>${item['charge']:,.2f}</td>
            </tr>
            """

        statements_html += f"""
        <div class="statement-card">
            <div class="statement-header">
                <div>
                    <strong>Statement Date:</strong> {stmt['statement_date']}<br/>
                    <strong>Account:</strong> {stmt['account_number']}
                </div>
                <div class="statement-status">
                    <span class="status status-{stmt['status'].lower().replace(' ', '-')}">{stmt['status']}</span>
                </div>
            </div>

            <table class="statement-table">
                <thead>
                    <tr>
                        <th>Service Date</th>
                        <th>Description</th>
                        <th>Charges</th>
                    </tr>
                </thead>
                <tbody>
                    {line_items_html}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="2" style="text-align: right; font-weight: bold;">Total Charges:</td>
                        <td style="font-weight: bold;">${stmt['total_charges']:,.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="2" style="text-align: right;">Insurance Paid:</td>
                        <td>-${stmt['insurance_paid']:,.2f}</td>
                    </tr>
                    <tr class="balance-row">
                        <td colspan="2" style="text-align: right; font-weight: bold;">Patient Balance:</td>
                        <td style="font-weight: bold; color: #dc3545;">${stmt['patient_balance']:,.2f}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{provider_name} - Patient Portal (DEMO)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .demo-banner {{
            background: #ff6b6b;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .portal-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(to right, #00b4db, #0083b0);
            color: white;
            padding: 30px;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .patient-info {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .info-item {{
            display: flex;
            flex-direction: column;
        }}

        .info-label {{
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 5px;
        }}

        .info-value {{
            font-size: 16px;
            font-weight: 600;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            color: #00b4db;
            font-size: 22px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #00b4db;
        }}

        .summary-card-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}

        .summary-card-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}

        .statement-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
        }}

        .statement-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #dee2e6;
        }}

        .statement-status {{
            text-align: right;
        }}

        .statement-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
        }}

        .statement-table thead {{
            background: #e9ecef;
        }}

        .statement-table th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            font-size: 14px;
        }}

        .statement-table td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
        }}

        .statement-table tbody tr:hover {{
            background: #f8f9fa;
        }}

        .statement-table tfoot {{
            background: #e9ecef;
            font-weight: 600;
        }}

        .statement-table tfoot td {{
            padding: 12px;
            border-bottom: none;
        }}

        .balance-row {{
            background: #fff3cd !important;
        }}

        .status {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}

        .status-current {{
            background: #fff3cd;
            color: #856404;
        }}

        .status-paid {{
            background: #d4edda;
            color: #155724;
        }}

        .status-payment-plan {{
            background: #cce5ff;
            color: #004085;
        }}

        .disclaimer {{
            background: #fff3cd;
            border: 2px dashed #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            text-align: center;
        }}

        .disclaimer-title {{
            font-weight: bold;
            font-size: 18px;
            color: #856404;
            margin-bottom: 10px;
        }}

        .disclaimer-text {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        ⚠️ SIMULATED SAMPLE PORTAL — FICTIONAL DATA FOR DEMONSTRATION PURPOSES ONLY
    </div>

    <div class="portal-container">
        <div class="header">
            <h1>🏥 {provider_name}</h1>
            <p>Patient Billing Portal</p>

            <div class="patient-info">
                <div class="info-item">
                    <div class="info-label">Patient Name</div>
                    <div class="info-value">{patient_name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Account Number</div>
                    <div class="info-value">{account_number}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Portal Access</div>
                    <div class="info-value">Demo Mode</div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>Account Summary</h2>
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="summary-card-label">Current Balance</div>
                        <div class="summary-card-value">${sum(s['patient_balance'] for s in statements):,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-card-label">Last Payment</div>
                        <div class="summary-card-value">${generate_fake_amount():,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-card-label">Statement Count</div>
                        <div class="summary-card-value">{len(statements)}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Recent Statements & Bills</h2>
                {statements_html}
            </div>

            <div class="disclaimer">
                <div class="disclaimer-title">⚠️ DEMO DISCLAIMER</div>
                <div class="disclaimer-text">
                    This is a <strong>simulated provider portal</strong> displaying <strong>fictional data only</strong>.<br/>
                    All account numbers, dates, charges, and patient information are completely fabricated for demonstration purposes.<br/>
                    <strong>No real medical bills or PHI are displayed or transmitted.</strong><br/>
                    For educational and demo use only.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """


# ==============================================================================
# Pharmacy Portal Template
# ==============================================================================


def generate_pharmacy_portal_html(
    pharmacy_name: str = "Demo Pharmacy",
    patient_name: str = "DEMO PATIENT",
    rx_number: str = "RX-456789"
) -> str:
    """Generate a simulated pharmacy portal.

    Args:
        pharmacy_name: Name of the fictional pharmacy
        patient_name: Fake patient name
        rx_number: Fake prescription number

    Returns:
        HTML string for pharmacy portal
    """

    medications = [
        {"name": "Lisinopril 10mg", "generic": True, "qty": 30, "refills": 3},
        {"name": "Atorvastatin 20mg", "generic": True, "qty": 30, "refills": 5},
        {"name": "Metformin 500mg", "generic": True, "qty": 60, "refills": 2},
        {"name": "Levothyroxine 50mcg", "generic": True, "qty": 30, "refills": 11},
    ]

    prescriptions_html = ""
    for i, med in enumerate(medications[:3]):
        days_ago = random.randint(10, 90)
        copay = round(random.uniform(5.00, 35.00), 2) if med["generic"] else round(random.uniform(25.00, 75.00), 2)

        prescriptions_html += f"""
        <div class="rx-card">
            <div class="rx-header">
                <div>
                    <strong>{med['name']}</strong>
                    <span class="generic-badge">{'Generic' if med['generic'] else 'Brand'}</span>
                </div>
                <div class="rx-status">
                    <span class="status status-active">Active</span>
                </div>
            </div>
            <div class="rx-details">
                <div class="rx-detail-item">
                    <span class="label">Rx Number:</span>
                    <span class="value">RX-{100000 + i}</span>
                </div>
                <div class="rx-detail-item">
                    <span class="label">Last Filled:</span>
                    <span class="value">{generate_fake_date(days_ago)}</span>
                </div>
                <div class="rx-detail-item">
                    <span class="label">Quantity:</span>
                    <span class="value">{med['qty']} tablets</span>
                </div>
                <div class="rx-detail-item">
                    <span class="label">Refills Left:</span>
                    <span class="value">{med['refills']} of {med['refills'] + random.randint(0, 2)}</span>
                </div>
                <div class="rx-detail-item">
                    <span class="label">Copay:</span>
                    <span class="value">${copay:.2f}</span>
                </div>
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pharmacy_name} - Patient Portal (DEMO)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .demo-banner {{
            background: #ff6b6b;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px 8px 0 0;
        }}

        .portal-container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 0 0 8px 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}

        .header {{
            background: linear-gradient(to right, #11998e, #38ef7d);
            color: white;
            padding: 30px;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 5px;
        }}

        .content {{
            padding: 30px;
        }}

        .section h2 {{
            color: #11998e;
            font-size: 22px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .rx-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #dee2e6;
        }}

        .rx-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }}

        .generic-badge {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 10px;
        }}

        .rx-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .rx-detail-item {{
            display: flex;
            flex-direction: column;
        }}

        .rx-detail-item .label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }}

        .rx-detail-item .value {{
            font-size: 14px;
            font-weight: 600;
        }}

        .status {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}

        .status-active {{
            background: #d4edda;
            color: #155724;
        }}

        .disclaimer {{
            background: #fff3cd;
            border: 2px dashed #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            text-align: center;
        }}

        .disclaimer-title {{
            font-weight: bold;
            font-size: 18px;
            color: #856404;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="demo-banner">
        ⚠️ SIMULATED SAMPLE PORTAL — FICTIONAL DATA FOR DEMONSTRATION PURPOSES ONLY
    </div>

    <div class="portal-container">
        <div class="header">
            <h1>💊 {pharmacy_name}</h1>
            <p>Prescription Management Portal</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>Active Prescriptions</h2>
                {prescriptions_html}
            </div>

            <div class="disclaimer">
                <div class="disclaimer-title">⚠️ DEMO DISCLAIMER</div>
                <div class="disclaimer-text">
                    This is a <strong>simulated pharmacy portal</strong> with <strong>fictional data only</strong>.<br/>
                    All prescription information is completely fabricated.<br/>
                    <strong>No real medication or PHI is displayed.</strong>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """


# ==============================================================================
# Export Functions
# ==============================================================================

__all__ = [
    'generate_insurance_portal_html',
    'generate_provider_portal_html',
    'generate_pharmacy_portal_html',
]

