using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace LMS.Domain.Entities;

public partial class Question
{
    [Key]
    public int QuestionId { get; set; }

    public int CourseId { get; set; }

    public string QuestionText { get; set; } = null!;

    public bool IsCode { get; set; }

    public bool HasMultipleAnswers { get; set; }

    [InverseProperty("Question")]
    public virtual ICollection<Choice> Choices { get; set; } = new List<Choice>();

    [ForeignKey("CourseId")]
    [InverseProperty("Questions")]
    public virtual Course Course { get; set; } = null!;

    [InverseProperty("Question")]
    public virtual ICollection<ExamQuestion> ExamQuestions { get; set; } = new List<ExamQuestion>();
}
