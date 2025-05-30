using FluentValidation;
using LMS.API.Filters;
using LMS.Application;
using LMS.Application.DTOs;
using LMS.Application.Interfaces.Courses;
using LMS.Application.Services;
using LMS.Domain.Entities;
using LMS.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Scalar.AspNetCore;

namespace LMS.API
{
    public class Program
    {
        public static void Main(string[] args)
        {
            #region Service - start
            var builder = WebApplication.CreateBuilder(args);
            //Add database
            builder.Services.AddDbContext<LmsContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("DbContext"),
                providerOptions => providerOptions.EnableRetryOnFailure()));
            // Add services to the container.

            builder.Services.AddControllers();
            // Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
            builder.Services.AddOpenApi();
            builder.Services.AddAutoMapper(typeof(MappingProfile));

            builder.Services.AddScoped<ICourseService, CourseService>();
            builder.Services.AddScoped<ICourseRepository, CourseRepository>();

            builder.Services.AddCors(options =>
            {
                options.AddPolicy("default", policy =>
                    {
                        policy.AllowAnyOrigin()
                              .AllowAnyMethod()
                              .AllowAnyHeader();
                    });
            });

            builder.Services.AddControllers(options =>
            {
                options.Filters.Add<ValidationFilter>();
            }).ConfigureApiBehaviorOptions(options =>
            {
                options.SuppressModelStateInvalidFilter = true; // Disable default model state validation
            });

            builder.Services.AddValidatorsFromAssemblyContaining<CreateCourseDto>();
            builder.Services.AddValidatorsFromAssemblyContaining<UpdateCourseDto>();
            #endregion Service - end

            #region middleware - start
            var app = builder.Build();

            app.UseCors("default");

            // Configure the HTTP request pipeline.
            //if (app.Environment.IsDevelopment())
            {
                app.MapOpenApi();
                app.MapScalarApiReference(options =>
                {
                    options.WithTitle("My API");
                    options.WithTheme(ScalarTheme.Saturn);
                    options.WithSidebar(true);
                });
                app.UseSwaggerUi(options =>
                {
                    options.DocumentPath = "openapi/v1.json";
                });
            }

            app.UseHttpsRedirection();

            app.UseAuthorization();


            app.MapControllers();

            app.Run();
            #endregion middleware - end
        }
    }
}