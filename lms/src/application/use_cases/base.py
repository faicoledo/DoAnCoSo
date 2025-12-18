"""
Base Use Case
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

InputDTO = TypeVar('InputDTO')
OutputDTO = TypeVar('OutputDTO')


class UseCase(ABC, Generic[InputDTO, OutputDTO]):
    """
    Base class for all use cases.
    
    Use cases represent application-specific business rules.
    They orchestrate the flow of data to and from entities,
    and direct those entities to use their business rules.
    """
    
    @abstractmethod
    def execute(self, input_dto: InputDTO) -> OutputDTO:
        """Execute the use case"""
        pass


class NoInputUseCase(ABC, Generic[OutputDTO]):
    """Use case that doesn't require input"""
    
    @abstractmethod
    def execute(self) -> OutputDTO:
        """Execute the use case"""
        pass

