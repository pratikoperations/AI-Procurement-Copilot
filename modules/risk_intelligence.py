"""Procurement risk intelligence and mitigation recommendations."""

SEVERITY_ORDER = {"Critical":4,"High":3,"Medium":2,"Low":1}


def _severity(score):
    if score >= 80: return "Critical"
    if score >= 60: return "High"
    if score >= 35: return "Medium"
    return "Low"


def assess_procurement_risks(scored_df, allocation_df=None):
    risks=[]
    if scored_df.empty:
        return {"risks":[],"highest_severity":"Critical","top_mitigation":"No supplier data is available.","critical_count":1,"high_count":0}
    top=scored_df.iloc[0]
    concentration=100.0 if allocation_df is None or allocation_df.empty else float(allocation_df["Recommended Allocation %"].max())
    risks.extend([
        {"Risk":"Supply concentration","Severity":_severity(concentration),"Evidence":f"Largest recommended supplier share is {concentration:.0f}%.","Mitigation":"Retain a qualified backup supplier and define contingency allocation triggers."},
        {"Risk":"Logistics risk","Severity":_severity(min(100,float(top.get("Lead Time Days",0))*2.5)),"Evidence":f"Recommended supplier lead time is {float(top.get('Lead Time Days',0)):.0f} days.","Mitigation":"Set lead-time SLA, safety-stock logic, and escalation triggers."},
        {"Risk":"Capacity risk","Severity":_severity(max(0,90-float(top.get("Capacity Buffer %",10))*4)),"Evidence":f"Reported capacity buffer is {float(top.get('Capacity Buffer %',10)):.1f}%.","Mitigation":"Validate available capacity and secure reserved capacity in contract."},
        {"Risk":"ESG risk","Severity":_severity(max(0,100-float(top.get("esg_score",50)))),"Evidence":f"ESG score is {float(top.get('esg_score',50)):.1f}/100.","Mitigation":"Close documentation gaps and agree corrective-action milestones."},
        {"Risk":"Quality risk","Severity":_severity(min(100,float(top.get("Quality PPM",1000))/20)),"Evidence":f"Quality performance is {float(top.get('Quality PPM',1000)):.0f} PPM.","Mitigation":"Set PPM targets, incoming-quality controls, and chargeback clauses."},
    ])
    currency=str(top.get("Currency","USD")).upper()
    risks.append({"Risk":"Currency risk","Severity":"Medium" if currency not in {"INR","LOCAL"} else "Low","Evidence":f"Quote currency is {currency}.","Mitigation":"Use FX adjustment bands, hedging policy, or local-currency quotation where practical."})

    material=str(top.get("Material","")).strip()
    if material=="Kraft Paper":
        risks.extend([
            {"Risk":"Kraft mill allocation risk","Severity":_severity(float(top.get("Mill Allocation %",100))),"Evidence":f"Recommended supplier mill allocation is {float(top.get('Mill Allocation %',100)):.1f}%.","Mitigation":"Secure mill allocation visibility, backup mill approval, and supply-trigger escalation clauses."},
            {"Risk":"Kraft moisture and yield risk","Severity":_severity(min(100,float(top.get("Moisture %",15))*7)),"Evidence":f"Reported Kraft Paper moisture is {float(top.get('Moisture %',15)):.1f}%.","Mitigation":"Define moisture tolerance, incoming inspection, rejection, and yield-loss recovery terms."},
            {"Risk":"Kraft fibre availability risk","Severity":_severity(max(0,100-float(top.get("Fibre Availability %",0)))),"Evidence":f"Required fibre-profile availability is {float(top.get('Fibre Availability %',0)):.1f}%.","Mitigation":"Qualify alternate fibre sources and agree allocation priority during paper shortages."},
            {"Risk":"Kraft quality continuity risk","Severity":_severity(max(0,100-float(top.get("Quality Continuity Score",0)))),"Evidence":f"Quality-continuity score is {float(top.get('Quality Continuity Score',0)):.1f}/100.","Mitigation":"Use controlled BF/GSM specifications, COA review, trial approval, and periodic mill-quality audits."},
        ])

    if material=="Flexible Laminates":
        synthetic="Synthetic demonstration assumption; not audited supplier evidence."
        risks.extend([
            {"Risk":"Laminate substrate availability","Severity":_severity(max(0,100-float(top.get("Substrate Availability %",0)))),"Evidence":f"Substrate availability is {float(top.get('Substrate Availability %',0)):.1f}%. {synthetic}","Mitigation":"Qualify alternate substrate sources and establish allocation triggers."},
            {"Risk":"Printing and lamination capacity","Severity":_severity(max(float(top.get("Press Capacity Utilisation %",100)),float(top.get("Lamination Capacity Utilisation %",100)))),"Evidence":f"Press/lamination utilisation is {float(top.get('Press Capacity Utilisation %',100)):.1f}%/{float(top.get('Lamination Capacity Utilisation %',100)):.1f}%. {synthetic}","Mitigation":"Validate available hours, backup assets, and reserved-capacity terms."},
            {"Risk":"Laminate technical continuity","Severity":_severity(max(0,100-min(float(top.get("Bond Strength Continuity Score",0)),float(top.get("Seal Integrity Continuity Score",0)),float(top.get("Solvent Retention Control Score",0))))),"Evidence":f"Bond/seal/solvent-control scores are {float(top.get('Bond Strength Continuity Score',0)):.1f}/{float(top.get('Seal Integrity Continuity Score',0)):.1f}/{float(top.get('Solvent Retention Control Score',0)):.1f}. {synthetic}","Mitigation":"Require trials, approved specifications, test records, and periodic technical review."},
            {"Risk":"Laminate technical eligibility","Severity":"Low" if bool(top.get("technical_eligible",False)) else "Critical","Evidence":"Supplier is technically eligible under controlled C2 thresholds." if bool(top.get("technical_eligible",False)) else "No technically eligible recommendation is permitted under controlled C2 thresholds.","Mitigation":"Human technical approval remains mandatory; resolve every ineligibility reason before award."},
        ])

    risks.extend([
        {"Risk":"Country risk","Severity":"Low","Evidence":"Country-level external data is not supplied.","Mitigation":"Complete country-risk review before final award."},
        {"Risk":"Geographic risk","Severity":"Low","Evidence":"Plant/location diversification data is limited.","Mitigation":"Confirm manufacturing site and alternate-site capability."},
        {"Risk":"Financial risk","Severity":"Medium","Evidence":"Financial health data is not included in the RFQ.","Mitigation":"Complete credit and financial due diligence before contracting."},
    ])
    risks=sorted(risks,key=lambda item:SEVERITY_ORDER[item["Severity"]],reverse=True)
    return {"risks":risks,"highest_severity":risks[0]["Severity"] if risks else "Low","top_mitigation":risks[0]["Mitigation"] if risks else "No mitigation required.","critical_count":sum(item["Severity"]=="Critical" for item in risks),"high_count":sum(item["Severity"]=="High" for item in risks)}
