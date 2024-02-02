from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
import traceback

import utils.customer_data
import utils.load_data

from .crud import (get_correct_interest_rate, get_credit_rating,
                   get_customer_from_customer_id, get_loan_obj_from_load_id,
                   get_loan_objs_from_customer_id, get_monthly_installment)
from .serializers import (CreateLoanSerializer, LoanSerializer,
                          RegisterSerializer)

class Register(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        return super().create(request, *args, **kwargs)
    
class AddCustomerData(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        utils.customer_data.add_customer_data()
        return Response("Customer Data Added Successfully")


class AddLoanData(APIView):
    @staticmethod
    def post(request, *args, **kwargs):
        utils.load_data.add_loan_data()
        return Response("Loan Data Added Successfully")





class CreateLoan(generics.CreateAPIView):
    serializer_class = CreateLoanSerializer


class GetLoanFromLoanID(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get(self, request, pk):
        loan_obj = get_loan_obj_from_load_id(loan_id=pk)
        serializer = self.serializer_class(loan_obj, many=False)
        return Response(serializer.data)


class GetLoansFromCustomerID(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get(self, request, pk):
        loan_obj = get_loan_objs_from_customer_id(customer_id=pk)
        serializer = self.serializer_class(loan_obj, many=True, context={"many": True})
        return Response(serializer.data)


class CheckLoanEligibity(APIView):
    @staticmethod
    def post(request):
        try:
            customer_id = request.data.get("customer_id")
            loan_amount = request.data.get("loan_amount")
            interest_rate = request.data.get("interest_rate")
            tenure = request.data.get("tenure")
            
            # Validate inputs
            if not all([customer_id, loan_amount, interest_rate, tenure]):
                raise ValidationError("Missing required parameters")
            
            # Get the customer
            customer = get_customer_from_customer_id(customer_id=customer_id)
            if not customer:
                raise ValidationError("Customer does not exist")
            
            # Check if the customer has existing loans
            existing_loans = get_loan_objs_from_customer_id(customer_id=customer_id)
            if not existing_loans:
                raise ValidationError("Customer has no existing loans")
            
            # Calculate credit rating
            credit_rating = get_credit_rating(
                customer=customer,
                customer_id=customer_id,
                loan_amount=loan_amount,
                approved_limit=customer.approved_limit,
            )

            # Calculate correct interest rate and monthly installment
            correct_interest_rate = get_correct_interest_rate(
                credit_rating=credit_rating, interest_rate=interest_rate
            )
            monthly_installment = get_monthly_installment(
                interest_rate=correct_interest_rate, loan_amount=loan_amount, tenure=tenure
            )
            
            # Prepare response data
            data = {
                "customer_id": customer_id,
                "approval": True,
                "interest_rate": interest_rate,
                "corrected_interest_rate": correct_interest_rate,
                "tenure": tenure,
                "monthly_installment": monthly_installment,
            }
            response = {"success": True, "data": data}
            return Response(response)
        except ValidationError as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()  # Log the traceback
            return Response({"success": False, "error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
