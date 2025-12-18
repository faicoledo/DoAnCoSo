import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { QuizService } from '../../../core/services/quiz.service';
import { AttemptResult } from '../../../core/models';

@Component({
  selector: 'app-quiz-result',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      @if (isLoading) {
        <app-loading [overlay]="true" message="Đang tải kết quả..."></app-loading>
      } @else if (result) {
        <div class="quiz-result">
          <app-card>
            <div class="result-header">
              <div class="score-circle" [class.pass]="isPassing" [class.fail]="!isPassing">
                <span class="score">{{ result.score | number:'1.1-1' }}</span>
                <span class="max-score">/ {{ result.max_score }}</span>
              </div>
              
              <h1>{{ result.assignment_title }}</h1>
              
              <div class="result-stats">
                <div class="stat">
                  <span class="stat-value">{{ result.correct_count }}</span>
                  <span class="stat-label">Câu đúng</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ result.total_questions - result.correct_count }}</span>
                  <span class="stat-label">Câu sai</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ result.total_questions }}</span>
                  <span class="stat-label">Tổng câu</span>
                </div>
              </div>
              
              <div class="result-message" [class.pass]="isPassing" [class.fail]="!isPassing">
                @if (isPassing) {
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Chúc mừng! Bạn đã hoàn thành tốt bài kiểm tra.
                } @else {
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                  </svg>
                  Hãy cố gắng hơn trong lần tới!
                }
              </div>
            </div>
          </app-card>
          
          <h2>Chi tiết câu trả lời</h2>
          
          <div class="details-list">
            @for (detail of result.details; track detail.question_id; let i = $index) {
              <app-card>
                <div class="detail-item" [class.correct]="detail.is_correct" [class.incorrect]="!detail.is_correct">
                  <div class="detail-header">
                    <span class="question-num">Câu {{ i + 1 }}</span>
                    <span class="status-badge" [class.correct]="detail.is_correct">
                      @if (detail.is_correct) {
                        Đúng
                      } @else {
                        Sai
                      }
                    </span>
                  </div>
                  
                  <p class="question-text">{{ detail.question_text }}</p>
                  
                  <div class="answers">
                    <div class="answer your-answer" [class.correct]="detail.is_correct" [class.incorrect]="!detail.is_correct">
                      <span class="answer-label">Câu trả lời của bạn:</span>
                      <span class="answer-value">{{ detail.selected_answer || 'Không trả lời' }}</span>
                    </div>
                    @if (!detail.is_correct) {
                      <div class="answer correct-answer">
                        <span class="answer-label">Đáp án đúng:</span>
                        <span class="answer-value">{{ detail.correct_answer }}</span>
                      </div>
                    }
                  </div>
                  
                  @if (detail.explanation) {
                    <div class="explanation">
                      <strong>Giải thích:</strong> {{ detail.explanation }}
                    </div>
                  }
                </div>
              </app-card>
            }
          </div>
          
          <div class="actions">
            <a routerLink="/dashboard" class="btn btn-primary">Về trang chủ</a>
          </div>
        </div>
      }
    </app-main-layout>
  `,
  styles: [`
    .quiz-result {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .result-header {
      text-align: center;
      padding: 20px;
    }
    
    .score-circle {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      border: 6px solid;
    }
    
    .score-circle.pass {
      background: #e8f5e9;
      border-color: #4caf50;
      color: #2e7d32;
    }
    
    .score-circle.fail {
      background: #fdeaea;
      border-color: #e74c3c;
      color: #c0392b;
    }
    
    .score {
      font-size: 2.5rem;
      font-weight: 700;
      line-height: 1;
    }
    
    .max-score {
      font-size: 1rem;
      opacity: 0.7;
    }
    
    .result-header h1 {
      font-size: 1.5rem;
      color: #1a1a2e;
      margin-bottom: 24px;
    }
    
    .result-stats {
      display: flex;
      justify-content: center;
      gap: 40px;
      margin-bottom: 24px;
    }
    
    .stat {
      text-align: center;
    }
    
    .stat-value {
      display: block;
      font-size: 1.75rem;
      font-weight: 700;
      color: #1a1a2e;
    }
    
    .stat-label {
      font-size: 0.9rem;
      color: #888;
    }
    
    .result-message {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 16px 24px;
      border-radius: 12px;
      font-weight: 500;
    }
    
    .result-message.pass {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    .result-message.fail {
      background: #fff3e0;
      color: #ef6c00;
    }
    
    .result-message svg {
      width: 24px;
      height: 24px;
    }
    
    h2 {
      font-size: 1.25rem;
      color: #1a1a2e;
      margin: 32px 0 20px;
    }
    
    .details-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    
    .question-num {
      font-weight: 600;
      color: #0f3460;
    }
    
    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      background: #fdeaea;
      color: #e74c3c;
    }
    
    .status-badge.correct {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    .question-text {
      font-size: 1.05rem;
      color: #333;
      line-height: 1.6;
      margin-bottom: 16px;
    }
    
    .answers {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .answer {
      display: flex;
      justify-content: space-between;
      padding: 12px 16px;
      border-radius: 8px;
      background: #f5f7fa;
    }
    
    .answer.correct {
      background: #e8f5e9;
    }
    
    .answer.incorrect {
      background: #fdeaea;
    }
    
    .answer-label {
      color: #666;
    }
    
    .answer-value {
      font-weight: 600;
    }
    
    .correct-answer {
      background: #e8f5e9;
    }
    
    .correct-answer .answer-value {
      color: #2e7d32;
    }
    
    .explanation {
      margin-top: 16px;
      padding: 16px;
      background: #fff8e1;
      border-radius: 8px;
      font-size: 0.95rem;
      color: #666;
      line-height: 1.5;
    }
    
    .actions {
      text-align: center;
      margin-top: 32px;
    }
    
    .btn {
      display: inline-block;
      padding: 14px 32px;
      border-radius: 12px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.3s ease;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
    }
    
    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(15, 52, 96, 0.4);
    }
  `]
})
export class QuizResultComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private quizService = inject(QuizService);
  
  result: AttemptResult | null = null;
  isLoading = true;

  get isPassing(): boolean {
    if (!this.result) return false;
    return this.result.score >= this.result.max_score * 0.5;
  }

  ngOnInit(): void {
    const attemptId = Number(this.route.snapshot.paramMap.get('attemptId'));
    this.loadResult(attemptId);
  }

  private loadResult(attemptId: number): void {
    this.quizService.getAttemptResult(attemptId).subscribe({
      next: (result) => {
        this.result = result;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}


