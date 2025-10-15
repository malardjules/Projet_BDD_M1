from django.contrib import admin
from .models import Employee, Mailbox, Conversation, Word, Mail

admin.site.register(Employee)
admin.site.register(Mailbox)
admin.site.register(Conversation)
admin.site.register(Word)
admin.site.register(Mail)
