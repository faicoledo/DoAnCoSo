import { Component, inject, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <header class="header">
      <div class="header-left">
        <button class="menu-toggle" (click)="toggleSidebar.emit()">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <a routerLink="/dashboard" class="logo">LMS</a>
      </div>
      
      <div class="header-right">
        <button class="notification-btn" routerLink="/notifications">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          @if (unreadCount > 0) {
            <span class="badge">{{ unreadCount }}</span>
          }
        </button>
        
        <div class="user-menu">
          <button class="user-btn" (click)="showDropdown = !showDropdown">
            @if (authService.currentUser()?.avatar) {
              <img [src]="getAvatarUrl()" class="avatar-img" alt="Avatar">
            } @else {
              <div class="avatar">{{ userInitial }}</div>
            }
            <span class="user-name">{{ authService.currentUser()?.full_name }}</span>
          </button>
          
          @if (showDropdown) {
            <div class="dropdown">
              <a routerLink="/profile" class="dropdown-item">Hồ sơ cá nhân</a>
              @if (authService.isTeacher() || authService.isAdmin()) {
                <a routerLink="/teacher" class="dropdown-item">Quản lý giảng dạy</a>
              }
              @if (authService.isAdmin()) {
                <a routerLink="/admin" class="dropdown-item">Quản trị hệ thống</a>
              }
              <hr>
              <button class="dropdown-item logout" (click)="logout()">Đăng xuất</button>
            </div>
          }
        </div>
      </div>
    </header>
  `,
  styles: [`
    .header {
      height: 64px;
      background: #fff;
      border-bottom: 1px solid #e0e0e0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
    }
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .menu-toggle {
      display: flex;
      flex-direction: column;
      gap: 4px;
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
    }
    
    .menu-toggle span {
      width: 20px;
      height: 2px;
      background: #333;
      transition: 0.3s;
    }
    
    .logo {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1a1a2e;
      text-decoration: none;
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .notification-btn {
      position: relative;
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
      color: #666;
    }
    
    .notification-btn:hover {
      color: #1a1a2e;
    }
    
    .badge {
      position: absolute;
      top: 0;
      right: 0;
      background: #e74c3c;
      color: #fff;
      font-size: 0.7rem;
      padding: 2px 6px;
      border-radius: 10px;
      min-width: 18px;
      text-align: center;
    }
    
    .user-menu {
      position: relative;
    }
    
    .user-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      background: none;
      border: none;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: 8px;
      transition: 0.2s;
    }
    
    .user-btn:hover {
      background: #f5f5f5;
    }
    
    .avatar {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
    }
    
    .avatar-img {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      object-fit: cover;
    }
    
    .user-name {
      font-weight: 500;
      color: #333;
    }
    
    .dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      min-width: 200px;
      padding: 8px 0;
      margin-top: 8px;
    }
    
    .dropdown-item {
      display: block;
      width: 100%;
      padding: 12px 20px;
      text-align: left;
      background: none;
      border: none;
      cursor: pointer;
      color: #333;
      text-decoration: none;
      font-size: 0.95rem;
    }
    
    .dropdown-item:hover {
      background: #f5f5f5;
    }
    
    .dropdown hr {
      margin: 8px 0;
      border: none;
      border-top: 1px solid #eee;
    }
    
    .logout {
      color: #e74c3c;
    }
  `]
})
export class HeaderComponent {
  @Input() unreadCount = 0;
  @Output() toggleSidebar = new EventEmitter<void>();
  
  authService = inject(AuthService);
  showDropdown = false;

  get userInitial(): string {
    const name = this.authService.currentUser()?.full_name || '';
    return name.charAt(0).toUpperCase();
  }

  getAvatarUrl(): string {
    const avatar = this.authService.currentUser()?.avatar;
    if (!avatar) return '';
    if (avatar.startsWith('http')) return avatar;
    return `http://localhost:8000${avatar}`;
  }

  logout(): void {
    this.authService.logout();
  }
}


