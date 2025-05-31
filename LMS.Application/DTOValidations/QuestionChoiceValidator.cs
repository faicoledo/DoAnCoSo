using FluentValidation;
using LMS.Application.DTOs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LMS.Application.DTOValidations
{
    public class QChoiceValidator : AbstractValidator<ChoiceDto>
    {
        public QChoiceValidator()
        {
            RuleFor(x => x.ChoiceText).NotEmpty().WithMessage("Choice text is required.");
        }
    }

    public class CQuestionValidator : AbstractValidator<QuestionDto>
    {
        public CQuestionValidator()
        {
            RuleFor(x => x.QuestionText).NotEmpty().WithMessage("Question text is required.");
        }
    }
}
