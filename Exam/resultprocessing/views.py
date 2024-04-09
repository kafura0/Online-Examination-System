from django.shortcuts import render

# Create your views here.
from .models import Student, Score

def calculate_gpa(scores):
    total_credit_units = 0
    total_grade_points = 0

    for score in scores:
        total_credit_units += score.course.credit_units
        total_grade_points += (score.total_score / 100) * score.course.credit_units

    if total_credit_units == 0:
        return 0.0
    else:
        return total_grade_points / total_credit_units

def calculate_cgpa(student):
    all_scores = Score.objects.filter(student=student)
    semesters = {score.semester for score in all_scores}
    cgpa = 0.0

    for semester in semesters:
        semester_scores = all_scores.filter(semester=semester)
        semester_gpa = calculate_gpa(semester_scores)
        cgpa += semester_gpa

    return cgpa / len(semesters) if semesters else 0.0

def get_class(gpa):
    if gpa >= 3.5:
        return "First Class"
    elif gpa >= 2.5:
        return "Second Class"
    elif gpa >= 1.5:
        return "Third Class"
    else:
        return "Pass"

def student_results(request, student_id):
    student = Student.objects.get(id=student_id)
    scores = Score.objects.filter(student=student)

    results = [
        {
            'course': score.course,
            'semester': score.semester,
            'total_score': score.total_score,
        }
        for score in scores
    ]
    gpa = calculate_gpa(scores)
    cgpa = calculate_cgpa(student)
    student_class = get_class(gpa)

    context = {
        'student': student,
        'gpa': gpa,
        'cgpa': cgpa,
        'student_class': student_class,
        'results': results
    }

    return render(request, 'student_results.html', context)


def program_result_sheet(request, department_id):
    department_programs = Program.objects.filter(department_id=department_id)
    program_results = []

    for program in department_programs:
        program_students = Student.objects.filter(program=program)
        program_result = {
            'program': program,
            'students': []
        }

        for student in program_students:
            scores = Score.objects.filter(student=student)
            gpa = calculate_gpa(scores)
            cgpa = calculate_cgpa(student)
            student_class = get_class(gpa)

            program_result['students'].append({
                'student': student,
                'gpa': gpa,
                'cgpa': cgpa,
                'student_class': student_class
            })

        program_results.append(program_result)

    context = {
        'department_id': department_id,
        'program_results': program_results
    }

    return render(request, 'program_result_sheet.html', context)
