from django.contrib import admin
from .models import BoardItem, Contact, CustomUser, Subtask

@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the BoardItem model.
    """

    list_display = ('id', 'title', 'category', 'created_at', 'author')
    search_fields = ('title', 'description', 'category', 'author__username')
    filter_horizontal = ('assignedTo',)

    def get_assigned_users(self, obj):
        """
        Display assigned users for a BoardItem.
            Args:
                obj (BoardItem): The BoardItem instance.
            Returns:
                str: A comma-separated list of assigned users' names.
        """

        return ", ".join([f"{user.first_name} {user.last_name}" for user in obj.assignedTo.all()])
    get_assigned_users.short_description = 'Assigned To'


admin.site.register(Contact)
"""
Admin interface configuration for the Contact model.
"""

@admin.register(CustomUser)
class CustomUserItemAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the CustomUser model.
    """

    list_display = ('email', 'first_name', 'last_name', 'username', 'date_joined')


@admin.register(Subtask)
class SubtasksAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Subtask model.
    """

    list_display = ('title', 'is_checked')