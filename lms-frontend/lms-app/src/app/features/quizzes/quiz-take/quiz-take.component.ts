import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { QuizService } from '../../../core/services/quiz.service';
import { QuizStart, Question, Answer } from '../../../core/models';

@Component({
  selector: 'app-quiz-take',
  standalone: true,
  imports: [CommonModule, MainLayoutComponent, CardComponent],
  template: `
    <app-main-layout>
      @if (quiz) {
        <div class="quiz-take">
          <div class="quiz-header">
            <h1>{{ quiz.assignment_title }}</h1>
            @if (quiz.time_limit) {
              <div class="timer" [class.warning]="timeRemaining < 60">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ formatTime(timeRemaining) }}
              </div>
            }
          </div>
          
          <div class="quiz-content">
            <div class="question-panel">
              @if (currentQuestion) {
                <app-card>
                  <div class="question">
                    <div class="question-header">
                      <span class="question-number">Câu {{ currentIndex + 1 }}/{{ quiz.questions.length }}</span>
                      <span class="question-points">{{ currentQuestion.points }} điểm</span>
                    </div>
                    
                    <p class="question-text">{{ currentQuestion.text }}</p>
                    
                    <div class="options">
                      @for (option of ['A', 'B', 'C', 'D']; track option) {
                        <button 
                          class="option"
                          [class.selected]="selectedAnswers[currentQuestion.id] === option"
                          (click)="selectAnswer(option)"
                        >
                          <span class="option-letter">{{ option }}</span>
                          <span class="option-text">{{ getOptionText(option) }}</span>
                        </button>
                      }
                    </div>
                  </div>
                </app-card>
              }
              
              <div class="navigation">
                <button 
                  class="btn btn-outline" 
                  (click)="previousQuestion()"
                  [disabled]="currentIndex === 0"
                >
                  Câu trước
                </button>
                
                @if (currentIndex < quiz.questions.length - 1) {
                  <button class="btn btn-primary" (click)="nextQuestion()">
                    Câu tiếp
                  </button>
                } @else {
                  <button 
                    class="btn btn-success" 
                    (click)="submitQuiz()"
                    [disabled]="isSubmitting"
                  >
                    @if (isSubmitting) {
                      Đang nộp...
                    } @else {
                      Nộp bài
                    }
                  </button>
                }
              </div>
            </div>
            
            <div class="question-nav">
              <app-card title="Danh sách câu hỏi">
                <div class="question-grid">
                  @for (q of quiz.questions; track q.id; let i = $index) {
                    <button 
                      class="question-btn"
                      [class.current]="i === currentIndex"
                      [class.answered]="selectedAnswers[q.id]"
                      (click)="goToQuestion(i)"
                    >
                      {{ i + 1 }}
                    </button>
                  }
                </div>
                
                <div class="legend">
                  <div class="legend-item">
                    <span class="dot current"></span> Đang làm
                  </div>
                  <div class="legend-item">
                    <span class="dot answered"></span> Đã trả lời
                  </div>
                  <div class="legend-item">
                    <span class="dot"></span> Chưa trả lời
                  </div>
                </div>
                
                <div class="progress-info">
                  <span>Đã trả lời: {{ answeredCount }}/{{ quiz.questions.length }}</span>
                </div>
              </app-card>
            </div>
          </div>
        </div>
      }
    </app-main-layout>
  `,
  styles: [`
    .quiz-take {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .quiz-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    
    .quiz-header h1 {
      font-size: 1.5rem;
      color: #1a1a2e;
    }
    
    .timer {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 20px;
      background: #f5f7fa;
      border-radius: 12px;
      font-size: 1.25rem;
      font-weight: 600;
      color: #1a1a2e;
    }
    
    .timer.warning {
      background: #fdeaea;
      color: #e74c3c;
      animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    
    .timer svg {
      width: 24px;
      height: 24px;
    }
    
    .quiz-content {
      display: grid;
      grid-template-columns: 1fr 280px;
      gap: 24px;
    }
    
    @media (max-width: 900px) {
      .quiz-content {
        grid-template-columns: 1fr;
      }
      
      .question-nav {
        order: -1;
      }
    }
    
    .question-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 20px;
    }
    
    .question-number {
      font-weight: 600;
      color: #0f3460;
    }
    
    .question-points {
      color: #888;
      font-size: 0.9rem;
    }
    
    .question-text {
      font-size: 1.15rem;
      color: #1a1a2e;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    
    .options {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .option {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: #f5f7fa;
      border: 2px solid transparent;
      border-radius: 12px;
      cursor: pointer;
      text-align: left;
      transition: all 0.2s ease;
    }
    
    .option:hover {
      background: #e3f2fd;
      border-color: #90caf9;
    }
    
    .option.selected {
      background: #e3f2fd;
      border-color: #1565c0;
    }
    
    .option-letter {
      width: 36px;
      height: 36px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: #666;
      flex-shrink: 0;
    }
    
    .option.selected .option-letter {
      background: #1565c0;
      color: #fff;
    }
    
    .option-text {
      font-size: 1rem;
      color: #333;
    }
    
    .navigation {
      display: flex;
      justify-content: space-between;
      margin-top: 24px;
    }
    
    .btn {
      padding: 14px 28px;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
    }
    
    .btn-success {
      background: linear-gradient(135deg, #2e7d32, #1b5e20);
      color: #fff;
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #e0e0e0;
      color: #666;
    }
    
    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .question-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 20px;
    }
    
    .question-btn {
      width: 100%;
      aspect-ratio: 1;
      border: 2px solid #e0e0e0;
      background: #fff;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .question-btn:hover {
      border-color: #0f3460;
    }
    
    .question-btn.current {
      background: #0f3460;
      border-color: #0f3460;
      color: #fff;
    }
    
    .question-btn.answered {
      background: #e8f5e9;
      border-color: #4caf50;
      color: #2e7d32;
    }
    
    .legend {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      margin-bottom: 16px;
    }
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: #666;
    }
    
    .dot {
      width: 16px;
      height: 16px;
      border: 2px solid #e0e0e0;
      border-radius: 4px;
      background: #fff;
    }
    
    .dot.current {
      background: #0f3460;
      border-color: #0f3460;
    }
    
    .dot.answered {
      background: #e8f5e9;
      border-color: #4caf50;
    }
    
    .progress-info {
      text-align: center;
      font-size: 0.9rem;
      color: #666;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
    }
  `]
})
export class QuizTakeComponent implements OnInit, OnDestroy {
  private router = inject(Router);
  private quizService = inject(QuizService);
  
