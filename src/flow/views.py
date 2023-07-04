import datetime, json, os, random, re, smtplib, ssl, stripe, time, base64, cv2, httpagentparser, subprocess
from contextlib import suppress
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import viewsets

from .models import UserAccount, Company, Select, Employee, ProjectFolder, Project, TaskFolder, Task, TaskComment, \
    StatusPreset, StatusList, Status, Calendar, Sort, TaskVideo, VideoComment, CompanyPayment, PaymentSession, TaskHead

from .serializers import CompanySerializer, EmployeeSerializer, ProjectFolderSerializer, ProjectSerializer, \
    TaskFolderSerializer, TaskSerializer, StatusSerializer, StatusPresetSerializer, StatusListSerializer, \
    TaskHeadSerializer, CalendarSerializer, UserAccountSerializer, TaskVideoSerializer, VideoCommentSerializer

stripe.api_key = 'sk_test_hZnYTNV1WCcZuMlF1d6Lu3QW00vwJqjCov'
task_columns = [' ', 'Name', ' ', 'Due Date', 'Outreach', 'Video', 'Status', 'Person', 'Email', 'Notes', 'Notes', 'Notes',
                'Notes', 'Notes', 'Notes', 'Notes', 'Notes', 'Notes', 'Notes', ' ']

allowed_site_for_api = ['zapier.com']


# Create your views here.
@login_required(login_url='/accounts/login/')
def mail(request):
    template_name = 'flow/mail.html'
    context = {
        'title': "Mail",
    }
    return render(request, template_name, context)


def valid_email(email):
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))


@login_required(login_url='/accounts/login/')
def send_email(request):
    try:
        mail_to = request.POST.get('mail_to_one')
        mail_subject = request.POST.get('subject')
        mail_content = request.POST.get('content')
        to_bulk_email_exclude = (request.POST.get('to_bulk_email_exclude')).split(',')

        user_account = UserAccount.objects.get(user=request.user)
        username = user_account.username
        password = user_account.password
        mail_from = user_account.username
        smtp_server = user_account.server
        smtp_port = user_account.port

        task_queryset = None
        if mail_to == '':
            task_queryset = Task.objects.filter(
                folder_id__in=(''.join(i for i in request.POST.get('mail_to_many') if i.isdigit() or i in ',\\')).split(
                    ',')
            ).exclude(email__exact='')

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(username, password)

            if mail_to == '':
                for task in task_queryset:
                    email = task.email
                    first_name = (task.name.split(' ')[0]).title()
                    if valid_email(email) and email not in to_bulk_email_exclude:
                        try:
                            msg_cont = str(mail_content).replace('%FIRSTNAME%', first_name)
                        except Exception:
                            msg_cont = mail_content.replace('%FIRSTNAME%', '')
                        message = f"Subject: {mail_subject}\nFrom:{User.objects.get(id=request.user.id).first_name.title()} <{mail_from}>\nTo: {email}\nContent-Type: text/html\n\n{msg_cont}"

                        server.sendmail(mail_from, email, message)

            elif valid_email(mail_to):
                message = f"Subject: {mail_subject}\nFrom:{User.objects.get(id=request.user.id).first_name.title()} <{mail_from}>\nTo: {mail_to}\nContent-Type: text/html\n\n{mail_content}"
                server.sendmail(mail_from, mail_to, message)
        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False})


# @login_required(login_url='/accounts/login/')
def index(request):
    if not request.user.is_authenticated:
        return redirect('https://visionaryfire.com/mastermind/#productionflow')

    free = UserAccount.objects.get(user=request.user)
    context = {
        'title': "Task",
        'free': free.free
    }
    return render(request, 'flow/flow.html', context)


"""  Start Status """


class ListProjectStatusView(viewsets.ModelViewSet):
    serializer_class = StatusSerializer

    def get_queryset(self):
        project_id = self.request.GET.get('project_id')
        return Status.objects.filter(project_id=project_id, is_deleted=False)


class ListStatusPresetView(viewsets.ModelViewSet):
    serializer_class = StatusPresetSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return StatusPreset.objects.filter(company_id=company_id, is_deleted=False).distinct()


