using FluentValidation;
using LMS.Application.DTOs;
using LMS.Application.Interfaces.Courses;

namespace LMS.Application.DTOValidations
{
    public class CreateCourseValidator : AbstractValidator<CreateCourseDto>
    {
        public CreateCourseValidator(ICourseRepository repository)
        {
            RuleFor(x => x.Title)
                .NotNull()
                .NotEmpty()
                .MaximumLength(100)
                .MaximumLength(100)
                .MustAsync(async (title, cancellation) =>
                    !await repository.IsTitleDuplicatedAsync(title))
                .WithMessage("The course title must be unique.");

            RuleFor(x => x.Description)
               .NotNull()
               .NotEmpty()
              .MaximumLength(500);
        }

    }
}
