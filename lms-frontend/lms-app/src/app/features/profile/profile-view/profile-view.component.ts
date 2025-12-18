import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { AuthService } from '../../../core/services/auth.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-profile-view',
  standalone: true,
  imports: [CommonModule, FormsModule, MainLayoutComponent, CardComponent],
  template: `
    <app-main-layout>
      <div class="profile-page">
        <app-card>
          <div class="profile-header">
            <div class="avatar-container">
              @if (avatarPreview || authService.currentUser()?.avatar) {
                <img [src]="avatarPreview || getAvatarUrl()" class="avatar-img" alt="Avatar">
              } @else {
                <div class="avatar">{{ userInitial }}</div>
              }
              @if (isEditing) {
                <label class="avatar-upload">
                  <input type="file" accept="image/*" (change)="onAvatarChange($event)" hidden>
                  <span class="upload-icon">📷</span>
                </label>
              }
            </div>
            <div class="profile-info">
              <h1>{{ authService.currentUser()?.full_name }}</h1>
              <p class="email">{{ authService.currentUser()?.email }}</p>
              <span class="role-badge">{{ getRoleName() }}</span>
            </div>
          </div>
        </app-card>
        
        @if (!isEditing) {
          <app-card title="Thông tin tài khoản">
            <div class="info-list">
              <div class="info-item">
                <span class="label">Họ và tên</span>
                <span class="value">{{ authService.currentUser()?.full_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">Email</span>
                <span class="value">{{ authService.currentUser()?.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">Vai trò</span>
                <span class="value">{{ getRoleName() }}</span>
              </div>
            </div>
            <button class="btn btn-primary" (click)="startEditing()">Chỉnh sửa hồ sơ</button>
          </app-card>
        } @else {
          <app-card title="Chỉnh sửa hồ sơ">
            <form (ngSubmit)="saveProfile()">
              <div class="form-group">
                <label>Email đăng nhập</label>
                <input type="email" [(ngModel)]="editForm.email" name="email" class="form-control">
              </div>
              <div class="form-group">
                <label>Họ và tên</label>
                <input type="text" [(ngModel)]="editForm.full_name" name="full_name" class="form-control">
              </div>
              <div class="form-group">
                <label>Số điện thoại</label>
                <input type="text" [(ngModel)]="editForm.phone" name="phone" class="form-control">
              </div>
              <div class="form-group">
                <label>Giới thiệu</label>
                <textarea [(ngModel)]="editForm.bio" name="bio" class="form-control" rows="3"></textarea>
              </div>
              
              <h3 class="section-title">Đổi mật khẩu</h3>
              <div class="form-group">
                <label>Mật khẩu mới</label>
                <input type="password" [(ngModel)]="editForm.password" name="password" class="form-control" placeholder="Để trống nếu không đổi">
              </div>
              <div class="form-group">
                <label>Xác nhận mật khẩu</label>
                <input type="password" [(ngModel)]="editForm.password_confirm" name="password_confirm" class="form-control">
              </div>
              
              @if (errorMessage) {
                <div class="alert alert-error">{{ errorMessage }}</div>
              }
              @if (successMessage) {
                <div class="alert alert-success">{{ successMessage }}</div>
              }
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" [disabled]="isSaving">
                  {{ isSaving ? 'Đang lưu...' : 'Lưu thay đổi' }}
                </button>
                <button type="button" class="btn btn-outline" (click)="cancelEditing()">Hủy</button>
              </div>
            </form>
          </app-card>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .profile-page {
      max-width: 800px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    .profile-header {
      display: flex;
      align-items: center;
      gap: 24px;
      padding: 20px;
    }
    
    .avatar {
      width: 100px;
      height: 100px;
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.5rem;
      font-weight: 600;
    }
    
    .profile-info h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    
    .email {
      color: #666;
      margin-bottom: 12px;
    }
    
    .role-badge {
      display: inline-block;
      padding: 6px 16px;
      background: #e3f2fd;
      color: #1565c0;
      border-radius: 20px;
      font-size: 0.9rem;
      font-weight: 500;
    }
    
    .info-list {
      display: flex;
      flex-direction: column;
    }
    
    .info-item {
      display: flex;
      justify-content: space-between;
      padding: 16px 0;
      border-bottom: 1px solid #f0f0f0;
    }
    
    .info-item:last-child {
      border-bottom: none;
    }
    
    .label {
      color: #666;
    }
    
    .value {
      font-weight: 500;
      color: #1a1a2e;
    }
    
    .avatar-container {
      position: relative;
    }
    
    .avatar-img {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
    }
    
    .avatar-upload {
      position: absolute;
      bottom: 0;
      right: 0;
      width: 32px;
      height: 32px;
      background: #0f3460;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    
    .upload-icon {
      font-size: 14px;
    }
    
    .form-group {
      margin-bottom: 16px;
    }
    
    .form-group label {
      display: block;
      margin-bottom: 6px;
      color: #666;
      font-size: 0.9rem;
    }
    
    .form-control {
      width: 100%;
      padding: 12px;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      font-size: 1rem;
    }
    
    .form-control:focus {
      outline: none;
      border-color: #0f3460;
    }
    
    .section-title {
      margin: 24px 0 16px;
      font-size: 1.1rem;
      color: #1a1a2e;
    }
    
    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 24px;
    }
    
    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
    }
    
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(15, 52, 96, 0.3);
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #e0e0e0;
      color: #666;
    }
    
    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .alert {
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    
    .alert-error {
      background: #fdeaea;
      color: #e74c3c;
    }
    
    .alert-success {
      background: #d4edda;
      color: #155724;
    }
  `]
})
export class ProfileViewComponent implements OnInit {
  authService = inject(AuthService);
  api = inject(ApiService);
  
