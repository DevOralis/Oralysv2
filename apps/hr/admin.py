from django.contrib import admin
from .models.employee import Employee
from .models.contract import Contract
from .models.child import Child
from .models.department import Department
from .models.position import Position
from .models.contract_type import ContractType
from .models.leave_type import LeaveType
from .models.leave_request import LeaveRequest
from .models.leave_balance import LeaveBalance
from .models.leave_approval import LeaveApproval
from .models.social_contribution import SocialContribution
from .models.speciality import Speciality

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'speciality', 'position', 'department', 'get_contract')
    search_fields = ('employee_id', 'full_name')
    list_filter = ('speciality', 'position', 'department')
    
    def get_contract(self, obj):
        """Afficher le type de contrat de l'employé"""
        contract = obj.contracts.first()
        return contract.contract_type.name if contract else 'Aucun contrat'
    get_contract.short_description = 'Contrat'

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Contract)
admin.site.register(Child)
admin.site.register(Department)
admin.site.register(Position)
admin.site.register(ContractType)
admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
admin.site.register(LeaveBalance)
admin.site.register(LeaveApproval)
admin.site.register(SocialContribution)
admin.site.register(Speciality)
