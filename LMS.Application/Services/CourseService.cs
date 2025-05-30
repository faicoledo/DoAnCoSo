using AutoMapper;
using LMS.Application.DTOs;
using LMS.Application.Interfaces.Courses;
using LMS.Domain.Entities;

namespace LMS.Application.Services
{
    public class CourseService : ICourseService
    {
        private readonly ICourseRepository _courseRepository;
        private readonly IMapper _mapper;

        public CourseService(ICourseRepository courseRepository, IMapper mapper)
        {
            this._courseRepository = courseRepository;
            this._mapper = mapper;
        }
        public async Task AddCourseAsync(CreateCourseDto courseDto)
        {
            var course = _mapper.Map<Course>(courseDto);
            course.CreatedBy = 2;
            course.CreatedOn = DateTime.UtcNow;

            await _courseRepository.AddCourseAsync(course);
        }

        public async Task DeleteCourseAsync(int courseId)
        {
            var course = await _courseRepository.GetCourseByIdAsync(courseId);
            if (course == null)
            {
                throw new KeyNotFoundException($"Course with ID {courseId} not found.");
            }
            await _courseRepository.DeleteCourseAsync(course);
        }

        public async Task<IEnumerable<CourseDto>> GetAllCoursesAsync()
        {
            var courses = await _courseRepository.GetAllCoursesAsync();
            return _mapper.Map<IEnumerable<CourseDto>>(courses);
        }

        public async Task<CourseDto?> GetCourseByIdAsync(int courseId)
        {
            var course = await _courseRepository.GetCourseByIdAsync(courseId);
            return course == null ? null : _mapper.Map<CourseDto>(course);
        }

        public async Task<bool> IsTitleDuplicatedAsync(string title)
        {
            return await _courseRepository.IsTitleDuplicatedAsync(title);
        }

        public async Task UpdateCourseAsync(int courseId, UpdateCourseDto courseDto)
        {
            var course = await _courseRepository.GetCourseByIdAsync(courseId);
            if (course == null)
            {
                throw new KeyNotFoundException($"Course with ID {courseId} not found.");
            }
            _mapper.Map(courseDto, course);
            await _courseRepository.UpdateCourseAsync(course);
        }

        public async Task UpdateDescriptionAsync(int courseId, string description)
        {
            await _courseRepository.UpdateDescriptionAsync(courseId, description);
        }
    }
}
