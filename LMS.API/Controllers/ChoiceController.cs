using LMS.Application.DTOs;
using LMS.Application.Interfaces.QuestionChoice;
using Microsoft.AspNetCore.Mvc;

namespace LMS.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ChoiceController : Controller
    {

        private readonly IChoiceService _choice;

        public ChoiceController(IChoiceService choice)
        {
            this._choice = choice;
        }

        [HttpGet("{questionId}")]
        public async Task<IActionResult> GetChoicesByQuestionId(int questionId)
        {
            return Ok(await _choice.GetAllChoicesAsync(questionId));
        }

        [HttpGet("{questionId}/{Id}")]
        public async Task<IActionResult> GetChoiceById(int questionId, int Id)
        {
            var choice = await _choice.GetChoiceByIdAsync(Id);
            return choice != null ? Ok(choice) : NotFound();
        }

        [HttpPost]
        public async Task<IActionResult> CreateChoice([FromBody] CreateChoiceDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _choice.AddChoiceAsync(dto);
            return CreatedAtAction(nameof(GetChoicesByQuestionId), new { questionId = dto.QuestionId });
        }

        [HttpPut("{Id}")]
        public async Task<IActionResult> UpdateChoice(int Id, [FromBody] UpdateChoiceDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _choice.UpdateChoiceAsync(Id, dto);
            return NoContent();
        }

        [HttpPatch("{Id}")]
        public async Task<IActionResult> UpdateUserChoice(int Id, [FromBody] UpdateUserChoice dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }
            await _choice.UpdateUserChoiceAsync(Id, dto);
            return NoContent();
        }

        [HttpDelete("{Id}")]
        public async Task<IActionResult> DeleteChoice(int Id)
        {
            var choice = await _choice.GetChoiceByIdAsync(Id);
            if (choice == null)
            {
                return NotFound();
            }
            await _choice.DeleteChoiceAsync(Id);
            return NoContent();
        }
    }
}
