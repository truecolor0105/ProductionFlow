from django.contrib import admin
from .models import UserAccount, Select, Company, Employee, TaskHead, ProjectFolder, Project, TaskFolder, Task, TaskComment, StatusPreset, \
    StatusList, Status, Calendar, Sort, TaskVideo, VideoComment, CompanyPayment, PaymentSession


# Register your models here.
admin.site.register(Company)
admin.site.register(CompanyPayment)
admin.site.register(PaymentSession)

admin.site.register(Employee)

admin.site.register(ProjectFolder)
admin.site.register(Project)

admin.site.register(TaskHead)
admin.site.register(TaskFolder)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(TaskVideo)

admin.site.register(VideoComment)

admin.site.register(StatusPreset)
admin.site.register(StatusList)
admin.site.register(Status)

admin.site.register(Calendar)
admin.site.register(Sort)
admin.site.register(UserAccount)

admin.site.register(Select)