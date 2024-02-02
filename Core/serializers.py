from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from .crud import (create_customer, create_loan_with_customer_id,
                   get_correct_interest_rate, get_credit_rating,
                   get_customer_from_customer_id, get_monthly_installment)
from .models import Customer, Loan

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["customer_id", "first_name", "last_name", "age", "monthly_salary", "phone_number"]

    def create(self, validated_data):
        customer_id = validated_data.get("customer_id")
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        age = validated_data.get("age")
        monthly_salary = validated_data.get("monthly_salary")
        phone_number = validated_data.get("phone_number")

        # Assuming customer_id is required and provided in the request
        if not customer_id:
            raise serializers.ValidationError("customer_id is required")

        # Create or update the customer record
        customer, created = Customer.objects.update_or_create(
            customer_id=customer_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "monthly_salary": monthly_salary,
                "phone_number": phone_number,
                # Add other fields as needed
            }
        )

        return customer

class CreateLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["customer_id", "loan_amount", "tenure", "interest_rate"]

    @staticmethod
    def create(data):
        customer = get_customer_from_customer_id(
            customer_id=data["customer_id"].customer_id
        )
        credit_rating = get_credit_rating(
            customer=customer,
            customer_id=data["customer_id"],
            loan_amount=data["loan_amount"],
            approved_limit=customer.approved_limit,
        )

        correct_interest_rate = get_correct_interest_rate(
            credit_rating=credit_rating, interest_rate=data["interest_rate"]
        )
        monthly_installment = get_monthly_installment(
            interest_rate=correct_interest_rate,
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
        )
        loan_obj = create_loan_with_customer_id(
            customer_id=data["customer_id"],
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
            interest_rate=data["interest_rate"],
            monthly_emi=monthly_installment,
        )
        return loan_obj

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["loan_id"] = instance.loan_id
        data["loan_approved"] = True
        data["message"] = "Congratulations! You're loan is approved"
        data["monthly_installment"] = instance.monthly_emi
        data.pop("loan_amount")
        data.pop("tenure")
        data.pop("interest_rate")

        response_data = {"success": True, "data": data}

        return response_data


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["loan_id", "loan_amount", "interest_rate", "monthly_emi", "tenure"]

    def to_representation(self, instance):
        validated_data = super().to_representation(instance)
        many = self.context.get("many", False)
        if many:
            return validated_data

        customer = RegisterSerializer(
            instance.customer_id, context={"loan_obj": True}
        ).data
        validated_data["customer"] = customer
        response_data = {"success": True, "data": validated_data}
        return response_data