  isEditing = false;
  isSaving = false;
  errorMessage = '';
  successMessage = '';
  avatarPreview: string | null = null;
  avatarFile: File | null = null;
  
  editForm = {
    email: '',
    full_name: '',
    phone: '',
    bio: '',
    password: '',
    password_confirm: ''
  };

  ngOnInit(): void {
    this.fetchProfile();
  }

  fetchProfile(): void {
    // Load fresh profile from API
    this.api.get<any>('/auth/me/').subscribe({
      next: (user) => {
        this.authService.updateCurrentUser(user);
        this.loadFormData();
      },
      error: () => {
        this.loadFormData();
      }
    });
  }

  loadFormData(): void {
    const user = this.authService.currentUser();
    if (user) {
      this.editForm.email = user.email || '';
      this.editForm.full_name = user.full_name || '';
      this.editForm.phone = user.phone || '';
      this.editForm.bio = user.bio || '';
    }
  }

  loadProfile(): void {
    this.loadFormData();
  }

  get userInitial(): string {
    const name = this.authService.currentUser()?.full_name || '';
    return name.charAt(0).toUpperCase();
  }

  getRoleName(): string {
    const roles: Record<string, string> = {
      'STUDENT': 'Học viên',
      'TEACHER': 'Giảng viên',
      'ADMIN': 'Quản trị viên'
    };
    return roles[this.authService.currentUser()?.role || ''] || 'Không xác định';
  }

  getAvatarUrl(): string {
    const avatar = this.authService.currentUser()?.avatar;
    if (!avatar) return '';
    // If already full URL, return as is
    if (avatar.startsWith('http')) return avatar;
    // Otherwise prepend backend URL
    return `http://localhost:8000${avatar}`;
  }

  startEditing(): void {
    this.loadProfile();
    this.isEditing = true;
    this.errorMessage = '';
    this.successMessage = '';
  }

  cancelEditing(): void {
    this.isEditing = false;
    this.avatarPreview = null;
    this.avatarFile = null;
    this.editForm.password = '';
    this.editForm.password_confirm = '';
  }

  onAvatarChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.avatarFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.avatarPreview = e.target?.result as string;
      };
      reader.readAsDataURL(this.avatarFile);
    }
  }

  saveProfile(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.isSaving = true;

    const formData = new FormData();
    if (this.editForm.email) formData.append('email', this.editForm.email);
    if (this.editForm.full_name) formData.append('full_name', this.editForm.full_name);
    formData.append('phone', this.editForm.phone || '');
    formData.append('bio', this.editForm.bio || '');
    if (this.avatarFile) formData.append('avatar', this.avatarFile);
    if (this.editForm.password && this.editForm.password.trim()) {
      formData.append('password', this.editForm.password);
      formData.append('password_confirm', this.editForm.password_confirm || '');
    }

    this.api.patch<any>('/auth/me/', formData).subscribe({
      next: (res) => {
        this.isSaving = false;
        this.successMessage = 'Cập nhật hồ sơ thành công!';
        // Update local user data
        if (res.user) {
          this.authService.updateCurrentUser(res.user);
        }
        this.editForm.password = '';
        this.editForm.password_confirm = '';
        setTimeout(() => {
          this.isEditing = false;
          this.successMessage = '';
        }, 1500);
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || 'Có lỗi xảy ra. Vui lòng thử lại.';
      }
    });
  }
}