@login_required(login_url='/accounts/login/')
def api_create_status_preset(request):
    company_id = request.POST['company_id']
    user = request.user
    date_time = datetime.datetime.now()

    sp = StatusPreset()
    sp.company_id = company_id
    sp.name = 'New Preset'
    sp.created = date_time
    sp.creator = user
    sp.save()

    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_update_status_preset(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    preset = StatusPreset.objects.get(id=data_id)

    if data_of == 'name':
        preset.name = data_value

    preset.updated = datetime.datetime.now()
    preset.updater = request.user
    preset.save()
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_select_status_preset(request):
    company_id = request.POST['company_id']
    status_preset_id = request.POST['status_preset_id']

    Select.objects.get(user=request.user, company_id=company_id, status=True).update(status_preset_id=status_preset_id)

    return JsonResponse({'success': True})


class ListStatusListView(viewsets.ModelViewSet):
    serializer_class = StatusListSerializer

    def get_queryset(self):
        status_preset_id = self.request.GET.get('status_preset_id')
        return StatusList.objects.filter(status_preset_id=status_preset_id, is_deleted=False).distinct()


@login_required(login_url='/accounts/login/')
def api_create_status_list(request):
    status_preset_id = request.POST['status_preset_id']
    color_list = ['#FE9A9A', '#F9DBA5', '#A0CAF5', '#ADEEC9', '#b7b7b7']

    sl = StatusList()
    sl.status_preset_id = status_preset_id
    sl.name = 'New Item'
    sl.color = random.choice(color_list)  # '#E15252'
    sl.created = datetime.datetime.now()
    sl.creator = request.user
    sl.save()

    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_update_status_list(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    status = StatusList.objects.get(id=data_id)

    if data_of == 'name':
        status.name = data_value

    status.updated = datetime.datetime.now()
    status.updater = request.user
    status.save()
    return JsonResponse({'success': True})


class ListStatusView(viewsets.ModelViewSet):
    serializer_class = StatusSerializer

    def get_queryset(self):
        task_id = self.request.GET.get('task_id')
        return Status.objects.filter(task_id=task_id, is_deleted=False)


@login_required(login_url='/accounts/login/')
def api_add_status(request):
    project_id = request.POST['project_id']

    status = Status()
    status.project_id = project_id
    status.name = 'New Status'
    status.employee = ''
    status.creator = request.user
    status.created = datetime.datetime.now()
    status.save()
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_update_status(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    status = Status.objects.get(id=data_id)

    if data_of == 'color':
        status.color = data_value

    elif data_of == 'employee':
        status.employee = data_value

    elif data_of == 'name':
        status.name = data_value

    status.updated = datetime.datetime.now()
    status.updater = request.user
    status.save()
    return JsonResponse({'success': True})


"""  End Status """

"""  Start Company """


class ListCompanyView(viewsets.ModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        user_id = self.request.user.id
        with suppress(Exception):
            if self.request.GET['site'] in allowed_site_for_api:
                key = ((base64.b64decode((self.request.GET['key']).encode('ascii'))).decode('ascii')).split(',')
                user_id = User.objects.get(id=key[0], email=key[1]).id
        # except:
        #     return HttpResponseNotFound("Invalid Secret Key")

        # free = UserAccount.objects.get(user=self.request.user)
        # if free.free:
        #     company_list.extend((Company.objects.filter(creator=self.request.user).order_by('id').first().id,
        #                          Employee.objects.filter(user=self.request.user, is_deleted=False).distinct().exclude(
        #                              company__creator=self.request.user).values_list('company_id', flat=True)))
        #
        # else:
        company_list = list(
            Employee.objects.filter(user_id=user_id, is_deleted=False).distinct().values_list('company_id', flat=True)
        )
        return Company.objects.filter(id__in=company_list, is_deleted=False).distinct()


@login_required(login_url='/accounts/login/')
def company(request):
    template_name = 'flow/company.html'
    context = {
        'title': "Select"
    }
    return render(request, template_name, context)


@login_required(login_url='/accounts/login/')
def renew_company(request, company_id, company_name):
    template_name = 'flow/renew_company.html'
    context = {
        'title': "Renew Company",
        'company_id': company_id,
        'company_name': company_name
    }
    return render(request, template_name, context)


@login_required(login_url='/accounts/login/')
def api_renew_checkout(request, company_id):
    base_url = f'{request.scheme}://{request.get_host()}'

    s = stripe.checkout.Session.create(
        success_url=f'{base_url}/api_renew_company/{company_id}',
        cancel_url=f'{base_url}',
        line_items=[
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': "Pay to ProductionFlow",
                    },
                    'unit_amount': 900
                },
                "quantity": 1,
            },
        ],
        mode='payment',
        customer_email=f'{request.user.email}',  # default is None
        expires_at=int(time.time()) + 3600  # 1 hour expiry
    )

    psession = PaymentSession()
    psession.user = request.user
    psession.session = s['id']
    psession.creator = request.user
    psession.created = datetime.datetime.now()
    psession.save()

    return redirect(s['url'])


@login_required(login_url='/accounts/login/')
def api_checkout_orignal(request):
    base_url = f'{request.scheme}://{request.get_host()}'

    s = stripe.checkout.Session.create(
        success_url=f'{base_url}/api_create_company',
        cancel_url=f'{base_url}',
        line_items=[
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': "Pay to ProductionFlow",
                    },
                    'unit_amount': 900
                },
                "quantity": 1,
            },
        ],
        mode='payment',
        customer_email=f'{request.user.email}',  # default is None
        expires_at=int(time.time()) + 3600  # 1 hour expiry
    )

    psession = PaymentSession()
    psession.user = request.user
    psession.session = s['id']
    psession.creator = request.user
    psession.created = datetime.datetime.now()
    psession.save()

    return redirect(s['url'])


@login_required(login_url='/accounts/login/')
def api_create_company(request):
    user = request.user
    date_time = datetime.datetime.now()
    session = PaymentSession.objects.filter(user=user, paid=False).latest('id')
    session_id = session.session

    checkout_sess = stripe.checkout.Session.retrieve(session_id)

    if checkout_sess['status'] == checkout_sess['payment_status'] or checkout_sess['payment_status'] == 'paid':
        create_company(request)

        ua = UserAccount.objects.get(id=request.user.id)
        ua.free = False
        ua.save()

    session.paid = True
    session.updated = date_time
    session.updater = user
    session.save()

    return redirect('/')


# def create_company(request):
# need to chnage
def api_checkout(request):
    user = request.user
    date_time = datetime.datetime.now()
    company = Company()
    company.name = 'Team Name'
    company.created = date_time
    company.creator = user
    company.save()

    employee = Employee()
    employee.company = company
    employee.user = user
    employee.creator = user
    employee.created = date_time
    employee.save()

    status_preset = StatusPreset()
    status_preset.company = company
    status_preset.name = 'Basic Preset'
    status_preset.created = date_time
    status_preset.creator = user
    status_preset.save()

    status_list = [{'color': '#FE9A9A', 'name': 'Not Started'},
                   {'color': '#F9DBA5', 'name': 'In Progress'},
                   {'color': '#A0CAF5', 'name': 'Review'},
                   {'color': '#A0CAF5', 'name': 'Revision'},
                   {'color': '#ADEEC9', 'name': ' '},
                   {'color': '#ADEEC9', 'name': ' '},
                   {'color': '#ADEEC9', 'name': ' '},
                   {'color': '#ADEEC9', 'name': ' '},
                   {'color': '#b7b7b7', 'name': 'Done'}
                   ]

    for status in status_list:
        sl = StatusList()
        sl.status_preset = status_preset
        sl.name = status['name']
        sl.color = status['color']
        sl.created = datetime.datetime.now()
        sl.creator = request.user
        sl.save()

    project_folder = ProjectFolder()
    project_folder.name = 'Projects'
    project_folder.company = company
    project_folder.creator = request.user
    project_folder.created = datetime.datetime.now()
    project_folder.save()

    sort_list = Sort.objects.filter(Q(user=request.user) and Q(company=company)).order_by('order')
    for order, item in enumerate(sort_list, start=1):
        item.order = order
        item.save()
    sort = Sort()
    sort.order = 0
    sort.user = request.user
    sort.company = company
    sort.project_folder = project_folder
    sort.save()

    status_preset_id = Select.objects.filter(user=user, company=company).values_list('status_preset_id', flat=True)[0]
    status_list = StatusList.objects.filter(status_preset_id=status_preset_id)



    for project_name in ['Project 1', 'Misc.', 'Contacts']:
        """ Start """
        project = Project()
        project.company = company
        project.name = project_name
        project.creator = user
        project.created = date_time

        if project_name == 'Contacts':
            project.contacts = True

        project.save()

        if project_name == 'Project 1':
            project.folder = project_folder
            project.save()

            tf = TaskFolder()
            tf.name = f"{request.user.first_name}'s Tasks"
            tf.project = project
            tf.creator = user
            tf.created = datetime.datetime.now()
            tf.save()

            t = Task()
            t.project = project
            t.folder = tf
            t.name = 'Watch Quickstart Tutorials (link at top right of screen)'
            t.notes = ''
            t.notes1 = ''
            t.notes2 = ''
            t.employee = f'{user.id}'
            t.status = Status.objects.filter(project=project).first()
            t.creator = user
            t.created = date_time
            t.save()

        for emp in Employee.objects.filter(company=company).order_by('user'):
            for order, col in enumerate(task_columns):
                th = TaskHead()
                th.user_id = emp.user.id
                th.order = order
                th.project = project
                th.name = col
                if col in ['Email', 'Notes', 'Outreach']:
                    th.active = False
                th.save()

        for status in status_list:
            st = Status()
            st.project = project
            st.name = status.name
            st.employee = status.employee
            st.color = status.color
            st.active = status.active
            st.save()

            """ End """

    cpayment = CompanyPayment()
    cpayment.user = user
    cpayment.company = company
    cpayment.creator = user
    cpayment.created = date_time
    cpayment.save()

    return redirect('/')


