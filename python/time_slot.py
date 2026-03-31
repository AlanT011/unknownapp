class TimeSlot:
    """
    Represents a scheduled time slot for a course, including day(s) and start/end times.
    """

    def __init__(self, days=None, start_time=None, end_time=None):
        self.days = days  # e.g. "MWF" or "TTh"
        self.start_time = start_time  # 24-hour format "HH:mm"
        self.end_time = end_time  # 24-hour format "HH:mm"

    def overlaps(self, other):
        """
        Returns true if this time slot overlaps with the given time slot.
        Two slots conflict if they share at least one common day AND their time ranges overlap.
        """
        if other is None or self.days is None or other.days is None:
            return False
        if not self._share_days(self.days, other.days):
            return False
        # Convert times to minutes for easy comparison
        this_start = self._to_minutes(self.start_time)
        this_end = self._to_minutes(self.end_time)
        other_start = self._to_minutes(other.start_time)
        other_end = self._to_minutes(other.end_time)

        if this_start < 0 or this_end < 0 or other_start < 0 or other_end < 0:
            return False
        # Overlap when one interval starts before the other ends
        return this_start < other_end and other_start < this_end

    def _share_days(self, d1, d2):
        """Returns true when the two day strings share at least one day character/token."""
        # Normalize to uppercase
        a = d1.upper()
        b = d2.upper()

        # Treat "T" as Thursday and "Th" as a distinct token; handle "TTh" style strings
        tokens = ["TH", "M", "T", "W", "F", "S", "U"]
        for token in tokens:
            if token in a and token in b:
                return True
        return False

    def _to_minutes(self, time):
        """Converts "HH:mm" to total minutes. Returns -1 if format is invalid."""
        if time is None or ":" not in time:
            return -1
        try:
            parts = time.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            return -1

    def __str__(self):
        return f"{self.days} {self.start_time}-{self.end_time}"