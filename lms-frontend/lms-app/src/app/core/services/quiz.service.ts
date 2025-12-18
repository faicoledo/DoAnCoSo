import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { QuizStart, QuizSubmit, AttemptResult } from '../models';

export interface AssignmentInfo {
  id: number;
  title: string;
  time_limit: number | null;
  attempts_allowed: number | null;
  attempts_remaining: number | null;
  can_start: boolean;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class QuizService {
  constructor(private api: ApiService) {}

  getAssignmentInfo(assignmentId: number): Observable<AssignmentInfo> {
    return this.api.get<AssignmentInfo>(`/assessments/assignments/${assignmentId}/info/`);
  }

  startQuiz(assignmentId: number): Observable<QuizStart> {
    return this.api.post<QuizStart>(`/assessments/assignments/${assignmentId}/start/`, {});
  }

  submitQuiz(attemptId: number, data: QuizSubmit): Observable<any> {
    return this.api.post(`/assessments/attempts/${attemptId}/submit/`, data);
  }

  getAttemptResult(attemptId: number): Observable<AttemptResult> {
    return this.api.get<AttemptResult>(`/assessments/attempts/${attemptId}/result/`);
  }

  getMyAttempts(assignmentId: number): Observable<any[]> {
    return this.api.get<any[]>(`/assessments/assignments/${assignmentId}/my-attempts/`);
  }
}


