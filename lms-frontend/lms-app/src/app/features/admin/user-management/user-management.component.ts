import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent, LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { AdminService, User } from '../../../core/services/admin.service';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <div>
            <a routerLink="/admin" class="back-link">← Quay lại</a>
            <h1>Quản lý người dùng</h1>
          </div>
          <button class="btn btn-primary" (click)="openCreateModal()">+ Thêm người dùng</button>
        </div>

        <!-- Filter -->
        <div class="filters">
          <input type="text" [(ngModel)]="searchTerm" placeholder="Tìm kiếm..." class="search-input" (input)="filterUsers()">
          <select [(ngModel)]="roleFilter" (change)="filterUsers()" class="filter-select">
            <option value="">Tất cả vai trò</option>
            <option value="STUDENT">Học viên</option>
            <option value="TEACHER">Giảng viên</option>
            <option value="ADMIN">Quản trị viên</option>
          </select>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && filteredUsers.length === 0"
          title="Không có người dùng"
          message="Chưa có người dùng nào hoặc không tìm thấy kết quả."
        ></app-empty-state>

        <div class="users-table" *ngIf="!isLoading && filteredUsers.length > 0">
          <app-card>
            <table>
              <thead>
                <tr>
                  <th>Người dùng</th>
                  <th>Email</th>
                  <th>Vai trò</th>
                  <th>Trạng thái</th>
                  <th>Ngày tạo</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                @for (user of filteredUsers; track user.id) {
                  <tr>
                    <td class="user-cell">
                      @if (user.avatar) {
                        <img [src]="user.avatar" class="avatar-img">
                      } @else {
                        <div class="avatar">{{ (user.full_name || 'U').charAt(0) }}</div>
                      }
                      <span>{{ user.full_name || user.username }}</span>
                    </td>
                    <td>{{ user.email }}</td>
                    <td><span class="role-badge" [class]="user.role.toLowerCase()">{{ user.role_display }}</span></td>
                    <td>
                      <span class="status-badge" [class.active]="user.is_active" [class.inactive]="!user.is_active">
                        {{ user.is_active ? 'Hoạt động' : 'Bị khóa' }}
                      </span>
                    </td>
                    <td>{{ user.date_joined | date:'dd/MM/yyyy' }}</td>
                    <td>
                      <button class="btn-icon" (click)="openEditModal(user)" title="Sửa">✏️</button>
                      <button class="btn-icon" (click)="deleteUser(user)" title="Xóa">🗑️</button>
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
              <h2>{{ editingUser ? 'Chỉnh sửa người dùng' : 'Thêm người dùng' }}</h2>
              <form (ngSubmit)="saveUser()">
                <div class="form-group">
                  <label>Username *</label>
                  <input type="text" [(ngModel)]="formData.username" name="username" [disabled]="!!editingUser" required>
                </div>
                <div class="form-group">
                  <label>Email *</label>
                  <input type="email" [(ngModel)]="formData.email" name="email" required>
                </div>
                <div class="form-group">
                  <label>Họ và tên</label>
                  <input type="text" [(ngModel)]="formData.full_name" name="full_name">
                </div>
                <div class="form-group">
                  <label>Vai trò</label>
                  <select [(ngModel)]="formData.role" name="role">
                    <option value="STUDENT">Học viên</option>
                    <option value="TEACHER">Giảng viên</option>
                    <option value="ADMIN">Quản trị viên</option>
                  </select>
                </div>
                @if (!editingUser) {
                  <div class="form-group">
                    <label>Mật khẩu *</label>
                    <input type="password" [(ngModel)]="formData.password" name="password" required>
                  </div>
                } @else {
                  <div class="form-group">
                    <label>Mật khẩu mới (để trống nếu không đổi)</label>
                    <input type="password" [(ngModel)]="formData.password" name="password">
                  </div>
                  <div class="form-group">
                    <label>
                      <input type="checkbox" [(ngModel)]="formData.is_active" name="is_active">
                      Tài khoản hoạt động
                    </label>
                  </div>
                }
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

    .filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
    .search-input, .filter-select { padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; }
    .search-input { flex: 1; min-width: 200px; }
    .filter-select { min-width: 150px; }
    .search-input:focus, .filter-select:focus { outline: none; border-color: #0f3460; }

    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #f0f0f0; }
    th { background: #f5f7fa; font-weight: 600; color: #1a1a2e; }
    tr:hover { background: #fafafa; }

    .user-cell { display: flex; align-items: center; gap: 12px; }
    .avatar { width: 36px; height: 36px; background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }
    .avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }

    .role-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .role-badge.student { background: #e8f5e9; color: #2e7d32; }
    .role-badge.teacher { background: #fff3e0; color: #ef6c00; }
    .role-badge.admin { background: #fce4ec; color: #c2185b; }

    .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .status-badge.active { background: #e8f5e9; color: #2e7d32; }
    .status-badge.inactive { background: #ffebee; color: #c62828; }

    .btn-icon { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 4px 8px; }
    .btn-icon:hover { opacity: 0.7; }

    .btn { padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }

    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .modal { background: #fff; border-radius: 16px; padding: 24px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
    .modal h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 20px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; }
    .form-group input, .form-group select { width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 0.95rem; }
    .form-group input:focus, .form-group select:focus { outline: none; border-color: #0f3460; }
    .form-group input[type="checkbox"] { width: auto; margin-right: 8px; }
    .modal-actions { display: flex; gap: 12px; margin-top: 20px; }
    .alert-error { padding: 10px; background: #ffebee; color: #c62828; border-radius: 8px; margin-bottom: 12px; }
  `]
})
export class UserManagementComponent implements OnInit {
  adminService = inject(AdminService);
  
  users: User[] = [];
  filteredUsers: User[] = [];
  isLoading = true;
  
  searchTerm = '';
  roleFilter = '';
  
  showModal = false;
  editingUser: User | null = null;
  formData: any = {};
  isSaving = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadUsers();
  }

  private loadUsers(): void {
    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.filterUsers();
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  filterUsers(): void {
    this.filteredUsers = this.users.filter(user => {
      const matchSearch = !this.searchTerm || 
        user.full_name?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        user.username?.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchRole = !this.roleFilter || user.role === this.roleFilter;
      return matchSearch && matchRole;
    });
  }

  openCreateModal(): void {
    this.editingUser = null;
    this.formData = { role: 'STUDENT', is_active: true };
    this.errorMessage = '';
    this.showModal = true;
  }

  openEditModal(user: User): void {
    this.editingUser = user;
    this.formData = {
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active,
      password: ''
    };
    this.errorMessage = '';
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.editingUser = null;
    this.formData = {};
  }

  saveUser(): void {
    this.errorMessage = '';
    this.isSaving = true;

    const observable = this.editingUser
      ? this.adminService.updateUser(this.editingUser.id, this.formData)
      : this.adminService.createUser(this.formData);

    observable.subscribe({
      next: () => {
        this.isSaving = false;
        this.closeModal();
        this.loadUsers();
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  deleteUser(user: User): void {
    if (confirm(`Bạn có chắc muốn xóa người dùng "${user.full_name || user.username}"?`)) {
      this.adminService.deleteUser(user.id).subscribe({
        next: () => this.loadUsers(),
        error: (err) => alert(err.error?.detail || 'Có lỗi xảy ra')
      });
    }
  }
}

