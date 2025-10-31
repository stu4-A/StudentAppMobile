# careers/utils/grades.py
from functools import reduce

# -------------------------------
# ✅ Grading Scale
# -------------------------------
GRADE_SCALE = {
    "A": 5.0,
    "B+": 4.5,
    "B": 4.0,
    "C+": 3.5,
    "C": 3.0,
    "D": 2.0,
    "F": 0.0,
}


def get_grade_point(score):
    """
    Determines grade letter and point from numeric score.
    """
    if score >= 80:
        return ("A", GRADE_SCALE["A"])
    elif score >= 75:
        return ("B+", GRADE_SCALE["B+"])
    elif score >= 70:
        return ("B", GRADE_SCALE["B"])
    elif score >= 65:
        return ("C+", GRADE_SCALE["C+"])
    elif score >= 60:
        return ("C", GRADE_SCALE["C"])
    elif score >= 50:
        return ("D", GRADE_SCALE["D"])
    else:
        return ("F", GRADE_SCALE["F"])


# -------------------------------
# Compute GPA for a single semester
# -------------------------------
def compute_gpa(subjects):
    """
    Computes GPA for a semester using map and reduce.
    :param subjects: list of dicts with keys {'name', 'score', 'credits'}
    :return: float GPA
    """
    graded_subjects = list(map(
        lambda s: {**s, **dict(zip(['grade', 'points'], get_grade_point(s['score'])))},
        subjects
    ))

    total_weighted_points = reduce(lambda acc, s: acc + s['points'] * s['credits'], graded_subjects, 0)
    total_credits = reduce(lambda acc, s: acc + s['credits'], graded_subjects, 0)

    return round(total_weighted_points / total_credits, 2) if total_credits else 0.0


# -------------------------------
# Compute CGPA across multiple semesters
# -------------------------------
def compute_cgpa(all_semesters):
    """
    Computes cumulative GPA across multiple semesters.
    :param all_semesters: list of semester dicts {'subjects': [...]}
    :return: float CGPA
    """
    valid_semesters = list(filter(lambda sem: sem['subjects'], all_semesters))
    semester_gpas = list(map(lambda sem: compute_gpa(sem['subjects']), valid_semesters))
    if not semester_gpas:
        return 0.0
    return round(reduce(lambda acc, gpa: acc + gpa, semester_gpas, 0) / len(semester_gpas), 2)


# -------------------------------
# Generate detailed grade report
# -------------------------------
def generate_grade_report(all_semesters):
    """
    Returns a detailed report of semester GPAs and overall CGPA.
    :param all_semesters: list of semester dicts {'subjects': [...]}
    :return: dict {'semesters': [...], 'cgpa': float}
    """
    semester_reports = [
        {
            "semester": i + 1,
            "gpa": compute_gpa(sem["subjects"]),
            "subjects": [
                {**subj, **dict(zip(['grade', 'points'], get_grade_point(subj['score'])))}
                for subj in sem["subjects"]
            ]
        }
        for i, sem in enumerate(all_semesters)
    ]

    overall_cgpa = compute_cgpa(all_semesters)

    return {
        "semesters": semester_reports,
        "cgpa": overall_cgpa,
    }


# -------------------------------
# ✅ compute_gpa_summary for Django views
# -------------------------------
from collections import defaultdict

# careers/utils/grades.py

def compute_gpa_summary(grades_queryset):
    """
    Converts a StudentGrade queryset into a GPA/CGPA summary dict.
    :param grades_queryset: Django queryset of StudentGrade objects
    :return: dict {'gpa': float, 'cgpa': float, 'semesters': [{'semester': str, 'gpa': float}]}
    """
    from collections import defaultdict

    if not grades_queryset.exists():
        return {"gpa": 0.0, "cgpa": 0.0, "semesters": []}

    # Group grades by semester
    semesters = defaultdict(list)
    for g in grades_queryset:
        semesters[g.semester].append(g)

    semester_reports = []
    total_points = 0.0
    total_credits = 0

    for sem, grades in semesters.items():
        sem_points = sum([g.grade_points * g.credit_units for g in grades])
        sem_credits = sum([g.credit_units for g in grades])
        sem_gpa = round(sem_points / sem_credits, 2) if sem_credits else 0.0

        semester_reports.append({
            "semester": sem,
            "gpa": sem_gpa
        })

        total_points += sem_points
        total_credits += sem_credits

    cgpa = round(total_points / total_credits, 2) if total_credits else 0.0

    latest_semester = sorted(semester_reports, key=lambda x: x["semester"].id if x["semester"] else 0, reverse=True)[0]

    return {
        "gpa": latest_semester["gpa"],
        "cgpa": cgpa,
        "semesters": semester_reports
    }
