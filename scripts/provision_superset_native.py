"""
Native Apache Superset ORM Provisioner.
Executed inside enterprise_superset container to programmatically create
Database, Datasets, SqlMetrics, Charts, and Dashboards with zero manual steps.
"""

import sys
import json
import logging

from superset.app import create_app

app = create_app()

def provision():
    print("[NativeSupersetProvisioner] Initializing Superset App Context...")
    with app.app_context():
        from superset import db
        from superset.models.core import Database
        from superset.connectors.sqla.models import SqlaTable, SqlMetric
        from superset.models.slice import Slice
        from superset.models.dashboard import Dashboard

        # 1. Database Connection
        db_name = "Enterprise Analytics Engine"
        sqlalchemy_uri = "postgresql+psycopg2://platform_user:platform_password@postgres:5432/enterprise_db"

        database = db.session.query(Database).filter_by(database_name=db_name).first()
        if not database:
            database = Database(database_name=db_name, sqlalchemy_uri=sqlalchemy_uri)
            db.session.add(database)
            db.session.commit()
            print(f"[SupersetProvisioner] Registered Database: {db_name} (ID: {database.id})")
        else:
            database.sqlalchemy_uri = sqlalchemy_uri
            db.session.commit()
            print(f"[SupersetProvisioner] Existing Database Verified: {db_name} (ID: {database.id})")

        # 2. Register Datasets (SqlaTable) & SqlMetrics
        tables_meta = [
            ("gold_multi_sector_summary", "Unified Cross-Sector Gold Summary", [
                ("primary_metric_value", "AVG(primary_metric_value)"),
                ("secondary_metric_value", "AVG(secondary_metric_value)"),
                ("total_records", "SUM(total_records)")
            ]),
            ("gold_credit_card", "Credit Card Transactions & Fraud", [
                ("amount_usd", "SUM(amount_usd)"),
                ("fraud_risk_score", "AVG(fraud_risk_score)"),
                ("is_fraud", "SUM(is_fraud)")
            ]),
            ("gold_banking_loan_risk", "Banking Credit & Default Risk", [
                ("default_risk_score", "AVG(default_risk_score)"),
                ("loan_amount", "SUM(loan_amount)"),
                ("applicant_income", "AVG(applicant_income)")
            ]),
            ("gold_healthcare_ogd", "Healthcare Facility Capacity & Occupancy", [
                ("bed_occupancy_pct", "AVG(bed_occupancy_pct)"),
                ("total_beds", "SUM(total_beds)"),
                ("occupied_beds", "SUM(occupied_beds)")
            ]),
            ("gold_clinical_readmission", "Clinical EHR 30-Day Readmission Risk", [
                ("readmission_risk", "AVG(readmission_risk)"),
                ("days_in_hospital", "AVG(days_in_hospital)")
            ]),
            ("gold_insurance_claims", "Insurance Claims Fraud Analytics", [
                ("fraud_probability", "AVG(fraud_probability)"),
                ("claim_amount_usd", "SUM(claim_amount_usd)")
            ]),
            ("gold_retail_sales", "Retail Revenue & Product Demand", [
                ("gross_revenue_usd", "SUM(gross_revenue_usd)"),
                ("items_sold", "SUM(items_sold)")
            ])
        ]

        dataset_map = {}
        for tbl_name, verbose_name, metrics_list in tables_meta:
            sqla_tbl = db.session.query(SqlaTable).filter_by(database_id=database.id, table_name=tbl_name).first()
            if not sqla_tbl:
                sqla_tbl = SqlaTable(
                    table_name=tbl_name,
                    database_id=database.id,
                    database=database,
                    schema="public"
                )
                db.session.add(sqla_tbl)
                db.session.commit()
                print(f"[SupersetProvisioner] Registered Dataset: {tbl_name} (ID: {sqla_tbl.id})")
            else:
                print(f"[SupersetProvisioner] Existing Dataset Verified: {tbl_name} (ID: {sqla_tbl.id})")

            # Fetch metadata to populate columns
            try:
                sqla_tbl.fetch_metadata()
                db.session.commit()
            except Exception as ex:
                print(f"[SupersetProvisioner] Metadata fetch notice for {tbl_name}: {ex}")

            # Register SqlMetrics explicitly on SqlaTable
            for mname, mexpr in metrics_list:
                existing_m = db.session.query(SqlMetric).filter_by(table_id=sqla_tbl.id, metric_name=mname).first()
                if not existing_m:
                    new_m = SqlMetric(
                        metric_name=mname,
                        expression=mexpr,
                        table_id=sqla_tbl.id
                    )
                    db.session.add(new_m)
                    print(f"   + SqlMetric added: '{mname}' -> {mexpr}")
                else:
                    existing_m.expression = mexpr

            db.session.commit()
            dataset_map[tbl_name] = sqla_tbl

        # 3. Create Native Charts (Slice)
        chart_defs = [
            # Cross-Sector Summary Charts
            {
                "name": "Cross-Sector Metric Values",
                "viz_type": "bar",
                "table": "gold_multi_sector_summary",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_multi_sector_summary'].id}__table",
                    "metrics": ["primary_metric_value"],
                    "groupby": ["sector"],
                    "adhoc_filters": []
                })
            },
            {
                "name": "Total Records Processed by Sector",
                "viz_type": "pie",
                "table": "gold_multi_sector_summary",
                "params": json.dumps({
                    "viz_type": "pie",
                    "datasource": f"{dataset_map['gold_multi_sector_summary'].id}__table",
                    "metric": "total_records",
                    "groupby": ["sector"]
                })
            },
            # Credit Card Charts
            {
                "name": "Credit Card Fraud Risk Breakdown",
                "viz_type": "pie",
                "table": "gold_credit_card",
                "params": json.dumps({
                    "viz_type": "pie",
                    "datasource": f"{dataset_map['gold_credit_card'].id}__table",
                    "metric": "amount_usd",
                    "groupby": ["risk_level"]
                })
            },
            {
                "name": "Transaction Amount vs Fraud Score",
                "viz_type": "bar",
                "table": "gold_credit_card",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_credit_card'].id}__table",
                    "metrics": ["amount_usd"],
                    "groupby": ["risk_level"]
                })
            },
            # Banking Charts
            {
                "name": "Banking Default Rate by Purpose",
                "viz_type": "bar",
                "table": "gold_banking_loan_risk",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_banking_loan_risk'].id}__table",
                    "metrics": ["default_risk_score"],
                    "groupby": ["loan_purpose"]
                })
            },
            # Healthcare Charts
            {
                "name": "Healthcare Bed Occupancy by State",
                "viz_type": "bar",
                "table": "gold_healthcare_ogd",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_healthcare_ogd'].id}__table",
                    "metrics": ["bed_occupancy_pct"],
                    "groupby": ["state"]
                })
            },
            # Clinical Charts
            {
                "name": "Clinical Readmission Risk by Age Group",
                "viz_type": "bar",
                "table": "gold_clinical_readmission",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_clinical_readmission'].id}__table",
                    "metrics": ["readmission_risk"],
                    "groupby": ["age_group"]
                })
            },
            # Insurance Claims Charts
            {
                "name": "Insurance Fraud Probability by Incident Type",
                "viz_type": "bar",
                "table": "gold_insurance_claims",
                "params": json.dumps({
                    "viz_type": "bar",
                    "datasource": f"{dataset_map['gold_insurance_claims'].id}__table",
                    "metrics": ["fraud_probability"],
                    "groupby": ["incident_type"]
                })
            },
            # Retail Sales Charts
            {
                "name": "Retail Revenue by Product Category",
                "viz_type": "pie",
                "table": "gold_retail_sales",
                "params": json.dumps({
                    "viz_type": "pie",
                    "datasource": f"{dataset_map['gold_retail_sales'].id}__table",
                    "metric": "gross_revenue_usd",
                    "groupby": ["category"]
                })
            }
        ]

        created_slices = {}
        for cdef in chart_defs:
            tbl_obj = dataset_map[cdef["table"]]
            slice_obj = db.session.query(Slice).filter_by(slice_name=cdef["name"]).first()
            if not slice_obj:
                slice_obj = Slice(
                    slice_name=cdef["name"],
                    viz_type=cdef["viz_type"],
                    datasource_type="table",
                    datasource_id=tbl_obj.id,
                    params=cdef["params"]
                )
                db.session.add(slice_obj)
                db.session.commit()
                print(f"[SupersetProvisioner] Created Chart: '{cdef['name']}' (ID: {slice_obj.id})")
            else:
                slice_obj.params = cdef["params"]
                db.session.commit()
                print(f"[SupersetProvisioner] Updated Existing Chart: '{cdef['name']}' (ID: {slice_obj.id})")
            created_slices[cdef["name"]] = slice_obj

        # 4. Create Native Dashboards (Dashboard) & Attach Slices
        dashboard_defs = [
            {
                "title": "Executive Command Center",
                "slug": "executive-command-center",
                "charts": ["Cross-Sector Metric Values", "Total Records Processed by Sector"]
            },
            {
                "title": "Credit Card Fraud Intelligence",
                "slug": "fraud-intelligence",
                "charts": ["Credit Card Fraud Risk Breakdown", "Transaction Amount vs Fraud Score"]
            },
            {
                "title": "Banking Credit Risk Analytics",
                "slug": "banking-credit-risk",
                "charts": ["Banking Default Rate by Purpose"]
            },
            {
                "title": "Healthcare Capacity & Utilization",
                "slug": "healthcare-utilization",
                "charts": ["Healthcare Bed Occupancy by State"]
            },
            {
                "title": "Clinical EHR Readmission Risk",
                "slug": "clinical-readmission",
                "charts": ["Clinical Readmission Risk by Age Group"]
            },
            {
                "title": "Insurance Claims Fraud Analytics",
                "slug": "insurance-claims-fraud",
                "charts": ["Insurance Fraud Probability by Incident Type"]
            },
            {
                "title": "Retail Sales & Product Demand",
                "slug": "retail-demand-revenue",
                "charts": ["Retail Revenue by Product Category"]
            }
        ]

        created_dashboards = []
        for ddef in dashboard_defs:
            dash_obj = db.session.query(Dashboard).filter_by(slug=ddef["slug"]).first()
            attached_slices = [created_slices[cname] for cname in ddef["charts"] if cname in created_slices]
            
            if not dash_obj:
                dash_obj = Dashboard(
                    dashboard_title=ddef["title"],
                    slug=ddef["slug"],
                    published=True,
                    slices=attached_slices
                )
                db.session.add(dash_obj)
                db.session.commit()
                print(f"[SupersetProvisioner] Created Dashboard: '{ddef['title']}' (ID: {dash_obj.id}) with {len(attached_slices)} charts")
            else:
                dash_obj.published = True
                dash_obj.slices = attached_slices
                db.session.commit()
                print(f"[SupersetProvisioner] Updated Existing Dashboard: '{ddef['title']}' (ID: {dash_obj.id}) with {len(attached_slices)} charts")
            
            created_dashboards.append(dash_obj)

        db.session.commit()
        print(f"[SupersetProvisioner] Provisioning Completed Successfully! ({len(created_dashboards)} Dashboards, {len(created_slices)} Charts, {len(dataset_map)} Datasets)")

if __name__ == "__main__":
    provision()
