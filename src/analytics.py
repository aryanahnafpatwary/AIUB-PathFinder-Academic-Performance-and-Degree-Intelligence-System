import numpy as np

from src.models import ACADEMIC_DOMAINS, GRADE_POINT_MAP


class AcademicAnalyticsEngine:
    def __init__(self, profile):
        self.__profile = profile

    def compute_statistical_overview(self):
        history = self.__profile.get_sgpa_history()
        if not history:
            return {}

        sgpas = np.array([item[1] for item in history], dtype=np.float64)
        credits = np.array([item[2] for item in history], dtype=np.float64)

        mean_val = float(np.mean(sgpas))
        median_val = float(np.median(sgpas))
        std_val = float(np.std(sgpas))
        var_val = float(np.var(sgpas))
        min_val = float(np.min(sgpas))
        max_val = float(np.max(sgpas))
        p25 = float(np.percentile(sgpas, 25))
        p50 = float(np.percentile(sgpas, 50))
        p75 = float(np.percentile(sgpas, 75))

        if std_val < 0.10:
            stability = "Highly Stable / Exceptional Consistency"
        elif std_val < 0.20:
            stability = "Consistent & Steady Performance"
        else:
            stability = "High Volatility / Fluctuating Semester Momentum"

        best_idx = int(np.argmax(sgpas))
        lowest_idx = int(np.argmin(sgpas))

        return {
            "count": len(sgpas),
            "mean": round(mean_val, 3),
            "median": round(median_val, 3),
            "std_dev": round(std_val, 3),
            "variance": round(var_val, 4),
            "min_sgpa": round(min_val, 2),
            "max_sgpa": round(max_val, 2),
            "percentile_25": round(p25, 2),
            "percentile_50": round(p50, 2),
            "percentile_75": round(p75, 2),
            "stability_rating": stability,
            "best_semester": (history[best_idx][0], history[best_idx][1]),
            "lowest_semester": (history[lowest_idx][0], history[lowest_idx][1]),
            "total_evaluated_credits": float(np.sum(credits)),
        }

    def generate_sgpa_progression_table(self):
        records = []
        prev_sgpa = None
        for s in self.__profile.semesters:
            if s.is_current:
                records.append({
                    "semester": s.semester_name,
                    "credits": s.calculate_total_credits(),
                    "sgpa": "-",
                    "cgpa": f"{self.__profile.cgpa:.2f}",
                    "momentum": "[IN PROGRESS - CURRENT SEMESTER]",
                    "status": "Ongoing"
                })
            else:
                delta = 0.0 if prev_sgpa is None else round(s.sgpa - prev_sgpa, 2)
                if prev_sgpa is None:
                    momentum = "Baseline"
                elif delta > 0:
                    momentum = f"+{delta:.2f} (Improving)"
                elif delta < 0:
                    momentum = f"{delta:.2f} (Dipping)"
                else:
                    momentum = "0.00 (Stable)"

                records.append({
                    "semester": s.semester_name,
                    "credits": s.calculate_earned_credits(),
                    "sgpa": f"{s.sgpa:.2f}",
                    "cgpa": f"{s.cgpa:.2f}" if s.cgpa > 0 else "-",
                    "momentum": momentum,
                    "status": "Completed"
                })
                prev_sgpa = s.sgpa
        return records

    def forecast_next_semester_sgpa(self):
        history = self.__profile.get_sgpa_history()
        if len(history) < 2:
            return {"error": "Need at least 2 completed semesters for linear regression."}

        y = np.array([item[1] for item in history], dtype=np.float64)
        x = np.arange(1, len(y) + 1, dtype=np.float64)

        slope, intercept = np.polyfit(x, y, 1)

        next_x = len(y) + 1
        raw_pred = float(slope * next_x + intercept)
        clamped_pred = max(0.0, min(4.0, raw_pred))

        if len(y) >= 3:
            recent_weights = np.array([0.2, 0.3, 0.5])
            weighted_avg = float(np.sum(y[-3:] * recent_weights))
        else:
            weighted_avg = float(np.mean(y))

        total_tgp = 0.0
        total_ecr = 0.0
        for s in self.__profile.semesters:
            if not s.is_current:
                sem_tgp = s.tgp
                sem_ecr = s.ecr
                if (sem_tgp == 0.0 or sem_ecr == 0.0) and s.courses:
                    sem_tgp = sum(c.calculate_weighted_points() for c in s.courses)
                    sem_ecr = s.calculate_earned_credits()
                total_tgp += sem_tgp
                total_ecr += sem_ecr

        if total_ecr == 0.0 and self.__profile.completed_credits > 0.0:
            total_ecr = self.__profile.completed_credits
            total_tgp = self.__profile.cgpa * self.__profile.completed_credits

        enrolled_courses = self.__profile.get_in_progress_courses()
        enrolled_cr = sum(c.credits for c in enrolled_courses) if enrolled_courses else 15.0

        projected_sem_tgp = clamped_pred * enrolled_cr
        projected_total_tgp = total_tgp + projected_sem_tgp
        projected_total_ecr = total_ecr + enrolled_cr

        projected_new_cgpa = (
            projected_total_tgp / projected_total_ecr
            if projected_total_ecr > 0
            else 0.0
        )

        return {
            "linear_slope": round(float(slope), 4),
            "trend_direction": "Upward Momentum" if slope > 0 else "Downward / Stabilizing Trend",
            "forecasted_sgpa": round(clamped_pred, 2),
            "weighted_recent_avg": round(weighted_avg, 2),
            "projected_cgpa_after_current": round(float(projected_new_cgpa), 3),
            "total_tgp": round(total_tgp, 2),
            "total_ecr": round(total_ecr, 2),
            "evaluated_semesters_count": len(y),
        }

    def simulate_current_semester_scenarios(self, target_grades):
        total_tgp = 0.0
        total_ecr = 0.0
        for s in self.__profile.semesters:
            if not s.is_current:
                sem_tgp = s.tgp
                sem_ecr = s.ecr
                if (sem_tgp == 0.0 or sem_ecr == 0.0) and s.courses:
                    sem_tgp = sum(c.calculate_weighted_points() for c in s.courses)
                    sem_ecr = s.calculate_earned_credits()
                total_tgp += sem_tgp
                total_ecr += sem_ecr

        if total_ecr == 0.0 and self.__profile.completed_credits > 0.0:
            total_ecr = self.__profile.completed_credits
            total_tgp = self.__profile.cgpa * self.__profile.completed_credits

        curr_cgpa = self.__profile.cgpa
        current_courses = self.__profile.get_in_progress_courses()

        simulated_points = 0.0
        simulated_credits = 0.0
        details = []

        target_grades = target_grades or {}
        for c in current_courses:
            code = c.course_code
            target_letter = str(target_grades.get(code, "A")).strip().upper()
            gp = GRADE_POINT_MAP.get(target_letter, 3.75)
            pts = c.credits * gp
            simulated_points += pts
            simulated_credits += c.credits
            details.append({
                "course_code": code,
                "course_name": c.course_name,
                "credits": c.credits,
                "simulated_grade": target_letter,
                "grade_point": gp,
                "total_points": pts,
            })

        simulated_sgpa = simulated_points / simulated_credits if simulated_credits > 0 else 0.0
        new_total_tgp = total_tgp + simulated_points
        new_total_ecr = total_ecr + simulated_credits
        new_cgpa = (
            new_total_tgp / new_total_ecr
            if new_total_ecr > 0
            else 0.0
        )

        delta = round(new_cgpa - curr_cgpa, 3)
        sign = "+" if delta >= 0 else ""

        return {
            "current_cgpa": curr_cgpa,
            "simulated_sgpa": round(simulated_sgpa, 2),
            "new_projected_cgpa": round(new_cgpa, 3),
            "cgpa_delta": f"{sign}{delta}",
            "simulated_courses": details,
            "total_simulated_credits": simulated_credits,
            "completed_tgp": round(total_tgp, 2),
            "completed_credits": round(total_ecr, 2),
            "simulated_points": round(simulated_points, 2),
            "total_tgp": round(new_total_tgp, 2),
            "total_evaluated_credits": round(new_total_ecr, 2),
        }

    def compute_domain_strengths(self, course_domain_map):
        domain_points = {d: [] for d in ACADEMIC_DOMAINS}
        domain_credits = {d: [] for d in ACADEMIC_DOMAINS}
        domain_courses = {d: [] for d in ACADEMIC_DOMAINS}

        for c in self.__profile.get_completed_courses_list():
            code = c.course_code
            domain = course_domain_map.get(code, "CS_CORE")
            if domain in domain_points:
                domain_points[domain].append(c.calculate_weighted_points())
                domain_credits[domain].append(c.credits)
                domain_courses[domain].append(f"{code} ({c.final_grade})")

        results = {}
        for d in ACADEMIC_DOMAINS:
            pts_arr = np.array(domain_points[d], dtype=np.float64)
            cr_arr = np.array(domain_credits[d], dtype=np.float64)
            total_cr = float(np.sum(cr_arr))

            if total_cr > 0:
                domain_gpa = float(np.sum(pts_arr) / total_cr)
                if domain_gpa >= 3.85:
                    eval_str = "Outstanding Mastery"
                elif domain_gpa >= 3.65:
                    eval_str = "High Proficiency"
                elif domain_gpa >= 3.30:
                    eval_str = "Solid Competence"
                else:
                    eval_str = "Room for Improvement"
            else:
                domain_gpa = 0.0
                eval_str = "No Courses Completed"

            results[d] = {
                "domain_name": self._format_domain_title(d),
                "total_credits": round(total_cr, 1),
                "domain_gpa": round(domain_gpa, 2),
                "evaluation": eval_str,
                "course_count": len(domain_points[d]),
                "sample_courses": domain_courses[d][:5],
            }

        return results

    @staticmethod
    def _format_domain_title(domain_key):
        titles = {
            "CS_CORE": "CS & Software Engineering",
            "MATH_STAT": "Mathematics & Statistics",
            "HARDWARE": "Hardware, Circuits & Architecture",
            "BASIC_SCI": "Basic Natural Sciences (Physics/Chem)",
            "BUSINESS": "Business, Economics & Management",
            "HUMANITIES": "Humanities, Languages & Ethics",
        }
        return titles.get(domain_key, domain_key)