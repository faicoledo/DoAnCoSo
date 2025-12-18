import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { AdminService, Course, Subject } from '../../../core/services/admin.service';

@Component({
  selector: 'app-course-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <div>
            <a routerLink="/admin" class="back-link">← Quay lại</a>
            <h1>Quản lý khóa học</h1>
          </div>
          <button class="btn btn-primary" (click)="openCreateModal()">+ Thêm khóa học</button>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && courses.length === 0"
          title="Chưa có khóa học"
          message="Hãy thêm khóa học mới."
        ></app-empty-state>

        <div class="courses-grid" *ngIf="!isLoading && courses.length > 0">
          @for (course of courses; track course.id) {
            <app-card class="course-card">
              <div class="course-header">
                <span class="subject-tag" *ngIf="course.subject">{{ course.subject.title }}</span>
                <div class="actions">
                  <button class="btn-icon" (click)="openEditModal(course)" title="Sửa">✏️</button>
                  <button class="btn-icon" (click)="deleteCourse(course)" title="Xóa">🗑️</button>
                </div>
              </div>
              <h3>{{ course.title }}</h3>
              <p class="description">{{ course.description || 'Không có mô tả' }}</p>
              <div class="course-meta">
                <span class="status" [class]="(course.status || '').toLowerCase()">{{ course.status_display }}</span>
                <span class="students">{{ course.total_students }} học viên</span>
              </div>
              <div class="dates" *ngIf="course.start_date || course.end_date">
                <span *ngIf="course.start_date">Bắt đầu: {{ course.start_date | date:'dd/MM/yyyy' }}</span>
                <span *ngIf="course.end_date">Kết thúc: {{ course.end_date | date:'dd/MM/yyyy' }}</span>
              </div>
            </app-card>
          }
        </div>

        <!-- Modal -->
        @if (showModal) {
          <div class="modal-overlay" (click)="closeModal()">
            <div class="modal" (click)="$event.stopPropagation()">
              <h2>{{ editingCourse ? 'Chỉnh sửa khóa học' : 'Thêm khóa học' }}</h2>
              <form (ngSubmit)="saveCourse()">
                <div class="form-group">
                  <label>Tên khóa học *</label>
                  <input type="text" [(ngModel)]="formData.title" name="title" required>
                </div>
                <div class="form-group">
                  <label>Môn học</label>
                  <select [(ngModel)]="formData.subject_id" name="subject_id">
                    <option [ngValue]="null">-- Chọn môn học --</option>
                    @for (subject of subjects; track subject.id) {
                      <option [ngValue]="subject.id">{{ subject.title }}</option>
                    }
                  </select>
                </div>
                <div class="form-group">
                  <label>Mô tả</label>
                  <textarea [(ngModel)]="formData.description" name="description" rows="3"></textarea>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Ngày bắt đầu</label>
                    <input type="date" [(ngModel)]="formData.start_date" name="start_date">
                  </div>
                  <div class="form-group">
                    <label>Ngày kết thúc</label>
                    <input type="date" [(ngModel)]="formData.end_date" name="end_date">
                  </div>
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

    .courses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
    .course-card { height: 100%; }
    .course-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
    .subject-tag { background: #e3f2fd; color: #1565c0; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .actions { display: flex; gap: 4px; }
    h3 { font-size: 1.1rem; color: #1a1a2e; margin-bottom: 8px; }
    .description { color: #666; font-size: 0.9rem; line-height: 1.5; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .course-meta { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f0f0f0; }
    .status { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .status.ongoing { background: #e8f5e9; color: #2e7d32; }
    .status.upcoming { background: #fff3e0; color: #ef6c00; }
    .status.completed { background: #e3f2fd; color: #1565c0; }
    .students { font-size: 0.85rem; color: #888; }
    .dates { margin-top: 8px; font-size: 0.8rem; color: #888; display: flex; flex-direction: column; gap: 2px; }

    .btn-icon { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 4px; }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }

    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .modal { background: #fff; border-radius: 16px; padding: 24px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
    .modal h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 20px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; }
    .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #0f3460; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .modal-actions { display: flex; gap: 12px; margin-top: 20px; }
    .alert-error { padding: 10px; background: #ffebee; color: #c62828; border-radius: 8px; margin-bottom: 12px; }
  `]
})
export class CourseManagementComponent implements OnInit {
  adminService = inject(AdminService);
  
  courses: Course[] = [];
  subjects: Subject[] = [];
  isLoading = true;
  
  showModal = false;
  editingCourse: Course | null = null;
  formData: any = {};
  isSaving = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.adminService.getSubjects().subscribe(subjects => this.subjects = subjects);
    this.adminService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  openCreateModal(): void {
    this.editingCourse = null;
    this.formData = {};
    this.errorMessage = '';
    this.showModal = true;
  }

  openEditModal(course: Course): void {
    this.editingCourse = course;
    this.formData = {
      title: course.title,
      description: course.description,
      subject_id: course.subject?.id || null,
      start_date: course.start_date,
      end_date: course.end_date
    };
    this.errorMessage = '';
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.editingCourse = null;
    this.formData = {};
  }

  saveCourse(): void {
    this.errorMessage = '';
    this.isSaving = true;

    const observable = this.editingCourse
      ? this.adminService.updateCourse(this.editingCourse.id, this.formData)
      : this.adminService.createCourse(this.formData);

    observable.subscribe({
      next: () => {
        this.isSaving = false;
        this.closeModal();
        this.loadData();
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  deleteCourse(course: Course): void {
    if (confirm(`Bạn có chắc muốn xóa khóa học "${course.title}"?`)) {
      this.adminService.deleteCourse(course.id).subscribe({
        next: () => this.loadData(),
        error: (err) => alert(err.error?.detail || 'Có lỗi xảy ra')
      });
    }
  }
}