@login_required(login_url='/accounts/login/')
def api_update_company(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    company = Company.objects.get(id=data_id)

    if data_of == 'name':
        company.name = data_value

    company.updated = datetime.datetime.now()
    company.updater = request.user
    company.save()
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_renew_company(request, company_id):
    user = request.user
    date_time = datetime.datetime.now()
    session = PaymentSession.objects.filter(user=user, paid=False).latest('id')
    session_id = session.session

    checkout_sess = stripe.checkout.Session.retrieve(session_id)
    if checkout_sess['status'] == checkout_sess['payment_status'] or checkout_sess['payment_status'] == 'paid':
        cpayment = CompanyPayment.objects.get(user=user, company_id=company_id)
        cpayment.start = date_time
        cpayment.end = date_time + timedelta(days=30)
        cpayment.updated = date_time
        cpayment.updater = user
        cpayment.save()

    session.paid = True
    session.updated = date_time
    session.updater = user
    session.save()

    return redirect('/')


@login_required(login_url='/accounts/login/')
def api_skip_renew(request):
    user = request.user
    return redirect('/')


@login_required(login_url='/accounts/login/')
def api_invite_in_company(request):
    company_id = request.POST['company_id']
    email_to = request.POST['email_to']
    link = request.build_absolute_uri('/')[:-1]
    from_email = settings.EMAIL_HOST_USER
    company_name = Company.objects.get(id=company_id).name

    # checking if this email is already added or not
    is_sent = False
    try:
        user = User.objects.get(email=email_to)
        try:
            Employee.objects.get(company_id=company_id, user=user, is_deleted=False)
            return JsonResponse(status=404, data={'success': False, 'message': 'Failed'})
        except Exception:
            is_sent = True
            link += f'/invite/{company_id}'
    except Exception:
        is_sent = True
        link += f'/invite/{company_id}'

    message = f'Hello..! \nYou are invited to join "{company_name}" on ProductionFlow \nSTEP 1 - Create a ProductionFlow.io account here: productionflow.io/accounts/login/ \nSTEP 2 - Click the following link to join "{company_name}": {link}\n\nThank you'
    if is_sent:
        subject = 'Invitation From Productionflow.io'
        send_mail(subject, message, from_email, [email_to])

    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_add_invited_in_company(request, company_id):
    user = request.user

    if Employee.objects.filter(company_id=company_id, user=user, is_deleted=False).count() == 0:
        employee = Employee()
        employee.company_id = company_id
        employee.user = user
        employee.creator = user
        employee.created = datetime.datetime.now()
        employee.save()

    return redirect('/')


"""  End Company """

"""  Start Employee """


class ListEmployeeView(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return Employee.objects.filter(company_id=company_id, is_deleted=False).distinct()


@login_required(login_url='/accounts/login/')
def api_delete_employee(request):
    employee_id = request.POST['employee_id'] or 0
    Employee.objects.filter(id=employee_id).delete()

    return JsonResponse({'success': True})


"""  End Employee """

"""  Start Project """


class ListProjectFolderView(viewsets.ModelViewSet):
    serializer_class = ProjectFolderSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return ProjectFolder.objects.filter(company_id=company_id, is_deleted=False).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListProjectFolderView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],))
        return response


class ListProjectView(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return Project.objects.filter(company_id=company_id, is_deleted=False).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListProjectView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],), reverse=True)
        return response


@login_required(login_url='/accounts/login/')
def api_create_project_folder(request):
    company_id = request.POST['company_id']

    pf = ProjectFolder()
    pf.name = 'New Folder'
    pf.company_id = company_id
    pf.creator = request.user
    pf.created = datetime.datetime.now()
    pf.save()

    folder = ProjectFolderSerializer(instance=ProjectFolder.objects.get(id=pf.id)).data

    return JsonResponse({'success': True, 'folder': folder})


@login_required(login_url='/accounts/login/')
def api_update_project_folder(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    pf = ProjectFolder.objects.get(id=data_id)

    if data_of == 'name':
        pf.name = data_value

    pf.updated = datetime.datetime.now()
    pf.updater = request.user
    pf.save()
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_delete_project_folder(request):
    folder_id = request.POST['folder_id'] or 0
    pf = ProjectFolder.objects.get(id=folder_id)
    pf.is_deleted = True
    pf.deleted = datetime.datetime.now()
    pf.deleter = request.user
    pf.save()
    Project.objects.filter(folder=pf).update(deleted=datetime.datetime.now(), deleter=request.user)
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
# def api_create_project(request, company_id, folder_id, user):
def api_create_project(request):
    company_id = request.POST['company_id']
    folder_id = request.POST['folder_id']
    user = request.user
    date_time = datetime.datetime.now()

    project = Project()
    project.company_id = company_id
    if int(folder_id) != 0:
        project.folder_id = folder_id
    project.name = 'New Project'
    project.contacts = False
    project.creator = user
    project.created = date_time
    project.save()

    status_preset_id = Select.objects.get(user=request.user, company_id=company_id, status=True).status_preset.id
    status_list = StatusList.objects.filter(status_preset_id=status_preset_id)
    # status_list = StatusList.objects.filter(status_preset_id=StatusPreset.objects.get(company_id=company_id))

    for status in status_list:
        st = Status()
        st.project = project
        st.name = status.name
        st.employee = status.employee
        st.color = status.color
        st.active = status.active
        st.save()

    tf = TaskFolder()
    tf.name = 'New Folder'
    tf.project = project
    tf.creator = user
    tf.created = datetime.datetime.now()
    tf.save()

    for employee in Employee.objects.filter(company=project.company).order_by('user'):
        user_id = employee.user.id
        for order, col in enumerate(task_columns):
            th = TaskHead()
            th.user_id = user_id
            th.order = order
            th.project = project
            th.name = col
            if col == 'Notes':
                th.active = False
            th.save()

    data = ProjectSerializer(instance=Project.objects.get(id=project.id)).data
    return JsonResponse({'success': True, 'project': data})


@login_required(login_url='/accounts/login/')
def api_update_project(request):
    data_id = request.POST['data_id']
    data_of = request.POST['data_of']
    data_value = request.POST['data_value']
    p = Project.objects.get(id=data_id)

    if data_of == 'folder':
        if data_value == "0":
            p.folder = None
        else:
            p.folder_id = data_value

    elif data_of == 'name':
        p.name = data_value

    p.updated = datetime.datetime.now()
    p.updater = request.user
    p.save()
    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_delete_project(request):
    project_id = request.POST['project_id'] or 0
    p = Project.objects.get(id=project_id)
    p.is_deleted = True
    p.deleted = datetime.datetime.now()
    p.deleter = request.user
    p.save()
    return JsonResponse({'success': True})


"""  End Project """

"""  Start Task """


class ListEmployeeTaskFolderView(viewsets.ModelViewSet):
    serializer_class = TaskFolderSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        employee_id = self.request.GET.get('employee_id')
        all_task_list = Task.objects.filter(project__company_id=company_id, is_deleted=False).exclude(
            employee="").distinct()
        folder_ids = []
        for task in all_task_list:
            if task.employee is not None and int(employee_id) in [int(n) for n in
                                                                  task.employee.replace(' ', '').split(',')]:
                with suppress(Exception):
                    folder_ids.append(task.folder.id)
        return TaskFolder.objects.filter(id__in=list(set(folder_ids))).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListEmployeeTaskFolderView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],))
        return response


