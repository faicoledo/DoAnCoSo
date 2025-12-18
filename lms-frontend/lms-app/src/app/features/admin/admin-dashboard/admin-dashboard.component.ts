import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { LoadingComponent } from '../../../shared/components';
import { AdminService, AdminStats } from '../../../core/services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, LoadingComponent],
  template: `
    <app-main-layout>
      <div class="admin-dashboard">
        <div class="page-header">
          <h1>Quản trị hệ thống</h1>
          <p>Tổng quan và quản lý toàn bộ hệ thống</p>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <div class="stats-grid" *ngIf="!isLoading && stats">
          <div class="stat-card">
            <div class="stat-icon users">👥</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_users }}</span>
              <span class="stat-label">Người dùng</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon students">🎓</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_students }}</span>
              <span class="stat-label">Học viên</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon teachers">👨‍🏫</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_teachers }}</span>
              <span class="stat-label">Giảng viên</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon courses">📚</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_courses }}</span>
              <span class="stat-label">Khóa học</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon subjects">📖</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_subjects }}</span>
              <span class="stat-label">Môn học</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon enrollments">📝</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_enrollments }}</span>
              <span class="stat-label">Đăng ký</span>
            </div>
          </div>
        </div>

        <div class="management-section">
          <h2>Quản lý</h2>
          <div class="management-grid">
            <a routerLink="/admin/users" class="management-card">
              <div class="card-icon">👥</div>
              <div class="card-info">
                <h3>Người dùng</h3>
                <p>Quản lý tài khoản người dùng</p>
              </div>
              <span class="arrow">→</span>
            </a>
            <a routerLink="/admin/subjects" class="management-card">
              <div class="card-icon">📖</div>
              <div class="card-info">
                <h3>Môn học</h3>
                <p>Quản lý danh mục môn học</p>
              </div>
              <span class="arrow">→</span>
            </a>
            <a routerLink="/admin/courses" class="management-card">
              <div class="card-icon">📚</div>
              <div class="card-info">
                <h3>Khóa học</h3>
                <p>Quản lý các khóa học</p>
              </div>
              <span class="arrow">→</span>
            </a>
            <a routerLink="/admin/enrollments" class="management-card">
              <div class="card-icon">📝</div>
              <div class="card-info">
                <h3>Đăng ký</h3>
                <p>Quản lý đăng ký khóa học</p>
              </div>
              <span class="arrow">→</span>
            </a>
          </div>
        </div>

        <div class="quick-actions">
          <h2>Truy cập nhanh</h2>
          <a href="http://localhost:8000/admin/" target="_blank" class="django-admin-link">
            <span class="link-icon">⚙️</span>
            <span>Django Admin (Quản lý chi tiết)</span>
            <span class="external">↗</span>
          </a>
          <p class="admin-note">
            Django Admin cho phép quản lý chi tiết: nội dung khóa học, bài tập, câu hỏi, import Excel, v.v.
          </p>
        </div>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .admin-dashboard { max-width: 1200px; margin: 0 auto; }
    .page-header { margin-bottom: 32px; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; margin-bottom: 4px; }
    .page-header p { color: #666; }

    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 40px; }
    .stat-card { display: flex; align-items: center; gap: 16px; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .stat-icon { font-size: 2rem; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
    .stat-icon.users { background: #e3f2fd; }
    .stat-icon.students { background: #e8f5e9; }
    .stat-icon.teachers { background: #fff3e0; }
    .stat-icon.courses { background: #fce4ec; }
    .stat-icon.subjects { background: #f3e5f5; }
    .stat-icon.enrollments { background: #e0f7fa; }
    .stat-info { display: flex; flex-direction: column; }
    .stat-value { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; }
    .stat-label { font-size: 0.85rem; color: #888; }

    .management-section, .quick-actions { margin-bottom: 32px; }
    .management-section h2, .quick-actions h2 { font-size: 1.25rem; color: #1a1a2e; margin-bottom: 16px; }

    .management-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
    .management-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      text-decoration: none;
      color: inherit;
      transition: all 0.3s;
      border: 2px solid transparent;
    }
    .management-card:hover { border-color: #0f3460; transform: translateX(4px); }
    .card-icon { font-size: 2rem; }
    .card-info { flex: 1; }
    .card-info h3 { font-size: 1.1rem; color: #1a1a2e; margin-bottom: 4px; }
    .card-info p { font-size: 0.9rem; color: #666; }
    .arrow { font-size: 1.2rem; color: #ccc; }
    .management-card:hover .arrow { color: #0f3460; }

    .django-admin-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 500;
      transition: all 0.3s;
    }
    .django-admin-link:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(15, 52, 96, 0.3); }
    .link-icon { font-size: 1.5rem; }
    .external { margin-left: auto; opacity: 0.7; }
    .admin-note { margin-top: 12px; font-size: 0.9rem; color: #666; }
  `]
})
export class AdminDashboardComponent implements OnInit {
  adminService = inject(AdminService);
  stats: AdminStats | null = null;
  isLoading = true;

  ngOnInit(): void {
    this.loadStats();
  }

  private loadStats(): void {
    this.adminService.getStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
