import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { TeacherService, TeacherStats } from '../../../core/services/teacher.service';
import { AuthService } from '../../../core/services/auth.service';
import { Course } from '../../../core/models';

@Component({
  selector: 'app-teacher-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      <div class="teacher-dashboard">
        <div class="page-header">
          <h1>Quản lý giảng dạy</h1>
          <p>Xin chào, {{ authService.currentUser()?.full_name }}</p>
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
                <span class="stat-value">{{ stats?.total_courses || 0 }}</span>
                <span class="stat-label">Khóa học</span>
              </div>
            </div>
          </app-card>
          
          <app-card>
            <div class="stat-item">
              <div class="stat-icon green">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                </svg>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats?.total_students || 0 }}</span>
                <span class="stat-label">Học viên</span>
              </div>
            </div>
          </app-card>
          
          <app-card>
            <div class="stat-item">
              <div class="stat-icon purple">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats?.total_assignments || 0 }}</span>
                <span class="stat-label">Bài tập</span>
              </div>
            </div>
          </app-card>
          
          <app-card>
            <div class="stat-item">
              <div class="stat-icon orange">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats?.pending_submissions || 0 }}</span>
                <span class="stat-label">Chờ chấm điểm</span>
              </div>
            </div>
          </app-card>
        </div>
        
        <section class="courses-section">
          <div class="section-header">
            <h2>Khóa học của tôi</h2>
            <a routerLink="courses" class="btn btn-outline">Quản lý khóa học</a>
          </div>
          
          @if (isLoading) {
            <app-loading message="Đang tải..."></app-loading>
          } @else {
            <div class="courses-grid">
              @for (course of courses.slice(0, 4); track course.id) {
                <app-card [hoverable]="true" [clickable]="true" [noPadding]="true">
                  <a [routerLink]="['courses', course.id]" class="course-card">
                    <div class="course-thumbnail">
                      @if (course.thumbnail) {
                        <img [src]="course.thumbnail" [alt]="course.title">
                      } @else {
                        <div class="placeholder">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                          </svg>
                        </div>
                      }
                    </div>
                    <div class="course-info">
                      <h3>{{ course.title }}</h3>
                      <span class="course-subject">{{ course.subject?.name }}</span>
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
    .teacher-dashboard {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .page-header {
      margin-bottom: 32px;
    }
    
    .page-header h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    
    .page-header p {
      color: #666;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
    
    .stat-icon.blue { background: #e3f2fd; color: #1565c0; }
    .stat-icon.green { background: #e8f5e9; color: #2e7d32; }
    .stat-icon.purple { background: #f3e5f5; color: #7b1fa2; }
    .stat-icon.orange { background: #fff3e0; color: #ef6c00; }
    
    .stat-value {
      display: block;
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
    
    .btn {
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 500;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #0f3460;
      color: #0f3460;
    }
    
    .btn-outline:hover {
      background: #0f3460;
      color: #fff;
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
      height: 140px;
      overflow: hidden;
    }
    
    .course-thumbnail img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #1a1a2e, #0f3460);
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255,255,255,0.5);
    }
    
    .placeholder svg {
      width: 40px;
      height: 40px;
    }
    
    .course-info {
      padding: 16px;
    }
    
    .course-info h3 {
      font-size: 1rem;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    
    .course-subject {
      font-size: 0.85rem;
      color: #666;
    }
  `]
})
export class TeacherDashboardComponent implements OnInit {
  private teacherService = inject(TeacherService);
  authService = inject(AuthService);
  
  stats: TeacherStats | null = null;
  courses: Course[] = [];
  isLoading = true;

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.teacherService.getStats().subscribe({
      next: (stats) => this.stats = stats,
      error: () => {}
    });

    this.teacherService.getMyCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}