class ListEmployeeTaskView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        employee_id = self.request.GET.get('employee_id')
        all_task_list = Task.objects.filter(folder__project__folder__company_id=company_id, is_deleted=False).exclude(
            employee="").exclude(employee=None).distinct()
        task_ids = [task.id for task in all_task_list if
                    int(employee_id) in [int(n) for n in task.employee.replace(' ', '').split(',')]]
        return Task.objects.filter(id__in=list(set(task_ids))).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListEmployeeTaskView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],), reverse=True)
        return response


class ListTaskFolderView(viewsets.ModelViewSet):
    serializer_class = TaskFolderSerializer

    def get_queryset(self):
        project_id = self.request.GET.get('project_id')
        if project_id == 'contacts':
            return TaskFolder.objects.filter(
                project=Project.objects.get(name='Contacts', company_id=self.request.GET.get('company_id')),
                is_deleted=False).distinct()
        else:
            return TaskFolder.objects.filter(project_id=project_id, is_deleted=False).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListTaskFolderView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],))
        return response


class ListTaskFolderBulkEmailView(viewsets.ModelViewSet):
    serializer_class = TaskFolderSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return TaskFolder.objects.filter(project__company_id=company_id, is_deleted=False).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListTaskFolderBulkEmailView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'],))
        return response


class ListTaskHeadView(viewsets.ModelViewSet):
    serializer_class = TaskHeadSerializer

    def get_queryset(self):
        project_id = self.request.GET.get('project_id')
        return TaskHead.objects.filter(project_id=project_id, user=self.request.user).distinct()


class ListTaskView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def get_queryset(self):
        project_id = self.request.GET.get('project_id')
        if project_id == 'contacts':
            return Task.objects.filter(
                project=Project.objects.get(name='Contacts', company_id=self.request.GET.get('company_id')),
                is_deleted=False).distinct()
        else:
            return Task.objects.filter(project_id=project_id, is_deleted=False).distinct()

    def list(self, request, *args, **kwargs):
        response = super(ListTaskView, self).list(request, args, kwargs)
        response.data = sorted(response.data, key=lambda k: (k['order'], k['project_id']), reverse=True)
        return response


class ListTaskDetailView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def get_queryset(self):
        task_id = self.request.GET.get('task_id')
        return Task.objects.filter(id=task_id, is_deleted=False)


class ListTaskRowView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        task_folder_id = self.request.GET.get('task_folder_id')
        return Task.objects.get_latest_by(folder_id=task_folder_id, is_deleted=False)


@login_required(login_url='/accounts/login/')
def api_create_task_folder(request):
    company_id = request.POST['company_id']
    project_id = request.POST['project_id']
    folder_from = request.POST['folder_from']
    user = request.user
    date_time = datetime.datetime.now()

    tf = TaskFolder()
    tf.name = 'New Folder'

    if folder_from == 'employee':
        try:
            misc = Project.objects.get(name='Misc.', company_id=company_id)
        except Exception:
            misc = Project.objects.create(company_id=company_id, name='Misc.', creator=user, created=date_time)
            status_preset_id = Select.objects.get(user=request.user, company_id=company_id,
                                                  status=True).status_preset.id
            status_list = StatusList.objects.filter(status_preset_id=status_preset_id)
            for status in status_list:
                st = Status()
                st.project = misc
                st.name = status.name
                st.employee = status.employee
                st.color = status.color
                st.active = status.active
                st.save()

        tf.project = misc
    else:
        tf.project_id = project_id
    tf.creator = user
    tf.created = date_time
    tf.save()

    folder = TaskFolderSerializer(instance=TaskFolder.objects.get(id=tf.id)).data

    return JsonResponse({'success': True, 'folder': folder})


