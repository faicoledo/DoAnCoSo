import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { AdminService, Subject } from '../../../core/services/admin.service';

@Component({
  selector: 'app-subject-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <div>
            <a routerLink="/admin" class="back-link">← Quay lại</a>
            <h1>Quản lý môn học</h1>
          </div>
          <button class="btn btn-primary" (click)="openCreateModal()">+ Thêm môn học</button>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && subjects.length === 0"
          title="Chưa có môn học"
          message="Hãy thêm môn học mới."
        ></app-empty-state>

        <div class="subjects-grid" *ngIf="!isLoading && subjects.length > 0">
          @for (subject of subjects; track subject.id) {
            <app-card class="subject-card">
              <div class="subject-header">
                <h3>{{ subject.title }}</h3>
                <div class="actions">
                  <button class="btn-icon" (click)="openEditModal(subject)" title="Sửa">✏️</button>
                  <button class="btn-icon" (click)="deleteSubject(subject)" title="Xóa">🗑️</button>
                </div>
              </div>
              <p class="description">{{ subject.description || 'Không có mô tả' }}</p>
              <div class="meta">
                <span class="courses-count">{{ subject.courses_count }} khóa học</span>
              </div>
            </app-card>
          }
        </div>

        <!-- Modal -->
        @if (showModal) {
          <div class="modal-overlay" (click)="closeModal()">
            <div class="modal" (click)="$event.stopPropagation()">
              <h2>{{ editingSubject ? 'Chỉnh sửa môn học' : 'Thêm môn học' }}</h2>
              <form (ngSubmit)="saveSubject()">
                <div class="form-group">
                  <label>Tên môn học *</label>
                  <input type="text" [(ngModel)]="formData.title" name="title" required>
                </div>
                <div class="form-group">
                  <label>Mô tả</label>
                  <textarea [(ngModel)]="formData.description" name="description" rows="3"></textarea>
                </div>
                @if (errorMessage) {
                  <div class="alert alert-error">{{ errorMessage }}</div>
                }
                <div class="modal-actions">
                  <button type="submit" class="btn btn-primary" [disabled]="isSaving">
                    {{ isSaving ? 'Đang lưu...' : 'Lưu' }}
                  </button>
                  <button type="button" class="btn btn-outline" (click)="closeModal()">Hủy</button>
                </div>
              </form>
            </div>
          </div>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .page-container { max-width: 1200px; margin: 0 auto; }
    .page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
    .back-link { color: #0f3460; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 8px; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; }

    .subjects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
    .subject-card { height: 100%; }
    .subject-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .subject-header h3 { font-size: 1.1rem; color: #1a1a2e; }
    .actions { display: flex; gap: 4px; }
    .description { color: #666; font-size: 0.9rem; line-height: 1.5; margin-bottom: 12px; }
    .meta { padding-top: 12px; border-top: 1px solid #f0f0f0; }
    .courses-count { font-size: 0.85rem; color: #0f3460; font-weight: 600; }

    .btn-icon { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 4px; }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }

    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .modal { background: #fff; border-radius: 16px; padding: 24px; width: 90%; max-width: 500px; }
    .modal h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 20px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; }
    .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; }
    .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #0f3460; }
    .modal-actions { display: flex; gap: 12px; margin-top: 20px; }
    .alert-error { padding: 10px; background: #ffebee; color: #c62828; border-radius: 8px; margin-bottom: 12px; }
  `]
})
export class SubjectManagementComponent implements OnInit {
  adminService = inject(AdminService);
  
  subjects: Subject[] = [];
  isLoading = true;
  
  showModal = false;
  editingSubject: Subject | null = null;
  formData: any = {};
  isSaving = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadSubjects();
  }

  private loadSubjects(): void {
    this.adminService.getSubjects().subscribe({
      next: (subjects) => {
        this.subjects = subjects;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  openCreateModal(): void {
    this.editingSubject = null;
    this.formData = {};
    this.errorMessage = '';
    this.showModal = true;
  }

  openEditModal(subject: Subject): void {
    this.editingSubject = subject;
    this.formData = { title: subject.title, description: subject.description };
    this.errorMessage = '';
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.editingSubject = null;
    this.formData = {};
  }

  saveSubject(): void {
    this.errorMessage = '';
    this.isSaving = true;

    const observable = this.editingSubject
      ? this.adminService.updateSubject(this.editingSubject.id, this.formData)
      : this.adminService.createSubject(this.formData);

    observable.subscribe({
      next: () => {
        this.isSaving = false;
        this.closeModal();
        this.loadSubjects();
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  deleteSubject(subject: Subject): void {
    if (confirm(`Bạn có chắc muốn xóa môn học "${subject.title}"?`)) {
      this.adminService.deleteSubject(subject.id).subscribe({
        next: () => this.loadSubjects(),
        error: (err) => alert(err.error?.detail || 'Có lỗi xảy ra')
      });
    }
  }
}

