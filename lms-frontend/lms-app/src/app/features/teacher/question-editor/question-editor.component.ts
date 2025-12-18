import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { ApiService } from '../../../core/services/api.service';

interface Question {
  id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
  points: number;
  order: number;
}

interface AssignmentSettings {
  id: number;
  title: string;
  type: string;
  shuffle_questions: boolean;
  shuffle_answers: boolean;
  show_result: boolean;
}

@Component({
  selector: 'app-question-editor',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      @if (isLoading) {
        <app-loading [overlay]="true" message="Đang tải..."></app-loading>
      } @else {
        <div class="question-editor">
          <div class="page-header">
            <a routerLink="/teacher/courses" class="back-link">← Quay lại</a>
            <div class="header-row">
              <div>
                <h1>Quản lý câu hỏi</h1>
                <p class="subtitle">{{ assignment?.title }}</p>
              </div>
              <div class="header-actions">
                <button class="btn btn-outline" (click)="showSettings = true">⚙️ Cài đặt</button>
                <button class="btn btn-outline" (click)="showImport = true">📥 Import Excel</button>
                <button class="btn btn-primary" (click)="openAddQuestion()">+ Thêm câu hỏi</button>
              </div>
            </div>
          </div>

          <!-- Settings Summary -->
          <app-card>
            <div class="settings-summary">
              <span class="setting-item" [class.active]="assignment?.shuffle_questions">
                🔀 Trộn câu hỏi: {{ assignment?.shuffle_questions ? 'Bật' : 'Tắt' }}
              </span>
              <span class="setting-item" [class.active]="assignment?.shuffle_answers">
                🔀 Trộn đáp án: {{ assignment?.shuffle_answers ? 'Bật' : 'Tắt' }}
              </span>
              <span class="setting-item" [class.active]="assignment?.show_result">
                📊 Hiển thị kết quả: {{ assignment?.show_result ? 'Bật' : 'Tắt' }}
              </span>
              <span class="setting-item">
                📝 Tổng: {{ questions.length }} câu hỏi
              </span>
            </div>
          </app-card>

          <!-- Questions List -->
          <div class="questions-list">
            @for (question of questions; track question.id; let i = $index) {
              <app-card>
                <div class="question-item">
                  <div class="question-header">
                    <div class="question-number">
                      <span>Câu {{ i + 1 }}</span>
                      <span class="points">{{ question.points }} điểm</span>
                    </div>
                    <div class="question-actions">
                      @if (i > 0) {
                        <button class="btn-order" (click)="moveQuestion(question, 'up', i)">▲</button>
                      }
                      @if (i < questions.length - 1) {
                        <button class="btn-order" (click)="moveQuestion(question, 'down', i)">▼</button>
                      }
                      <button class="btn-icon" (click)="openEditQuestion(question)">✏️</button>
                      <button class="btn-icon danger" (click)="deleteQuestion(question)">🗑️</button>
                    </div>
                  </div>
                  <p class="question-text">{{ question.question_text }}</p>
                  <div class="options">
                    <div class="option" [class.correct]="question.correct_answer === 'A'">
                      <span class="option-label">A</span> {{ question.option_a }}
                    </div>
                    <div class="option" [class.correct]="question.correct_answer === 'B'">
                      <span class="option-label">B</span> {{ question.option_b }}
                    </div>
                    <div class="option" [class.correct]="question.correct_answer === 'C'">
                      <span class="option-label">C</span> {{ question.option_c }}
                    </div>
                    <div class="option" [class.correct]="question.correct_answer === 'D'">
                      <span class="option-label">D</span> {{ question.option_d }}
                    </div>
                  </div>
                </div>
              </app-card>
            }

            @if (questions.length === 0) {
              <app-card>
                <div class="empty-state">
                  <p>Chưa có câu hỏi nào.</p>
                  <button class="btn btn-primary" (click)="openAddQuestion()">Thêm câu hỏi đầu tiên</button>
                  <p class="or">hoặc</p>
                  <button class="btn btn-outline" (click)="showImport = true">Import từ Excel</button>
                </div>
              </app-card>
            }
          </div>
        </div>

        <!-- Question Modal -->
        @if (showQuestionModal) {
          <div class="modal-overlay" (click)="closeQuestionModal()">
            <div class="modal modal-lg" (click)="$event.stopPropagation()">
              <div class="modal-header">
                <h3>{{ editingQuestion ? 'Sửa câu hỏi' : 'Thêm câu hỏi' }}</h3>
                <button class="close-btn" (click)="closeQuestionModal()">&times;</button>
              </div>
              <div class="modal-body">
                <div class="form-group">
                  <label>Nội dung câu hỏi *</label>
                  <textarea [(ngModel)]="questionForm.question_text" rows="3" placeholder="Nhập nội dung câu hỏi"></textarea>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Đáp án A *</label>
                    <input type="text" [(ngModel)]="questionForm.option_a" placeholder="Đáp án A">
                  </div>
                  <div class="form-group">
                    <label>Đáp án B *</label>
                    <input type="text" [(ngModel)]="questionForm.option_b" placeholder="Đáp án B">
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Đáp án C</label>
                    <input type="text" [(ngModel)]="questionForm.option_c" placeholder="Đáp án C">
                  </div>
                  <div class="form-group">
                    <label>Đáp án D</label>
                    <input type="text" [(ngModel)]="questionForm.option_d" placeholder="Đáp án D">
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Đáp án đúng *</label>
                    <select [(ngModel)]="questionForm.correct_answer">
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                      <option value="D">D</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Điểm</label>
                    <input type="number" [(ngModel)]="questionForm.points" min="1">
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-outline" (click)="closeQuestionModal()">Hủy</button>
                <button class="btn btn-primary" (click)="saveQuestion()" [disabled]="isSaving">
                  {{ isSaving ? 'Đang lưu...' : 'Lưu' }}
                </button>
              </div>
            </div>
          </div>
        }

        <!-- Settings Modal -->
        @if (showSettings) {
          <div class="modal-overlay" (click)="showSettings = false">
            <div class="modal" (click)="$event.stopPropagation()">
              <div class="modal-header">
                <h3>Cài đặt bài tập</h3>
                <button class="close-btn" (click)="showSettings = false">&times;</button>
              </div>
              <div class="modal-body">
                <div class="form-group checkbox-group">
                  <label>
                    <input type="checkbox" [(ngModel)]="settingsForm.shuffle_questions">
                    Trộn thứ tự câu hỏi
                  </label>
                  <p class="help-text">Mỗi học viên sẽ thấy câu hỏi theo thứ tự khác nhau</p>
                </div>
                <div class="form-group checkbox-group">
                  <label>
                    <input type="checkbox" [(ngModel)]="settingsForm.shuffle_answers">
                    Trộn thứ tự đáp án
                  </label>
                  <p class="help-text">Thứ tự các đáp án A, B, C, D sẽ được xáo trộn</p>
                </div>
                <div class="form-group checkbox-group">
                  <label>
                    <input type="checkbox" [(ngModel)]="settingsForm.show_result">
                    Hiển thị kết quả sau khi nộp
                  </label>
                  <p class="help-text">Học viên có thể xem đáp án đúng sau khi hoàn thành</p>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-outline" (click)="showSettings = false">Hủy</button>
                <button class="btn btn-primary" (click)="saveSettings()" [disabled]="isSaving">
                  {{ isSaving ? 'Đang lưu...' : 'Lưu' }}
                </button>
              </div>
            </div>
          </div>
        }

        <!-- Import Modal -->
        @if (showImport) {
          <div class="modal-overlay" (click)="showImport = false">
            <div class="modal" (click)="$event.stopPropagation()">
              <div class="modal-header">
                <h3>Import câu hỏi từ Excel</h3>
                <button class="close-btn" (click)="showImport = false">&times;</button>
              </div>
              <div class="modal-body">
                <div class="import-info">
                  <h4>Định dạng file Excel:</h4>
                  <table class="format-table">
                    <tr>
                      <th>Câu hỏi</th>
                      <th>Đáp án A</th>
                      <th>Đáp án B</th>
                      <th>Đáp án C</th>
                      <th>Đáp án D</th>
                      <th>Đáp án đúng</th>
                      <th>Điểm</th>
                    </tr>
                    <tr>
                      <td>Nội dung...</td>
                      <td>A...</td>
                      <td>B...</td>
                      <td>C...</td>
                      <td>D...</td>
                      <td>A/B/C/D</td>
                      <td>1</td>
                    </tr>
                  </table>
                </div>
                <div class="form-group">
                  <label>Chọn file Excel (.xlsx, .xls)</label>
                  <input type="file" accept=".xlsx,.xls" (change)="onFileSelect($event)">
                </div>
                @if (importError) {
                  <div class="error-message">{{ importError }}</div>
                }
                @if (importSuccess) {
                  <div class="success-message">{{ importSuccess }}</div>
                }
              </div>
              <div class="modal-footer">
                <button class="btn btn-outline" (click)="showImport = false">Đóng</button>
                <button class="btn btn-primary" (click)="importQuestions()" [disabled]="!selectedFile || isImporting">
                  {{ isImporting ? 'Đang import...' : 'Import' }}
                </button>
              </div>
            </div>
          </div>
        }
      }
    </app-main-layout>
  `,
  styles: [`
    .question-editor { max-width: 900px; margin: 0 auto; }
    .page-header { margin-bottom: 24px; }
    .back-link { color: #666; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 8px; }
    .header-row { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; margin-bottom: 4px; }
    .subtitle { color: #0f3460; font-weight: 500; }
    .header-actions { display: flex; gap: 8px; flex-wrap: wrap; }

    .settings-summary { display: flex; flex-wrap: wrap; gap: 16px; }
    .setting-item { padding: 8px 16px; background: #f5f7fa; border-radius: 8px; font-size: 0.9rem; color: #666; }
    .setting-item.active { background: #e8f5e9; color: #2e7d32; }

    .questions-list { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }

    .question-item { }
    .question-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .question-number { display: flex; align-items: center; gap: 12px; }
    .question-number span:first-child { font-weight: 600; color: #0f3460; }
    .points { font-size: 0.8rem; padding: 4px 10px; background: #e3f2fd; color: #1565c0; border-radius: 12px; }
    .question-actions { display: flex; gap: 6px; }
    .question-text { font-size: 1.05rem; color: #1a1a2e; margin-bottom: 16px; line-height: 1.5; }

    .options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .option { padding: 12px 16px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; gap: 12px; }
    .option.correct { background: #e8f5e9; border: 2px solid #4caf50; }
    .option-label { width: 28px; height: 28px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.85rem; }
    .option.correct .option-label { background: #4caf50; color: #fff; }

    .btn-order { width: 24px; height: 24px; font-size: 0.7rem; background: #f5f7fa; border: 1px solid #e0e0e0; border-radius: 4px; cursor: pointer; }
    .btn-order:hover { background: #e3f2fd; }
    .btn-icon { width: 32px; height: 32px; border: none; background: #f5f7fa; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
    .btn-icon:hover { background: #e3f2fd; }
    .btn-icon.danger:hover { background: #fdeaea; }

    .empty-state { text-align: center; padding: 40px 20px; }
    .empty-state p { color: #666; margin-bottom: 16px; }
    .or { color: #999; margin: 16px 0; }

    .btn { display: inline-block; padding: 10px 20px; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.3s ease; border: none; cursor: pointer; font-size: 0.9rem; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(15, 52, 96, 0.3); }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }
    .btn-outline:hover { border-color: #0f3460; color: #0f3460; }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }

    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
    .modal { background: #fff; border-radius: 16px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
    .modal-lg { max-width: 700px; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
    .modal-header h3 { font-size: 1.2rem; color: #1a1a2e; }
    .close-btn { width: 32px; height: 32px; border: none; background: #f5f7fa; border-radius: 8px; font-size: 1.5rem; cursor: pointer; line-height: 1; }
    .modal-body { padding: 24px; }
    .modal-footer { padding: 16px 24px; border-top: 1px solid #f0f0f0; display: flex; justify-content: flex-end; gap: 12px; }

    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; font-size: 0.9rem; }
    .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; box-sizing: border-box; }
    .form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #0f3460; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

    .checkbox-group label { display: flex; align-items: center; gap: 10px; cursor: pointer; }
    .checkbox-group input[type="checkbox"] { width: 20px; height: 20px; }
    .help-text { font-size: 0.8rem; color: #888; margin-top: 4px; margin-left: 30px; }

    .import-info { margin-bottom: 20px; }
    .import-info h4 { font-size: 0.95rem; margin-bottom: 12px; color: #333; }
    .format-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    .format-table th, .format-table td { padding: 8px; border: 1px solid #e0e0e0; text-align: left; }
    .format-table th { background: #f5f7fa; font-weight: 600; }

    .error-message { padding: 12px; background: #fdeaea; color: #c62828; border-radius: 8px; margin-top: 12px; }
    .success-message { padding: 12px; background: #e8f5e9; color: #2e7d32; border-radius: 8px; margin-top: 12px; }

    @media (max-width: 600px) {
      .options { grid-template-columns: 1fr; }
      .form-row { grid-template-columns: 1fr; }
    }
  `]
})
export class QuestionEditorComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);

  assignmentId = 0;
  assignment: AssignmentSettings | null = null;
  questions: Question[] = [];
  isLoading = true;
  isSaving = false;

  // Question modal
  showQuestionModal = false;
  editingQuestion: Question | null = null;
  questionForm = {
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_answer: 'A',
    points: 1
  };

  // Settings modal
  showSettings = false;
  settingsForm = {
    shuffle_questions: false,
    shuffle_answers: false,
    show_result: true
  };

  // Import modal
  showImport = false;
  selectedFile: File | null = null;
  isImporting = false;
  importError = '';
  importSuccess = '';

  ngOnInit(): void {
    this.assignmentId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadQuestions();
  }

  loadQuestions(): void {
    this.api.get<any>(`/teacher/assignments/${this.assignmentId}/questions/`).subscribe({
      next: (data) => {
        this.assignment = data.assignment;
        this.questions = data.questions;
        this.settingsForm = {
          shuffle_questions: this.assignment?.shuffle_questions || false,
          shuffle_answers: this.assignment?.shuffle_answers || false,
          show_result: this.assignment?.show_result || true
        };
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  openAddQuestion(): void {
    this.editingQuestion = null;
    this.questionForm = {
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_answer: 'A',
      points: 1
    };
    this.showQuestionModal = true;
  }

  openEditQuestion(question: Question): void {
    this.editingQuestion = question;
    this.questionForm = { ...question };
    this.showQuestionModal = true;
  }

  closeQuestionModal(): void {
    this.showQuestionModal = false;
    this.editingQuestion = null;
  }

  saveQuestion(): void {
    if (!this.questionForm.question_text || !this.questionForm.option_a || !this.questionForm.option_b) {
      alert('Vui lòng nhập nội dung câu hỏi và ít nhất 2 đáp án');
      return;
    }

    this.isSaving = true;
    const data = { ...this.questionForm, assignment: this.assignmentId };

    const request = this.editingQuestion
      ? this.api.patch(`/teacher/questions/${this.editingQuestion.id}/`, data)
      : this.api.post('/teacher/questions/', data);

    request.subscribe({
      next: () => {
        this.closeQuestionModal();
        this.loadQuestions();
        this.isSaving = false;
      },
      error: () => {
        alert('Lỗi khi lưu câu hỏi');
        this.isSaving = false;
      }
    });
  }

  deleteQuestion(question: Question): void {
    if (confirm(`Xóa câu hỏi này?`)) {
      this.api.delete(`/teacher/questions/${question.id}/`).subscribe({
        next: () => this.loadQuestions(),
        error: () => alert('Không thể xóa câu hỏi')
      });
    }
  }

  moveQuestion(question: Question, direction: 'up' | 'down', index: number): void {
    const swapIndex = direction === 'up' ? index - 1 : index + 1;
    const items = [
      { id: this.questions[index].id, order: this.questions[swapIndex].order },
      { id: this.questions[swapIndex].id, order: this.questions[index].order }
    ];

    this.api.patch('/teacher/update-order/', { type: 'question', items }).subscribe({
      next: () => this.loadQuestions(),
      error: () => alert('Không thể cập nhật thứ tự')
    });
  }

  saveSettings(): void {
    this.isSaving = true;
    this.api.patch(`/teacher/assignments/${this.assignmentId}/settings/`, this.settingsForm).subscribe({
      next: () => {
        this.showSettings = false;
        this.loadQuestions();
        this.isSaving = false;
      },
      error: () => {
        alert('Lỗi khi lưu cài đặt');
        this.isSaving = false;
      }
    });
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      this.importError = '';
      this.importSuccess = '';
    }
  }

  importQuestions(): void {
    if (!this.selectedFile) return;

    this.isImporting = true;
    this.importError = '';
    this.importSuccess = '';

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.api.post<any>(`/teacher/assignments/${this.assignmentId}/import-questions/`, formData).subscribe({
      next: (res) => {
        this.importSuccess = res.detail || `Import thành công ${res.created} câu hỏi`;
        this.loadQuestions();
        this.isImporting = false;
        this.selectedFile = null;
      },
      error: (err) => {
        this.importError = err.error?.detail || 'Lỗi khi import file';
        this.isImporting = false;
      }
    });
  }
}

