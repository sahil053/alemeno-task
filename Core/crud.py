from django.db.models import F, Sum, Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Customer, Loan

def create_customer(
    first_name: str,
    last_name: str,
    age: int,
    monthly_salary: int,
    phone_number: str,
    approved_limit,
) -> Customer:
    customer = Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        age=age,
        monthly_salary=monthly_salary,
        phone_number=phone_number,
        approved_limit=approved_limit,
    )
    return customer

def get_customer_from_customer_id(customer_id: int) -> Customer:
    customer = Customer.objects.filter(customer_id=customer_id).first()

    if not customer:
        raise ValidationError(
            {
                "success": False,
                "error": "Customer does not exists with given customer id",
            }
        )
    return customer


def calculate_credit_rating(
    past_loans_paid_on_time,
    num_loans_taken_in_past,
    loan_activity_current_year,
    loan_approved_volume,
    current_loans_sum,
    approved_limit,
) -> int:
    credit_score = 0
    if past_loans_paid_on_time:
        credit_score += 20
    if num_loans_taken_in_past == 0:
        credit_score += 15
    elif num_loans_taken_in_past <= 2:
        credit_score += 10
    else:
        credit_score += 5

    if loan_activity_current_year >= 2:
        credit_score += 10

    if loan_approved_volume >= 50000:
        credit_score += 15

    if current_loans_sum <= approved_limit:
        credit_score += 20

    return credit_score


def get_credit_rating(
    customer: Customer, customer_id: int, loan_amount: int, approved_limit: int
) -> int:
    loans_of_customer = Loan.objects.filter(customer_id=customer_id)
    num_loans_taken_in_past = loans_of_customer.count()
    past_loans_paid_on_time = loans_of_customer.filter(
        tenure=F("emi_paid_on_time")
    ).count()
    loan_activity_current_year = loans_of_customer.filter(
        start_date__year=timezone.now().year
    ).count()
    loan_approved_volume = loans_of_customer.aggregate(Sum("loan_amount"))[
        "loan_amount__sum"
    ]

    monthly_emi_sum = loans_of_customer.aggregate(Sum("monthly_emi"))[
        "monthly_emi__sum"
    ]

    if monthly_emi_sum is None:
        raise ValidationError("Monthly EMI sum is not available")

    if monthly_emi_sum > customer.monthly_salary / 2:
        raise ValidationError(
            {
                "success": False,
                "approval": False,
                "error": "Loan cannot be approved because of low monthly salary",
            }
        )

    credit_rating = calculate_credit_rating(
        past_loans_paid_on_time=past_loans_paid_on_time,
        num_loans_taken_in_past=num_loans_taken_in_past,
        loan_activity_current_year=loan_activity_current_year,
        loan_approved_volume=loan_approved_volume,
        current_loans_sum=loan_amount,
        approved_limit=approved_limit,
    )

    return credit_rating
    
def get_correct_interest_rate(credit_rating: int, interest_rate: float) -> float:
    if credit_rating > 50:
        return interest_rate
    if credit_rating < 50 and credit_rating > 30:
        if interest_rate > 12.0:
            return interest_rate
        else:
            return 12.0
    if credit_rating <= 30 and credit_rating > 10:
        if interest_rate > 16.0:
            return interest_rate
        else:
            return 16.0
    if credit_rating < 10:
        raise ValidationError(
            {
                "success": False,
                "approval": False,
                "error": "Loan cannot be approved because of low credit score",
            }
        )

def get_monthly_installment(
    interest_rate: float, loan_amount: float, tenure: int
) -> int:
    monthly_interest_rate = ((interest_rate) / 100) / 12
    total_payments = tenure * 12
    emi = (
        loan_amount
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments)
        / ((1 + monthly_interest_rate) ** total_payments - 1)
    )
    return emi

def create_loan_with_customer_id(
    customer_id: Customer,
    loan_amount: float,
    tenure: int,
    interest_rate: float,
    monthly_emi: int,
) -> Loan:
    loan_obj = Loan.objects.create(
        customer_id=customer_id,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=interest_rate,
        monthly_emi=monthly_emi,
    )
    return loan_obj


def get_loan_obj_from_load_id(loan_id: int) -> Loan:
    loan_obj = Loan.objects.filter(loan_id=loan_id).first()
    if not loan_obj:
        raise ValidationError(
            {"success": False, "error": "Loan Object with given ID does not exist"}
        )
    return loan_obj


def get_loan_objs_from_customer_id(customer_id: int) -> list[Loan]:
    loan_objs = Loan.objects.filter(customer_id=customer_id)
    return loan_objs

def delete_duplicate_customers():
    # Identify duplicate customer_id values and count their occurrences
    duplicates = (
        Customer.objects.values('customer_id')
        .annotate(count=Count('customer_id'))
        .filter(count__gt=1)
    )

    # Iterate over duplicate customer_id values
    for duplicate in duplicates:
        customer_id = duplicate['customer_id']

        # Get all Customer objects with the duplicate customer_id
        duplicate_customers = Customer.objects.filter(customer_id=customer_id)

        # Keep one instance and delete the rest
        for index, customer in enumerate(duplicate_customers):
            if index == 0:
                # Keep the first occurrence
                continue
            else:
                # Delete duplicate occurrences
                customer.delete()

# Call the function to delete duplicate customers
delete_duplicate_customers()