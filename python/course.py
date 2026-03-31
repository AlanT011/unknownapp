from time_slot import TimeSlot

class Course:
    """
    Represents a course in the catalog.
    """

    def __init__(self, code=None, title=None, credits=0, capacity=0, time_slot=None):
        self.code = code
        self.title = title
        self.credits = credits
        self.capacity = capacity
        self.time_slot = time_slot
        self.prerequisites = []  # course codes required before enrolling
        self.enrolled_students = []  # student IDs currently enrolled

    def get_enrollment_count(self):
        """Returns the number of students currently enrolled."""
        return len(self.enrolled_students)

    def is_full(self):
        """Returns true when the course has no remaining spots."""
        return len(self.enrolled_students) >= self.capacity

    def get_available_seats(self):
        """Returns the number of open seats remaining."""
        return max(0, self.capacity - len(self.enrolled_students))

    def has_student(self, student_id):
        """Returns true when the given student ID is already enrolled."""
        return student_id in self.enrolled_students

    def enroll_student(self, student_id):
        """Enrolls a student, returning false if the course is full or already enrolled."""
        if self.is_full() or self.has_student(student_id):
            return False
        self.enrolled_students.append(student_id)
        return True

    def remove_student(self, student_id):
        """Removes a student from this course. Returns false if the student was not enrolled."""
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            return True
        return False

    def __str__(self):
        prereq_str = "None" if not self.prerequisites else ", ".join(self.prerequisites)
        time_str = str(self.time_slot) if self.time_slot else "TBA"
        return (f"{self.code:<10} {self.title:<40} Credits: {self.credits}  "
                f"Capacity: {len(self.enrolled_students)}/{self.capacity}  "
                f"Time: {time_str:<18}  Prerequisites: {prereq_str}")