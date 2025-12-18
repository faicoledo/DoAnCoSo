import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { CourseService } from '../../../core/services/course.service';
import { AuthService } from '../../../core/services/auth.service';
import { Course } from '../../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="dashboard">
        <div class="welcome-section">
          <h1>Xin chào, {{ authService.currentUser()?.full_name }}!</h1>
          <p>Chào mừng bạn quay trở lại hệ thống học tập</p>
        </div>
        
        <div class="stats-grid">
          <app-card>
            <div class="stat-item">
              <div class="stat-icon blue">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                </svg>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ myCourses.length }}</span>
                <span class="stat-label">Khóa học đang học</span>
              </div>
            </div>
          </app-card>
          
          <app-card>
            <div class="stat-item">
              <div class="stat-icon green">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                </svg>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ submittedCount }}</span>
                <span class="stat-label">Bài tập đã nộp</span>
              </div>
            </div>
          </app-card>
        </div>
        
        <section class="courses-section">
          <div class="section-header">
            <h2>Khóa học của tôi</h2>
            <a routerLink="/courses" class="view-all">Xem tất cả</a>
          </div>
          
          @if (isLoading) {
            <app-loading message="Đang tải khóa học..."></app-loading>
          } @else if (myCourses.length === 0) {
            <app-empty-state 
              title="Không có khóa học đang diễn ra"
              description="Bạn không có khóa học nào đang diễn ra. Xem tất cả khóa học của bạn hoặc khám phá khóa học mới."
            >
              <a routerLink="/courses" class="btn btn-outline">Khóa học của tôi</a>
              <a routerLink="/courses/explore" class="btn btn-primary">Khám phá khóa học</a>
            </app-empty-state>
          } @else {
            <div class="courses-grid">
              @for (course of myCourses.slice(0, 4); track course.id) {
                <app-card [hoverable]="true" [clickable]="true" [noPadding]="true">
                  <a [routerLink]="['/courses', course.id]" class="course-card">
                    <div class="course-thumbnail">
                      @if (course.thumbnail) {
                        <img [src]="course.thumbnail" [alt]="course.title">
                      } @else {
                        <div class="placeholder-thumbnail">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                          </svg>
                        </div>
                      }
                    </div>
                    <div class="course-info">
                      <span class="course-subject">{{ course.subject?.name }}</span>
                      <h3 class="course-title">{{ course.title }}</h3>
                      <p class="course-teacher">{{ course.teacher?.full_name }}</p>
                    </div>
                  </a>
                </app-card>
              }
            </div>
          }
        </section>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .dashboard {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .welcome-section {
      margin-bottom: 32px;
    }
    
    .welcome-section h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .welcome-section p {
      color: #666;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .stat-icon svg {
      width: 28px;
      height: 28px;
    }
    
    .stat-icon.blue {
      background: linear-gradient(135deg, #e3f2fd, #bbdefb);
      color: #1565c0;
    }
    
    .stat-icon.green {
      background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
      color: #2e7d32;
    }
    
    .stat-icon.orange {
      background: linear-gradient(135deg, #fff3e0, #ffe0b2);
      color: #ef6c00;
    }
    
    .stat-info {
      display: flex;
      flex-direction: column;
    }
    
    .stat-value {
      font-size: 1.75rem;
      font-weight: 700;
      color: #1a1a2e;
    }
    
    .stat-label {
      font-size: 0.9rem;
      color: #666;
    }
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .section-header h2 {
      font-size: 1.25rem;
      color: #1a1a2e;
    }
    
    .view-all {
      color: #0f3460;
      text-decoration: none;
      font-weight: 500;
    }
    
    .view-all:hover {
      text-decoration: underline;
    }
    
    .courses-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
    }
    
    .course-card {
      display: block;
      text-decoration: none;
      color: inherit;
    }
    
    .course-thumbnail {
      height: 160px;
      overflow: hidden;
    }
    
    .course-thumbnail img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .placeholder-thumbnail {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #1a1a2e, #0f3460);
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255,255,255,0.5);
    }
    
    .placeholder-thumbnail svg {
      width: 48px;
      height: 48px;
    }
    
    .course-info {
      padding: 20px;
    }
    
    .course-header-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }
    
    .course-subject {
      font-size: 0.8rem;
      color: #0f3460;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .status-badge {
      font-size: 0.7rem;
      padding: 3px 8px;
      border-radius: 12px;
      font-weight: 600;
    }
    
    .status-badge.ongoing {
      background: #d4edda;
      color: #155724;
    }
    
    .status-badge.upcoming {
      background: #fff3cd;
      color: #856404;
    }
    
    .status-badge.completed {
      background: #e2e3e5;
      color: #383d41;
    }
    
    .course-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 8px 0;
      line-height: 1.4;
    }
    
    .course-teacher {
      font-size: 0.9rem;
      color: #666;
    }
    
    .btn {
      display: inline-block;
      padding: 12px 24px;
      border-radius: 10px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.3s ease;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
    }
    
    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(15, 52, 96, 0.4);
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #0f3460;
      color: #0f3460;
      margin-right: 12px;
    }
    
    .btn-outline:hover {
      background: #0f3460;
      color: #fff;
    }
  `]
})
export class DashboardComponent implements OnInit {
  courseService = inject(CourseService);
  authService = inject(AuthService);
  
  myCourses: Course[] = [];
  submittedCount = 0;
  isLoading = true;

  ngOnInit(): void {
    this.loadMyCourses();
    this.loadSubmittedCount();
  }

  private loadMyCourses(): void {
    // Chỉ lấy khóa học đang diễn ra cho dashboard
    this.courseService.getMyCourses({ status: 'ONGOING' }).subscribe({
      next: (res) => {
        this.myCourses = res.results;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  private loadSubmittedCount(): void {
    this.courseService.getSubmittedAttemptsCount().subscribe({
      next: (res) => {
        this.submittedCount = res.count;
      },
      error: () => {}
    });
  }
}


