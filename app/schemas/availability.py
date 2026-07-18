from datetime import time

from pydantic import BaseModel, model_validator

from app.models.availability import Weekday


class AvailabilityCreate(BaseModel):
    day_of_week: Weekday
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_time_order(self):
        """
        Runs after Pydantic validates the individual fields.
        Catches an easy real-world mistake: a doctor accidentally
        entering an end time before the start time.
        """
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AvailabilityOut(BaseModel):
    id: int
    day_of_week: Weekday
    start_time: time
    end_time: time

    class Config:
        from_attributes = True
