from django.db import models
from django.contrib.auth  import get_user_model

# Create your models here.
# analytics/models.py

User=get_user_model()

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20)  # "user" | "assistant"
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ToolCall(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="tool_calls"
    )
    tool_name = models.CharField(max_length=100)
    input_json = models.JSONField()
    result_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class FlatResponse(models.Model):
    response_id = models.IntegerField(primary_key=True)
    visit_id = models.IntegerField()
    campus = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    survey_id = models.IntegerField()
    question_id = models.IntegerField()
    question_code = models.CharField(max_length=100)
    question_description = models.CharField(max_length=500, null=True)
    question_type= models.CharField(max_length=100)
    parent_question_id= models.IntegerField()
    parent_question_code = models.CharField(max_length=100, null=True)
    parent_question_description = models.CharField(max_length=500, null=True)
    subcategory = models.CharField(max_length=200),
    category = models.CharField(max_length=200),
    answer_type = models.CharField(max_length=5),
    answer_value = models.CharField(max_length=500, null=True)

    class Meta:
        managed = False
        db_table = "flat_responses"