@login_required(login_url='/accounts/login/')
def api_update_task_head(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    th = TaskHead.objects.get(id=data_id)

    if data_of == 'name':
        th.name = data_value

    if data_of == 'active':
        th.active = data_value

    th.updated = datetime.datetime.now()
    th.updater = request.user
    th.save()

    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_update_task_folder(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    tf = TaskFolder.objects.get(id=data_id)

    if data_of == 'name':
        tf.name = data_value

    tf.updated = datetime.datetime.now()
    tf.updater = request.user
    tf.save()

    return JsonResponse({'success': True})


@login_required(login_url='/accounts/login/')
def api_delete_task_folder(request):
    folder_id = request.POST['folder_id'] or 0
    tf = TaskFolder.objects.get(id=folder_id)
    tf.is_deleted = True
    tf.deleted = datetime.datetime.now()
    tf.deleter = request.user
    tf.save()

    Task.objects.filter(folder=tf).update(folder=None)
    return JsonResponse({'success': True})


def api_create_task_by_site(request):
    try:
        site = request.GET['site']
        if site in allowed_site_for_api:
            key = ((base64.b64decode((request.GET['key']).encode('ascii'))).decode('ascii')).split(',')
            user = User.objects.get(id=key[0], email=key[1])
            company_id = request.GET['company_id']
            project_id = request.GET['project_id']
            task_name = request.GET['task_name']
            task_email = request.GET['task_email']
            task_outreach = request.GET['task_outreach']
            task_datetime = request.GET['task_datetime']
            return create_task(request, "project", company_id, project_id, 0, task_name, task_email, user.id, user,
                               task_datetime, task_outreach, site)
        else:
            return JsonResponse(status=404, data={'status': False, 'message': "You website not registered"})
    except Exception:
        return JsonResponse(status=404, data={'status': False, 'message': "Invalid Secret key"})


@login_required(login_url='/accounts/login/')
def api_create_task(request):
    data = json.loads(request.POST['data_value'])
    user = request.user
    task_from = data['task_from']
    company_id = data['company_id']
    project_id = data['project_id']
    folder_id = data['folder_id']
    employee_id = data['employee_id']
    task_datetime = data['task_datetime']

    return create_task(request, task_from, company_id, project_id, folder_id, "", "", employee_id, user, task_datetime,
                       "", 'productionflow.io')


def create_task(request, task_from, company_id, project_id, folder_id, task_name, task_email, employee_id, user,
                task_datetime, task_outreach, site):
    calendar_data = []
    date_time = datetime.datetime.now()
    task = Task()
    if task_from == 'employee':
        misc = Project.objects.get(name='Misc.', company_id=company_id)
        task.project = misc
        task.employee = f"{employee_id}"
    else:
        task.project_id = project_id
        task.employee = f"{Employee.objects.get(user_id=user.id, company_id=company_id).id}"

    if folder_id != 0:
        task.folder_id = folder_id

    task.name = 'New Task' if task_name == "" else task_name
    if task_email != "":
        task.email = task_email

    if task_outreach != "":
        task.outreach = task_outreach

    task.notes = ''
    task.notes1 = ''
    task.notes2 = ''
    task.status = Status.objects.filter(project=task.project).first()
    task.creator = user
    task.created = date_time
    task.save()

    if task_datetime != '':
        calendar = Calendar()
        calendar.company_id = company_id
        calendar.task = task
        calendar.event_on = task_datetime
        calendar.creator = user
        calendar.created = date_time
        calendar.save()
        calendar_data = [CalendarSerializer(instance=Calendar.objects.get(id=calendar.id)).data]

    task_data = TaskSerializer(instance=Task.objects.get(id=task.id, is_deleted=False), context={'user': user}).data
    return JsonResponse(status=200, data={
        'success': True, 'message': 'Success', 'task': task_data, 'calendar': calendar_data
    })


@login_required(login_url='/accounts/login/')
def api_update_task(request):
    data_id = request.POST['data_id'] or 0
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    t = Task.objects.get(id=data_id)

    if data_of == 'folder':
        if (int(data_value) == 0):
            t.folder = None
        else:
            t.folder_id = data_value

    elif data_of == 'employee':
        t.employee = ''.join(i for i in data_value if i.isdigit() or i in ',\\')

    elif data_of == 'name':
        t.name = data_value

    elif data_of == 'project':
        t.project_id = data_value

    elif data_of == 'notes':
        t.notes = data_value

    elif data_of == 'email':
        t.email = data_value

    elif data_of == 'notes1':
        t.notes1 = data_value

    elif data_of == 'notes2':
        t.notes2 = data_value

    elif data_of == 'notes3':
        t.notes3 = data_value

    elif data_of == 'notes4':
        t.notes4 = data_value

    elif data_of == 'notes5':
        t.notes5 = data_value

    elif data_of == 'notes6':
        t.notes6 = data_value

    elif data_of == 'notes7':
        t.notes7 = data_value

    elif data_of == 'notes8':
        t.notes8 = data_value

    elif data_of == 'notes9':
        t.notes9 = data_value

    elif data_of == 'status':
        t.status_id = data_value

    elif data_of == 'shift':
        t.shift = data_value

    elif data_of == 'outreach':
        t.outreach = data_value

    t.updated = datetime.datetime.now()
    t.updater = request.user
    t.save()

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


@login_required(login_url='/accounts/login/')
def api_delete_task(request):
    selected_task_list = request.POST['selected_task_list'].split(',')
    if '' in selected_task_list:
        del selected_task_list[selected_task_list.index("")]

    for task_id in selected_task_list:
        t = Task.objects.get(id=task_id)
        t.is_deleted = True
        t.deleted = datetime.datetime.now()
        t.deleter = request.user
        t.save()

        with suppress(Exception):
            event = Calendar.objects.get(task_id=task_id)
            event.is_deleted = True
            event.deleted = datetime.datetime.now()
            event.deleter = request.user
            event.save()
    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})

@login_required(login_url='/accounts/login/')
def api_bulk_task(request):
    task_ids = [ int(x) for x in request.POST['data_value'].split(',') ]
    data_of = request.POST['data_of']

    for task_id in task_ids:
        task = Task.objects.get(id=task_id)

        if data_of == 'move':
            project_id = int(request.POST['project_id'])
            folder_id =  int(request.POST['folder_id'])

            task.project_id = project_id
            if folder_id == 0:
                task.folder_id = None
            else:
                task.folder_id = folder_id

        elif data_of == 'delete':
            task.deleted = datetime.datetime.now()
            task.deleter = request.user
            task.is_deleted = True

        task.save()



    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})

"""  End Task """

"""  Start Sorting """


@login_required(login_url='/accounts/login/')
def api_update_sorting(request):
    data_of = request.POST['data_of']
    data_value = json.loads(request.POST['data_value'])
    user = request.user

    if data_of == 'project_folder':
        for folder in data_value:
            try:
                sort = Sort.objects.get(user=user, project_folder_id=folder['folder_id'])
                sort.order = folder['order']
                sort.save()

            except Exception:
                sort = Sort()
                sort.order = folder['order']
                sort.project_folder_id = folder['folder_id']
                sort.user = request.user
                sort.save()

    elif data_of == 'project':
        for project in data_value:
            try:
                sort = Sort.objects.get(user=user, project_id=project['project_id'])
                sort.order = project['order']
                sort.save()

            except Exception:
                sort = Sort()
                sort.order = project['order']
                sort.project_id = project['project_id']
                sort.user = request.user
                sort.save()

    elif data_of == 'task_folder':
        for folder in data_value:
            try:
                sort = Sort.objects.get(user=user, task_folder_id=folder['folder_id'])
                sort.order = folder['order']
                sort.save()

            except Exception:
                sort = Sort()
                sort.order = folder['order']
                sort.task_folder_id = folder['folder_id']
                sort.user = request.user
                sort.save()

    elif data_of == 'task':
        for task in data_value:
            try:
                sort = Sort.objects.get(user=user, task_id=task['task_id'])
                sort.order = task['order']
                sort.save()

            except Exception:
                sort = Sort()
                sort.order = task['order']
                sort.task_id = task['task_id']
                sort.user = request.user
                sort.save()

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


@login_required(login_url='/accounts/login/')
def api_create_task_comment(request):
    task_id = request.POST['task_id']
    comment = request.POST['comment']

    tc = TaskComment()
    tc.task_id = task_id
    tc.comment = comment
    tc.time = datetime.datetime.now().time().strftime('%H:%M:%S')
    tc.creator = request.user
    tc.created = datetime.datetime.now()
    tc.save()

    item = {'id': tc.id, 'time': tc.time, 'comment': tc.comment, 'creator': tc.creator.first_name}
    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'item': item})


"""  End Sorting """

"""  Start Video Version """


class ListVideoCommentView(viewsets.ModelViewSet):
    serializer_class = VideoCommentSerializer

    def get_queryset(self):
        file_id = self.request.GET.get('file_id')
        return VideoComment.objects.filter(task_video_id=file_id, is_deleted=False).order_by('-created')


@login_required(login_url='/accounts/login/')
def api_create_video_comment(request):
    file_id = request.POST['file_id']
    comment = request.POST['comment']
    comment_time = request.POST['comment_time'].replace(' ', '')
    print(comment_time)

    vc = VideoComment()
    if file_id != 0:
        vc.task_video_id = file_id
    vc.time = comment_time
    vc.comment = comment
    vc.creator = request.user
    vc.created = datetime.datetime.now()
    vc.save()

    item = {'id': vc.id, 'time': vc.time, 'comment': vc.comment, 'creator': vc.creator.first_name}
    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'item': item})

