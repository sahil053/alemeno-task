import pandas as pd
from django.core.management.base import BaseCommand
from Core.models import Customer, Loan

class Command(BaseCommand):
    help = 'Ingest data from Excel files'

    def handle(self, *args, **kwargs):
        customer_data = pd.read_excel('C:\\Users\\Sahil\\Desktop\\React Projects\\alemeno assignment\\credit_approval_system\\customer_data.xlsx')
        loan_data = pd.read_excel('C:\\Users\\Sahil\\Desktop\\React Projects\\alemeno assignment\\credit_approval_system\\loan_data.xlsx')

        for _, row in customer_data.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],              
            )

        for _, row in loan_data.iterrows():
            customer = Customer.objects.get(customer_id=row['Customer ID'])
            Loan.objects.create(
                customer=customer,
                loan_id=row['Loan ID'],
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                monthly_repayment=row['Monthly payment'],
                emis_paid_on_time=row['EMIs paid on Time'],
                start_date=row['Date of Approval'],
                end_date=row['End Date']
            )

        self.stdout.write(self.style.SUCCESS('Data ingestion completed successfully'))
