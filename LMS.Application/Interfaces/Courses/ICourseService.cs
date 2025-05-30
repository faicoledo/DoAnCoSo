using LMS.Application.DTOs;
using LMS.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LMS.Application.Interfaces.Courses
{
    public interface ICourseService
    {
        Task<IEnumerable<CourseDto>> GetAllCoursesAsync();
        Task<CourseDto?> GetCourseByIdAsync(int courseId);
        Task<bool> IsTitleDuplicatedAsync(string title);
        Task AddCourseAsync(CreateCourseDto courseDto);
        Task UpdateCourseAsync(int courseId, UpdateCourseDto courseDto);
        Task DeleteCourseAsync(int courseId);
        Task UpdateDescriptionAsync(int courseId, string description);
    }
}
