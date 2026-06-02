from rest_framework import serializers
from .models import Question
from option.models import Option
from option.serailizer import OptionSerializer
from subcategory.serializer import SubcategorySerializer


class QuestionSerializerSimple(serializers.ModelSerializer):
    subcategory_name = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = "__all__"

    def get_subcategory_name(self, obj: Question):
        if obj.subcategory:
            return obj.subcategory.name
        return None


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    sub_questions = serializers.SerializerMethodField()

    subcategory = SubcategorySerializer()

    class Meta:
        model = Question
        fields = [
            "id",
            "subcategory",
            "code",
            "question_type",
            "description",
            "parent_question",
            "survey",
            "options",
            "position",
            "sub_questions",
            "is_required",
            "input_type",
        ]

    def get_sub_questions(self, obj):
        children = [
            child
            for child in self.context.get("all_questions")
            if child.parent_question and child.parent_question.id == obj.id
        ]
        serializer = QuestionSerializer(children, many=True, context=self.context)
        return serializer.data

    def get_subcategory(self, obj: Question):
        if obj.subcategory:
            return obj.subcategory.name
        return None


class QuestionSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = "__all__"
