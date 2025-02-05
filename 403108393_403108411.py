import json
import os
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from datetime import datetime, time
from typing import Dict, List, Optional, Union
import unittest

class User:
    def __init__(self, id: str, name: str, email: str, password: str, phone: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = self._hash_password(password)
        self.phone = phone
        self.stay_logged_in = False
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self._hash_password(password) == self.password


class Student(User):
    def __init__(self, id: str, name: str, email: str, password: str, phone: str):
        super().__init__(id, name, email, password, phone)
        self.enrolled_courses: List[str] = []


class Professor(User):
    def __init__(self, id: str, name: str, email: str, password: str, phone: str):
        super().__init__(id, name, email, password, phone)
        self.courses: List[str] = []


class Course:
    def __init__(self, id: str, name: str, professor: Professor, capacity: int):
        self.id = id
        self.name = name
        self.professor = professor
        self.capacity = capacity
        self.students: List[Student] = []
        self.schedules: List[ClassSchedule] = []
        self.grade_components = {
            'Quiz 1': 0,
            'Midterm': 0,
            'Quiz 2': 0,
            'Final': 0,
            'Assignments': 0
        }
        self.student_grades: Dict[str, Dict[str, float]] = {}
        self.is_grades_visible = False

    def add_student(self, student: Student):
        if len(self.students) < self.capacity:
            self.students.append(student)
            student.enrolled_courses.append(self.id)
            self.student_grades[student.id] = {
                comp: 0 for comp in self.grade_components.keys()}
            print(f"{student.name} successfully enrolled in {self.name}.")
        else:
            print("Course is full!")


class ClassSchedule:
    def __init__(self, day: str, start_time: time, end_time: time):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class LearningManagementSystem:
    def __init__(self):
        self.users: Dict[str, Union[Student, Professor]] = {}
        self.courses: Dict[str, Course] = {}
        self.logged_in_users: Dict[str, Union[Student, Professor]] = {}
        self.load_data()

    def generate_student_id(self) -> str:
        """Generate a unique 9-digit student ID"""
        while True:
            student_id = '4' + \
                ''.join([str(random.randint(0, 9)) for _ in range(8)])
            if student_id not in self.users:
                return student_id

    def generate_professor_id(self) -> str:
        """Generate a unique 4-digit professor ID"""
        while True:
            professor_id = '1' + \
                ''.join([str(random.randint(0, 9)) for _ in range(3)])
            if professor_id not in self.users:
                return professor_id

    def register_user(self) -> Optional[Union[Student, Professor]]:
        """Register a new user"""
        print("\n=== User Registration ===")
        print("1. Student")
        print("2. Professor")
        user_type = input("Select user type: ").strip()

        name = input("Enter full name: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        phone = input("Enter phone number: ").strip()

        if user_type == "1":
            user_id = self.generate_student_id()
            user = Student(user_id, name, email, password, phone)
            print(f"Generated Student ID: {user_id}")
        elif user_type == "2":
            user_id = self.generate_professor_id()
            user = Professor(user_id, name, email, password, phone)
            print(f"Generated Professor ID: {user_id}")
        else:
            print("Invalid user type!")
            return None

        self.users[user_id] = user
        self.save_data()
        print("Registration successful!")
        return user

    def login(self) -> Optional[Union[Student, Professor]]:
        """User login"""
        print("\n=== Login ===")
        id = input("Enter ID: ").strip()

        if id in self.logged_in_users:
            return self.logged_in_users[id]

        password = input("Enter password: ").strip()

        if id in self.users and self.users[id].check_password(password):
            user = self.users[id]
            stay_logged_in = input(
                "Stay logged in? (y/n): ").strip().lower() == 'y'
            user.stay_logged_in = stay_logged_in
            if stay_logged_in:
                self.logged_in_users[id] = user
            self.save_data()
            print("Login successful!")
            return user

        print("Invalid credentials!")
        return None

    def student_menu(self, student: Student):
        """Student menu"""
        while True:
            print("\n=== Student Menu ===")
            print("1. View Available Courses")
            print("2. Enroll in Course")
            print("3. View My Grades")
            print("4. Logout")

            choice = input("Select option: ").strip()

            if choice == "1":
                self.list_courses()
            elif choice == "2":
                course_id = input("Enter course ID: ").strip()
                if course_id in self.courses:
                    self.courses[course_id].add_student(student)
            elif choice == "3":
                self.view_student_grades(student)
            elif choice == "4":
                self.logout(student.id)
                break

    def professor_menu(self, professor: Professor):
        """Professor menu"""
        while True:
            print("\n=== Professor Menu ===")
            print("1. Create New Course")
            print("2. View My Courses")
            print("3. Manage Grades")
            print("4. Export Grade Sheet")
            print("5. View Class Statistics")
            print("6. Logout")

            choice = input("Select option: ").strip()

            if choice == "1":
                self.create_course(professor)
            elif choice == "2":
                self.list_professor_courses(professor)
            elif choice == "3":
                self.manage_grades(professor)
            elif choice == "4":
                self.export_grades(professor)
            elif choice == "5":
                self.view_class_statistics(professor)
            elif choice == "6":
                self.logout(professor.id)
                break

    def save_data(self):
        """Save system data to JSON file"""
        data = {
            'users': {
                uid: {
                    'type': 'Student' if isinstance(user, Student) else 'Professor',
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'password': user.password,
                    'phone': user.phone,
                    'stay_logged_in': user.stay_logged_in,
                    'enrolled_courses' if isinstance(user, Student) else 'courses':
                        user.enrolled_courses if isinstance(
                            user, Student) else user.courses
                }
                for uid, user in self.users.items()
            },
            'courses': {}
        }

        with open('lms_data.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        """Load system data from JSON file"""
        if not os.path.exists('lms_data.json'):
            return

        with open('lms_data.json', 'r') as f:
            data = json.load(f)

        # Load users
        for uid, user_data in data['users'].items():
            user_class = Student if user_data['type'] == 'Student' else Professor
            user = user_class(
                user_data['id'],
                user_data['name'],
                user_data['email'],
                '',
                user_data['phone']
            )
            user.password = user_data['password']
            user.stay_logged_in = user_data['stay_logged_in']
            if isinstance(user, Student):
                user.enrolled_courses = user_data['enrolled_courses']
            else:
                user.courses = user_data['courses']
            self.users[uid] = user

            if user.stay_logged_in:
                self.logged_in_users[uid] = user

    def list_courses(self):
        """Display all available courses"""
        print("\n=== Available Courses ===")
        for course in self.courses.values():
            print(f"\nCourse ID: {course.id}")
            print(f"Name: {course.name}")
            print(f"Professor: {course.professor.name}")
            print(f"Capacity: {len(course.students)}/{course.capacity}")

    def create_course(self, professor: Professor):
        """Create a new course"""
        print("\n=== Create New Course ===")
        name = input("Enter course name: ").strip()
        try:
            capacity = int(input("Enter course capacity: ").strip())
        except ValueError:
            print("Invalid capacity!")
            return None

        course_id = str(random.randint(1000, 9999))
        while course_id in self.courses:
            course_id = str(random.randint(1000, 9999))

        course = Course(course_id, name, professor, capacity)
        self.courses[course_id] = course
        professor.courses.append(course_id)
        self.save_data()
        print(f"Course created successfully! Course ID: {course_id}")

    def manage_grades(self, professor: Professor):
        """Manage grades for a course"""
        print("\n=== Manage Grades ===")
        course_id = input("Enter course ID: ").strip()
        if course_id not in professor.courses:
            print("Invalid course ID!")
            return

        course = self.courses[course_id]
        print("\n1. Enter grades\n2. Toggle grade visibility")
        choice = input("Select option: ").strip()

        if choice == "1":
            for student in course.students:
                print(f"\nStudent: {student.name} ({student.id})")
                for component in course.grade_components.keys():
                    try:
                        grade = float(input(f"Enter {component} grade: ").strip())
                        course.student_grades[student.id][component] = grade
                    except ValueError:
                        print("Invalid grade! Please enter a number.")
        elif choice == "2":
            course.is_grades_visible = not course.is_grades_visible
            print(f"Grades visibility set to {course.is_grades_visible}")
        else:
            print("Invalid option!")
            return

        self.save_data()
        print("Grades updated successfully!")

    def view_class_statistics(self, professor: Professor):
        """Show class performance statistics with Pandas & Matplotlib"""
        course_id = input("Enter course ID: ").strip()
        if course_id in professor.courses:
            course = self.courses[course_id]
            if not course.student_grades:
                print("No grades available for this course.")
                return

            df = pd.DataFrame.from_dict(course.student_grades, orient='index')
            print(df.describe())  # نمایش خلاصه آماری نمرات

            plt.figure(figsize=(8, 5))
            sns.boxplot(data=df)
            plt.title(f"Grade Distribution for {course.name}")
            plt.xlabel("Grade Components")
            plt.ylabel("Scores")
            plt.show()

    def export_grades(self, professor: Professor):
        """Export grades to a CSV file"""
        course_id = input("Enter course ID: ").strip()
        if course_id not in professor.courses:
            print("Invalid course ID!")
            return

        course = self.courses[course_id]
        if not course.student_grades:
            print("No grades available for this course.")
            return

        df = pd.DataFrame.from_dict(course.student_grades, orient='index')
        df['Total'] = df.sum(axis=1)  # Add a total column
        filename = f"grades_{course_id}.csv"
        df.to_csv(filename)
        print(f"Grades exported successfully to {filename}!")

    def view_student_grades(self, student: Student):
        """Display grades for a student"""
        print("\n=== Your Grades ===")
        for course_id in student.enrolled_courses:
            if course_id in self.courses:
                course = self.courses[course_id]
                if course.is_grades_visible:
                    print(f"\nCourse: {course.name} ({course.id})")
                    grades = course.student_grades.get(student.id, {})
                    for component, score in grades.items():
                        print(f"{component}: {score}")
                    total = sum(grades.values())
                    print(f"Total Grade: {total}")
                else:
                    print(f"\nGrades for {course.name} are not yet available.")
            else:
                print(f"\nCourse {course_id} no longer exists.")

    def list_professor_courses(self, professor: Professor):
        """List courses taught by the professor"""
        print("\n=== Your Courses ===")
        for course_id in professor.courses:
            if course_id in self.courses:
                course = self.courses[course_id]
                print(f"ID: {course.id}, Name: {course.name}, Students Enrolled: {len(course.students)}/{course.capacity}")
            else:
                print(f"Course {course_id} not found.")

    def logout(self, user_id: str):
        """User logout"""
        if user_id in self.users:
            self.users[user_id].stay_logged_in = False
            if user_id in self.logged_in_users:
                del self.logged_in_users[user_id]
            self.save_data()
            print("Logged out successfully!")


def main():
    lms = LearningManagementSystem()

    while True:
        print("\n=== Learning Management System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            user = lms.register_user()
        elif choice == "2":
            user = lms.login()
            if user:
                if isinstance(user, Professor):
                    lms.professor_menu(user)
                elif isinstance(user, Student):
                    lms.student_menu(user)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
