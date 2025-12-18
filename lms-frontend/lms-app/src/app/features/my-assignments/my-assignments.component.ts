import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainLayoutComponent } from '../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../shared/components';
import { ApiService } from '../../core/services';

interface Attempt {
  id: number;
  assignment_title: string;
  assignment_type: string;
  course_title: string;
  status: string;
  status_display: string;
  score: number | null;
  max_score: number | null;
  feedback: string;
  submitted_at: string | null;
  started_at: string;
}

@Component({
  selector: 'app-my-assignments',
  standalone: true,
  imports: [CommonModule, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <h1>Bài tập của tôi</h1>
          <p>Danh sách các bài tập đã làm và điểm số</p>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && attempts.length === 0"
          title="Chưa có bài tập nào"
          message="Bạn chưa làm bài tập nào. Hãy vào khóa học để bắt đầu làm bài."
        ></app-empty-state>

        <div class="attempts-list" *ngIf="!isLoading && attempts.length > 0">
          <app-card *ngFor="let attempt of attempts" class="attempt-card">
            <div class="attempt-item">
              <div class="attempt-info">
                <div class="title-row">
                  <h3 class="assignment-title">{{ attempt.assignment_title }}</h3>
                  <span class="type-badge" [ngClass]="attempt.assignment_type.toLowerCase()">
                    {{ attempt.assignment_type === 'QUIZ' ? '📝 Trắc nghiệm' : '📁 Nộp file' }}
                  </span>
                </div>
                <p class="course-title">{{ attempt.course_title }}</p>
                <p class="submitted-time" *ngIf="attempt.submitted_at">
                  Nộp lúc: {{ attempt.submitted_at | date:'dd/MM/yyyy HH:mm' }}
                </p>
              </div>
              <div class="attempt-score">
                <span class="status-badge" [ngClass]="getStatusClass(attempt.status)">
                  {{ attempt.status_display }}
                </span>
                <div class="score" *ngIf="attempt.score !== null">
                  <span class="score-value">{{ attempt.score }}</span>
                  <span class="score-max" *ngIf="attempt.max_score">/{{ attempt.max_score }}</span>
                </div>
              </div>
            </div>
            <!-- Feedback section -->
            <div class="feedback-section" *ngIf="attempt.status === 'GRADED'">
              <div class="feedback-header">
                <span class="feedback-label">📋 Nhận xét của giảng viên:</span>
              </div>
              <p class="feedback-content" *ngIf="attempt.feedback">{{ attempt.feedback }}</p>
              <p class="feedback-empty" *ngIf="!attempt.feedback">Không có nhận xét</p>
            </div>
          </app-card>
        </div>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .page-container {
      padding: 24px;
      max-width: 900px;
      margin: 0 auto;
    }
    .page-header {
      margin-bottom: 24px;
    }
    .page-header h1 {
      font-size: 1.8rem;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    .page-header p {
      color: #666;
    }
    .attempts-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .attempt-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }
    .attempt-info {
      flex: 1;
    }
    .assignment-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    .course-title {
      color: #666;
      font-size: 0.9rem;
      margin-bottom: 4px;
    }
    .submitted-time {
      color: #888;
      font-size: 0.85rem;
    }
    .attempt-score {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
    }
    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .status-badge.in-progress {
      background: #fff3cd;
      color: #856404;
    }
    .status-badge.submitted {
      background: #cce5ff;
      color: #004085;
    }
    .status-badge.graded {
      background: #d4edda;
      color: #155724;
    }
    .score {
      font-size: 1.5rem;
      font-weight: 700;
      color: #0f3460;
    }
    .score-max {
      font-size: 1rem;
      color: #666;
    }
    .title-row {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .type-badge {
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .type-badge.quiz {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .type-badge.submission {
      background: #e3f2fd;
      color: #1565c0;
    }
    .feedback-section {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #eee;
    }
    .feedback-header {
      margin-bottom: 8px;
    }
    .feedback-label {
      font-weight: 600;
      color: #333;
      font-size: 0.9rem;
    }
    .feedback-content {
      background: #f8f9fa;
      padding: 12px 16px;
      border-radius: 8px;
      color: #333;
      line-height: 1.5;
      border-left: 3px solid #0f3460;
    }
    .feedback-empty {
      color: #888;
      font-style: italic;
      font-size: 0.9rem;
    }
  `]
})
export class MyAssignmentsComponent implements OnInit {
  api = inject(ApiService);
  attempts: Attempt[] = [];
  isLoading = true;

  ngOnInit(): void {
    this.loadAttempts();
  }

  private loadAttempts(): void {
    this.api.get<{ results: Attempt[] }>('/assessments/my-attempts/').subscribe({
      next: (res) => {
        this.attempts = res.results;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'IN_PROGRESS': return 'in-progress';
      case 'SUBMITTED': return 'submitted';
      case 'GRADED': return 'graded';
      default: return '';
    }
  }
}

