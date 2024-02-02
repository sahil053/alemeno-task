import pandas as pd
import logging

from Core.models import Customer, Loan

logger = logging.getLogger(__name__)

def add_loan_data():
    df = pd.read_excel("utils/loan_data.xlsx")
    for index, row in df.iterrows():
        customer_id = row["Customer ID"]
        try:
            customer_obj = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            logger.error(f"Customer with ID {customer_id} does not exist")
            continue
        
        try:
            Loan.objects.update_or_create(
                customer_id=customer_obj,
                loan_id=row["Loan ID"],
                defaults={
                    "loan_amount": row["Loan Amount"],
                    "tenure": row["Tenure"],
                    "interest_rate": row["Interest Rate"],
                    "monthly_emi": row["Monthly payment"],
                    "emi_paid_on_time": row["EMIs paid on Time"],
                    "start_date": row["Date of Approval"],
                    "end_date": row["End Date"],
                }
            )
        except Exception as e:
            logger.error(f"Error processing loan data for customer {customer_id}: {e}")
