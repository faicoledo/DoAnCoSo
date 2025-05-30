using LMS.Application.Interfaces.Courses;
using LMS.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LMS.Infrastructure
{
    public class CourseRepository : ICourseRepository
    {
        private readonly LmsContext _dbContext;
        public CourseRepository(LmsContext dbContext)
        {
            this._dbContext = dbContext;
        }

        public async Task AddCourseAsync(Course course)
        {
            _dbContext.Courses.Add(course);
            await _dbContext.SaveChangesAsync();
        }

        public async Task DeleteCourseAsync(Course courses)
        {
            _dbContext.Courses.Remove(courses);
            await _dbContext.SaveChangesAsync();
        }

        public async Task<IEnumerable<Course>> GetAllCoursesAsync()
        {
            return await _dbContext.Courses.ToListAsync();
        }

        public async Task<Course?> GetCourseByIdAsync(int courseId)
        {
            return await _dbContext.Courses.FindAsync(courseId);
        }

        public async Task<bool> IsTitleDuplicatedAsync(string title)
        {
            return await _dbContext.Courses.AnyAsync(c => c.Title == title);
        }

        public async Task UpdateCourseAsync(Course course)
        {
            _dbContext.Courses.Update(course);
            await _dbContext.SaveChangesAsync();
        }

        public async Task UpdateDescriptionAsync(int courseId, string description)
        {
            var course = await _dbContext.Courses.FindAsync(courseId);
            if (course == null)
            {
                throw new KeyNotFoundException($"Course with ID {courseId} not found.");
            }
            course.Description = description;
            await _dbContext.SaveChangesAsync();
        }
    }
}
