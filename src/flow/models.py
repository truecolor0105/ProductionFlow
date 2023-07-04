import contextlib, cv2
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


# User Account
class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='useraccount_user')
    key = models.TextField(null=True, blank=True)
    matrics_link = models.URLField(null=True, blank=True)
    calendar_link = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    review1 = models.TextField(null=True, blank=True)
    review2 = models.TextField(null=True, blank=True)
    review3 = models.TextField(null=True, blank=True)
    review4 = models.TextField(null=True, blank=True)
    review5 = models.TextField(null=True, blank=True)
    free = models.BooleanField(default=False)

    """  SMTP """
    username = models.EmailField(null=True, blank=True, unique=False)
    password = models.TextField(null=True, blank=True)
    server = models.CharField(max_length=100, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    """  SMTP """

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserAccount.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserAccount.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserAccount.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.user.first_name}'

    def __str__(self):
        return f'{self.user.first_name}'

    class Meta:
        ordering = ['id']
        verbose_name = "0 User Account"
        verbose_name_plural = "0 User Account"


# Company
class Company(models.Model):
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Company.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Company.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Company.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "1. Company"
        verbose_name_plural = "1. Company"


# Employee
class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employee_company')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_user', null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Employee.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Employee.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Employee.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.company.name} - {self.user}'

    def __str__(self):
        return f'{self.company.name} - {self.user}'

    class Meta:
        ordering = ['id']
        verbose_name = "2. Employee"
        verbose_name_plural = "2. Employee"


# ProjectFolder
class ProjectFolder(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projectfolder_company')
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ProjectFolder.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ProjectFolder.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ProjectFolder.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "3. Project Folder"
        verbose_name_plural = "3. Project Folder"


# Project
class Project(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='project_company')
    folder = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='project_folder', null=True,
                               blank=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    notes = models.TextField(default='', null=True, blank=True)
    contacts = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Project.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Project.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Project.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "4. Project"
        verbose_name_plural = "4. Project"


# Preset Status
class StatusPreset(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='statuspreset_company')
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusPreset.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusPreset.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusPreset.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.company.id}'

    def __str__(self):
        return f'{self.company.id}'

    class Meta:
        ordering = ['id']
        verbose_name = "7. Status Preset"
        verbose_name_plural = "7. Status Preset"


# Status
class StatusList(models.Model):
    status_preset = models.ForeignKey(StatusPreset, on_delete=models.CASCADE, related_name='statuslist_statuspreset')
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)
    employee = models.CharField(max_length=1000, default='', unique=False, null=True, blank=True)
    color = models.CharField(max_length=10, default='', unique=False, null=True, blank=True)
    notes = models.TextField(default='', null=True, blank=True)
    active = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusList.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusList.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='StatusList.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['id']
        verbose_name = "8. Status List"
        verbose_name_plural = "8. Status List"


# Status
class Status(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='status_task')
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)
    color = models.CharField(max_length=10, default='', unique=False, null=True, blank=True)
    notes = models.TextField(default='', null=True, blank=True)
    active = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Status.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Status.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Status.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['id']
        verbose_name = "9. Status"
        verbose_name_plural = "9. Status"


# TaskFolder
class TaskFolder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='taskfolder_project')
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskFolder.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskFolder.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskFolder.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "5. Task Folder"
        verbose_name_plural = "5. Task Folder"


# Task
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='task_project', null=True, blank=True)
    folder = models.ForeignKey(TaskFolder, on_delete=models.CASCADE, related_name='task_folder', null=True, blank=True)
    name = models.TextField(default='', unique=False, null=True, blank=True)
    email = models.TextField(default='', null=True, blank=True)
    notes = models.TextField(default='', null=True, blank=True)
    notes1 = models.TextField(default='', null=True, blank=True)
    notes2 = models.TextField(default='', null=True, blank=True)
    notes3 = models.TextField(default='', null=True, blank=True)
    notes4 = models.TextField(default='', null=True, blank=True)
    notes5 = models.TextField(default='', null=True, blank=True)
    notes6 = models.TextField(default='', null=True, blank=True)
    notes7 = models.TextField(default='', null=True, blank=True)
    notes8 = models.TextField(default='', null=True, blank=True)
    notes9 = models.TextField(default='', null=True, blank=True)
    employee = models.CharField(max_length=1000, default='', unique=False, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True, related_name='task_status')
    outreach = models.TextField(default='', null=True, blank=True)
    shift = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Task.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Task.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Task.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.id}: {self.name}'

    def __str__(self):
        return f'{self.id}: {self.name}'

    class Meta:
        ordering = ['id']
        verbose_name = "6. Task"
        verbose_name_plural = "6. Task"


# Task Head
class TaskHead(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='taskhead_project')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taskhead_user', null=True, blank=True)
    name = models.CharField(max_length=100, default='', unique=False, null=True, blank=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "6.1 Task Head"
        verbose_name_plural = "6.1 Task Head"


# Video
def make_file_path(instance, filename):
    project_id = instance.task.project.id
    task_id = instance.task.id
    return f'uploads/files/{project_id}/{task_id}/{filename}'


class TaskVideo(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='taskvideo_task')
    file = models.FileField(upload_to=make_file_path, null=True, blank=True, max_length=1000)
    thumbnail = models.ImageField(upload_to=make_file_path, null=True, blank=True, max_length=1000)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskVideo.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskVideo.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskVideo.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.file}'

    def __str__(self):
        return f'{self.file}'

    class Meta:
        ordering = ['id']
        verbose_name = "Video File"
        verbose_name_plural = "Video File"


