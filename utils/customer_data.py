import pandas as pd
import logging

from Core.models import Customer

logger = logging.getLogger(__name__)

def add_customer_data():
    df = pd.read_excel("utils/customer_data.xlsx")
    for index, row in df.iterrows():
        try:
            phone_number = "+91" + str(row["Phone Number"])
            customer_id = row["Customer ID"]
            defaults = {
                "first_name": row["First Name"],
                "last_name": row["Last Name"],
                "age": row["Age"],
                "phone_number": phone_number,
                "monthly_salary": row["Monthly Salary"],
                "approved_limit": row["Approved Limit"],
            }
            # Update existing record if found, or create a new one
            customer_obj, created = Customer.objects.update_or_create(
                customer_id=customer_id,
                defaults=defaults
            )
            if created:
                logger.info(f"New customer created with ID: {customer_id}")
            else:
                logger.info(f"Customer updated with ID: {customer_id}")
        except Exception as e:
            logger.error(f"Error processing customer data for ID {customer_id}: {e}")
