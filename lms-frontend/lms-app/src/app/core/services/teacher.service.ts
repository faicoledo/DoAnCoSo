import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Course } from '../models';

export interface TeacherStats {
  total_courses: number;
  total_students: number;
  total_assignments: number;
  pending_submissions: number;
}

export interface Submission {
  id: number;
  student: {
    id: number;
    full_name: string;
    email: string;
  };
  assignment_title: string;
  submitted_at: string;
  score?: number;
  status: string;
  submitted_file?: string;
  submitted_text?: string;
}

@Injectable({
  providedIn: 'root'
})
export class TeacherService {
  constructor(private api: ApiService) {}

  getStats(): Observable<TeacherStats> {
    return this.api.get<TeacherStats>('/teacher/stats/');
  }

  getMyCourses(): Observable<Course[]> {
    return this.api.get<Course[]>('/teacher/courses/');
  }

  getCourseStudents(courseId: number): Observable<any[]> {
    return this.api.get<any[]>(`/teacher/courses/${courseId}/students/`);
  }

  getAssignmentSubmissions(assignmentId: number): Observable<Submission[]> {
    return this.api.get<Submission[]>(`/teacher/assignments/${assignmentId}/submissions/`);
  }

  getAllSubmissions(): Observable<Submission[]> {
    return this.api.get<Submission[]>('/teacher/submissions/');
  }

  gradeSubmission(attemptId: number, score: number, feedback?: string): Observable<any> {
    return this.api.post(`/assessments/attempts/${attemptId}/grade/`, { score, feedback });
  }

  importQuestions(assignmentId: number, file: File): Observable<any> {
    return this.api.uploadFile(`/assessments/assignments/${assignmentId}/import-excel/`, file, 'file');
  }
}


