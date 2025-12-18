"""
Base Entity class for all domain entities.
Entities are objects with a distinct identity that persists over time.
"""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4


@dataclass
class Entity(ABC):
    """
    Base class for all domain entities.
    
    Key characteristics:
    - Has a unique identity (id)
    - Equality is based on identity, not attributes
    - Mutable state
    - Has lifecycle (created_at, updated_at)
    """
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def is_new(self) -> bool:
        """Check if entity is new (not persisted yet)"""
        return self.id is None


@dataclass
class AggregateRoot(Entity):
    """
    Aggregate Root - Entry point for an aggregate.
    
    All external references should only point to the aggregate root.
    The aggregate root is responsible for maintaining invariants.
    """
    _domain_events: list = field(default_factory=list, repr=False)
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to be dispatched"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> list:
        """Clear and return all domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

