import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { TeacherService } from '../../../core/services/teacher.service';
import { Course } from '../../../core/models';

@Component({
  selector: 'app-course-management',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="course-management">
        <div class="page-header">
          <div>
            <a routerLink="/teacher" class="back-link">← Quay lại</a>
            <h1>Quản lý khóa học</h1>
          </div>
        </div>
        
        @if (isLoading) {
          <app-loading message="Đang tải khóa học..."></app-loading>
        } @else if (courses.length === 0) {
          <app-empty-state 
            title="Chưa có khóa học"
            description="Bạn chưa được phân công giảng dạy khóa học nào"
          ></app-empty-state>
        } @else {
          <div class="courses-grid">
            @for (course of courses; track course.id) {
              <app-card [hoverable]="true">
                <div class="course-card">
                  <div class="course-header">
                    <span class="subject-tag">{{ course.subject?.name || 'Chưa phân loại' }}</span>
                    <span class="status-badge" [class]="getStatusClass(course)">
                      {{ course.status_display || course.status }}
                    </span>
                  </div>
                  
                  <h3 class="course-title">{{ course.title }}</h3>
                  
                  @if (course.description) {
                    <p class="course-desc">{{ course.description | slice:0:120 }}{{ course.description.length > 120 ? '...' : '' }}</p>
                  }
                  
                  <div class="course-stats">
                    <div class="stat">
                      <span class="stat-value">{{ (course.modules_count ?? course.total_modules) || 0 }}</span>
                      <span class="stat-label">Chương</span>
                    </div>
                    <div class="stat">
                      <span class="stat-value">{{ (course.students_count ?? course.total_students) || 0 }}</span>
                      <span class="stat-label">Học viên</span>
                    </div>
                  </div>
                  
                  <div class="course-dates">
                    <div class="date-item">
                      <span class="date-label">Bắt đầu:</span>
                      <span class="date-value">{{ (course.start_date | date:'dd/MM/yyyy') || 'Chưa đặt' }}</span>
                    </div>
                    <div class="date-item">
                      <span class="date-label">Kết thúc:</span>
                      <span class="date-value">{{ (course.end_date | date:'dd/MM/yyyy') || 'Chưa đặt' }}</span>
                    </div>
                  </div>
                  
                  <a [routerLink]="['/teacher/courses', course.id]" class="btn btn-primary btn-full">
                    Quản lý nội dung
                  </a>
                </div>
              </app-card>
            }
          </div>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .course-management { max-width: 1200px; margin: 0 auto; }
    .page-header { margin-bottom: 32px; }
    .back-link { color: #666; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 8px; }
    .back-link:hover { color: #0f3460; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; }
    
    .courses-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 24px;
    }
    
    .course-card { display: flex; flex-direction: column; height: 100%; }
    
    .course-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    
    .subject-tag {
      font-size: 0.75rem;
      color: #0f3460;
      font-weight: 600;
      text-transform: uppercase;
      background: #e3f2fd;
      padding: 4px 10px;
      border-radius: 4px;
    }
    
    .status-badge {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 12px;
    }
    .status-badge.ongoing { background: #e8f5e9; color: #2e7d32; }
    .status-badge.upcoming { background: #fff3e0; color: #ef6c00; }
    .status-badge.completed { background: #f5f5f5; color: #666; }
    
    .course-title {
      font-size: 1.15rem;
      color: #1a1a2e;
      margin: 0 0 8px 0;
      line-height: 1.4;
    }
    
    .course-desc {
      font-size: 0.9rem;
      color: #666;
      line-height: 1.5;
      margin: 0 0 16px 0;
      flex-grow: 1;
    }
    
    .course-stats {
      display: flex;
      gap: 24px;
      margin-bottom: 16px;
      padding: 12px 0;
      border-top: 1px solid #f0f0f0;
      border-bottom: 1px solid #f0f0f0;
    }
    
    .stat { text-align: center; }
    .stat-value { display: block; font-size: 1.25rem; font-weight: 700; color: #0f3460; }
    .stat-label { font-size: 0.8rem; color: #888; }
    
    .course-dates {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
      font-size: 0.85rem;
    }
    
    .date-item { display: flex; flex-direction: column; }
    .date-label { color: #888; font-size: 0.75rem; }
    .date-value { color: #333; font-weight: 500; }
    
    .btn {
      display: inline-block;
      padding: 12px 24px;
      border-radius: 10px;
      font-weight: 600;
      text-decoration: none;
      text-align: center;
      transition: all 0.3s ease;
    }
    .btn-full { width: 100%; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(15, 52, 96, 0.4); }
  `]
})
export class CourseManagementComponent implements OnInit {
  private teacherService = inject(TeacherService);
  
  courses: Course[] = [];
  isLoading = true;

  ngOnInit(): void {
    this.loadCourses();
  }

  private loadCourses(): void {
    this.teacherService.getMyCourses().subscribe({
      next: (courses: any[]) => {
        this.courses = courses;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  getStatusClass(course: any): string {
    const status = course.status?.toLowerCase() || '';
    if (status === 'ongoing') return 'ongoing';
    if (status === 'upcoming') return 'upcoming';
    if (status === 'completed') return 'completed';
    return '';
  }
}


