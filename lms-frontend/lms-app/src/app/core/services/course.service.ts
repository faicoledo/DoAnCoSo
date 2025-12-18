import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Course, Lesson } from '../models';

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  constructor(private api: ApiService) {}

  // Catalog APIs
  getCourses(params?: { subject?: number; search?: string; page?: number }): Observable<PaginatedResponse<Course>> {
    return this.api.get<PaginatedResponse<Course>>('/catalog/courses/', params);
  }

  getCourseDetail(id: number): Observable<Course> {
    return this.api.get<Course>(`/catalog/courses/${id}/`);
  }

  getMyCourses(params?: { status?: string; role?: string }): Observable<PaginatedResponse<Course>> {
    return this.api.get<PaginatedResponse<Course>>('/catalog/my-courses/', params);
  }

  getLessonDetail(id: number): Observable<Lesson> {
    return this.api.get<Lesson>(`/catalog/lessons/${id}/`);
  }

  enrollCourse(courseId: number): Observable<any> {
    return this.api.post(`/catalog/courses/${courseId}/enroll/`, {});
  }

  // Subject APIs
  getSubjects(): Observable<any[]> {
    return this.api.get<any[]>('/catalog/subjects/');
  }

  // Stats APIs
  getSubmittedAttemptsCount(): Observable<{ count: number }> {
    return this.api.get<{ count: number }>('/assessments/my-attempts/count/');
  }
}


