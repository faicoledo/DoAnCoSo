"""
DateRange Value Object
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    """
    DateRange Value Object
    
    Represents a range of dates with validation.
    """
    start_date: date
    end_date: date
    
    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
    
    def contains(self, check_date: date) -> bool:
        """Check if a date falls within the range"""
        return self.start_date <= check_date <= self.end_date
    
    def is_current(self) -> bool:
        """Check if today falls within the range"""
        today = date.today()
        return self.contains(today)
    
    def is_upcoming(self) -> bool:
        """Check if the range hasn't started yet"""
        return date.today() < self.start_date
    
    def is_past(self) -> bool:
        """Check if the range has ended"""
        return date.today() > self.end_date
    
    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another"""
        return self.start_date <= other.end_date and other.start_date <= self.end_date
    
    def days_count(self) -> int:
        """Get the number of days in the range (inclusive)"""
        return (self.end_date - self.start_date).days + 1
    
    def days_remaining(self) -> Optional[int]:
        """Get days remaining from today (None if already past)"""
        today = date.today()
        if today > self.end_date:
            return None
        if today < self.start_date:
            return self.days_count()
        return (self.end_date - today).days + 1
    
    def __str__(self) -> str:
        return f"{self.start_date} - {self.end_date}"

