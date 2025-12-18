import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { QuizService } from '../../../core/services/quiz.service';

@Component({
  selector: 'app-quiz-start',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent],
  template: `
    <app-main-layout>
      <div class="quiz-start">
        <app-card>
          <div class="quiz-info">
            <div class="quiz-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </div>
            
            <h1>{{ assignmentTitle || 'Bài kiểm tra trắc nghiệm' }}</h1>
            
            @if (isLoading) {
              <div class="loading">Đang tải thông tin...</div>
            } @else {
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Thời gian làm bài</span>
                  <span class="value">{{ timeLimit ? timeLimit + ' phút' : 'Không giới hạn' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Số lần làm còn lại</span>
                  <span class="value">{{ attemptsRemaining !== null ? attemptsRemaining + ' lần' : 'Không giới hạn' }}</span>
                </div>
              </div>
            }
            
            <div class="rules">
              <h3>Lưu ý:</h3>
              <ul>
                <li>Sau khi bắt đầu, bạn không thể tạm dừng bài làm</li>
                <li>Hết thời gian bài làm sẽ tự động được nộp</li>
                <li>Mỗi câu hỏi chỉ có một đáp án đúng</li>
                <li>Bạn có thể quay lại các câu hỏi trước đó</li>
              </ul>
            </div>
            
            @if (errorMessage) {
              <div class="alert alert-error">{{ errorMessage }}</div>
            }
            
            <div class="actions">
              <button class="btn btn-primary btn-lg" (click)="startQuiz()" [disabled]="isStarting || isLoading || !canStart">
                @if (isStarting) {
                  <span class="spinner"></span> Đang bắt đầu...
                } @else {
                  Bắt đầu làm bài
                }
              </button>
              <a routerLink="/dashboard" class="btn btn-outline">Quay lại</a>
            </div>
          </div>
        </app-card>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .quiz-start {
      max-width: 600px;
      margin: 40px auto;
    }
    
    .quiz-info {
      text-align: center;
      padding: 20px;
    }
    
    .quiz-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      color: #2e7d32;
    }
    
    .quiz-icon svg {
      width: 40px;
      height: 40px;
    }
    
    h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 32px;
    }
    
    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 32px;
    }
    
    .info-item {
      padding: 20px;
      background: #f5f7fa;
      border-radius: 12px;
    }
    
    .info-item .label {
      display: block;
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 8px;
    }
    
    .info-item .value {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1a1a2e;
    }
    
    .rules {
      text-align: left;
      background: #fff8e1;
      padding: 20px;
      border-radius: 12px;
      margin-bottom: 32px;
    }
    
    .rules h3 {
      color: #f57f17;
      margin-bottom: 12px;
      font-size: 1rem;
    }
    
    .rules ul {
      margin: 0;
      padding-left: 20px;
      color: #666;
    }
    
    .rules li {
      margin-bottom: 8px;
      line-height: 1.5;
    }
    
    .alert {
      padding: 16px;
      border-radius: 10px;
      margin-bottom: 24px;
    }
    
    .alert-error {
      background: #fdeaea;
      color: #e74c3c;
    }
    
    .actions {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .btn {
      padding: 16px 32px;
      border: none;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      text-decoration: none;
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #2e7d32, #1b5e20);
      color: #fff;
    }
    
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(46, 125, 50, 0.4);
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #e0e0e0;
      color: #666;
    }
    
    .btn-outline:hover {
      border-color: #0f3460;
      color: #0f3460;
    }
    
    .btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
    
    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid #fff;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class QuizStartComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private quizService = inject(QuizService);
  
  assignmentId = 0;
  assignmentTitle = '';
  timeLimit: number | null = null;
  attemptsRemaining: number | null = null;
  isLoading = true;
  isStarting = false;
  errorMessage = '';
  canStart = true;

  ngOnInit(): void {
    this.assignmentId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadAssignmentInfo();
  }

  loadAssignmentInfo(): void {
    this.quizService.getAssignmentInfo(this.assignmentId).subscribe({
      next: (info) => {
        this.assignmentTitle = info.title;
        this.timeLimit = info.time_limit;
        this.attemptsRemaining = info.attempts_remaining;
        this.canStart = info.can_start;
        this.isLoading = false;
        if (!this.canStart) {
          this.errorMessage = info.message || 'Ban da het luot lam bai';
        }
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Khong the tai thong tin bai tap';
      }
    });
  }

  startQuiz(): void {
    if (!this.canStart) {
      return;
    }
    this.isStarting = true;
    this.errorMessage = '';

    this.quizService.startQuiz(this.assignmentId).subscribe({
      next: (result) => {
        // Store quiz data in session storage for the take component
        sessionStorage.setItem('currentQuiz', JSON.stringify(result));
        this.router.navigate(['/quizzes', this.assignmentId, 'take']);
      },
      error: (err) => {
        this.isStarting = false;
        this.errorMessage = err.error?.detail || 'Không thể bắt đầu bài kiểm tra. Vui lòng thử lại.';
      }
    });
  }
}