@login_required(login_url='/accounts/login/')
def api_update_video_comment(request):
    file_id = request.POST['data_id']
    data_of = request.POST['data_of']
    data_value = request.POST['data_value']

    vc = VideoComment.objects.get(id=file_id)

    if data_of == 'active':
        vc.active = data_value


    vc.updated = datetime.datetime.now()
    vc.updater = request.user
    vc.save()


    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})

@login_required(login_url='/accounts/login/')
def api_upload_video(request):
    task_id = request.POST['task_id']
    date_time = datetime.datetime.now()
    task_video_id = None
    if request.method == 'POST':
        user = request.user
        if file := request.FILES.getlist('files[]', None)[0]:
            tv = TaskVideo()
            tv.task_id = task_id
            tv.file = file
            tv.creator = user
            tv.created = date_time
            tv.save()
            task_video_id = tv.id
    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'task_video_id': task_video_id})

@login_required(login_url='/accounts/login/')
def api_create_video_thumbnail(request):
    agent_os = httpagentparser.detect(request.META["HTTP_USER_AGENT"])["os"]['name']

    file_id = request.POST['file_id']
    tv = TaskVideo.objects.get(id=file_id)
    tv.thumbnail.name = f"{str(tv.file.name).rsplit('.', 1)[0]}.jpeg"
    tv.save()

    file_path = tv.file.path

    if agent_os == 'Windows':
        vcap = cv2.VideoCapture(file_path)
        res, im_ar = vcap.read()
        while im_ar.mean() < res:
            res, im_ar = vcap.read()
        im_ar = cv2.resize(im_ar, (1920, 1080), 0, 0, cv2.INTER_LINEAR)
        cv2.imwrite(f"{str(file_path).rsplit('.', 1)[0]}.jpeg", im_ar)
    else:
        subprocess.call(['ffmpeg', '-i', file_path, '-ss', '00:00:00.000', '-vframes', '1', f"{str(file_path).rsplit('.', 1)[0]}.jpeg"])

    data = {
        'image_url': tv.thumbnail.url,
        'file_url': tv.file.url,
        'file_id': tv.id
    }
    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'data':data})


"""  End Video Version """

"""  Start Calendar """
class ListCalendarView(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        return Calendar.objects.filter(company_id=company_id, is_deleted=False).order_by('-created')


@login_required(login_url='/accounts/login/')
def api_update_calendar(request):
    company_id = request.POST['company_id']
    task_id = request.POST['task_id'] or 0
    calendar_id = request.POST['calendar_id'] or 0
    task_datetime = request.POST['task_datetime'] or ''

    try:
        t = Calendar.objects.get(id=calendar_id)
        t.event_on = task_datetime
        t.updated = datetime.datetime.now()
        t.updater = request.user
        t.is_deleted = False
        t.save()
        calendar_id = t.id

    except Exception:
        try:
            t = Calendar.objects.get(task_id=task_id)
            t.event_on = task_datetime
            t.updated = datetime.datetime.now()
            t.updater = request.user
            t.is_deleted = False
            t.save()
            calendar_id = t.id

        except Exception:
            calendar = Calendar()
            calendar.company_id = company_id
            calendar.task_id = task_id
            calendar.event_on = task_datetime
            calendar.creator = request.user
            calendar.created = datetime.datetime.now()
            calendar.save()
            calendar_id = calendar.id

    calendar_data = [CalendarSerializer(instance=Calendar.objects.get(id=calendar_id)).data]

    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'calendar': calendar_data})


@login_required(login_url='/accounts/login/')
def api_update_calendar_events(request):
    move = request.POST['move']
    company_id = request.POST['company_id']
    if move == 'left':
        events = Calendar.objects.filter(company_id=company_id).exclude(task__status__name="Done", is_deleted=False)
        for event in events:
            if not event.task.shift:
                event.event_on = event.event_on - timedelta(hours=24)
                event.save()


    elif move == 'right':
        events = Calendar.objects.filter(company_id=company_id).exclude(task__status__name="Done", is_deleted=False)
        for event in events:
            if not event.task.shift:
                event.event_on = event.event_on + timedelta(hours=24)
                event.save()

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


@login_required(login_url='/accounts/login/')
def api_delete_calendar(request):
    calendar_id = request.POST['calendar_id'] or 0
    t = Calendar.objects.get(id=calendar_id)
    t.is_deleted = True
    t.deleted = datetime.datetime.now()
    t.deleter = request.user
    t.save()

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


