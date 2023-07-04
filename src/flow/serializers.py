import datetime
from rest_framework import serializers
from .models import UserAccount, Company, Select, Employee, TaskHead, ProjectFolder, Project, TaskFolder, Task, \
    TaskComment, Sort, StatusList, StatusPreset, Status, Calendar, CompanyPayment, PaymentSession, TaskVideo, \
    VideoComment


# Create your serializers here.
class FilterDeletedObjectsSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(is_deleted=False)
        return super(FilterDeletedObjectsSerializer, self).to_representation(data)


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'


class StatusPresetSerializer(serializers.ModelSerializer):
    select = serializers.SerializerMethodField()

    class Meta:
        model = StatusPreset
        fields = ['id', 'name', 'select']

    def get_select(self, obj):
        try:
            user = self.context['request'].user
            return Select.objects.get(user=user, company=obj.company, status=True).status_preset.id == obj.id
        except Exception:
            return False


class StatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusList
        fields = ['id', 'name', 'color', 'employee', 'active']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'color', 'active']


class CompanySerializer(serializers.ModelSerializer):
    select = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'owner', 'paid', 'select']

    def get_paid(self, obj):
        try:
            user = self.context['request'].user
            return bool(CompanyPayment.objects.filter(company=obj, end__gte=datetime.datetime.now().date()).exists())
        except Exception:
            return False

    def get_select(self, obj):
        try:
            user = self.context['request'].user
            return bool(Select.objects.get(user=user, company=obj, status=True))
        except Exception:
            return False

    def get_owner(self, obj):
        try:
            user = self.context['request'].user
            try:
                return bool(Company.objects.filter(id=obj.id, creator=user).exists())
            except Exception:
                return False
        except Exception:
            return False


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.first_name')
    owner = serializers.SerializerMethodField()
    select = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'user', 'owner', 'select']

    def get_select(self, employee):
        try:
            user = self.context['request'].user
            return Select.objects.get(user=user, company=employee.company, status=True).employee.id == employee.id
        except Exception:
            return False

    def get_owner(self, obj):
        try:
            user = self.context['request'].user
            try:
                if Company.objects.get(id=obj.company.id, creator=obj.user):
                    return True
            except Exception:
                return False
        except Exception:
            return False


class ProjectFolderSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()

    class Meta:
        model = ProjectFolder
        list_serializer_class = FilterDeletedObjectsSerializer
        fields = ['id', 'name', "order"]

    def get_order(self, obj):
        try:
            user = self.context['request'].user
            return Sort.objects.filter(user=user, project_folder=obj).values_list('order', flat=True)[0]
        except Exception:
            return 0


class ProjectSerializer(serializers.ModelSerializer):
    select = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Project
        list_serializer_class = FilterDeletedObjectsSerializer
        fields = ['id', 'name', 'select', 'folder', 'order', 'contacts']

    def get_order(self, obj):
        try:
            user = self.context['request'].user
            return Sort.objects.filter(user=user, project=obj).values_list('order', flat=True)[0]
        except Exception:
            return 0

    def get_select(self, obj):
        try:
            user = self.context['request'].user
            return Select.objects.get(user=user, company=obj.company, status=True).project.id == obj.id
        except Exception:
            return False


class VideoCommentSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    class Meta:
        model = VideoComment
        fields = ['id', 'time', 'comment', 'active', 'creator']

    def get_creator(self, obj):
        return obj.creator.first_name


class TaskVideoSerializer(serializers.ModelSerializer):
    comments = VideoCommentSerializer(source='videocomment_file', read_only=True, many=True)

    class Meta:
        model = TaskVideo
        # fields = ['id', 'file', 'thumbnail', 'comments']
        fields = '__all__'


class TaskCommentSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ['id', 'time', 'comment', 'creator']

    def get_creator(self, obj):
        return obj.creator.first_name


class TaskHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHead
        fields = ['id', 'name', 'user', 'project', 'order', 'active']


class TaskSerializer(serializers.ModelSerializer):
    folder_id = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    select = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    is_event = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    status_list = serializers.SerializerMethodField()
    status_id = serializers.IntegerField(source='status.id', default=0)
    project_id = serializers.IntegerField(source='project.id', default=0)
    comments = TaskCommentSerializer(source='taskcomment_task', read_only=True, many=True)
    files = TaskVideoSerializer(source='taskvideo_task', read_only=True, many=True)
    task_head = serializers.SerializerMethodField()

    class Meta:
        model = Task
        list_serializer_class = FilterDeletedObjectsSerializer
        fields = [
            'folder_id', 'project_id', 'id', 'name', 'employee', 'email', 'notes', 'notes1', 'notes2', 'notes3',
            'notes4', 'notes5', 'notes6', 'notes7', 'notes8', 'notes9', 'status_id', 'status_list', 'comments',
            'files', 'event', 'is_event', 'select', 'shift', 'outreach', 'thumbnail_url', 'order', 'task_head'
        ]

    def get_task_head(self, task):
        return TaskHeadSerializer(
            instance=TaskHead.objects.filter(project=task.project, user=self.context['user']).exclude(name='Video'),
            many=True, context=self.context
        ).data

    def get_folder_id(self, task):
        try:
            return task.folder.id
        except Exception:
            return 0

    def get_thumbnail_url(self, task):
        try:
            return TaskVideo.objects.filter(task=task).latest('id').thumbnail.url
        except Exception:
            return ''

    def get_order(self, task):
        try:
            user = self.context['request'].user
            return Sort.objects.filter(user=user, task=task).values_list('order', flat=True)[0]
        except Exception:
            return 0

    def get_status_list(self, task):
        return StatusSerializer(instance=Status.objects.filter(project=task.project, is_deleted=False), many=True,
                                context=self.context).data

    def get_select(self, task):
        try:
            user = self.context['request'].user
            return Select.objects.get(user=user, company=task.folder.project.company).task_id == task.id
        except Exception:
            return False

    def get_is_event(self, task):
        try:
            return bool(event := Calendar.objects.filter(task=task, task__is_deleted=False, is_deleted=False))
        except Exception:
            return False

    def get_event(self, task):
        try:
            return \
                Calendar.objects.filter(task=task, task__is_deleted=False, is_deleted=False).values_list('event_on')[0][
                    0]

        except Exception:
            return '0000-00-00T00-00-00'


class TaskFolderSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='project.name')
    order = serializers.SerializerMethodField()


    class Meta:
        model = TaskFolder
        fields = ['id', 'name', 'project', 'order']

    def get_order(self, folder):
        try:
            user = self.context['request'].user
            return Sort.objects.filter(user=user, task_folder=folder).values_list('order', flat=True)[0]
        except Exception:
            return 0


class EmployeeTaskFolderSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True, many=True)
    project_name = serializers.CharField(source='project.name')

    class Meta:
        model = TaskFolder
        fields = ['id', 'name', 'task', 'project_name']


class CalendarSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source='task.id')
    task = serializers.CharField(source='task.name')
    complete = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ['id', 'task_id', 'task', 'project_id', 'project_name', 'event_on', 'complete']

    def get_complete(self, calendar):
        try:
            return calendar.task.status.name == "Done"
        except Exception:
            return False

    def get_project_id(self, calendar):
        try:
            return calendar.task.project.id
        except Exception:
            return 0

    def get_project_name(self, calendar):
        try:
            return calendar.task.project.name
        except Exception:
            return ''
