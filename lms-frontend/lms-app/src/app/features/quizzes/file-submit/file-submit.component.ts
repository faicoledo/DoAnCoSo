import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { ApiService } from '../../../core/services/api.service';
import { QuizService } from '../../../core/services/quiz.service';

@Component({
  selector: 'app-file-submit',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent],
  template: `
    <app-main-layout>
      <div class="file-submit">
        <app-card>
          <div class="submit-form">
            <div class="header">
              <div class="icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
              </div>
              <h1>{{ assignmentTitle || 'Nộp bài tập' }}</h1>
            </div>
            
            @if (isLoading) {
              <div class="loading">Đang tải thông tin...</div>
            } @else {
              <div class="info-section">
                <div class="info-item">
                  <span class="label">Số lần nộp còn lại</span>
                  <span class="value">{{ attemptsRemaining }} lần</span>
                </div>
                @if (timeLimit) {
                  <div class="info-item">
                    <span class="label">Hạn nộp</span>
                    <span class="value">{{ endAt | date:'dd/MM/yyyy HH:mm' }}</span>
                  </div>
                }
              </div>
              
              @if (!canSubmit) {
                <div class="alert alert-warning">
                  {{ errorMessage || 'Bạn đã hết lượt nộp bài hoặc bài tập đã đóng.' }}
                </div>
              } @else {
                <div class="form-section">
                  <div class="form-group">
                    <label>Tải file bài làm</label>
                    <div class="file-upload" [class.has-file]="selectedFile">
                      <input type="file" id="file-input" (change)="onFileSelect($event)" accept=".pdf,.doc,.docx,.zip,.rar">
                      <label for="file-input" class="file-label">
                        @if (selectedFile) {
                          <span class="file-name">📎 {{ selectedFile.name }}</span>
                          <button type="button" class="remove-file" (click)="removeFile($event)">✕</button>
                        } @else {
                          <span class="upload-icon">📁</span>
                          <span>Chọn file hoặc kéo thả vào đây</span>
                          <span class="hint">PDF, DOC, DOCX, ZIP, RAR (tối đa 50MB)</span>
                        }
                      </label>
                    </div>
                  </div>
                  
                  <div class="divider">
                    <span>hoặc</span>
                  </div>
                  
                  <div class="form-group">
                    <label>Nhập nội dung bài làm</label>
                    <textarea 
                      [(ngModel)]="submittedText" 
                      rows="8" 
                      placeholder="Nhập nội dung bài làm của bạn..."
                    ></textarea>
                  </div>
                </div>
              }
              
              @if (submitError) {
                <div class="alert alert-error">{{ submitError }}</div>
              }
              
              @if (submitSuccess) {
                <div class="alert alert-success">
                  <p>✅ Nộp bài thành công!</p>
                  <a routerLink="/my-assignments" class="btn btn-outline btn-sm">Xem bài đã nộp</a>
                </div>
              }
              
              <div class="actions">
                @if (canSubmit && !submitSuccess) {
                  <button 
                    class="btn btn-primary btn-lg" 
                    (click)="submitAssignment()" 
                    [disabled]="isSubmitting || (!selectedFile && !submittedText)"
                  >
                    @if (isSubmitting) {
                      <span class="spinner"></span> Đang nộp...
                    } @else {
                      Nộp bài
                    }
                  </button>
                }
                <a routerLink="/dashboard" class="btn btn-outline">Quay lại</a>
              </div>
            }
          </div>
        </app-card>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .file-submit { max-width: 600px; margin: 40px auto; }
    .submit-form { padding: 20px; }
    
    .header { text-align: center; margin-bottom: 32px; }
    .icon { width: 80px; height: 80px; background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: #1565c0; }
    .icon svg { width: 40px; height: 40px; }
    h1 { font-size: 1.5rem; color: #1a1a2e; }
    
    .info-section { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
    .info-item { padding: 16px; background: #f5f7fa; border-radius: 10px; text-align: center; }
    .info-item .label { display: block; font-size: 0.85rem; color: #666; margin-bottom: 4px; }
    .info-item .value { font-size: 1.1rem; font-weight: 600; color: #1a1a2e; }
    
    .form-section { margin-bottom: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
    
    .file-upload { position: relative; }
    .file-upload input[type="file"] { position: absolute; opacity: 0; width: 100%; height: 100%; cursor: pointer; }
    .file-label { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 32px; border: 2px dashed #e0e0e0; border-radius: 12px; background: #fafafa; cursor: pointer; transition: all 0.2s; min-height: 120px; }
    .file-label:hover { border-color: #0f3460; background: #f5f7fa; }
    .file-upload.has-file .file-label { border-color: #4caf50; background: #e8f5e9; flex-direction: row; justify-content: space-between; padding: 16px 20px; min-height: auto; }
    .upload-icon { font-size: 2rem; margin-bottom: 8px; }
    .file-label span { color: #666; }
    .hint { font-size: 0.8rem; color: #999; margin-top: 4px; }
    .file-name { color: #2e7d32; font-weight: 500; }
    .remove-file { background: none; border: none; color: #e74c3c; cursor: pointer; font-size: 1.2rem; padding: 4px 8px; }
    
    .divider { text-align: center; margin: 24px 0; position: relative; }
    .divider::before { content: ''; position: absolute; left: 0; top: 50%; width: 100%; height: 1px; background: #e0e0e0; }
    .divider span { background: #fff; padding: 0 16px; position: relative; color: #999; font-size: 0.9rem; }
    
    textarea { width: 100%; padding: 16px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1rem; resize: vertical; box-sizing: border-box; }
    textarea:focus { outline: none; border-color: #0f3460; }
    
    .alert { padding: 16px; border-radius: 10px; margin-bottom: 20px; }
    .alert-error { background: #fdeaea; color: #c62828; }
    .alert-warning { background: #fff3e0; color: #ef6c00; }
    .alert-success { background: #e8f5e9; color: #2e7d32; display: flex; align-items: center; justify-content: space-between; }
    
    .actions { display: flex; flex-direction: column; gap: 12px; }
    .btn { padding: 14px 28px; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; text-decoration: none; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .btn-lg { padding: 16px 32px; }
    .btn-sm { padding: 8px 16px; font-size: 0.9rem; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(15, 52, 96, 0.4); }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }
    .btn-outline:hover { border-color: #0f3460; color: #0f3460; }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }
    
    .spinner { width: 18px; height: 18px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    .loading { text-align: center; padding: 40px; color: #666; }
  `]
})
export class FileSubmitComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private api = inject(ApiService);
  private quizService = inject(QuizService);
  
  assignmentId = 0;
  assignmentTitle = '';
  attemptsRemaining = 0;
  timeLimit: number | null = null;
  endAt: string | null = null;
  canSubmit = true;
  
  isLoading = true;
  isSubmitting = false;
  errorMessage = '';
  submitError = '';
  submitSuccess = false;
  
  selectedFile: File | null = null;
  submittedText = '';

  ngOnInit(): void {
    this.assignmentId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadAssignmentInfo();
  }

  loadAssignmentInfo(): void {
    this.quizService.getAssignmentInfo(this.assignmentId).subscribe({
      next: (info: any) => {
        this.assignmentTitle = info.title;
        this.attemptsRemaining = info.attempts_remaining;
        this.timeLimit = info.time_limit;
        this.endAt = info.end_at;
        this.canSubmit = info.can_start;
        if (!this.canSubmit) {
          this.errorMessage = info.message || 'Bạn đã hết lượt nộp bài';
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Không thể tải thông tin bài tập';
        this.canSubmit = false;
      }
    });
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
    }
  }

  removeFile(event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.selectedFile = null;
  }

  submitAssignment(): void {
    if (!this.selectedFile && !this.submittedText.trim()) {
      this.submitError = 'Vui lòng chọn file hoặc nhập nội dung bài làm';
      return;
    }

    this.isSubmitting = true;
    this.submitError = '';

    const formData = new FormData();
    if (this.selectedFile) {
      formData.append('file', this.selectedFile);
    }
    if (this.submittedText.trim()) {
      formData.append('text', this.submittedText.trim());
    }

    this.api.post(`/assessments/assignments/${this.assignmentId}/submit-file/`, formData).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.submitSuccess = true;
        this.canSubmit = false;
      },
      error: (err) => {
        this.isSubmitting = false;
        this.submitError = err.error?.detail || 'Không thể nộp bài. Vui lòng thử lại.';
      }
    });
  }
}