class ListContactsCalendarView(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        project_id = self.request.GET.get('project_id')
        return Calendar.objects.filter(task__project_id=project_id, is_deleted=False).order_by('-created')


class ListProjectCalendarView(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        project_id = self.request.GET.get('project_id')
        return Calendar.objects.filter(task__project_id=project_id, is_deleted=False).order_by('-created')


class ListEmployeeCalendarView(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        employee_id = self.request.GET.get('employee_id')

        employee_list = []
        task_ids = Calendar.objects.filter(company_id=company_id, is_deleted=False).values_list('task_id', flat=True)
        for task_id in task_ids:
            employees = Task.objects.filter(id=task_id).values_list('employee', flat=True)[0]
            if employees is not None and employee_id in employees.split(','):
                employee_list.append(task_id)

        return Calendar.objects.filter(company_id=company_id, task_id__in=employee_list, is_deleted=False).order_by(
            '-created')


"""  End Sorting """

"""  Start Active """


@login_required(login_url='/accounts/login/')
def api_select(request):
    data_of = request.POST['data_of']
    company_id = request.POST['company_id']
    user = request.user
    success = False

    try:
        select = Select.objects.get(user=user, company_id=company_id)

    except Exception:
        select = Select()
        select.user = user
        select.company_id = company_id
        select.status_preset = StatusPreset.objects.get(company_id=company_id)

    if data_of == 'company':
        success = True
        Select.objects.filter(user=user).update(status=False)
        select.status = True

    elif data_of == 'employee':
        success = True
        select.project = None
        select.employee_id = request.POST['employee_id']

    elif data_of == 'project':
        success = True
        select.employee = None
        select.project_id = request.POST['project_id']

    elif data_of == 'task':
        success = True
        select.task_id = request.POST['task_id']

    elif data_of == 'tab':
        success = True
        select.tab = request.POST['tab']

    select.save()

    return JsonResponse({'success': success})


"""  End Active """

"""  Start User Account """


class ListUserAccountView(viewsets.ModelViewSet):
    serializer_class = UserAccountSerializer

    def get_queryset(self):
        return UserAccount.objects.filter(user=self.request.user)


@login_required(login_url='/accounts/login/')
def api_user_account_key(request):
    key = UserAccount.objects.get(user=request.user).key
    # decoded = (cryptocode.decrypt(key, 'P%F/Key_Genrator!')).split(',')
    return JsonResponse({'key': key})


@login_required(login_url='/accounts/login/')
def api_update_user_account(request):
    data_of = request.POST['data_of'] or ''
    data_value = request.POST['data_value'] or ''

    ua = UserAccount.objects.get(
        user=request.user,
        creator=request.user,
    )
    if data_of == 'notes':
        ua.notes = data_value

    elif data_of == 'matrics_link':
        ua.matrics_link = data_value

    elif data_of == 'calendar_link':
        ua.calendar_link = data_value

    elif data_of == 'username':
        ua.username = data_value

    elif data_of == 'password':
        ua.password = data_value

    elif data_of == 'server':
        ua.server = data_value

    elif data_of == 'port':
        ua.port = data_value

    ua.save()

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


@login_required(login_url='/accounts/login/')
def api_create_user_review(request):
    review = request.POST['review']
    review1 = request.POST['review1']
    ua = UserAccount.objects.get(
        user=request.user,
        creator=request.user,
    )
    ua.user = request.user
    ua.review = review
    ua.review1 = review1
    ua.save()
    # create_company(request)
    api_checkout(request)

    return JsonResponse(status=200, data={'success': True, 'message': 'Success'})


"""  End User Notes """

"""  Start Payment """


@login_required(login_url='/accounts/login/')
def checkout(request):
    template_name = 'payment/checkout.html'
    context = {
        'title': "Checkout"
    }
    return render(request, template_name, context)


def load_dot_env():
    """ Helper funtion that parses and loads local .env file. STRIPE_SECRET_KEY=sk_... """
    with suppress(FileNotFoundError):
        with open('.env', encoding='utf-8') as dot_env_file:
            for line in iter(lambda: dot_env_file.readline().strip(), ''):
                if not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value


"""  End Payment """

"""  Start Tab """


def api_show_tab(request):
    try:
        company_id = request.POST['company_id']
        tab = Select.objects.get(user=request.user, company_id=company_id, status=True).tab
    except Exception:
        tab = 'tab_calendar'

    return JsonResponse(status=200, data={'success': True, 'message': 'Success', 'tab': tab})


"""  End Tab """



""" Start CSV Truecolor"""
@login_required(login_url='/accounts/login/')
def api_create_folder_tasks(request):
    task_info = json.loads(request.POST['task_info'])
    company_id = request.POST['company_id']
    project_id = request.POST['project_id']
    folder_from = request.POST['folder_from']
    employee_id = request.POST['employee_id']
    task_datetime = request.POST['task_datetime']
    user = request.user

    tf = TaskFolder()
    tf.name = task_info[0]["FolderName"]
    del task_info[0]
    tf.created = datetime.datetime.now()
    tf.creator = user

    if folder_from == 'employee':
        try:
            misc = Project.objects.get(name='Misc.', company_id=company_id)
        except Exception:
            misc = Project.objects.create(company_id=company_id, name='Misc.', creator=user, created=task_datetime)
            status_preset_id = Select.objects.get(user=request.user, company_id=company_id, status=True).status_preset.id
            status_list = StatusList.objects.filter(
                status_preset_id=status_preset_id)
            for status in status_list:
                st = Status()
                st.project = misc
                st.name = status.name
                st.employee = status.employee
                st.color = status.color
                st.active = status.active
                st.save()

        tf.project = misc
    else:
        tf.project_id = project_id
    tf.save()
    folder = TaskFolderSerializer(
        instance=TaskFolder.objects.get(id=tf.id)).data

    # create tasks of folder
    print(task_info)
    task_datas = []
    for folder_task in task_info:
        calendar_data = []
        task = Task()
        task.name = folder_task['TaskName']
        task.email = folder_task['Email']
        task.notes = folder_task['Notes']
        task.notes1 = folder_task['Notes1']
        task.notes2 = folder_task['Notes2']
        task.notes3 = folder_task['Notes3']
        task.notes4 = folder_task['Notes4']
        task.notes5 = folder_task['Notes5']
        task.notes6 = folder_task['Notes6']
        task.notes7 = folder_task['Notes7']
        task.notes8 = folder_task['Notes8']
        task.notes9 = folder_task['Notes9']
        task.outreach = folder_task['Outreach']
        task.folder_id = tf.id
        task.creator = user
        task.created = datetime.datetime.now()
        if folder_from == 'employee':
            misc = Project.objects.get(name='Misc.', company_id=company_id)
            task.project = misc
            task.employee = f"{employee_id}"
        else:
            task.project_id = project_id
            task.employee = f"{Employee.objects.get(user_id=user.id, company_id=company_id).id}"
        task.status = Status.objects.filter(
            project=task.project, name=folder_task["Status"]).first()
        task.save()

        if task_datetime != '':
            calendar = Calendar()
            calendar.company_id = company_id
            calendar.task = task
            calendar.event_on = task_datetime
            calendar.creator = user
            calendar.created = datetime.datetime.now()
            calendar.save()
            calendar_data = [CalendarSerializer(
                instance=Calendar.objects.get(id=calendar.id)).data]

        task_data = TaskSerializer(instance=Task.objects.get(
            id=task.id, is_deleted=False), context={'user': user}).data
        task_datas.append(task_data)

    return JsonResponse({
        'success': True,
        'folder': folder,
        'message': 'Success',
        'task': task_datas,
        'calendar': calendar_data
    })
def api_create_imported_task(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data_value'])
        user = request.user
        task_from = data['task_from']
        company_id = data['company_id']
        project_id = data['project_id']
        folder_id = data['folder_id']
        employee_id = data['employee_id']
        task_datetime = data['task_datetime']
        taskData = data['task']
        return create_imported_task(request, task_from, company_id, project_id, folder_id, employee_id, user, task_datetime, "", taskData)
def create_imported_task(request, task_from, company_id, project_id, folder_id, employee_id, user, task_datetime, task_outreach, taskData):
    task = Task()
    calendar_data = []
    date_time = datetime.datetime.now()
    if task_from == 'employee':
        misc = Project.objects.get(name='Misc.', company_id=company_id)
        task.project = misc
        task.employee = f"{employee_id}"
    else:
        task.project_id = project_id
        task.employee = f"{Employee.objects.get(user_id=user.id, company_id=company_id).id}"

    if task_outreach != "":
        task.outreach = taskData['Outreach']
    task.name = taskData['TaskName']
    task.status = Status.objects.filter(
        project=task.project, name=taskData["Status"]).first()

    task.email = taskData['Email']
    task.notes = taskData['Notes']
    task.notes1 = taskData['Notes1']
    task.notes2 = taskData['Notes2']
    task.notes3 = taskData['Notes3']
    task.notes4 = taskData['Notes4']
    task.notes5 = taskData['Notes5']
    task.notes6 = taskData['Notes6']
    task.notes7 = taskData['Notes7']
    task.notes8 = taskData['Notes8']
    task.notes9 = taskData['Notes9']
    task.creator = user
    task.created = date_time
    task.save()

    if task_datetime != '':
        calendar = Calendar()
        calendar.company_id = company_id
        calendar.task = task
        calendar.event_on = task_datetime
        calendar.creator = user
        calendar.created = date_time
        calendar.save()
        calendar_data = [CalendarSerializer(
            instance=Calendar.objects.get(id=calendar.id)).data]
    task_data = TaskSerializer(instance=Task.objects.get(
        id=task.id, is_deleted=False), context={'user': user}).data
    return JsonResponse(
        status=200,
        data={'success': True, 'message': 'Success',
              'task': task_data, 'calendar': calendar_data}
    )
""" End CSV Feature Import Truecolor"""

""" Start CSV Feature Export Truecolor"""
@login_required(login_url='/accounts/login/')
def api_export_csv(request):
    if (request.method == "POST"):
        project_id=request.POST["project_id"]
        id = Status.objects.filter(project_id=project_id).first().id
        print(id)
        return JsonResponse({'id': id})
""" End CSV Truecolor"""


def api_update(request):
    """ Start Add Contacts and Mics. """
    # Project.objects.filter(name='Mics.').delete()
    #
    # for company in Company.objects.all():
    #     try:
    #         Project.objects.get(company=company, name='Contacts')
    #     except:
    #         p = Project()
    #         p.name = 'Contacts'
    #         p.contacts = True
    #         p.company = company
    #         p.creator = company.creator
    #         p.created = company.created
    #         p.save()
    #
    # for company in Company.objects.all():
    #     try:
    #         Project.objects.get(company=company, name='Misc.')
    #     except:
    #         p = Project()
    #         p.name = 'Misc.'
    #         p.contacts = False
    #         p.company = company
    #         p.creator = company.creator
    #         p.created = company.created
    #         p.save()
    """ End Add Contacts and Mics. """

    # print('true', len(Project.objects.filter(contacts=True)))
    # print('cont', len(Project.objects.filter(name='Contacts')))
    # print('comp', len(Company.objects.filter(is_deleted=False)))
    # print('sts pre', len(StatusPreset.objects.filter(is_deleted=False)))
    #
    # print('ext', len(Project.objects.filter(contacts=True).exclude(name='Contacts')))
    # Company.objects.filter(is_deleted=True).delete()
    # Project.objects.filter(is_deleted=True).delete()
    # ProjectFolder.objects.filter(is_deleted=True).delete()
    # Project.objects.filter(contacts=True).delete()
    # Select.objects.all().delete()

    """ Start Select """
    # count = 0
    # companies = Company.objects.all()
    # print(len(companies))
    # for company in companies:
    #     employees = Employee.objects.filter(company=company)
    #     if len(employees) > 0:
    #         for employee in employees:
    #             select = Select()
    #             select.user = employee.user
    #             select.company = company
    #             select.project = Project.objects.filter(company=company).first()
    #             select.status_preset = StatusPreset.objects.get(company=company)
    #             select.tab = '#tab_calendar'
    #             select.status = False
    #             select.save()
    #             count += 1
    #     else:
    #         company.delete()
    #     print(f'company: {company.name} - Total: {len(Employee.objects.filter(company=company))}')
    # print(count)
    #
    # for user in User.objects.all():
    #     sels = Select.objects.filter(user=user)
    #     for ind, sel in enumerate(sels):
    #         if ind == 0:
    #             sel.status=True
    #             sel.save()

    """ End Select """

    # for company in Company.objects.all():
    #     ps = Project.objects.filter(company=company, contacts=True)
    #     for p in ps:
    #         if p.name != 'Contacts':
    #             p.delete()
    # TaskHead.objects.filter(name='Email').update(active=False)

    """ Start Add Contacts Project """
    #
    # for sel in Select.objects.filter(status_preset__isnull=True):
    #     sel.status_preset = StatusPreset.objects.filter(company=sel.company).first()
    #     sel.save()
    #
    # Project.objects.filter(name='Contacts').delete()
    # print(len(Project.objects.filter(name='Contacts')))
    #
    # for company in Company.objects.all():
    #     api_create_project(request, company.id, 0, company.creator)
    #     print(Select.objects.filter(company_id=company.id, user=company.creator).first().status_preset.id)
    #
    # print(len(Project.objects.filter(name='Contacts')))

    # for ua in UserAccount.objects.all():
    #     ua.key = (base64.b64encode((f'{ua.user.id},{ua.user.email}').encode('ascii'))).decode('ascii')
    #     ua.save()
    """ End Add Contacts Project """

    """ remove employee with no user"""
    # employees = Employee.objects.filter(user__isnull=True)
    # for employee in employees:
    #     employee.delete()
    """ remove employee with no user"""

    """ Start task Head"""

    # TaskHead.objects.all().delete()
    # for employee in Employee.objects.all().order_by('user'):
    #     if employee.user is None:
    #         employee.delete()
    #     else:
    #         user_id = employee.user.id
    #         for project in Project.objects.filter(company=employee.company):
    #             for order, col in enumerate(task_columns):
    #                 th, created = TaskHead.objects.get_or_create(user_id=user_id, order=order, project=project, name=col)
    #                 if col in ['Email', 'Notes', 'Outreach']:
    #                     th.active = False
    #                 th.save()
    """ End task Head"""

    # for company in Company.objects.all():
    #     if status_preset_id := list(Select.objects.filter(user=company.creator, company=company).values_list('status_preset_id', flat=True)):
    #         status_preset_id = status_preset_id[0]
    #         status_list = StatusList.objects.filter(status_preset_id=status_preset_id)
    #         misc, created = Project.objects.get_or_create(company=company, name='Misc.')
    #         misc.creator = company.creator
    #         misc.created = company.created
    #         misc.save()

    #         for status in status_list:
    #             st = Status()
    #             st.project = misc
    #             st.name = status.name
    #             st.employee = status.employee
    #             st.color = status.color
    #             st.active = status.active
    #             st.save()

    # for employee in Employee.objects.all().order_by('user').distinct():
    #     select = Select()
    #     select.user = employee.employee
    #     select.company = employee.company
    #     select.user = employee
    #     select.status_preset = StatusPreset.objects.get(company=employee.company)
    #     select.status = False
    #     select.save()
    #
    # for sel in Select.objects.all().order_by('user_id').distinct('user'):
    #     sel.status = True
    #     sel.save()
    #
    # for row in Employee.objects.all().reverse():
    #     if Employee.objects.filter(id=row.id).count() > 1:
    #         row.delete()
    #
    # for row in Select.objects.all().reverse():
    #     if Select.objects.filter(user=row.user, company=row.company).count() > 1:
    #         row.delete()
    # for row in TaskHead.objects.all().reverse():
    #     if TaskHead.objects.filter(user=row.user, order=row.order, project=row.project, name=row.name).count() > 1:
    #         row.delete()

    # TaskHead.objects.filter(name='Outreach').update(active=False)
    return JsonResponse({'success': []})