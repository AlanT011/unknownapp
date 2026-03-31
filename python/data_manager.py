import json
import os
from enrollment_system import EnrollmentSystem
from course import Course
from student import Student
from time_slot import TimeSlot

class DataManager:
    """
    Handles loading and saving of students and courses to JSON files.

    Data is stored in the data/ directory relative to the working directory:
    - data/students.json
    - data/courses.json
    """

    DATA_DIR = "data"
    STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
    COURSES_FILE = os.path.join(DATA_DIR, "courses.json")

    def save_data(self, system):
        """Saves the current state (students and courses) to JSON files."""
        os.makedirs(self.DATA_DIR, exist_ok=True)

        # Save students
        student_list = system.get_all_students()
        with open(self.STUDENTS_FILE, 'w') as f:
            json.dump([self._student_to_dict(s) for s in student_list], f, indent=2)

        # Save courses
        course_list = system.get_all_courses()
        with open(self.COURSES_FILE, 'w') as f:
            json.dump([self._course_to_dict(c) for c in course_list], f, indent=2)

    def load_data(self, system):
        """Loads students and courses from JSON files into the provided system."""
        # Load courses first (students reference course codes)
        if os.path.exists(self.COURSES_FILE):
            with open(self.COURSES_FILE, 'r') as f:
                courses_data = json.load(f)
                for course_dict in courses_data:
                    course = self._dict_to_course(course_dict)
                    system.get_courses_map()[course.code] = course

        # Load students
        if os.path.exists(self.STUDENTS_FILE):
            with open(self.STUDENTS_FILE, 'r') as f:
                students_data = json.load(f)
                for student_dict in students_data:
                    student = self._dict_to_student(student_dict)
                    system.get_students_map()[student.id] = student

    def seed_default_data(self, system):
        """Seeds the system with a default course catalog and sample students."""
        # --- Default courses ---
        system.add_course(Course("CS101", "Intro to Programming", 3, 30, TimeSlot("MWF", "09:00", "10:00")))
        system.add_course(Course("CS201", "Data Structures", 3, 25, TimeSlot("MWF", "10:00", "11:00")))
        system.add_course(Course("CS301", "Algorithms", 3, 25, TimeSlot("TTh", "09:00", "10:30")))
        system.add_course(Course("CS401", "Operating Systems", 3, 20, TimeSlot("TTh", "10:30", "12:00")))
        system.add_course(Course("MATH101", "Calculus I", 4, 35, TimeSlot("MWF", "08:00", "09:00")))
        system.add_course(Course("MATH201", "Calculus II", 4, 30, TimeSlot("MWF", "11:00", "12:00")))
        system.add_course(Course("ENG101", "Technical Writing", 2, 40, TimeSlot("TTh", "13:00", "14:00")))
        system.add_course(Course("NET101", "Computer Networks", 3, 25, TimeSlot("MWF", "14:00", "15:00")))
        system.add_course(Course("DB101", "Database Systems", 3, 25, TimeSlot("TTh", "14:00", "15:30")))
        system.add_course(Course("SE101", "Software Engineering", 3, 30, TimeSlot("MWF", "15:00", "16:00")))

        # Set prerequisites
        system.get_course("CS201").prerequisites = ["CS101"]
        system.get_course("CS301").prerequisites = ["CS201"]
        system.get_course("CS401").prerequisites = ["CS301"]

        # --- Sample student accounts ---
        alice = Student("STU001", "Alice Johnson", "Computer Science")
        alice.completed_courses.append("CS101")  # Has completed CS101
        system.add_student(alice)

        bob = Student("STU002", "Bob Smith", "Mathematics")
        system.add_student(bob)

        carol = Student("STU003", "Carol Williams", "Information Technology")
        carol.completed_courses.extend(["CS101", "CS201"])
        system.add_student(carol)

    def data_files_exist(self):
        """Returns true when data files already exist on disk."""
        return os.path.exists(self.STUDENTS_FILE) and os.path.exists(self.COURSES_FILE)

    def _student_to_dict(self, student):
        return {
            "id": student.id,
            "name": student.name,
            "major": student.major,
            "enrolledCourses": student.enrolled_courses,
            "completedCourses": student.completed_courses
        }

    def _dict_to_student(self, d):
        student = Student(d["id"], d["name"], d["major"])
        student.enrolled_courses = d.get("enrolledCourses", [])
        student.completed_courses = d.get("completedCourses", [])
        return student

    def _course_to_dict(self, course):
        return {
            "code": course.code,
            "title": course.title,
            "credits": course.credits,
            "capacity": course.capacity,
            "timeSlot": {
                "days": course.time_slot.days if course.time_slot else None,
                "startTime": course.time_slot.start_time if course.time_slot else None,
                "endTime": course.time_slot.end_time if course.time_slot else None
            } if course.time_slot else None,
            "prerequisites": course.prerequisites,
            "enrolledStudents": course.enrolled_students
        }

    def _dict_to_course(self, d):
        time_slot_data = d.get("timeSlot")
        time_slot = None
        if time_slot_data:
            time_slot = TimeSlot(time_slot_data.get("days"),
                               time_slot_data.get("startTime"),
                               time_slot_data.get("endTime"))
        course = Course(d["code"], d["title"], d["credits"], d["capacity"], time_slot)
        course.prerequisites = d.get("prerequisites", [])
        course.enrolled_students = d.get("enrolledStudents", [])
        return course