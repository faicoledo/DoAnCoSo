import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { ApiService } from '../../../core/services/api.service';

interface Attempt {
  id: number;
  assignment_id: number;
  assignment_title: string;
  assignment_type: string;
  score: number | null;
  max_score: number;
  status: string;
  status_display: string;
  submitted_at: string | null;
  feedback: string;
}

interface StudentInfo {
  id: number;
  full_name: string;
  email: string;
  avatar: string | null;
}

@Component({
  selector: 'app-student-grades',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <a [routerLink]="['/teacher/students/course', courseId]" class="back-link">← Quay lại danh sách học viên</a>
          
          <div class="student-header" *ngIf="student">
            <div class="student-avatar">
              @if (student.avatar) {
                <img [src]="student.avatar" [alt]="student.full_name">
              } @else {
                <div class="avatar-placeholder">{{ student.full_name.charAt(0) }}</div>
              }
            </div>
            <div class="student-details">
              <h1>{{ student.full_name }}</h1>
              <p>{{ student.email }}</p>
            </div>
          </div>
          
          <div class="summary-stats" *ngIf="!isLoading">
            <div class="stat">
              <span class="value">{{ attempts.length }}</span>
              <span class="label">Bài đã làm</span>
            </div>
            <div class="stat">
              <span class="value">{{ gradedCount }}</span>
              <span class="label">Đã chấm</span>
            </div>
            <div class="stat">
              <span class="value">{{ averageScore | number:'1.1-1' }}</span>
              <span class="label">Điểm TB</span>
            </div>
          </div>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && attempts.length === 0"
          title="Chưa có bài làm"
          message="Học viên này chưa làm bài tập nào trong khóa học."
        ></app-empty-state>

        <div class="grades-list" *ngIf="!isLoading && attempts.length > 0">
          @for (attempt of attempts; track attempt.id) {
            <app-card class="grade-card">
              <div class="grade-item">
                <div class="assignment-info">
                  <div class="type-badge" [class]="attempt.assignment_type.toLowerCase()">
                    {{ attempt.assignment_type === 'QUIZ' ? '📝 Trắc nghiệm' : '📁 Nộp file' }}
                  </div>
                  <h3>{{ attempt.assignment_title }}</h3>
                  <p class="submitted-at" *ngIf="attempt.submitted_at">
                    Nộp lúc: {{ attempt.submitted_at | date:'dd/MM/yyyy HH:mm' }}
                  </p>
                </div>
                <div class="score-section">
                  <span class="status" [class]="attempt.status.toLowerCase()">{{ attempt.status_display }}</span>
                  <div class="score" *ngIf="attempt.score !== null">
                    <span class="score-value">{{ attempt.score | number:'1.1-1' }}</span>
                    <span class="score-max">/{{ attempt.max_score }}</span>
                  </div>
                  <div class="no-score" *ngIf="attempt.score === null">
                    Chưa chấm
                  </div>
                </div>
              </div>
              <div class="feedback-section" *ngIf="attempt.feedback">
                <strong>Nhận xét:</strong>
                <p>{{ attempt.feedback }}</p>
              </div>
            </app-card>
          }
        </div>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .page-container { padding: 24px; max-width: 900px; margin: 0 auto; }
    .page-header { margin-bottom: 24px; }
    .back-link { color: #0f3460; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 16px; }
    .back-link:hover { text-decoration: underline; }
    
    .student-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
    .student-avatar img, .avatar-placeholder {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      object-fit: cover;
    }
    .avatar-placeholder {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      font-weight: 600;
    }
    .student-details h1 { font-size: 1.5rem; color: #1a1a2e; margin-bottom: 4px; }
    .student-details p { color: #666; }
    
    .summary-stats { display: flex; gap: 24px; padding: 16px 20px; background: #f5f7fa; border-radius: 12px; }
    .stat { display: flex; flex-direction: column; align-items: center; }
    .stat .value { font-size: 1.5rem; font-weight: 700; color: #0f3460; }
    .stat .label { font-size: 0.8rem; color: #888; }
    
    .grades-list { display: flex; flex-direction: column; gap: 16px; }
    
    .grade-item { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
    .assignment-info { flex: 1; }
    .assignment-info h3 { font-size: 1rem; color: #1a1a2e; margin: 8px 0 4px; }
    .submitted-at { font-size: 0.85rem; color: #888; }
    
    .type-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .type-badge.quiz { background: #e8f5e9; color: #2e7d32; }
    .type-badge.submission { background: #e3f2fd; color: #1565c0; }
    
    .score-section { text-align: right; }
    .status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 8px; }
    .status.submitted { background: #fff3e0; color: #ef6c00; }
    .status.graded { background: #e8f5e9; color: #2e7d32; }
    .status.in_progress { background: #e3f2fd; color: #1565c0; }
    
    .score { display: flex; align-items: baseline; justify-content: flex-end; }
    .score-value { font-size: 1.75rem; font-weight: 700; color: #2e7d32; }
    .score-max { font-size: 0.9rem; color: #888; }
    .no-score { color: #888; font-style: italic; }
    
    .feedback-section { margin-top: 12px; padding-top: 12px; border-top: 1px solid #f0f0f0; }
    .feedback-section strong { font-size: 0.9rem; color: #333; }
    .feedback-section p { margin-top: 4px; color: #666; font-size: 0.9rem; }
  `]
})
export class StudentGradesComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);
  
  courseId: number = 0;
  studentId: number = 0;
  student: StudentInfo | null = null;
  attempts: Attempt[] = [];
  isLoading = true;

  get gradedCount(): number {
    return this.attempts.filter(a => a.status === 'GRADED').length;
  }

  get averageScore(): number {
    const graded = this.attempts.filter(a => a.score !== null && a.max_score > 0);
    if (graded.length === 0) return 0;
    const total = graded.reduce((sum, a) => sum + ((a.score || 0) / a.max_score) * 100, 0);
    return total / graded.length;
  }

  ngOnInit(): void {
    this.courseId = Number(this.route.snapshot.paramMap.get('courseId'));
    this.studentId = Number(this.route.snapshot.paramMap.get('studentId'));
    this.loadGrades();
  }

  private loadGrades(): void {
    this.api.get<any>(`/teacher/courses/${this.courseId}/students/${this.studentId}/grades/`).subscribe({
      next: (res) => {
        this.student = res.student;
        this.attempts = res.attempts || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}

