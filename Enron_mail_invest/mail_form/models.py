from django.db import models

class Employee(models.Model):
    category = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=False)
    firstname = models.CharField(max_length=50, null=False)

class Mailbox(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='mailboxes')
    is_internal = models.BooleanField(default=False, null = True)

class Conversation(models.Model):
    subject = models.CharField(max_length=200, primary_key=True) #n.b: identifier une conversation par le sujet peut etre problématique en raison de l'absecence potentiel d'unicité 
    participants = models.ManyToManyField('Mailbox', related_name='conversations')
    
class Word(models.Model):
    word = models.CharField(max_length=1000, primary_key=True)

class Mail(models.Model):
    message_id = models.CharField(max_length=100, primary_key=True)
    to = models.ManyToManyField(Mailbox, related_name='received_mails')
    cc = models.ManyToManyField(Mailbox, related_name='cc_mails')
    bcc =  models.ManyToManyField(Mailbox, related_name='bcc_mails')
    sender = models.ForeignKey(Mailbox, on_delete=models.CASCADE, related_name='sent_mails',null=True)
    date = models.DateTimeField(null=True)
    subject = models.CharField(max_length=200,null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, related_name='mails')
    word=models.ManyToManyField(Word, related_name='word_mails')
    content = models.TextField(max_length=10000,null=True)
    file=models.CharField(max_length=500,null=True)

