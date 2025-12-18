"""
Assessment Serializers

Serializers cho API Quiz.
"""
from rest_framework import serializers
from decimal import Decimal


# ==================== Assignment Serializers ====================

class CreateAssignmentSerializer(serializers.Serializer):
    """Input serializer cho tạo assignment"""
    lesson_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=255, required=True)
    instructions = serializers.CharField(required=False, allow_blank=True)
    start_at = serializers.DateTimeField(required=False)
    end_at = serializers.DateTimeField(required=False)
    time_limit = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    attempts_allowed = serializers.IntegerField(min_value=1, default=1)
    max_score = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100'))
    shuffle_questions = serializers.BooleanField(default=False)
    shuffle_answers = serializers.BooleanField(default=False)
    show_result = serializers.BooleanField(default=True)


class AssignmentOutputSerializer(serializers.Serializer):
    """Output serializer cho assignment"""
    id = serializers.IntegerField()
    lesson_id = serializers.IntegerField()
    title = serializers.CharField()
    instructions = serializers.CharField(allow_null=True)
    type = serializers.CharField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    time_limit = serializers.IntegerField(allow_null=True)
    attempts_allowed = serializers.IntegerField()
    max_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    shuffle_questions = serializers.BooleanField()
    shuffle_answers = serializers.BooleanField()
    show_result = serializers.BooleanField()
    question_count = serializers.IntegerField()
    is_open = serializers.BooleanField()
    created_at = serializers.DateTimeField()


# ==================== Question Serializers ====================

class CreateQuestionSerializer(serializers.Serializer):
    """Input serializer cho tạo câu hỏi"""
    text = serializers.CharField(required=True)
    option_a = serializers.CharField(max_length=500, required=True)
    option_b = serializers.CharField(max_length=500, required=True)
    option_c = serializers.CharField(max_length=500, required=True)
    option_d = serializers.CharField(max_length=500, required=True)
    correct_answer = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'], required=True)
    explanation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    points = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1'))
    order = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class UpdateQuestionSerializer(serializers.Serializer):
    """Input serializer cho cập nhật câu hỏi"""
    text = serializers.CharField(required=False)
    option_a = serializers.CharField(max_length=500, required=False)
    option_b = serializers.CharField(max_length=500, required=False)
    option_c = serializers.CharField(max_length=500, required=False)
    option_d = serializers.CharField(max_length=500, required=False)
    correct_answer = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'], required=False)
    explanation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    points = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    order = serializers.IntegerField(min_value=1, required=False)


class QuestionOutputSerializer(serializers.Serializer):
    """Output serializer cho câu hỏi (giáo viên xem)"""
    id = serializers.IntegerField()
    assignment_id = serializers.IntegerField()
    text = serializers.CharField()
    option_a = serializers.CharField()
    option_b = serializers.CharField()
    option_c = serializers.CharField()
    option_d = serializers.CharField()
    correct_answer = serializers.CharField()
    explanation = serializers.CharField(allow_null=True)
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    order = serializers.IntegerField()


class QuestionForStudentSerializer(serializers.Serializer):
    """Output serializer cho câu hỏi (học viên làm bài - không có đáp án đúng)"""
    id = serializers.IntegerField()
    order = serializers.IntegerField()
    text = serializers.CharField()
    option_a = serializers.CharField()
    option_b = serializers.CharField()
    option_c = serializers.CharField()
    option_d = serializers.CharField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)


# ==================== Import Excel Serializers ====================

class ImportExcelResultSerializer(serializers.Serializer):
    """Output serializer cho kết quả import"""
    total_rows = serializers.IntegerField()
    success_count = serializers.IntegerField()
    error_rows = serializers.ListField(child=serializers.DictField())


# ==================== Attempt Serializers ====================

class StartAttemptOutputSerializer(serializers.Serializer):
    """Output serializer khi bắt đầu làm bài"""
    attempt_id = serializers.IntegerField()
    assignment_title = serializers.CharField()
    time_limit = serializers.IntegerField(allow_null=True)
    started_at = serializers.DateTimeField()
    questions = QuestionForStudentSerializer(many=True)


class AnswerInputSerializer(serializers.Serializer):
    """Input serializer cho mỗi câu trả lời"""
    question_id = serializers.IntegerField()
    chosen_answer = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


class SubmitAttemptSerializer(serializers.Serializer):
    """Input serializer khi nộp bài"""
    answers = AnswerInputSerializer(many=True)


class SubmitAttemptOutputSerializer(serializers.Serializer):
    """Output serializer sau khi nộp bài"""
    attempt_id = serializers.IntegerField()
    submitted_at = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_questions = serializers.IntegerField()
    correct_count = serializers.IntegerField()


class QuestionResultSerializer(serializers.Serializer):
    """Output serializer cho kết quả từng câu"""
    question_id = serializers.IntegerField()
    order = serializers.IntegerField()
    text = serializers.CharField()
    chosen_answer = serializers.CharField(allow_null=True)
    correct_answer = serializers.CharField(allow_null=True)
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField(allow_null=True)


class AttemptResultOutputSerializer(serializers.Serializer):
    """Output serializer cho kết quả bài làm"""
    attempt_id = serializers.IntegerField()
    assignment_title = serializers.CharField()
    started_at = serializers.DateTimeField()
    submitted_at = serializers.DateTimeField(allow_null=True)
    score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    total_questions = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    questions = QuestionResultSerializer(many=True)




