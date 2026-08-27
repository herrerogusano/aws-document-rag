"""Bounded AWS SDK network and retry configuration."""

from botocore.config import Config

STANDARD_AWS_CONFIG = Config(
    connect_timeout=2,
    read_timeout=8,
    retries={"total_max_attempts": 2, "mode": "standard"},
)

MODEL_AWS_CONFIG = Config(
    connect_timeout=2,
    read_timeout=25,
    retries={"total_max_attempts": 1, "mode": "standard"},
)
