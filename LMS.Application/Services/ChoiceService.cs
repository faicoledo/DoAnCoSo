using AutoMapper;
using LMS.Application.DTOs;
using LMS.Application.Interfaces.QuestionChoice;
using LMS.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LMS.Application.Services
{
    public class ChoiceService : IChoiceService
    {
        private readonly IChoiceRepository _choiceRepository;
        private readonly IMapper _mapper;

        public ChoiceService(IChoiceRepository choiceRepository, IMapper mapper)
        {
            _choiceRepository = choiceRepository;
            _mapper = mapper;
        }

        public async Task<IEnumerable<ChoiceDto>> GetAllChoicesAsync(int questionId)
        {
            var choices = await _choiceRepository.GetAllChoicesAsync(questionId);
            return _mapper.Map<IEnumerable<ChoiceDto>>(choices);
        }

        public async Task<ChoiceDto?> GetChoiceByIdAsync(int choiceId)
        {
            var choice = await _choiceRepository.GetChoiceByIdAsync(choiceId);
            return choice != null ? _mapper.Map<ChoiceDto>(choice) : null;
        }

        public async Task AddChoiceAsync(CreateChoiceDto dto)
        {
            var choice = _mapper.Map<Choice>(dto);
            await _choiceRepository.AddChoiceAsync(choice);
        }

        public async Task UpdateChoiceAsync(int choiceId, UpdateChoiceDto dto)
        {
            var existingChoice = await _choiceRepository.GetChoiceByIdAsync(choiceId);
            if (existingChoice == null)
                throw new KeyNotFoundException($"Choice with ID {choiceId} not found.");

            _mapper.Map(dto, existingChoice);
            await _choiceRepository.UpdateChoiceAsync(existingChoice);
        }

        public async Task UpdateUserChoiceAsync(int choiceId, UpdateUserChoice dto)
        {
            var existingChoice = await _choiceRepository.GetChoiceByIdAsync(choiceId);
            if (existingChoice == null)
                throw new KeyNotFoundException($"Choice with ID {choiceId} not found.");

            _mapper.Map(dto, existingChoice);
            await _choiceRepository.UpdateChoiceAsync(existingChoice);
        }

        public async Task DeleteChoiceAsync(int choiceId)
        {
            var choice = await _choiceRepository.GetChoiceByIdAsync(choiceId);
            if (choice == null)
                throw new KeyNotFoundException($"Choice with ID {choiceId} not found.");

            await _choiceRepository.DeleteChoiceAsync(choice);
        }
    }
}
