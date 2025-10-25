from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer, Loan

class CreditSystemAPITests(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="1234567890",
            approved_limit=1800000
        )
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=9000,
            emis_paid_on_time=5,
            start_date="2023-01-01",
            end_date="2024-01-01"
        )

    def test_register_customer(self):
        url = "/api/register/"
        data = {
            "first_name": "New",
            "last_name": "Customer",
            "age": 25,
            "monthly_income": 60000,
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_check_eligibility_eligible(self):
        url = "/api/check-eligibility/"
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 200000,
            "interest_rate": 11,
            "tenure": 24
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['approval'])

    def test_check_eligibility_ineligible(self):
        # Test with high debt-to-income ratio
        self.customer.monthly_salary = 20000
        self.customer.save()
        url = "/api/check-eligibility/"
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 500000,
            "interest_rate": 15,
            "tenure": 36
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['approval'])

    def test_create_loan_approved(self):
        url = "/api/create-loan/"
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 150000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])
        self.assertEqual(Loan.objects.count(), 2)

    def test_create_loan_not_approved(self):
        self.customer.monthly_salary = 10000
        self.customer.save()
        url = "/api/create-loan/"
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 800000,
            "interest_rate": 20,
            "tenure": 48
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Loan not approved", response.data['message'])
        self.assertEqual(Loan.objects.count(), 1)

    def test_view_loan(self):
        url = f"/api/view-loan/{self.loan.loan_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], self.loan.loan_id)

    def test_view_customer_loans(self):
        url = f"/api/view-loans/{self.customer.customer_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
