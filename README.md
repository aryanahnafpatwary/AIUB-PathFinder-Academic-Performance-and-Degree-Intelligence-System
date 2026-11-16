# AIUB-PathFinder: Academic Performance and Degree Intelligence System

CSC 4162 / BSE 4112: Programming in Python | Mid-Term Project | Fall 2026-27
American International University-Bangladesh (AIUB)

---

## Overview

AIUB-PathFinder is a desktop application that helps an AIUB BSc in Computer Science and Engineering student understand an academic record. It reads the two official grade reports issued by the university (Grade Report by Semester and Grade Report by Curriculum), builds a structured record in memory, and reports on it with NumPy statistics, a trend forecast, a what-if grade simulator, a prerequisite unlock check and a specialization track ranking.

The core logic is written in plain Python with classes, lists, tuples, sets and dictionaries. NumPy is used for the numerical work, and Tkinter provides a fallback interface. The application reads files only. It does not write student data to disk, and the loaded record is cleared when the application is closed.

## Problem Statement

A student must complete 148 credits, and prerequisite rules decide the order of many courses. The grade reports list results but do not show which remaining courses are open, how current grades will change the CGPA, which subject areas are strongest, or which specialization track fits the completed work. This project answers those questions from the student's own reports.

## Features

| No. | Feature | Description |
|:---:|:---|:---|
| 1 | Dual report intake | Reads the Grade Report by Semester (PDF or TXT) and the Grade Report by Curriculum (PDF). Extracts student identity, semesters, completed and ongoing courses, and remaining curriculum requirements. A demo profile can be loaded with one action. |
| 2 | Statistical overview | Mean, median, standard deviation, variance, quartiles, best and lowest semester, and a consistency rating based on the standard deviation of SGPA. |
| 3 | Progression chart | CGPA and SGPA for each semester with a hover tooltip, a momentum figure and an honors standing label. Drawn as SVG in the dashboard and on a Canvas in the Tkinter interface. |
| 4 | Subject domain strength | Credit-weighted GPA across six domains: CS and Software Engineering, Mathematics and Statistics, Hardware, Basic Sciences, Business, and Humanities. Each domain receives a rating. |
| 5 | Forecast and what-if simulator | A linear forecast of the next SGPA from `np.polyfit`, and a simulator in which the user selects a grade for each current course, or uses a preset, to see the projected SGPA and CGPA. |
| 6 | Prerequisite unlock engine | Lists remaining core courses and eligible electives. A course is open when its prerequisite set is a subset of the completed course codes. |
| 7 | Specialization track matcher | Ranks four tracks from foundation course grades and the number of accessible electives. |

### Availability by interface

| Interface | Features |
|:---|:---|
| Dashboard (pywebview, `login.html` and `code.html`) | 1 to 5 |
| Tkinter interface (`--tkinter`) | 2 to 7, using the bundled sample report |

The dashboard bridge already prepares the unlock and track data. Showing it in the dashboard is listed under future work.

## Application Workflow

```
Grade Report by Semester (PDF/TXT)    Grade Report by Curriculum (PDF)    aiub_curriculum.csv
                  \                              /                                  |
                   v                            v                                   v
                      GradeReportParser (pypdf, re)                       CurriculumEngine (csv)
                                  |                                                 |
                                  v                                                 v
                     StudentAcademicProfile  ------------------------>  unlock and track ranking (sets)
                                  |                                                 |
                                  v                                                 |
                    AcademicAnalyticsEngine (NumPy)                                 |
                          |                 \                                       |
                          v                  v                                      v
             PathFinderBridge + dashboard    PathFinderDesktopApp (Tkinter) <-------+
```

`main.py` calls the launch function in `desktop_app.py`. The launcher opens the intake page `login.html` in a native pywebview window. If the `--tkinter` option is given, or the web view cannot start, the Tkinter interface opens instead.

## Project Structure

```
.
|-- main.py                     Entry point of the application
|-- desktop_app.py              Interface layer: PathFinderBridge, PathFinderDesktopApp, launch logic
|-- data/
|   |-- aiub_curriculum.csv                     Curriculum database (101 courses, curricula 309 and 338)
|   |-- sample_grade_report.txt                 Sample grade report in text form
|   |-- GradeReportBySemester23-54787-3.pdf     Sample Grade Report by Semester
|   `-- GradeReportByCurriculum23-54787-3.pdf   Sample Grade Report by Curriculum
|-- src/
|   |-- __init__.py
|   |-- models.py               Course, semester and student classes
|   |-- curriculum_engine.py    Curriculum loading, prerequisite logic, track matcher
|   |-- analytics.py            NumPy statistics, forecast, simulation, domain strength
|   `-- report_parser.py        PDF and TXT grade report parser
`-- stitch_dashboard/
    |-- login.html              Intake page for the two grade reports
    |-- code.html               Dashboard page
    `-- tailwind.min.js         Local styling bundle
```

## Requirements

- Python 3.10 or later
- Windows with Edge WebView2 for the dashboard. The Tkinter interface runs on Windows, Linux and macOS.

Install the third-party packages:

```bash
pip install numpy pypdf pywebview
```

Tkinter is part of the standard Python installation on Windows and macOS. On some Linux distributions it is installed separately, for example with the `python3-tk` package.

## How to Run

Start the dashboard:

```bash
python main.py
```

Start the Tkinter interface:

```bash
python main.py --tkinter
```

### Using the dashboard

1. On the intake page, select the Grade Report by Semester and the Grade Report by Curriculum, or choose the demo option to load the bundled sample files.
2. Submit the files. The application parses both reports and opens the dashboard.
3. Review the summary cards, the progression chart, the domain strength panel and the what-if simulator.
4. In the simulator, choose a grade for each current course or press a preset button to see the projected SGPA and CGPA.
5. Use the quit button to close the application. The loaded record is cleared from memory.

