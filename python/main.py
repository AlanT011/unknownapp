from enrollment_system import EnrollmentSystem
from data_manager import DataManager
from student import Student
from course import Course
from time_slot import TimeSlot
import sys

class Main:
    """
    Entry point for the Course Enrollment System command-line application.
    """

    ADMIN_PASSWORD = "admin123"
    SEPARATOR = "=" * 70
    THIN_SEP = "-" * 70

    def __init__(self):
        self.system = EnrollmentSystem()
        self.data_manager = DataManager()

    # -----------------------------------------------------------------------
    # Startup
    # -----------------------------------------------------------------------

    def run(self):
        self.print_banner()
        self.init_data()

        quit_app = False
        while not quit_app:
            quit_app = self.login_menu()

    def print_banner(self):
        print(self.SEPARATOR)
        print("       COURSE ENROLLMENT SYSTEM")
        print(self.SEPARATOR)

    def init_data(self):
        if self.data_manager.data_files_exist():
            try:
                self.data_manager.load_data(self.system)
                print("[INFO] Data loaded from disk.")
            except Exception as e:
                print(f"[WARN] Could not load saved data: {e}")
                print("[INFO] Starting with default data.")
                self.data_manager.seed_default_data(self.system)
        else:
            print("[INFO] First run detected — loading default course catalog and sample students.")
            self.data_manager.seed_default_data(self.system)

    # -----------------------------------------------------------------------
    # Login menu
    # -----------------------------------------------------------------------

    def login_menu(self):
        """
        Displays the login menu.

        Returns true when the user chooses to exit the application.
        """
        print()
        print(self.SEPARATOR)
        print("  LOGIN")
        print(self.SEPARATOR)
        print("  [1] Login as Student")
        print("  [2] Login as Admin")
        print("  [3] Exit")
        print(self.THIN_SEP)
        choice = input("  Select option: ").strip()
        if choice == "1":
            self.student_login()
        elif choice == "2":
            self.admin_login()
        elif choice == "3":
            self.save_and_exit()
            return True
        else:
            print("  [!] Invalid option. Please enter 1, 2, or 3.")
        return False

    def student_login(self):
        print()
        print("  --- Student Login ---")
        print("  Enter your Student ID (or 'new' to create a new profile): ")
        id_input = input("  > ").strip()

        if id_input.lower() == "new":
            new_student = self.create_student_profile()
            if new_student:
                self.student_menu(new_student)
            return

        student = self.system.get_student(id_input)
        if student is None:
            print("  [!] Student ID not found. Type 'new' to create a new profile.")
            return
        print(f"  Welcome, {student.name}!")
        self.student_menu(student)

    def admin_login(self):
        print()
        print("  --- Admin Login ---")
        pwd = input("  Password: ").strip()
        if pwd != self.ADMIN_PASSWORD:
            print("  [!] Incorrect password.")
            return
        print("  Welcome, Administrator!")
        self.admin_menu()

    # -----------------------------------------------------------------------
    # Student menu
    # -----------------------------------------------------------------------

    def student_menu(self, student):
        logout = False
        while not logout:
            print()
            print(self.SEPARATOR)
            print(f"  STUDENT MENU  –  {student.name} [{student.id}]")
            print(self.SEPARATOR)
            print("  [1] View Course Catalog")
            print("  [2] Register for a Course")
            print("  [3] Drop a Course")
            print("  [4] View My Schedule")
            print("  [5] Billing Summary")
            print("  [6] Edit My Profile")
            print("  [7] Logout and Save")
            print(self.THIN_SEP)
            choice = input("  Select option: ").strip()
            if choice == "1":
                self.view_course_catalog()
            elif choice == "2":
                self.register_for_course(student)
            elif choice == "3":
                self.drop_course(student)
            elif choice == "4":
                self.view_schedule(student)
            elif choice == "5":
                self.billing_summary(student)
            elif choice == "6":
                self.edit_profile(student)
            elif choice == "7":
                self.save_data()
                logout = True
            else:
                print("  [!] Invalid option.")

    def view_course_catalog(self):
        print()
        print(self.SEPARATOR)
        print("  COURSE CATALOG")
        print(self.SEPARATOR)
        courses = self.system.get_all_courses()
        if not courses:
            print("  No courses available.")
            return
        self.print_course_header()
        for c in courses:
            print(f"  {c}")

    def print_course_header(self):
        print("  Code       Title                                    Credits  Seats    Time               Prerequisites")
        print(f"  {self.THIN_SEP}")

    def register_for_course(self, student):
        print()
        print("  --- Register for a Course ---")
        self.view_course_catalog()
        print()
        code = input("  Enter course code to register (or press Enter to cancel): ").strip().upper()
        if not code:
            return
        result = self.system.register_course(student.id, code)
        if result.is_success():
            print(f"  [✓] {result.get_message()}")
        else:
            print(f"  [✗] {result.get_message()}")

    def drop_course(self, student):
        print()
        print("  --- Drop a Course ---")
        schedule = self.system.get_student_schedule(student.id)
        if not schedule:
            print("  You are not enrolled in any courses.")
            return
        print("  Your current courses:")
        for c in schedule:
            print(f"    {c.code} – {c.title}")
        print()
        code = input("  Enter course code to drop (or press Enter to cancel): ").strip().upper()
        if not code:
            return
        result = self.system.drop_course(student.id, code)
        if result.is_success():
            print(f"  [✓] {result.get_message()}")
        else:
            print(f"  [✗] {result.get_message()}")

    def view_schedule(self, student):
        print()
        print(self.SEPARATOR)
        print(f"  SCHEDULE FOR: {student.name} [{student.id}]")
        print(self.SEPARATOR)
        schedule = self.system.get_student_schedule(student.id)
        if not schedule:
            print("  You are not enrolled in any courses.")
            return
        self.print_course_header()
        for c in schedule:
            print(f"  {c}")
        total_credits = sum(c.credits for c in schedule)
        print()
        print(f"  Total Credits Enrolled: {total_credits}")

    def billing_summary(self, student):
        print()
        print(self.SEPARATOR)
        print(f"  BILLING SUMMARY FOR: {student.name} [{student.id}]")
        print(self.SEPARATOR)
        schedule = self.system.get_student_schedule(student.id)
        if not schedule:
            print("  You are not enrolled in any courses. Tuition: $0.00")
            return
        print("  Code       Title                                    Credits")
        print(f"  {self.THIN_SEP}")
        total_credits = 0
        for c in schedule:
            print(f"  {c.code:<10} {c.title:<40} {c.credits}")
            total_credits += c.credits
        tuition = self.system.calculate_tuition(student.id)
        print(f"  {self.THIN_SEP}")
        print(f"  Total Credits : {total_credits}")
        print("  Rate per Credit: $300.00")
        print(f"  {'TOTAL TUITION:':<42} ${tuition:.2f}")

    def edit_profile(self, student):
        print()
        print("  --- Edit My Profile ---")
        print(f"  Current: {student}")
        print("  (Press Enter to keep current value)")
        name = input(f"  New Name  [{student.name}]: ").strip()
        major = input(f"  New Major [{student.major}]: ").strip()
        self.system.update_student(student.id, name, major)
        print("  [✓] Profile updated.")
        print(f"  Updated: {student}")

    def create_student_profile(self):
        print()
        print("  --- Create New Student Profile ---")
        id_input = input("  Student ID: ").strip()
        if not id_input:
            print("  [!] Student ID cannot be empty.")
            return None
        if self.system.get_student(id_input):
            print("  [!] Student ID already exists.")
            return None
        name = input("  Full Name : ").strip()
        if not name:
            print("  [!] Name cannot be empty.")
            return None
        major = input("  Major     : ").strip()
        if not major:
            major = "Undeclared"
        student = Student(id_input, name, major)
        self.system.add_student(student)
        print(f"  [✓] New student profile created: {student}")
        return student

    # -----------------------------------------------------------------------
    # Admin menu
    # -----------------------------------------------------------------------

    def admin_menu(self):
        logout = False
        while not logout:
            print()
            print(self.SEPARATOR)
            print("  ADMIN MENU")
            print(self.SEPARATOR)
            print("  [1]  View Course Catalog")
            print("  [2]  View Class Roster")
            print("  [3]  View All Students")
            print("  [4]  Add New Student")
            print("  [5]  Edit Student Profile")
            print("  [6]  Add New Course")
            print("  [7]  Edit Course")
            print("  [8]  View Student Schedule")
            print("  [9]  Billing Summary (any student)")
            print("  [10] Logout and Save")
            print(self.THIN_SEP)
            choice = input("  Select option: ").strip()
            if choice == "1":
                self.view_course_catalog()
            elif choice == "2":
                self.admin_view_roster()
            elif choice == "3":
                self.admin_view_students()
            elif choice == "4":
                self.admin_add_student()
            elif choice == "5":
                self.admin_edit_student()
            elif choice == "6":
                self.admin_add_course()
            elif choice == "7":
                self.admin_edit_course()
            elif choice == "8":
                self.admin_view_schedule()
            elif choice == "9":
                self.admin_billing_summary()
            elif choice == "10":
                self.save_data()
                logout = True
            else:
                print("  [!] Invalid option.")

    def admin_view_roster(self):
        print()
        print("  --- Class Roster ---")
        self.view_course_catalog()
        print()
        code = input("  Enter course code (or press Enter to cancel): ").strip().upper()
        if not code:
            return
        course = self.system.get_course(code)
        if course is None:
            print(f"  [!] Course not found: {code}")
            return
        print()
        print(self.SEPARATOR)
        print(f"  ROSTER: {course.code} – {course.title}")
        print(self.SEPARATOR)
        roster = self.system.get_course_roster(code)
        if not roster:
            print("  No students enrolled.")
            return
        print("  ID         Name                      Major")
        print(f"  {self.THIN_SEP}")
        for s in roster:
            print(f"  {s.id:<15} {s.name:<25} {s.major}")
        print(f"  \nTotal enrolled: {len(roster)} / {course.capacity}")

    def admin_view_students(self):
        print()
        print(self.SEPARATOR)
        print("  ALL STUDENTS")
        print(self.SEPARATOR)
        students = self.system.get_all_students()
        if not students:
            print("  No students registered.")
            return
        print("  ID         Name                      Major                    Enrolled Courses")
        print(f"  {self.THIN_SEP}")
        for s in students:
            enrolled = ", ".join(s.enrolled_courses) if s.enrolled_courses else "None"
            print(f"  {s.id:<15} {s.name:<25} {s.major:<20} {enrolled}")

    def admin_add_student(self):
        print()
        print("  --- Add New Student ---")
        id_input = input("  Student ID: ").strip()
        if not id_input:
            print("  [!] Student ID cannot be empty.")
            return
        if self.system.get_student(id_input):
            print("  [!] Student ID already exists.")
            return
        name = input("  Full Name : ").strip()
        major = input("  Major     : ").strip()
        if not major:
            major = "Undeclared"
        self.system.add_student(Student(id_input, name, major))
        print("  [✓] Student added.")

    def admin_edit_student(self):
        print()
        print("  --- Edit Student Profile ---")
        self.admin_view_students()
        print()
        id_input = input("  Enter Student ID to edit (or press Enter to cancel): ").strip()
        if not id_input:
            return
        student = self.system.get_student(id_input)
        if student is None:
            print(f"  [!] Student not found: {id_input}")
            return
        print(f"  Current: {student}")
        print("  (Press Enter to keep current value)")
        name = input(f"  New Name  [{student.name}]: ").strip()
        major = input(f"  New Major [{student.major}]: ").strip()
        self.system.update_student(id_input, name, major)
        print("  [✓] Profile updated: {student}")

    def admin_add_course(self):
        print()
        print("  --- Add New Course ---")
        code = input("  Course Code    : ").strip().upper()
        if not code:
            print("  [!] Course code cannot be empty.")
            return
        if self.system.get_course(code):
            print(f"  [!] Course code already exists: {code}")
            return
        title = input("  Title          : ").strip()
        credits = self.parse_int_or_default(input("  Credits        : ").strip(), 3)
        capacity = self.parse_int_or_default(input("  Capacity       : ").strip(), 30)
        days = input("  Days (e.g. MWF): ").strip()
        start = input("  Start Time (HH:mm): ").strip()
        end = input("  End Time   (HH:mm): ").strip()
        prereq_input = input("  Prerequisites (comma-separated codes, or blank): ").strip()

        time_slot = TimeSlot(days, start, end)
        course = Course(code, title, credits, capacity, time_slot)
        if prereq_input:
            course.prerequisites = [p.strip() for p in prereq_input.split(",")]
        self.system.add_course(course)
        print(f"  [✓] Course added: {course}")

    def admin_edit_course(self):
        print()
        print("  --- Edit Course ---")
        self.view_course_catalog()
        print()
        code = input("  Enter course code to edit (or press Enter to cancel): ").strip().upper()
        if not code:
            return
        course = self.system.get_course(code)
        if course is None:
            print(f"  [!] Course not found: {code}")
            return
        print(f"  Current: {course}")
        print("  (Press Enter to keep current value)")
        title = input(f"  New Title    [{course.title}]: ").strip()
        credits_str = input(f"  New Credits  [{course.credits}]: ").strip()
        cap_str = input(f"  New Capacity [{course.capacity}]: ").strip()

        credits = self.parse_int_or_none(credits_str)
        capacity = self.parse_int_or_none(cap_str)
        self.system.update_course(code, title, credits, capacity)
        print(f"  [✓] Course updated: {course}")

    def admin_view_schedule(self):
        print()
        print("  --- View Student Schedule ---")
        self.admin_view_students()
        print()
        id_input = input("  Enter Student ID (or press Enter to cancel): ").strip()
        if not id_input:
            return
        student = self.system.get_student(id_input)
        if student is None:
            print(f"  [!] Student not found: {id_input}")
            return
        self.view_schedule(student)

    def admin_billing_summary(self):
        print()
        print("  --- Billing Summary ---")
        self.admin_view_students()
        print()
        id_input = input("  Enter Student ID (or press Enter to cancel): ").strip()
        if not id_input:
            return
        student = self.system.get_student(id_input)
        if student is None:
            print(f"  [!] Student not found: {id_input}")
            return
        self.billing_summary(student)

    # -----------------------------------------------------------------------
    # Persistence helpers
    # -----------------------------------------------------------------------

    def save_data(self):
        try:
            self.data_manager.save_data(self.system)
            print("  [✓] Data saved successfully.")
        except Exception as e:
            print(f"  [!] Error saving data: {e}")

    def save_and_exit(self):
        self.save_data()
        print()
        print("  Thank you for using the Course Enrollment System. Goodbye!")
        print(self.SEPARATOR)

    # -----------------------------------------------------------------------
    # Utility methods
    # -----------------------------------------------------------------------

    def parse_int_or_default(self, s, default):
        try:
            return int(s)
        except ValueError:
            return default

    def parse_int_or_none(self, s):
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None

if __name__ == "__main__":
    main = Main()
    main.run()