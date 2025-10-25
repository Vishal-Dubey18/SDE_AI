from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
import datetime

def _check_eligibility(customer_id, loan_amount, interest_rate, tenure):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return {"error": "Customer not found", "status": status.HTTP_404_NOT_FOUND}

    loans = Loan.objects.filter(customer=customer)
    
    # Improved credit score calculation
    total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    num_loans = len(loans)
    num_loans_current_year = len([loan for loan in loans if loan.start_date.year == datetime.date.today().year])
    total_loan_volume = sum(loan.loan_amount for loan in loans)

    credit_score = (total_emis_paid_on_time * 5) - (num_loans * 5) - (num_loans_current_year * 10)

    if total_loan_volume > customer.approved_limit:
        credit_score = 0

    corrected_interest_rate = interest_rate
    approval = False
    if credit_score > 50:
        approval = True
    elif 50 >= credit_score > 30:
        corrected_interest_rate = 12.0
        approval = True
    elif 30 >= credit_score > 10:
        corrected_interest_rate = 16.0
        approval = True
    else:
        approval = False

    # Check if sum of EMIs exceeds 50% of monthly salary
    monthly_repayment = (loan_amount * (1 + corrected_interest_rate / 100)) / tenure
    total_monthly_repayment = sum(loan.monthly_repayment for loan in loans)
    if total_monthly_repayment + monthly_repayment > customer.monthly_salary * 0.5:
        approval = False

    return {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "tenure": tenure,
        "monthly_installment": monthly_repayment
    }

@api_view(['POST'])
def register_customer(request):
    data = request.data
    try:
        first_name = data['first_name']
        last_name = data['last_name']
        age = data['age']
        monthly_salary = data['monthly_income']
        phone_number = data['phone_number']
    except KeyError as e:
        return Response({"error": f"Missing field: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    approved_limit = round(36 * monthly_salary / 100000) * 100000

    customer = Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        age=age,
        monthly_salary=monthly_salary,
        approved_limit=approved_limit,
        phone_number=phone_number,
    )

    response_data = {
        "customer_id": customer.customer_id,
        "name": f"{customer.first_name} {customer.last_name}",
        "age": customer.age,
        "monthly_income": customer.monthly_salary,
        "approved_limit": customer.approved_limit,
        "phone_number": customer.phone_number,
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    try:
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']
    except KeyError as e:
        return Response({"error": f"Missing field: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    result = _check_eligibility(customer_id, loan_amount, interest_rate, tenure)
    if "error" in result:
        return Response({"error": result["error"]}, status=result["status"])

    return Response(result, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_loan(request):
    data = request.data
    try:
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']
    except KeyError as e:
        return Response({"error": f"Missing field: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    result = _check_eligibility(customer_id, loan_amount, interest_rate, tenure)

    if not result['approval']:
        return Response({"message": "Loan not approved"}, status=status.HTTP_200_OK)

    customer = Customer.objects.get(pk=customer_id)
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=tenure * 30)

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=result['corrected_interest_rate'],
        monthly_repayment=result['monthly_installment'],
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date,
    )

    response_data = {
        "loan_id": loan.loan_id,
        "customer_id": customer.customer_id,
        "loan_approved": True,
        "message": "Loan Approved",
        "monthly_installment": result['monthly_installment']
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    customer = loan.customer
    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "age": customer.age,
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "tenure": loan.tenure,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_customer_loans(request, customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)
    response_data = []
    for loan in loans:
        response_data.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time
        })

    return Response(response_data, status=status.HTTP_200_OK)