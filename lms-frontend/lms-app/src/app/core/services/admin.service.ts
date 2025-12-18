import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  role_display: string;
  avatar: string | null;
  is_active: boolean;
  date_joined: string;
}

export interface Subject {
  id: number;
  title: string;
  description: string;
  courses_count: number;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  subject: Subject | null;
  status: string;
  status_display: string;
  start_date: string | null;
  end_date: string | null;
  total_students: number;
  total_modules: number;
}

export interface AdminStats {
  total_users: number;
  total_students: number;
  total_teachers: number;
  total_courses: number;
  total_subjects: number;
  total_enrollments: number;
  total_assignments: number;
  total_attempts: number;
}

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private api = inject(ApiService);

  // Stats
  getStats(): Observable<AdminStats> {
    return this.api.get<AdminStats>('/admin/stats/');
  }

  // Users
  getUsers(): Observable<User[]> {
    return this.api.get<User[]>('/admin/users/');
  }

  getUser(id: number): Observable<User> {
    return this.api.get<User>(`/admin/users/${id}/`);
  }

  createUser(data: any): Observable<User> {
    return this.api.post<User>('/admin/users/', data);
  }

  updateUser(id: number, data: any): Observable<User> {
    return this.api.patch<User>(`/admin/users/${id}/`, data);
  }

  deleteUser(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/users/${id}/`);
  }

  // Subjects
  getSubjects(): Observable<Subject[]> {
    return this.api.get<Subject[]>('/admin/subjects/');
  }

  createSubject(data: any): Observable<Subject> {
    return this.api.post<Subject>('/admin/subjects/', data);
  }

  updateSubject(id: number, data: any): Observable<Subject> {
    return this.api.patch<Subject>(`/admin/subjects/${id}/`, data);
  }

  deleteSubject(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/subjects/${id}/`);
  }

  // Courses
  getCourses(): Observable<Course[]> {
    return this.api.get<Course[]>('/admin/courses/');
  }

  getCourse(id: number): Observable<Course> {
    return this.api.get<Course>(`/admin/courses/${id}/`);
  }

  createCourse(data: any): Observable<Course> {
    return this.api.post<Course>('/admin/courses/', data);
  }

  updateCourse(id: number, data: any): Observable<Course> {
    return this.api.patch<Course>(`/admin/courses/${id}/`, data);
  }

  deleteCourse(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/courses/${id}/`);
  }

  // Enrollments
  getEnrollments(courseId?: number): Observable<any[]> {
    const url = courseId ? `/admin/enrollments/?course=${courseId}` : '/admin/enrollments/';
    return this.api.get<any[]>(url);
  }

  createEnrollment(data: any): Observable<any> {
    return this.api.post<any>('/admin/enrollments/', data);
  }

  deleteEnrollment(id: number): Observable<void> {
    return this.api.delete<void>(`/admin/enrollments/${id}/`);
  }
}

