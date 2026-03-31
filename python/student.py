class Student:
    """
    Represents a student in the enrollment system.
    """

    def __init__(self, id=None, name=None, major=None):
        self.id = id
        self.name = name
        self.major = major
        self.enrolled_courses = []  # course codes currently enrolled
        self.completed_courses = []  # course codes already completed (for prerequisite checks)

    def is_enrolled_in(self, course_code):
        """Returns true when the student is enrolled in the given course code."""
        return course_code in self.enrolled_courses

    def has_completed(self, course_code):
        """Returns true when the student has completed the given course code."""
        return course_code in self.completed_courses

    def enroll_in(self, course_code):
        """Adds a course code to the enrolled list. Returns false if already enrolled."""
        if self.is_enrolled_in(course_code):
            return False
        self.enrolled_courses.append(course_code)
        return True

    def drop_course(self, course_code):
        """Removes a course code from the enrolled list. Returns false if not enrolled."""
        if course_code in self.enrolled_courses:
            self.enrolled_courses.remove(course_code)
            return True
        return False

    def __str__(self):
        return f"ID: {self.id:<12}  Name: {self.name:<25}  Major: {self.major}"