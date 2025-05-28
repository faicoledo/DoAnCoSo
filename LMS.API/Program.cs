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
            #endregion Service - end

            #region middleware - start
            var app = builder.Build();

            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.MapOpenApi();
                app.MapScalarApiReference(options =>
                {
                    options.WithTitle("My API");
                    options.WithTheme(ScalarTheme.Saturn);
                    options.WithSidebar(true);
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