  quiz: QuizStart | null = null;
  currentIndex = 0;
  selectedAnswers: Record<number, string> = {};
  timeRemaining = 0;
  timerInterval: any;
  isSubmitting = false;

  get currentQuestion(): Question | null {
    return this.quiz?.questions[this.currentIndex] || null;
  }

  get answeredCount(): number {
    return Object.keys(this.selectedAnswers).length;
  }

  ngOnInit(): void {
    const quizData = sessionStorage.getItem('currentQuiz');
    if (quizData) {
      this.quiz = JSON.parse(quizData);
      if (this.quiz?.time_limit) {
        this.timeRemaining = this.quiz.time_limit * 60;
        this.startTimer();
      }
    } else {
      this.router.navigate(['/dashboard']);
    }
  }

  ngOnDestroy(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }

  private startTimer(): void {
    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      if (this.timeRemaining <= 0) {
        clearInterval(this.timerInterval);
        this.submitQuiz();
      }
    }, 1000);
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  getOptionText(option: string): string {
    if (!this.currentQuestion) return '';
    const key = `option_${option.toLowerCase()}` as keyof Question;
    return this.currentQuestion[key] as string || '';
  }

  selectAnswer(option: string): void {
    if (this.currentQuestion) {
      this.selectedAnswers[this.currentQuestion.id] = option;
    }
  }

  previousQuestion(): void {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }

  nextQuestion(): void {
    if (this.quiz && this.currentIndex < this.quiz.questions.length - 1) {
      this.currentIndex++;
    }
  }

  goToQuestion(index: number): void {
    this.currentIndex = index;
  }

  submitQuiz(): void {
    if (!this.quiz || this.isSubmitting) return;

    this.isSubmitting = true;
    
    const answers: Answer[] = Object.entries(this.selectedAnswers).map(([questionId, answer]) => ({
      question_id: Number(questionId),
      chosen_answer: answer as 'A' | 'B' | 'C' | 'D'
    }));

    this.quizService.submitQuiz(this.quiz.attempt_id, { answers }).subscribe({
      next: () => {
        sessionStorage.removeItem('currentQuiz');
        this.router.navigate(['/quizzes/attempt', this.quiz!.attempt_id, 'result']);
      },
      error: () => {
        this.isSubmitting = false;
      }
    });
  }
}


