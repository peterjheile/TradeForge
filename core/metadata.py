from dataclasses import dataclass
from typing import Optional, ClassVar
from datetime import datetime


@dataclass
class RunnerMetadata:

    #identity/runner config
    runner_id: str
    agent_type: str
    symbol: str
    paper: bool = True

    #runner timing configurations
    interval: int = 60                     #seconds between cycles
    duration: Optional[int] = None         #seconds, None means indefinite
    started_at: Optional[datetime] = None 
    ended_at: Optional[datetime] = None


    #logging configurations
    log: bool = True
    logging_filepath: Optional[str] = None
    logging_fields: Optional[list[str]] = None  #given by user, validated in __post_init__, default logging fields is all if not supplied

    #master list of allowed loggin fields
    ALLOWED_FIELDS: ClassVar[tuple[str, ...]] = (
        "timestamp", "run_id", "agent_type", "symbol",
        "signal", "order_id"
    )

    #validates user given loggin fields and sets defaults if none provided
    #also does basic validation for a few other fields
    def __post_init__(self):
        #interval validation
        if self.interval <= 0:
            raise ValueError("interval must be > 0")

        #default logging fields if none provided
        if self.logging_fields is None:
            self.logging_fields = list(self.ALLOWED_FIELDS)
        else:
            #validate & dedupe while preserving order for user given fields
            seen = set()
            validated: list[str] = []
            invalid: list[str] = []
            for f in self.logging_fields:
                if f in seen:
                    continue
                seen.add(f)
                if f in self.ALLOWED_FIELDS:
                    validated.append(f)
                else:
                    invalid.append(f)
            if invalid:
                raise ValueError(
                    f"Invalid logging fields: {invalid}. "
                    f"Allowed: {self.ALLOWED_FIELDS}"
                )
            self.logging_fields = validated