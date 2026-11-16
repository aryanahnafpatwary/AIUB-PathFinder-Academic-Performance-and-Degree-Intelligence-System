AIUB_GRADE_POINTS = (
    ("A+", 4.00),
    ("A",  3.75),
    ("B+", 3.50),
    ("B",  3.25),
    ("C+", 3.00),
    ("C",  2.75),
    ("D+", 2.50),
    ("D",  2.25),
    ("F",  0.00),
)

ACADEMIC_DOMAINS = (
    "CS_CORE",
    "MATH_STAT",
    "HARDWARE",
    "BASIC_SCI",
    "BUSINESS",
    "HUMANITIES",
)

GRADE_POINT_MAP = dict(AIUB_GRADE_POINTS)


class AcademicCourse:
    def __init__(self, course_code, course_name, credits):
        self.__course_code = course_code.strip().upper()
        self.__course_name = course_name.strip()
        self.credits = credits

    @property
    def course_code(self):
        return self.__course_code

    @property
    def course_name(self):
        return self.__course_name

    @property
    def credits(self):
        return self.__credits

    @credits.setter
    def credits(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Course credits must be a numeric value.")
        if value < 0.0 or value > 10.0:
            raise ValueError(f"Invalid credit value: {value}. Must be between 0.0 and 10.0.")
        self.__credits = float(value)

    def is_passed(self):
        return False

    def calculate_weighted_points(self):
        return 0.0

    def get_summary(self):
        """Polymorphic representation of course details."""
        return f"[{self.__course_code}] {self.__course_name} ({self.__credits:.1f} Cr)"

class CompletedCourse(AcademicCourse):
    def __init__(
        self,
        course_code,
        course_name,
        credits,
        mtg="-",
        ftg="-",
        final_grade="-",
        grade_point=0.0,
        earned_credits=0.0,
        status="VAL",
        semester_name=""
    ):
        super().__init__(course_code, course_name, credits)
        self.__mtg = mtg.strip()
        self.__ftg = ftg.strip()
        self.__final_grade = final_grade.strip()
        self.__grade_point = float(grade_point)
        self.__earned_credits = float(earned_credits)
        self.__status = status.strip()
        self.__semester_name = semester_name.strip()
        self.__is_in_progress = (self.__final_grade == "-" or self.__final_grade == "")

    @property
    def mtg(self):
        return self.__mtg

    @property
    def ftg(self):
        return self.__ftg

    @property
    def final_grade(self):
        return self.__final_grade

    @property
    def grade_point(self):
        return self.__grade_point

    @property
    def earned_credits(self):
        return self.__earned_credits

    @property
    def status(self):
        return self.__status

    @property
    def semester_name(self):
        return self.__semester_name

    @property
    def is_in_progress(self):
        return self.__is_in_progress

    def is_passed(self):
        if self.__is_in_progress:
            return False
        return self.__final_grade != "F" and self.__earned_credits > 0.0

    def calculate_weighted_points(self):
        if self.__is_in_progress:
            return 0.0
        return self.credits * self.__grade_point

    def get_summary(self):
        if self.__is_in_progress:
            return f"[{self.course_code}] {self.course_name} ({self.credits:.1f} Cr) -> [CURRENT ENROLLED]"
        return (
            f"[{self.course_code}] {self.course_name:<36} | Cr: {self.credits:.1f} | "
            f"MT: {self.__mtg:<2} | FT: {self.__ftg:<2} | Final: {self.__final_grade:<2} | "
            f"GP: {self.__grade_point:.2f}"
        )

class CurriculumCourse(AcademicCourse):
    def __init__(
        self,
        curriculum_no,
        curriculum_name,
        semester_slot,
        course_code,
        course_name,
        credits,
        prerequisites_raw,
        domain="CS_CORE"
    ):
        super().__init__(course_code, course_name, credits)
        self.__curriculum_no = int(curriculum_no)
        self.__curriculum_name = curriculum_name.strip()
        self.__semester_slot = semester_slot.strip()
        self.__domain = domain if domain in ACADEMIC_DOMAINS else "CS_CORE"
        self.__prerequisites = self._parse_prereqs(prerequisites_raw)

    @staticmethod
    def _parse_prereqs(raw):
        if not raw or raw.strip().lower() in ("", "none", "nan"):
            return set()
        codes = [c.strip().upper() for c in raw.replace(",", ";").split(";")]
        return {c for c in codes if c}

    @property
    def curriculum_no(self):
        return self.__curriculum_no

    @property
    def semester_slot(self):
        return self.__semester_slot

    @property
    def is_elective(self):
        return "Elective" in self.__semester_slot or self.__curriculum_no == 338

    @property
    def prerequisites(self):
        return set(self.__prerequisites)

    @property
    def domain(self):
        return self.__domain

    def is_unlocked(self, completed_course_codes):
        if not self.__prerequisites:
            return True
        return self.__prerequisites.issubset(completed_course_codes)

    def missing_prerequisites(self, completed_course_codes):
        return self.__prerequisites.difference(completed_course_codes)

    def get_summary(self):
        prereq_str = ", ".join(sorted(self.__prerequisites)) if self.__prerequisites else "None"
        tag = "[ELECTIVE]" if self.is_elective else f"[{self.__semester_slot}]"
        return f"{tag:<14} [{self.course_code}] {self.course_name:<36} ({self.credits:.1f} Cr) | Prereqs: {prereq_str}"

class SemesterRecord:
    def __init__(self, semester_name):
        self.__semester_name = semester_name.strip()
        self.__courses = []
        self.__sgpa = 0.0
        self.__cgpa = 0.0
        self.__tgp = 0.0
        self.__ecr = 0.0
        self.__is_current = False

    @property
    def semester_name(self):
        return self.__semester_name

    @property
    def courses(self):
        return list(self.__courses)

    @property
    def sgpa(self):
        return self.__sgpa

    @sgpa.setter
    def sgpa(self, value):
        self.__sgpa = max(0.0, min(4.0, float(value)))

    @property
    def cgpa(self):
        return self.__cgpa

    @cgpa.setter
    def cgpa(self, value):
        self.__cgpa = max(0.0, min(4.0, float(value)))

    @property
    def tgp(self):
        """Total Grade Points from report summary line."""
        return self.__tgp

    @tgp.setter
    def tgp(self, value):
        self.__tgp = max(0.0, float(value))

    @property
    def ecr(self):
        """Earned Credits from report summary line."""
        return self.__ecr

    @ecr.setter
    def ecr(self, value):
        self.__ecr = max(0.0, float(value))

    @property
    def is_current(self):
        return self.__is_current

    @is_current.setter
    def is_current(self, value):
        self.__is_current = bool(value)

    def add_course(self, course):
        self.__courses.append(course)
        if course.is_in_progress:
            self.__is_current = True

    def calculate_total_credits(self):
        return sum(c.credits for c in self.__courses)

    def calculate_earned_credits(self):
        return sum(c.earned_credits for c in self.__courses if c.is_passed())


class StudentAcademicProfile:
    def __init__(
        self,
        student_id,
        student_name,
        degree="BSc in Computer Science & Engineering",
        completed_credits=0.0,
        cgpa=0.0
    ):
        self.__student_id = student_id.strip()
        self.__student_name = student_name.strip()
        self.__degree = degree.strip()
        self.__completed_credits = float(completed_credits)
        self.__cgpa = float(cgpa)
        self.__semesters = []
        self.__curriculum_remaining = []

    @property
    def student_id(self):
        return self.__student_id

    @student_id.setter
    def student_id(self, value):
        if not value or not str(value).strip():
            raise ValueError("Student ID cannot be empty.")
        self.__student_id = str(value).strip()

    @property
    def student_name(self):
        return self.__student_name

    @student_name.setter
    def student_name(self, value):
        if not value or not str(value).strip():
            raise ValueError("Student name cannot be empty.")
        self.__student_name = str(value).strip()

    @property
    def degree(self):
        return self.__degree

    @property
    def completed_credits(self):
        return self.__completed_credits

    @completed_credits.setter
    def completed_credits(self, value):
        val = float(value)
        if val < 0.0 or val > 200.0:
            raise ValueError(f"Completed credits out of range: {val}")
        self.__completed_credits = val

    @property
    def cgpa(self):
        return self.__cgpa

    @cgpa.setter
    def cgpa(self, value):
        val = float(value)
        if val < 0.0 or val > 4.0:
            raise ValueError(f"CGPA out of range (0.00 - 4.00): {val}")
        self.__cgpa = val

    @property
    def semesters(self):
        return list(self.__semesters)

    @property
    def curriculum_remaining(self):
        return list(self.__curriculum_remaining)

    def set_curriculum_remaining(self, remaining):
        self.__curriculum_remaining = list(remaining)

    def add_semester(self, sem):
        self.__semesters.append(sem)

    def get_completed_course_codes(self):
        passed = set()
        for s in self.__semesters:
            for c in s.courses:
                if c.is_passed():
                    passed.add(c.course_code)
        return passed

    def get_in_progress_courses(self):
        in_progress = []
        for s in self.__semesters:
            if s.is_current:
                for c in s.courses:
                    if c.is_in_progress:
                        in_progress.append(c)
        return in_progress

    def get_completed_courses_list(self):
        return [c for s in self.__semesters for c in s.courses if c.is_passed()]

    def get_sgpa_history(self):
        history = []
        for s in self.__semesters:
            if not s.is_current and s.sgpa > 0.0:
                history.append((s.semester_name, s.sgpa, s.calculate_earned_credits()))
        return history