import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { TeacherService, Submission } from '../../../core/services/teacher.service';

@Component({
  selector: 'app-submission-list',
  standalone: true,
  imports: [CommonModule, FormsModule, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="submission-list">
        <div class="page-header">
          <h1>Bài nộp cần chấm điểm</h1>
          <p>Danh sách bài tập học viên đã nộp</p>
        </div>
        
        <!-- Filter tabs -->
        <div class="filter-tabs">
          <button 
            class="tab" 
            [class.active]="currentFilter === 'all'"
            (click)="filterSubmissions('all')"
          >
            Tất cả ({{ allSubmissions.length }})
          </button>
          <button 
            class="tab" 
            [class.active]="currentFilter === 'SUBMISSION'"
            (click)="filterSubmissions('SUBMISSION')"
          >
            📁 Bài nộp file ({{ fileSubmissions.length }})
          </button>
          <button 
            class="tab" 
            [class.active]="currentFilter === 'QUIZ'"
            (click)="filterSubmissions('QUIZ')"
          >
            📝 Trắc nghiệm ({{ quizSubmissions.length }})
          </button>
        </div>
        
        @if (isLoading) {
          <app-loading message="Đang tải bài nộp..."></app-loading>
        } @else if (submissions.length === 0) {
          <app-empty-state 
            title="Chưa có bài nộp"
            description="Chưa có học viên nào nộp bài"
          ></app-empty-state>
        } @else {
          <div class="submissions">
            @for (submission of submissions; track submission.id) {
              <app-card>
                <div class="submission-item">
                  <div class="submission-header">
                    <div class="student-info">
                      @if (submission.student.avatar) {
                        <img class="avatar-img" [src]="submission.student.avatar" [alt]="submission.student.full_name">
                      } @else {
                        <div class="avatar">{{ submission.student.full_name.charAt(0) }}</div>
                      }
                      <div>
                        <h3>{{ submission.student.full_name }}</h3>
                        <p>{{ submission.student.email }}</p>
                      </div>
                    </div>
                    <div class="type-badge" [class]="submission.assignment_type?.toLowerCase()">
                      {{ submission.assignment_type === 'QUIZ' ? '📝 Trắc nghiệm' : '📁 Nộp file' }}
                    </div>
                  </div>
                  
                  <div class="assignment-info">
                    <strong>{{ submission.assignment_title }}</strong>
                  </div>
                  
                  <div class="submission-meta">
                    <span class="submitted-at">Nộp lúc: {{ submission.submitted_at | date:'dd/MM/yyyy HH:mm' }}</span>
                    <span class="status" [class]="submission.status.toLowerCase()">
                      {{ getStatusText(submission.status) }}
                    </span>
                  </div>
                  
                  <!-- Quiz result -->
                  @if (submission.assignment_type === 'QUIZ') {
                    <div class="quiz-result">
                      <div class="quiz-stats">
                        <span>Đúng: {{ submission.correct_count }}/{{ submission.total_questions }} câu</span>
                      </div>
                      <div class="auto-score">
                        <span class="label">Điểm tự động:</span>
                        <span class="score-value">{{ submission.auto_score | number:'1.1-1' }}/{{ submission.max_score }}</span>
                      </div>
                    </div>
                  }
                  
                  <!-- File submission content -->
                  @if (submission.assignment_type !== 'QUIZ') {
                    <div class="submission-content">
                      @if (submission.submitted_file) {
                        <a [href]="submission.submitted_file" target="_blank" class="file-link">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                          </svg>
                          Tải file bài nộp
                        </a>
                      }
                      @if (submission.submitted_text) {
                        <div class="text-content">
                          <strong>Nội dung:</strong>
                          <p>{{ submission.submitted_text }}</p>
                        </div>
                      }
                    </div>
                  }
                  
                  <!-- Grading section -->
                  <div class="grading-section">
                    @if (submission.assignment_type === 'QUIZ') {
                      <!-- Quiz: show auto score with inline edit -->
                      <div class="quiz-grading">
                        <div class="inline-grade-form">
                          <div class="score-input-group">
                            <label>Điểm:</label>
                            <input 
                              type="number" 
                              [(ngModel)]="gradeData[submission.id].score" 
                              min="0" 
                              [max]="submission.max_score"
                              class="score-input"
                            >
                            <span class="max-score">/{{ submission.max_score }}</span>
                          </div>
                          <div class="feedback-input-group">
                            <input 
                              type="text" 
                              [(ngModel)]="gradeData[submission.id].feedback" 
                              placeholder="Nhận xét (tùy chọn)"
                              class="feedback-input"
                            >
                          </div>
                          <button 
                            class="btn btn-primary btn-sm save-btn" 
                            (click)="gradeSubmission(submission)" 
                            [disabled]="isGrading[submission.id]"
                          >
                            {{ isGrading[submission.id] ? '...' : 'Lưu' }}
                          </button>
                        </div>
                        <div class="auto-score-note">
                          <small>Điểm tự động: {{ submission.auto_score | number:'1.1-1' }} ({{ submission.correct_count }}/{{ submission.total_questions }} đúng)</small>
                        </div>
                      </div>
                    } @else {
                      <!-- File submission: need manual grading -->
                      @if (submission.status === 'SUBMITTED') {
                        <div class="grade-form">
                          <div class="form-group">
                            <label>Điểm (0-{{ submission.max_score }})</label>
                            <input type="number" [(ngModel)]="gradeData[submission.id].score" min="0" [max]="submission.max_score" placeholder="Nhập điểm">
                          </div>
                          <div class="form-group">
                            <label>Nhận xét</label>
                            <textarea [(ngModel)]="gradeData[submission.id].feedback" rows="3" placeholder="Nhập nhận xét..."></textarea>
                          </div>
                          <button class="btn btn-primary" (click)="gradeSubmission(submission)" [disabled]="isGrading[submission.id]">
                            {{ isGrading[submission.id] ? 'Đang chấm...' : 'Chấm điểm' }}
                          </button>
                        </div>
                      } @else if (submission.status === 'GRADED') {
                        <div class="graded-info">
                          <div class="score-display">
                            <span class="score">{{ submission.score | number:'1.1-1' }}</span>
                            <span class="max">/{{ submission.max_score }}</span>
                          </div>
                          <p class="graded-label">Đã chấm điểm</p>
                          <button class="btn btn-sm btn-outline" (click)="toggleEditScore(submission)">Chỉnh sửa</button>
                        </div>
                        @if (editingScore[submission.id]) {
                          <div class="edit-score-form">
                            <div class="form-row">
                              <div class="form-group">
                                <label>Điểm mới</label>
                                <input type="number" [(ngModel)]="gradeData[submission.id].score" min="0" [max]="submission.max_score">
                              </div>
                              <div class="form-group">
                                <label>Nhận xét</label>
                                <input type="text" [(ngModel)]="gradeData[submission.id].feedback" placeholder="Nhận xét">
                              </div>
                            </div>
                            <button class="btn btn-primary btn-sm" (click)="gradeSubmission(submission)" [disabled]="isGrading[submission.id]">
                              {{ isGrading[submission.id] ? 'Đang lưu...' : 'Lưu điểm' }}
                            </button>
                          </div>
                        }
                      }
                    }
                  </div>
                </div>
              </app-card>
            }
          </div>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .submission-list { max-width: 1000px; margin: 0 auto; }
    .page-header { margin-bottom: 24px; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; margin-bottom: 4px; }
    .page-header p { color: #666; }
    
    .filter-tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
    .tab { padding: 10px 20px; border: 2px solid #e0e0e0; background: #fff; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s; }
    .tab:hover { border-color: #0f3460; }
    .tab.active { background: #0f3460; color: #fff; border-color: #0f3460; }
    
    .submissions { display: flex; flex-direction: column; gap: 20px; }
    .submission-item { display: grid; gap: 16px; }
    
    .submission-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .student-info { display: flex; align-items: center; gap: 12px; }
    .avatar { width: 44px; height: 44px; background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 600; }
    .avatar-img { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; }
    .student-info h3 { font-size: 1rem; color: #1a1a2e; margin-bottom: 2px; }
    .student-info p { font-size: 0.85rem; color: #666; }
    
    .type-badge { padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
    .type-badge.quiz { background: #e8f5e9; color: #2e7d32; }
    .type-badge.submission { background: #e3f2fd; color: #1565c0; }
    
    .assignment-info { font-size: 0.95rem; color: #333; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
    
    .submission-meta { display: flex; gap: 16px; align-items: center; }
    .submitted-at { font-size: 0.85rem; color: #888; }
    .status { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; }
    .status.submitted { background: #fff3e0; color: #ef6c00; }
    .status.graded { background: #e8f5e9; color: #2e7d32; }
    .status.in_progress { background: #e3f2fd; color: #1565c0; }
    
    .quiz-result { padding: 12px 16px; background: #f8f9fa; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
    .quiz-stats { font-size: 0.9rem; color: #666; }
    .auto-score { display: flex; align-items: center; gap: 8px; }
    .auto-score .label { font-size: 0.85rem; color: #888; }
    .auto-score .score-value { font-weight: 700; color: #0f3460; }
    
    .submission-content { }
    .file-link { display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; background: #f5f7fa; border-radius: 8px; text-decoration: none; color: #0f3460; font-weight: 500; }
    .file-link svg { width: 20px; height: 20px; }
    .file-link:hover { background: #e3f2fd; }
    .text-content { padding: 16px; background: #f5f7fa; border-radius: 8px; }
    .text-content p { margin-top: 8px; color: #333; line-height: 1.6; }
    
    .grading-section { padding-top: 12px; border-top: 1px solid #f0f0f0; }
    
    .quiz-grading { display: flex; flex-direction: column; gap: 8px; }
    .inline-grade-form { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .score-input-group { display: flex; align-items: center; gap: 6px; }
    .score-input-group label { font-weight: 500; color: #333; font-size: 0.9rem; }
    .score-input { width: 70px; padding: 8px; border: 2px solid #e0e0e0; border-radius: 6px; text-align: center; font-weight: 600; }
    .score-input:focus { outline: none; border-color: #0f3460; }
    .max-score { color: #888; font-size: 0.9rem; }
    .feedback-input-group { flex: 1; min-width: 150px; }
    .feedback-input { width: 100%; padding: 8px 12px; border: 2px solid #e0e0e0; border-radius: 6px; }
    .feedback-input:focus { outline: none; border-color: #0f3460; }
    .save-btn { white-space: nowrap; }
    .auto-score-note { font-size: 0.8rem; color: #888; }
    
    .grade-form { padding: 16px; background: #f5f7fa; border-radius: 12px; }
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; font-size: 0.9rem; }
    .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box; }
    .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #0f3460; }
    
    .form-row { display: grid; grid-template-columns: 1fr 2fr; gap: 12px; }
    
    .edit-score-form { margin-top: 12px; padding: 12px; background: #f5f7fa; border-radius: 8px; }
    
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .btn-sm { padding: 8px 16px; font-size: 0.85rem; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }
    .btn-outline:hover { border-color: #0f3460; color: #0f3460; }
    .btn:disabled { opacity: 0.7; cursor: not-allowed; }
    
    .graded-info { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
    .score-display { display: flex; align-items: baseline; }
    .score { font-size: 1.75rem; font-weight: 700; color: #2e7d32; }
    .max { font-size: 0.9rem; color: #888; }
    .graded-label { color: #2e7d32; font-weight: 500; }
  `]
})
export class SubmissionListComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private teacherService = inject(TeacherService);
  
  allSubmissions: any[] = [];
  submissions: any[] = [];
  isLoading = true;
  gradeData: Record<number, { score: number; feedback: string }> = {};
  isGrading: Record<number, boolean> = {};
  editingScore: Record<number, boolean> = {};
  currentFilter: 'all' | 'QUIZ' | 'SUBMISSION' = 'all';

  get fileSubmissions(): any[] {
    return this.allSubmissions.filter(s => s.assignment_type !== 'QUIZ');
  }

  get quizSubmissions(): any[] {
    return this.allSubmissions.filter(s => s.assignment_type === 'QUIZ');
  }

  ngOnInit(): void {
    const assignmentId = this.route.snapshot.paramMap.get('id');
    if (assignmentId) {
      this.loadSubmissions(Number(assignmentId));
    } else {
      this.loadAllSubmissions();
    }
  }

  private loadSubmissions(assignmentId: number): void {
    this.teacherService.getAssignmentSubmissions(assignmentId).subscribe({
      next: (submissions: any[]) => {
        this.allSubmissions = submissions;
        this.initGradeData(submissions);
        this.filterSubmissions(this.currentFilter);
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  private loadAllSubmissions(): void {
    this.teacherService.getAllSubmissions().subscribe({
      next: (submissions: any[]) => {
        this.allSubmissions = submissions;
        this.initGradeData(submissions);
        this.filterSubmissions(this.currentFilter);
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  private initGradeData(submissions: any[]): void {
    submissions.forEach(s => {
      this.gradeData[s.id] = { 
        score: s.score || s.auto_score || 0, 
        feedback: '' 
      };
    });
  }

  filterSubmissions(filter: 'all' | 'QUIZ' | 'SUBMISSION'): void {
    this.currentFilter = filter;
    if (filter === 'all') {
      this.submissions = this.allSubmissions;
    } else if (filter === 'QUIZ') {
      this.submissions = this.quizSubmissions;
    } else {
      this.submissions = this.fileSubmissions;
    }
  }

  getStatusText(status: string): string {
    const map: Record<string, string> = {
      'IN_PROGRESS': 'Đang làm',
      'SUBMITTED': 'Chờ chấm',
      'GRADED': 'Đã chấm'
    };
    return map[status] || status;
  }

  toggleEditScore(submission: any): void {
    this.editingScore[submission.id] = !this.editingScore[submission.id];
    if (this.editingScore[submission.id]) {
      this.gradeData[submission.id].score = submission.score || submission.auto_score || 0;
    }
  }

  gradeSubmission(submission: any): void {
    const data = this.gradeData[submission.id];
    const maxScore = submission.max_score || 100;
    if (data.score < 0 || data.score > maxScore) {
      alert(`Điểm phải từ 0 đến ${maxScore}`);
      return;
    }

    this.isGrading[submission.id] = true;
    
    this.teacherService.gradeSubmission(submission.id, data.score, data.feedback).subscribe({
      next: () => {
        submission.status = 'GRADED';
        submission.score = data.score;
        this.isGrading[submission.id] = false;
        this.editingScore[submission.id] = false;
      },
      error: () => {
        this.isGrading[submission.id] = false;
        alert('Lỗi khi chấm điểm');
      }
    });
  }
}


