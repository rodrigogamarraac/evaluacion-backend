class AvailabilityService:
    def ensure_non_negative(self, value: int) -> int:
        return max(value, 0)
