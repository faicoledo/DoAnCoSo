import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>LMS</h1>
          <p>Tạo tài khoản mới</p>
        </div>
        
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label for="full_name">Họ và tên</label>
            <input 
              type="text" 
              id="full_name" 
              formControlName="full_name"
              placeholder="Nhập họ và tên"
            >
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              formControlName="email"
              placeholder="Nhập email của bạn"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Mật khẩu</label>
            <input 
              type="password" 
              id="password" 
              formControlName="password"
              placeholder="Nhập mật khẩu (tối thiểu 8 ký tự)"
            >
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">Xác nhận mật khẩu</label>
            <input 
              type="password" 
              id="confirmPassword" 
              formControlName="confirmPassword"
              placeholder="Nhập lại mật khẩu"
            >
          </div>
          
          @if (errorMessage) {
            <div class="alert alert-error">{{ errorMessage }}</div>
          }
          
          @if (successMessage) {
            <div class="alert alert-success">{{ successMessage }}</div>
          }
          
          <button type="submit" class="btn btn-primary" [disabled]="form.invalid || isLoading">
            @if (isLoading) {
              <span class="spinner"></span> Đang xử lý...
            } @else {
              Đăng ký
            }
          </button>
        </form>
        
        <div class="auth-footer">
          <p>Đã có tài khoản? <a routerLink="/auth/login">Đăng nhập</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 20px;
    }
    
    .auth-card {
      background: #fff;
      border-radius: 16px;
      padding: 40px;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .auth-header {
      text-align: center;
      margin-bottom: 32px;
    }
    
    .auth-header h1 {
      font-size: 2.5rem;
      font-weight: 700;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .auth-header p {
      color: #666;
    }
    
    .form-group {
      margin-bottom: 20px;
    }
    
    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #333;
    }
    
    .form-group input {
      width: 100%;
      padding: 14px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      font-size: 1rem;
      transition: all 0.3s ease;
      box-sizing: border-box;
    }
    
    .form-group input:focus {
      outline: none;
      border-color: #0f3460;
      box-shadow: 0 0 0 3px rgba(15, 52, 96, 0.1);
    }
    
    .alert {
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 20px;
    }
    
    .alert-error {
      background: #fdeaea;
      color: #e74c3c;
    }
    
    .alert-success {
      background: #d4edda;
      color: #155724;
    }
    
    .btn {
      width: 100%;
      padding: 14px;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
      color: #fff;
    }
    
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(15, 52, 96, 0.4);
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
    
    .auth-footer {
      text-align: center;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #eee;
    }
    
    .auth-footer a {
      color: #0f3460;
      font-weight: 600;
      text-decoration: none;
    }
  `]
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  form: FormGroup = this.fb.group({
    full_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', Validators.required]
  });

  isLoading = false;
  errorMessage = '';
  successMessage = '';

  onSubmit(): void {
    if (this.form.invalid) return;
    
    if (this.form.value.password !== this.form.value.confirmPassword) {
      this.errorMessage = 'Mật khẩu xác nhận không khớp';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const data = {
      full_name: this.form.value.full_name,
      email: this.form.value.email,
      password: this.form.value.password,
      password_confirm: this.form.value.confirmPassword
    };

    this.authService.register(data).subscribe({
      next: () => {
        this.successMessage = 'Đăng ký thành công! Đang chuyển hướng...';
        setTimeout(() => this.router.navigate(['/auth/login']), 2000);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
      }
    });
  }
}