class VideoComment(models.Model):
    task_video = models.ForeignKey(TaskVideo, on_delete=models.CASCADE, related_name='videocomment_task_video',
                                   null=True, blank=True, default=None)
    time = models.TimeField(default='00:00:00', null=True, blank=True)
    comment = models.TextField(default='', unique=False, null=True, blank=True)
    active = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='VideoComment.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='VideoComment.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='VideoComment.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.time}'

    def __str__(self):
        return f'{self.time}'

    class Meta:
        ordering = ['id']
        verbose_name = "Video Comment"
        verbose_name_plural = "Video Comment"


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='taskcomment_task')
    time = models.TimeField(default='00:00:00', null=True, blank=True)
    comment = models.TextField(default='', unique=False, null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskComment.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskComment.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='TaskComment.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.time}'

    def __str__(self):
        return f'{self.time}'

    class Meta:
        ordering = ['id']
        verbose_name = "Task Comment"
        verbose_name_plural = "Task Comment"


# Calendar
class Calendar(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='calendar_company')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='calendar_task')
    event_on = models.DateTimeField(null=True, blank=True)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Calendar.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Calendar.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Calendar.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.task.name} - {self.event_on}'

    def __str__(self):
        return f'{self.task.name} - {self.event_on}'

    class Meta:
        ordering = ['id']
        verbose_name = "Calendar"
        verbose_name_plural = "Calendar"


# Sort
class Sort(models.Model):
    order = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sort_user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sort_company', null=True, blank=True)
    project_folder = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name='sort_project_folder',
                                       null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sort_project', null=True, blank=True)
    task_folder = models.ForeignKey(TaskFolder, on_delete=models.CASCADE, related_name='sort_task_folder',
                                    null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='sort_task', null=True, blank=True)

    def __unicode__(self):
        return f'{self.order}'

    def __str__(self):
        return f'{self.order}'

    class Meta:
        ordering = ['-id']
        verbose_name = "Sort"
        verbose_name_plural = "Sort"


# Company Payment
class CompanyPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companypayment_user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='companypayment_company', null=True,
                                blank=True)
    start = models.DateField(default=datetime.now)
    end = models.DateField(default=datetime.now() + timedelta(days=30))

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='CompanyPayment.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='CompanyPayment.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='CompanyPayment.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.user.first_name}'

    def __str__(self):
        return f'{self.user.first_name}'

    class Meta:
        ordering = ['id']
        verbose_name = "Company Payment"
        verbose_name_plural = "Company Payment"


# Session Payment
class PaymentSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paymentsession_user')
    session = models.TextField()
    paid = models.BooleanField(default=False)

    """  developer """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='PaymentSession.creator+', null=True,
                                blank=True)
    created = models.DateTimeField(null=True, blank=True)
    updater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='PaymentSession.updater+', null=True,
                                blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    deleter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='PaymentSession.deleter+', null=True,
                                blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    """  developer """

    def __unicode__(self):
        return f'{self.user.first_name}'

    def __str__(self):
        return f'{self.user.first_name}'

    class Meta:
        ordering = ['id']
        verbose_name = "Payment Session"
        verbose_name_plural = "Payment Session"


# Select
class Select(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='select_user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='select_company')

    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='select_employee')
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE, related_name='select_project')
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE, related_name='select_task')
    status_preset = models.ForeignKey(StatusPreset, null=True, blank=True, on_delete=models.CASCADE, related_name='select_status_preset')
    tab = models.CharField(max_length=20, default='#tab_calendar')
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return f'{self.user.first_name} - {self.company.id}'

    def __str__(self):
        return f'{self.user.first_name} - {self.company.id}'

    class Meta:
        ordering = ['company']
        verbose_name = "Select"
        verbose_name_plural = "Select"


@receiver(post_save, sender=Company)
def post_save_company(sender, instance, *args, **kwargs):
    user = instance.creator
    Select.objects.filter(user=user).update(status=False)

    try:
        select = Select.objects.get(user=user, company=instance)
        select.company = instance
        select.save()

    except Exception:
        select = Select()
        select.user = user
        select.company = instance
        select.status = True
        select.save()


@receiver(post_save, sender=Employee)
def post_save_employee(sender, instance, *args, **kwargs):
    user = instance.creator

    try:
        select = Select.objects.get(user=user, company=instance.company)
        select.employee = instance
        select.project = None
        select.save()

    except Exception:
        select = Select()
        select.user = user
        select.company = instance.company
        select.employee = instance
        select.project = None
        select.save()


@receiver(post_save, sender=ProjectFolder)
def post_save_project_folder(sender, instance, *args, **kwargs):
    user = instance.creator


@receiver(post_save, sender=Project)
def post_save_project(sender, instance, *args, **kwargs):
    user = instance.creator

    try:
        select = Select.objects.get(user=user, company=instance.company)
        select.project = instance
        select.save()

    except Exception:
        select = Select()
        select.user = user
        select.company = instance.company
        select.project = instance
        select.save()


@receiver(post_save, sender=TaskFolder)
def post_save_task_folder(sender, instance, *args, **kwargs):
    user = instance.creator


@receiver(post_save, sender=Task)
def post_save_task(sender, instance, *args, **kwargs):
    user = instance.creator

    try:
        select = Select.objects.get(user=user, company=instance.project.company)
        select.task = instance
        select.save()

    except Exception:
        select = Select()
        select.user = user
        select.company = instance.project.company
        select.task = instance
        select.save()


@receiver(post_save, sender=StatusPreset)
def post_save_status_preset(sender, instance, *args, **kwargs):
    user = instance.creator
    try:
        select = Select.objects.get(user=user, company=instance.company)
        select.status_preset = instance
        select.save()

    except Exception:
        select = Select()
        select.user = user
        select.company = instance.company
        select.status_preset = instance
        select.save()