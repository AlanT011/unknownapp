from collections import OrderedDict
from course import Course
from student import Student

class EnrollmentSystem:
    """
    Core business logic for the course enrollment system.
    Manages students and courses and enforces enrollment rules.
    """

    TUITION_PER_CREDIT = 300.0

    def __init__(self):
        self.students = OrderedDict()  # Map<String, Student>
        self.courses = OrderedDict()   # Map<String, Course>

    # -----------------------------------------------------------------------
    # Student management
    # -----------------------------------------------------------------------

    def add_student(self, student):
        """Adds a new student. Returns false when the student ID already exists."""
        if student is None or student.id in self.students:
            return False
        self.students[student.id] = student
        return True

    def get_student(self, id):
        """Returns the student with the given ID, or null if not found."""
        return self.students.get(id)

    def update_student(self, id, new_name=None, new_major=None):
        """Updates an existing student's name and major. Returns false if not found."""
        student = self.students.get(id)
        if student is None:
            return False
        if new_name and new_name.strip():
            student.name = new_name
        if new_major and new_major.strip():
            student.major = new_major
        return True

    def get_all_students(self):
        """Returns an unmodifiable view of all students."""
        return list(self.students.values())

    # -----------------------------------------------------------------------
    # Course management
    # -----------------------------------------------------------------------

    def add_course(self, course):
        """Adds a new course to the catalog. Returns false when the course code already exists."""
        if course is None or course.code in self.courses:
            return False
        self.courses[course.code] = course
        return True

    def get_course(self, code):
        """Returns the course with the given code, or null if not found."""
        return self.courses.get(code)

    def update_course(self, code, new_title=None, new_credits=None, new_capacity=None):
        """Updates editable fields of an existing course. Returns false if not found."""
        course = self.courses.get(code)
        if course is None:
            return False
        if new_title and new_title.strip():
            course.title = new_title
        if new_credits and new_credits > 0:
            course.credits = new_credits
        if new_capacity and new_capacity > 0:
            course.capacity = new_capacity
        return True

    def get_all_courses(self):
        """Returns an unmodifiable view of all courses."""
        return list(self.courses.values())

    # -----------------------------------------------------------------------
    # Enrollment logic
    # -----------------------------------------------------------------------

    def register_course(self, student_id, course_code):
        """
        Attempts to register the student in the course.

        Returns an EnrollmentResult indicating success or the reason for failure.
        """
        student = self.students.get(student_id)
        if student is None:
            return EnrollmentResult.failure(f"Student not found: {student_id}")

        course = self.courses.get(course_code)
        if course is None:
            return EnrollmentResult.failure(f"Course not found: {course_code}")

        # Already enrolled check
        if student.is_enrolled_in(course_code):
            return EnrollmentResult.failure(f"You are already enrolled in {course_code}.")

        # Capacity check
        if course.is_full():
            return EnrollmentResult.failure(f"Course {course_code} is full (capacity: {course.capacity}).")

        # Prerequisite check
        for prereq in course.prerequisites:
            if not student.has_completed(prereq):
                prereq_course = self.courses.get(prereq)
                prereq_title = prereq_course.title if prereq_course else prereq
                return EnrollmentResult.failure(
                    f"Prerequisite not met: you must complete \"{prereq_title}\" ({prereq}) before enrolling in {course_code}.")

        # Time conflict check
        for enrolled_code in student.enrolled_courses:
            enrolled = self.courses.get(enrolled_code)
            if (enrolled and enrolled.time_slot and course.time_slot and
                enrolled.time_slot.overlaps(course.time_slot)):
                return EnrollmentResult.failure(
                    f"Schedule conflict: {course_code} ({course.time_slot}) overlaps with {enrolled_code} ({enrolled.time_slot}).")

        # All checks passed — perform enrollment
        student.enroll_in(course_code)
        course.enroll_student(student_id)
        return EnrollmentResult.success(f"Successfully enrolled in {course_code} – {course.title}.")

    def drop_course(self, student_id, course_code):
        """
        Drops the student from the course.

        Returns an EnrollmentResult indicating success or the reason for failure.
        """
        student = self.students.get(student_id)
        if student is None:
            return EnrollmentResult.failure(f"Student not found: {student_id}")

        course = self.courses.get(course_code)
        if course is None:
            return EnrollmentResult.failure(f"Course not found: {course_code}")

        if not student.is_enrolled_in(course_code):
            return EnrollmentResult.failure(f"You are not enrolled in {course_code}.")

        student.drop_course(course_code)
        course.remove_student(student_id)
        return EnrollmentResult.success(f"Successfully dropped {course_code} – {course.title}.")

    # -----------------------------------------------------------------------
    # Reporting
    # -----------------------------------------------------------------------

    def get_student_schedule(self, student_id):
        """
        Returns the list of courses a student is enrolled in,
        or an empty list if the student does not exist.
        """
        student = self.students.get(student_id)
        if student is None:
            return []
        schedule = []
        for code in student.enrolled_courses:
            course = self.courses.get(code)
            if course:
                schedule.append(course)
        return schedule

    def get_course_roster(self, course_code):
        """
        Returns the list of students enrolled in the given course,
        or an empty list if the course does not exist.
        """
        course = self.courses.get(course_code)
        if course is None:
            return []
        roster = []
        for sid in course.enrolled_students:
            student = self.students.get(sid)
            if student:
                roster.append(student)
        return roster

    def calculate_tuition(self, student_id):
        """
        Calculates the total tuition for a student based on enrolled credits.
        Returns -1.0 if the student is not found.
        """
        student = self.students.get(student_id)
        if student is None:
            return -1.0
        total_credits = 0
        for code in student.enrolled_courses:
            course = self.courses.get(code)
            if course:
                total_credits += course.credits
        return total_credits * self.TUITION_PER_CREDIT

    # -----------------------------------------------------------------------
    # Raw map access for DataManager serialization
    # -----------------------------------------------------------------------

    def get_students_map(self):
        return self.students

    def get_courses_map(self):
        return self.courses


class EnrollmentResult:
    """Immutable result of an enrollment or drop operation."""

    def __init__(self, success, message):
        self.success = success
        self.message = message

    @staticmethod
    def success(message):
        return EnrollmentResult(True, message)

    @staticmethod
    def failure(message):
        return EnrollmentResult(False, message)

    def is_success(self):
        return self.success

    def get_message(self):
        return self.message