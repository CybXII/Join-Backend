from rest_framework import serializers
from .models import BoardItem, Subtask, CustomUser

class SubtaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Subtask model.
    Serializes 'id', 'title', and 'is_checked' fields.
    """
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'is_checked']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    Serializes 'first_name', 'last_name', and 'id' fields.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'id']


class BoardItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BoardItem model.
    Includes nested serialization for assigned users and subtasks.
    Formats 'due_date' as 'YYYY-MM-DD'.
    """
    
    assignedTo = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all(), required=False)
    subtasks = SubtaskSerializer(many=True, required=False)
    due_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = BoardItem
        fields = [
            'id',
            'title',
            'description',
            'assignedTo',
            'due_date',
            'prio',
            'category',
            'task_status',
            'created_at',
            'subtasks'
        ]

    def create(self, validated_data):
        """
        Creates a new BoardItem instance along with assigned users and subtasks.
            Args:
                validated_data (dict): Validated data from the request.
            Returns:
                BoardItem: The created BoardItem instance.
            Raises:
                serializers.ValidationError: If the user is not authenticated.
        """

        subtasks_data, assigned_users = self.extract_task_data(validated_data)
        author = self.get_authenticated_user()
        board_item = self.create_board_item(validated_data, author)
        self.assign_users_to_task(board_item, assigned_users)
        self.create_subtasks(board_item, subtasks_data)

        return board_item

    def extract_task_data(self, validated_data):
        """
        Extracts subtasks and assigned users from validated data.
            Args:
                validated_data (dict): The validated data containing the task information.
            Returns:
                tuple: A tuple containing subtasks data and assigned users.
        """

        subtasks_data = validated_data.pop('subtasks', [])
        assigned_users = validated_data.pop('assignedTo', [])
        return subtasks_data, assigned_users

    def get_authenticated_user(self):
        """
        Retrieves the authenticated user from the request context.
            Returns:
                CustomUser: The authenticated user.
            Raises:
                serializers.ValidationError: If the user is not authenticated.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user
        raise serializers.ValidationError("Authentication credentials were not provided.")

    def create_board_item(self, validated_data, author):
        """
        Creates a BoardItem instance with the validated data and author.
            Args:
                validated_data (dict): Validated data for creating the BoardItem.
                author (CustomUser): The user who is the author of the task.
            Returns:
                BoardItem: The created BoardItem instance.
        """

        return BoardItem.objects.create(author=author, **validated_data)

    def assign_users_to_task(self, board_item, assigned_users):
        """
        Assigns users to the created task.
            Args:
                board_item (BoardItem): The task to which users are assigned.
                assigned_users (list): List of user IDs to assign to the task.
        """

        board_item.assignedTo.set(assigned_users)

    def create_subtasks(self, board_item, subtasks_data):
        """
        Creates subtasks for the task.
            Args:
                board_item (BoardItem): The task to which subtasks are associated.
                subtasks_data (list): List of subtask data to create.
        """

        for subtask_data in subtasks_data:
            Subtask.objects.create(parent_task=board_item, **subtask_data)
