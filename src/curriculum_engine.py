import csv
import os

from src.models import CurriculumCourse

SPECIALIZATION_TRACKS = {
    "DATA_SCIENCE_AI": {
        "title": "Intelligent Systems & Data Science",
        "description": "Focus on Machine Learning, NLP, Data Mining, Computer Vision, and AI.",
        "foundation_codes": ["CSC2108", "CSC2211", "MAT3103", "CSC3217"],
        "elective_codes": [
            "CSC4180",
            "CSC4232",
            "CSC4233",
            "CSC4285",
            "COE4234",
            "COE4231",
            "CSC4230",
        ],
    },
    "SOFTWARE_ENGINEERING": {
        "title": "Software Engineering & Enterprise Systems",
        "description": "Focus on Architecture, Testing, Project Management, and Web/Mobile Dev.",
        "foundation_codes": ["CSC1205", "CSC2108", "CSC2210", "CSC3112", "CSC3215"],
        "elective_codes": [
            "CSC4160",
            "CSC4271",
            "CSC4270",
            "CSC4273",
            "CSC4272",
            "CSC4161",
            "CSC4163",
            "CSC4164",
        ],
    },
    "NETWORKS_SECURITY": {
        "title": "Networks, Systems & Cyber Security",
        "description": "Focus on Advanced Networks, Cyber Laws, Wireless Sensors, and Security.",
        "foundation_codes": ["COE3103", "COE3104", "COE3206", "CSC3214"],
        "elective_codes": [
            "COE4126",
            "COE4232",
            "COE4127",
            "COE4233",
            "CSC4183",
            "COE4125",
        ],
    },
    "HARDWARE_ROBOTICS": {
        "title": "Hardware, Embedded Systems & Robotics",
        "description": "Focus on Digital Design, VLSI, Telecom, and Robotics Engineering.",
        "foundation_codes": ["EEE2103", "EEE3101", "COE3104", "COE3205"],
        "elective_codes": [
            "COE4128",
            "COE4235",
            "EEE4209",
            "EEE4217",
            "EEE4233",
            "EEE3103",
        ],
    },
}


class CurriculumEngine:
    def __init__(self, curriculum_csv_path):
        self.__csv_path = curriculum_csv_path
        self.__catalog = {}
        self.__course_domain_map = {}
        self._load_curriculum()

    @property
    def catalog(self):
        return dict(self.__catalog)

    @property
    def domain_map(self):
        return dict(self.__course_domain_map)

    def _load_curriculum(self):
        if not os.path.exists(self.__csv_path):
            raise FileNotFoundError(f"Curriculum CSV not found at: {self.__csv_path}")

        with open(self.__csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["Course Code"].strip().upper()
                name = row["Course Name"].strip()
                curr_no = int(row.get("Curriculum No", 309))
                curr_name = row.get("Curriculum", "BSc in CSE")
                sem_slot = row.get("Semester", "")
                cr = float(row.get("Total Credits", 3.0))
                prereqs = row.get("Prerequisites", "")

                domain = self._determine_domain(code, name)
                self.__course_domain_map[code] = domain

                course_obj = CurriculumCourse(
                    curriculum_no=curr_no,
                    curriculum_name=curr_name,
                    semester_slot=sem_slot,
                    course_code=code,
                    course_name=name,
                    credits=cr,
                    prerequisites_raw=prereqs,
                    domain=domain
                )
                self.__catalog[code] = course_obj

    @staticmethod
    def _determine_domain(course_code, course_name):
        prefix = course_code[:3].upper()
        if prefix in ("MAT",):
            return "MATH_STAT"
        elif prefix in ("PHY", "CHE"):
            return "BASIC_SCI"
        elif prefix in ("COE", "EEE"):
            return "HARDWARE"
        elif prefix in ("BBA", "ECO", "MGT", "MIS"):
            return "BUSINESS"
        elif prefix in ("ENG", "BAS", "BAE"):
            return "HUMANITIES"
        elif prefix in ("CSC",):
            # Special exceptions
            if "STATISTICS" in course_name.upper():
                return "MATH_STAT"
            return "CS_CORE"
        return "CS_CORE"

    def get_remaining_core_courses(self, completed_codes):
        remaining = []
        for code, course in self.__catalog.items():
            if not course.is_elective and code not in completed_codes:
                remaining.append(course)
        return sorted(remaining, key=lambda c: (c.semester_slot, c.course_code))

    def get_unlocked_core_courses(self, completed_codes):
        remaining = self.get_remaining_core_courses(completed_codes)
        unlocked = [c for c in remaining if c.is_unlocked(completed_codes)]
        return sorted(unlocked, key=lambda c: (c.semester_slot, c.course_code))

    def get_unlocked_electives(self, completed_codes):
        unlocked = []
        for code, course in self.__catalog.items():
            if course.is_elective and code not in completed_codes:
                if course.is_unlocked(completed_codes):
                    unlocked.append(course)
        return sorted(unlocked, key=lambda c: c.course_code)

    def evaluate_specialization_tracks(
        self,
        completed_courses,
        completed_codes,
        current_codes=None
    ):
      
        current_codes = current_codes or set()
        course_grade_map = {c.course_code: c.grade_point for c in completed_courses}
        rankings = []

        for track_key, track_info in SPECIALIZATION_TRACKS.items():
            foundations = set(track_info["foundation_codes"])
            taken_foundations = foundations.intersection(completed_codes)

            if taken_foundations:
                points = [course_grade_map[c] for c in taken_foundations if c in course_grade_map]
                foundation_gpa = sum(points) / len(points) if points else 0.0
            else:
                foundation_gpa = 0.0

            track_electives = set(track_info["elective_codes"])
            unlocked_in_track = []
            total_accessible_count = 0

            for code in track_electives:
                if code in self.__catalog:
                    course_obj = self.__catalog[code]
                    if course_obj.is_unlocked(completed_codes) or code in completed_codes or code in current_codes:
                        total_accessible_count += 1

                    if (
                        code not in completed_codes
                        and code not in current_codes
                        and course_obj.is_unlocked(completed_codes)
                    ):
                        unlocked_in_track.append(course_obj)

            perf_factor = (foundation_gpa / 4.0) * 70.0
            readiness_factor = (total_accessible_count / max(1, len(track_electives))) * 30.0
            match_score = round(perf_factor + readiness_factor, 1)

            if match_score >= 85.0:
                fit_label = "Prime Alignment / Highly Recommended"
            elif match_score >= 70.0:
                fit_label = "Strong Compatibility"
            else:
                fit_label = "Viable Alternative"

            rankings.append({
                "track_key": track_key,
                "title": track_info["title"],
                "description": track_info["description"],
                "match_score": match_score,
                "foundation_gpa": round(foundation_gpa, 2),
                "taken_foundations_count": f"{len(taken_foundations)}/{len(foundations)}",
                "unlocked_electives_count": len(unlocked_in_track),
                "unlocked_electives": unlocked_in_track,
                "fit_label": fit_label,
            })

        return sorted(rankings, key=lambda r: r["match_score"], reverse=True)