### Using the Tkinter interface

The interface loads `data/sample_grade_report.txt` and shows summary cards and five tabs: CGPA chart, domain strengths, what-if simulator, course unlocks and major specializations.

## Calculation Methods

| Item | Method |
|:---|:---|
| CGPA | `total_tgp / total_ecr`, summed over completed semesters, following the AIUB formula |
| Weighted points of a course | `credits * grade_point` |
| Grade scale | A+ 4.00, A 3.75, B+ 3.50, B 3.25, C+ 3.00, C 2.75, D+ 2.50, D 2.25, F 0.00 |
| Consistency rating | Population standard deviation of semester SGPA: below 0.10 is highly stable, below 0.20 is consistent, otherwise volatile |
| Next SGPA forecast | Degree 1 `np.polyfit` over semester index and SGPA, evaluated at the next index and limited to 0.00 to 4.00 |
| Recent average | Weights 0.2, 0.3 and 0.5 applied to the last three semesters |
| Domain GPA | Sum of weighted points divided by sum of credits for the courses in the domain |
| Track match score | 70 percent of foundation GPA (as a share of 4.00) plus 30 percent of elective accessibility |

The track weights are a design choice of this project and not an AIUB rule.

## Python Concepts Demonstrated

| Concept | Where it appears |
|:---|:---|
| Variables and data types | `float` credits and grade points, `int` counts, `str` identifiers, `bool` flags |
| Operators | Weighted points, CGPA division, range checks, membership tests |
| Conditional statements | Rating labels, honors label, file type selection |
| Loops | `while` loops that rejoin PDF lines, `for` loops over semesters, courses and tracks |
| Functions and methods | Over forty functions and methods across six modules |
| List | Semester and course collections, ranked track results |
| Tuple | `AIUB_GRADE_POINTS`, `ACADEMIC_DOMAINS`, `(semester, sgpa, credits)` history entries |
| Set | Prerequisites, completed course codes, track foundation codes (`issubset`, `difference`, `intersection`) |
| Dictionary | Course catalog, domain map, grade point map, track definitions, name to code lookup |
| File handling | `csv.DictReader` for the curriculum, `open()` for text reports, `pypdf` for PDF reports |
| Exception handling | `FileNotFoundError`, `ValueError`, `TypeError`, and status dictionaries returned by the bridge |
| Object-oriented programming | Encapsulation, inheritance, polymorphism and aggregation |

## Object-Oriented Design

```
AcademicCourse                      (base class)
  |-- CompletedCourse               (grades, earned credits, in-progress flag)
  `-- CurriculumCourse              (prerequisite set, semester slot, domain)

StudentAcademicProfile  has many  SemesterRecord  has many  CompletedCourse
CurriculumEngine        has many  CurriculumCourse
```

| Class | Role |
|:---|:---|
| `AcademicCourse` | Base class with private code, name and credits. The credits setter rejects non-numeric values and values outside 0 to 10. |
| `CompletedCourse` | Adds grade fields. Overrides `is_passed()`, `calculate_weighted_points()` and `get_summary()`. |
| `CurriculumCourse` | Adds the prerequisite set. Provides `is_unlocked()` and `missing_prerequisites()`. |
| `SemesterRecord` | Holds the courses of one semester with SGPA, CGPA, TGP and ECR. |
| `StudentAcademicProfile` | Holds the student identity, semesters and completed credits, with validating setters. |
| `CurriculumEngine` | Loads the curriculum CSV and answers unlock and track queries. |
| `GradeReportParser` | Converts PDF or text reports into profile objects. |
| `AcademicAnalyticsEngine` | Performs all NumPy calculations on a profile. |
| `PathFinderBridge` | Exposes Python methods to the dashboard through pywebview. |
| `PathFinderDesktopApp` | Builds the Tkinter fallback interface. |

## Error Handling

| Case | Behavior |
|:---|:---|
| Missing curriculum CSV or report file | `FileNotFoundError` with the file path. The bridge returns an error message and Tkinter shows a message box. |
| Report with no semester records | `ValueError` explaining that the format should be checked. |
| Course name not in the curriculum | The course receives the placeholder code `GEN0000` and parsing continues. |
| Invalid credits, CGPA, identity values | Setters raise `TypeError` or `ValueError`. |
| One or both intake files missing | A notice is shown and the bridge repeats the check. |
| Cancelled file dialog | The bridge returns a cancelled status. |
| Unknown grade in a simulation call | Falls back to 3.75. The interface uses a fixed list of grades. |
| Fewer than two semesters for a forecast | An error entry is returned instead of an exception. |
| Web view cannot start | The Tkinter interface opens. |

## Limitations

- Only the BSc in CSE curricula 309 (core) and 338 (electives) are modeled.
- Parsing depends on the current layout of the AIUB PDF reports. A layout change would require updated regular expressions.
- Courses whose names are missing from the curriculum file and the alias table do not count toward prerequisites.
- The forecast is a straight line fitted to a short series and gives an indication only.
- The unlock and track views are available only in the Tkinter interface at present.
- No data is saved between runs.

## Future Work

The final-term plan is to move the data layer to Pandas, add Matplotlib charts, and show the unlock and track views in the dashboard. Further items include saving a summary to CSV or JSON, support for other AIUB programs through additional curriculum files, and a cohort view for advisors.

## Academic Integrity

This project was developed for the CSC 4162 / BSE 4112 Programming in Python course at AIUB and follows the university academic integrity policy.
