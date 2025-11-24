import logging
from src.application.dto.add_expense import AddExpenseInput, AddExpenseOutput
from src.domain.entities.expense import Expense
from src.domain.repositories.expense_repository import ExpenseRepository

log = logging.getLogger(__name__)

class AddExpenseUseCase:
    def __init__(self, expense_repo: ExpenseRepository):
        self._expense_repo = expense_repo

    def execute(self, input_dto: AddExpenseInput) -> AddExpenseOutput:
        expense = Expense(
            amount=input_dto.amount,
            description=input_dto.description,
            date=input_dto.date,
            type=input_dto.type,
            category=input_dto.category,
            msg_id=input_dto.msg_id,
            chat_id=input_dto.chat_id,
            user_id=input_dto.user_id,
            created_at=input_dto.created_at,
            updated_at=input_dto.updated_at,
            deleted_at=None,
        )
        try:
            expense = self._expense_repo.create(
                expense,
            )
            return AddExpenseOutput(expense=expense)
        except Exception as e:
            log.error(f"Failed to add expense: {e}")
            raise Exception(f"Error saving expense: {str(e)}")
