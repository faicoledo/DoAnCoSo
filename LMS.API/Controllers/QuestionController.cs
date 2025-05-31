using LMS.Application.DTOs;
using LMS.Application.Interfaces.QuestionChoice;
using Microsoft.AspNetCore.Mvc;

namespace LMS.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class QuestionController : Controller
    {
        private readonly IQuestionService _service;

        public QuestionController(IQuestionService service)
        {
            this._service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAllQuestions()
        {
            return Ok(await _service.GetAllQuestionsAsync());
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetQuestionById(int id)
        {
            var question = await _service.GetQuestionByIdAsync(id);
            return question != null ? Ok(question) : NotFound();
        }

        [HttpPost]
        public async Task<IActionResult> CreateQuestion([FromBody] CreateQuestionDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _service.AddQuestionAsync(dto);
            return CreatedAtAction(nameof(GetQuestionById), new { id = dto.CourseId }, dto);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateQuestion(int id, [FromBody] UpdateQuestionDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _service.UpdateQuestionAsync(id, dto);
            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteQuestion(int id)
        {
            var question = await _service.GetQuestionByIdAsync(id);
            if (question == null)
            {
                return NotFound();
            }
            await _service.DeleteQuestionAsync(id);
            return NoContent();
        }

        [HttpPut("UpdateQuestionAndChoices/{id}")]
        public async Task<IActionResult> UpdateQuestionAndChoices(int id, [FromBody] QuestionDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _service.UpdateQuestionAndChoicesAsync(id, dto);
            return NoContent();
        }
    }
}
