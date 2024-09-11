from django.conf import settings
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    CustomUser model extending the default Django User model.
    Username is replaced by email for authentication.
    """

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        """
        Overridden save method to set the first_name to username and 
        update username to full name before saving.
        """

        self.set_default_first_name()
        self.update_username_to_full_name()
        super().save(*args, **kwargs)

    def set_default_first_name(self):
        """Set the first_name to the username if it is not provided."""

        if not self.first_name:
            self.first_name = self.username

    def update_username_to_full_name(self):
        """Update the username field with the user's full name."""

        self.username = self.get_full_name()

    def __str__(self):
        """
        String representation of the user, showing first and last name.
        """

        return f'{self.first_name} {self.last_name}'

class Contact(models.Model):
    """
    Contact model to store information about a person.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

class BoardItem(models.Model):
    """
    Model for tasks (BoardItems) with assignment to users and optional subtasks.
    """

    CATEGORY_CHOICES = [
        ('Technical Task', 'Technical Task'),
        ('User Story', 'User Story'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, default=None)
    assignedTo = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_boarditems',
        blank=True
    )
    due_date = models.DateField()
    prio = models.IntegerField(blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=False,
        null=False
    )
    task_status = models.IntegerField(blank=False, null=False, default=0)
    position = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """
        Overridden save method to calculate position before saving the BoardItem.
        """

        self.set_default_position()
        super().save(*args, **kwargs)

    def set_default_position(self):
        """
        Set the position of the BoardItem if it is not already set.
        """

        if self.position is None:
            self.position = self.get_next_position()

    def get_next_position(self):
        """
        Retrieve the next available position for the BoardItem in its category.
            Returns:
                int: Next available position value.
        """

        max_position = BoardItem.objects.filter(category=self.category).aggregate(models.Max('position'))['position__max']
        return (max_position or 0) + 1

    @staticmethod
    def update_task_positions(tasks):
        """
        Update positions of a list of tasks sequentially.
            Args:
                tasks (QuerySet): List of tasks to update positions.
        """

        for index, task in enumerate(tasks):
            task.position = index + 1
            task.save()

    def __str__(self):
        """
        String representation of the BoardItem with its title, author, and assigned users.
            Returns:
                str: String containing the task title, author, and assigned users.
        """

        return f'({self.id}) Created by {self.author.first_name} {self.author.last_name} Title: {self.title} Assigned to: {self.get_assigned_usernames()}'

    def get_assigned_usernames(self):
        """
        Generate a string of assigned users' first and last names.
            Returns:
                str: Comma-separated list of assigned users.
        """

        return ', '.join([f"{user.first_name} {user.last_name}" for user in self.assignedTo.all()])

    @property
    def username(self):
        """
        Retrieve the username of the author of the BoardItem.
            Returns:
                str: Username of the author.
        """

        return self.author.username

class Subtask(models.Model):
    """
    Model for subtasks related to a BoardItem.
    """

    title = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)
    parent_task = models.ForeignKey(
        BoardItem,
        related_name='subtasks',
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        """
        Overridden save method to assign a new ID if the subtask is newly created.
        """

        self.assign_new_id_if_needed()
        super().save(*args, **kwargs)

    def assign_new_id_if_needed(self):
        """
        Assign a new ID if the subtask doesn't have one.
        """

        if not self.id:
            self.id = self.get_next_subtask_id()

    @staticmethod
    def get_next_subtask_id():
        """
        Get the next available subtask ID.
            Returns:
                int: Next available subtask ID.
        """

        last_subtask = Subtask.objects.last()
        return (last_subtask.id + 1) if last_subtask else 1
