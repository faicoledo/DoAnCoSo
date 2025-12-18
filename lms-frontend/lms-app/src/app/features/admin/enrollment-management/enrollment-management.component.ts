import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { AdminService, Course, User } from '../../../core/services/admin.service';

@Component({
  selector: 'app-enrollment-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <div>
            <a routerLink="/admin" class="back-link">← Quay lại</a>
            <h1>Quản lý đăng ký</h1>
          </div>
          <button class="btn btn-primary" (click)="openCreateModal()">+ Thêm đăng ký</button>
        </div>

        <!-- Filter -->
        <div class="filters">
          <select [(ngModel)]="courseFilter" (change)="loadEnrollments()" class="filter-select">
            <option value="">Tất cả khóa học</option>
            @for (course of courses; track course.id) {
              <option [ngValue]="course.id">{{ course.title }}</option>
            }
          </select>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && enrollments.length === 0"
          title="Chưa có đăng ký"
          message="Chưa có ai đăng ký khóa học nào."
        ></app-empty-state>

        <div class="enrollments-table" *ngIf="!isLoading && enrollments.length > 0">
          <app-card>
            <table>
              <thead>
                <tr>
                  <th>Người dùng</th>
                  <th>Khóa học</th>
                  <th>Vai trò</th>
                  <th>Ngày đăng ký</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                @for (enrollment of enrollments; track enrollment.id) {
                  <tr>
                    <td class="user-cell">
                      @if (enrollment.user.avatar) {
                        <img [src]="enrollment.user.avatar" class="avatar-img">
                      } @else {
                        <div class="avatar">{{ enrollment.user.full_name?.charAt(0) || 'U' }}</div>
                      }
                      <div class="user-info">
                        <span class="name">{{ enrollment.user.full_name }}</span>
                        <span class="email">{{ enrollment.user.email }}</span>
                      </div>
                    </td>
                    <td>{{ enrollment.course.title }}</td>
                    <td>
                      <span class="role-badge" [class]="enrollment.role_in_course?.toLowerCase()">
                        {{ enrollment.role_display }}
                      </span>
                    </td>
                    <td>{{ enrollment.joined_at | date:'dd/MM/yyyy' }}</td>
                    <td>
                      <button class="btn-icon" (click)="deleteEnrollment(enrollment)" title="Xóa">🗑️</button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </app-card>
        </div>

        <!-- Modal -->
        @if (showModal) {
          <div class="modal-overlay" (click)="closeModal()">
            <div class="modal" (click)="$event.stopPropagation()">
              <h2>Thêm đăng ký</h2>
              <form (ngSubmit)="saveEnrollment()">
                <div class="form-group">
                  <label>Người dùng *</label>
                  <select [(ngModel)]="formData.user_id" name="user_id" required>
                    <option [ngValue]="null">-- Chọn người dùng --</option>
                    @for (user of users; track user.id) {
                      <option [ngValue]="user.id">{{ user.full_name }} ({{ user.email }})</option>
                    }
                  </select>
                </div>
                <div class="form-group">
                  <label>Khóa học *</label>
                  <select [(ngModel)]="formData.course_id" name="course_id" required>
                    <option [ngValue]="null">-- Chọn khóa học --</option>
                    @for (course of courses; track course.id) {
                      <option [ngValue]="course.id">{{ course.title }}</option>
                    }
                  </select>
                </div>
                <div class="form-group">
                  <label>Vai trò</label>
                  <select [(ngModel)]="formData.role_in_course" name="role_in_course">
                    <option value="STUDENT">Học viên</option>
                    <option value="TEACHER">Giảng viên</option>
                  </select>
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

    .filters { margin-bottom: 20px; }
    .filter-select { padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; min-width: 250px; }
    .filter-select:focus { outline: none; border-color: #0f3460; }

    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #f0f0f0; }
    th { background: #f5f7fa; font-weight: 600; color: #1a1a2e; }
    tr:hover { background: #fafafa; }

    .user-cell { display: flex; align-items: center; gap: 12px; }
    .avatar { width: 40px; height: 40px; background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
    .user-info { display: flex; flex-direction: column; }
    .user-info .name { font-weight: 500; color: #1a1a2e; }
    .user-info .email { font-size: 0.85rem; color: #888; }

    .role-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .role-badge.student { background: #e8f5e9; color: #2e7d32; }
    .role-badge.teacher { background: #fff3e0; color: #ef6c00; }

    .btn-icon { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 4px 8px; }
    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }

    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .modal { background: #fff; border-radius: 16px; padding: 24px; width: 90%; max-width: 500px; }
    .modal h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 20px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; }
    .form-group select { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; }
    .form-group select:focus { outline: none; border-color: #0f3460; }
    .modal-actions { display: flex; gap: 12px; margin-top: 20px; }
    .alert-error { padding: 10px; background: #ffebee; color: #c62828; border-radius: 8px; margin-bottom: 12px; }
  `]
})
export class EnrollmentManagementComponent implements OnInit {
  adminService = inject(AdminService);
  
  enrollments: any[] = [];
  courses: Course[] = [];
  users: User[] = [];
  isLoading = true;
  
  courseFilter: number | '' = '';
  
  showModal = false;
  formData: any = {};
  isSaving = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.adminService.getCourses().subscribe(courses => this.courses = courses);
    this.adminService.getUsers().subscribe(users => this.users = users);
    this.loadEnrollments();
  }

  loadEnrollments(): void {
    this.isLoading = true;
    const courseId = this.courseFilter || undefined;
    this.adminService.getEnrollments(courseId).subscribe({
      next: (enrollments) => {
        this.enrollments = enrollments;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  openCreateModal(): void {
    this.formData = { role_in_course: 'STUDENT' };
    this.errorMessage = '';
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.formData = {};
  }

  saveEnrollment(): void {
    this.errorMessage = '';
    this.isSaving = true;

    this.adminService.createEnrollment(this.formData).subscribe({
      next: () => {
        this.isSaving = false;
        this.closeModal();
        this.loadEnrollments();
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  deleteEnrollment(enrollment: any): void {
    if (confirm(`Bạn có chắc muốn xóa đăng ký của "${enrollment.user.full_name}" khỏi khóa học "${enrollment.course.title}"?`)) {
      this.adminService.deleteEnrollment(enrollment.id).subscribe({
        next: () => this.loadEnrollments(),
        error: (err) => alert(err.error?.detail || 'Có lỗi xảy ra')
      });
    }
  }
}

