import pandas as pd
from django.core.management.base import BaseCommand
from credit_system.models import Customer, Loan

class Command(BaseCommand):
    help = 'Ingest data from Excel files'

    def handle(self, *args, **options):
        # Clear existing data
        Loan.objects.all().delete()
        Customer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared existing data'))

        # Ingest customer data
        customer_df = pd.read_excel('customer_data.xlsx')
        for index, row in customer_df.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
                current_debt=0  # Defaulting current_debt to 0 as it is not in the excel
            )
        self.stdout.write(self.style.SUCCESS('Successfully ingested customer data'))

        # Ingest loan data
        loan_df = pd.read_excel('loan_data.xlsx')
        loan_df.drop_duplicates(subset=['Loan ID'], keep='first', inplace=True)

        for index, row in loan_df.iterrows():
            customer = Customer.objects.get(pk=row['Customer ID'])
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
        self.stdout.write(self.style.SUCCESS('Successfully ingested loan data'))
