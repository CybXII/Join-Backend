from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from join.models import BoardItem, CustomUser, Subtask
from join.serializers import BoardItemSerializer, UserSerializer, SubtaskSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import status

class BoardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Retrieves all board items and all users.

        Args:
            request (Request): The HTTP request object.
            format (str, optional): The format for the response.

        Returns:
            Response: A response containing tasks and users data.
        """
        todos = BoardItem.objects.all()
        users = CustomUser.objects.all()
        user_serializer = UserSerializer(users, many=True)
        task_serializer = BoardItemSerializer(todos, many=True)
        combined_data = {
            'tasks': task_serializer.data,
            'assignAble': user_serializer.data
        }
        return Response(combined_data)
    
    def post(self, request, *args, **kwargs):
        """
        Creates a new board item with the provided data.

        Args:
            request (Request): The HTTP request object containing the board item data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The created board item data if successful, otherwise error details.
        """
        serializer = BoardItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, *args, **kwargs):
        """
        Updates a board item with the provided data.

        Args:
            request (Request): The HTTP request object containing the update data.
            id (int): The ID of the board item to update.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: The updated board item data.
        """
        task = get_object_or_404(BoardItem, id=id)
        self.update_task_fields(task, request.data)
        self.update_assigned_users(task, request.data.get('assignedTo', []))
        self.handle_subtasks(task, request.data.get('subtasks', []))
        response_data = self.generate_response_data(task)
        return JsonResponse(response_data)

    def delete(self, request, id, *args, **kwargs):
        """
        Deletes a board item with the specified ID.

        Args:
            request (Request): The HTTP request object.
            id (int): The ID of the board item to delete.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Confirmation message if successful, otherwise error details.
        """
        task = get_object_or_404(BoardItem, id=id)
        task.delete()
        return Response({'status': 'Task deleted successfully'}, status=status.HTTP_200_OK)

    def update_fields(self, obj, data, fields):
        """
        Update specific fields of an object based on provided data.

        Args:
            obj (Model): The object to update.
            data (dict): The data containing the new field values.
            fields (list): The list of fields to update.

        Returns:
            None
        """
        for field in fields:
            setattr(obj, field, data.get(field, getattr(obj, field)))
        obj.save()

    def update_task_fields(self, task, data):
        """
        Update the main fields of a task.

        Args:
            task (BoardItem): The task object to update.
            data (dict): The data containing the new field values for the task.

        Returns:
            None
        """
        fields = ['title', 'description', 'due_date', 'prio', 'task_status', 'position', 'category']
        self.update_fields(task, data, fields)

    def update_assigned_users(self, task, assigned_users):
        """
        Update the assigned users for a task.

        Args:
            task (BoardItem): The task object to update.
            assigned_users (list): List of user IDs to assign to the task.

        Returns:
            None
        """
        if assigned_users:
            task.assignedTo.set(assigned_users)
        else:
            task.assignedTo.clear()

    def delete_removed_subtasks(self, task, incoming_subtask_ids):
        """
        Delete subtasks that are not in the incoming subtask IDs.

        Args:
            task (BoardItem): The task object to which the subtasks belong.
            incoming_subtask_ids (set): Set of subtask IDs that should remain.

        Returns:
            None
        """
        existing_subtasks = task.subtasks.all()
        for subtask in existing_subtasks:
            if subtask.id not in incoming_subtask_ids:
                subtask.delete()

    def update_or_create_subtask(self, task, subtask_data):
        """
        Update an existing subtask or create a new one based on the provided data.

        Args:
            task (BoardItem): The parent task to which the subtask belongs.
            subtask_data (dict): Data of the subtask to update or create.

        Returns:
            None
        """
        subtask_id = subtask_data.get('id')

        if subtask_id:
            try:
                subtask = Subtask.objects.get(id=subtask_id, parent_task=task)
                subtask.title = subtask_data.get('title', subtask.title)
                subtask.is_checked = subtask_data.get('is_checked', subtask.is_checked)
                subtask.save()
            except Subtask.DoesNotExist:
                Subtask.objects.create(
                    parent_task=task,
                    title=subtask_data.get('title', 'New Subtask'),
                    is_checked=subtask_data.get('is_checked', False)
                )
        else:
            Subtask.objects.create(
                parent_task=task,
                title=subtask_data.get('title', 'New Subtask'),
                is_checked=subtask_data.get('is_checked', False)
            )

    def handle_subtasks(self, task, subtasks_data):
        """
        Handle the creation, update, and deletion of subtasks.

        Args:
            task (BoardItem): The task object that contains the subtasks.
            subtasks_data (list): List of subtask data dicts.

        Returns:
            None
        """
        incoming_subtask_ids = {subtask['id'] for subtask in subtasks_data if subtask.get('id')}
        self.delete_removed_subtasks(task, incoming_subtask_ids)
        for subtask_data in subtasks_data:
            self.update_or_create_subtask(task, subtask_data)

    def generate_response_data(self, task):
        """
        Generate response data for a task.

        Args:
            task (BoardItem): The task object to serialize.

        Returns:
            dict: Serialized task data including subtasks and assigned users.
        """
        return {
            'status': 'success',
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date,
            'prio': task.prio,
            'task_status': task.task_status,
            'position': task.position,
            'category': task.category,
            'assignedTo': list(task.assignedTo.values_list('id', flat=True)),
            'subtasks': SubtaskSerializer(task.subtasks.all(), many=True).data
        }

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        Authenticates a user and returns a token if the credentials are valid.

        Args:
            request (Request): The HTTP request object containing 'username' and 'password'.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response containing the authentication token if successful.
                Otherwise, returns an error message with status 400.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token = self.get_or_create_token(user)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    def get_or_create_token(self, user):
        """
        Gets or creates an authentication token for the user.

        Args:
            user (CustomUser): The user object for whom the token is generated.

        Returns:
            str: The authentication token for the user.
        """
        token, created = Token.objects.get_or_create(user=user)
        return token.key

class SignUpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Registers a new user and returns a success message if successful.

        Args:
            request (Request): The HTTP request object containing 'username', 'lastname', 'email', and 'password'.

        Returns:
            Response: A response containing a success message if the user is created.
                Otherwise, returns an error message with status 400.
        """
        user_data = self.get_user_data(request)
        if not self.validate_user_data(user_data):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = self.create_user(user_data)
            if user:
                return Response({'answer': 'New User signed up successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'User could not be created'}, status=status.HTTP_400_BAD_REQUEST)

    def get_user_data(self, request):
        """
        Extracts user data from the request object.

        Args:
            request (Request): The HTTP request object containing user data.

        Returns:
            dict: A dictionary containing 'username', 'lastname', 'email', and 'password'.
        """
        return {
            'username': request.data.get('username'),
            'lastname': request.data.get('lastname'),
            'email': request.data.get('email'),
            'password': request.data.get('password')
        }

    def validate_user_data(self, user_data):
        """
        Validates if the user data contains all required fields.

        Args:
            user_data (dict): The user data to validate.

        Returns:
            bool: True if all required fields are present, False otherwise.
        """
        return all([user_data.get('username'), user_data.get('email'), user_data.get('password')])

    def create_user(self, user_data):
        """
        Creates a new user with the provided data.

        Args:
            user_data (dict): A dictionary containing the user's information.

        Returns:
            CustomUser: The created user object.
        """
        return CustomUser.objects.create_user(
            username=user_data['username'],
            first_name=user_data['username'],
            last_name=user_data['lastname'],
            email=user_data['email'],
            password=user_data['password']
        )
