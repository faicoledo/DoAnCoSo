import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { CourseService } from '../../../core/services/course.service';
import { Course } from '../../../core/models';

@Component({
  selector: 'app-my-courses',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="my-courses-page">
        <div class="page-header">
          <h1>Khóa học của tôi</h1>
          <p>Tất cả các khóa học bạn đã đăng ký</p>
        </div>
        
        <div class="filter-tabs">
          <button 
            class="tab" 
            [class.active]="activeFilter === 'all'"
            (click)="filterCourses('all')"
          >
            Tất cả ({{ allCourses.length }})
          </button>
          <button 
            class="tab" 
            [class.active]="activeFilter === 'ONGOING'"
            (click)="filterCourses('ONGOING')"
          >
            Đang diễn ra ({{ countByStatus('ONGOING') }})
          </button>
          <button 
            class="tab" 
            [class.active]="activeFilter === 'UPCOMING'"
            (click)="filterCourses('UPCOMING')"
          >
            Sắp diễn ra ({{ countByStatus('UPCOMING') }})
          </button>
          <button 
            class="tab" 
            [class.active]="activeFilter === 'COMPLETED'"
            (click)="filterCourses('COMPLETED')"
          >
            Đã hoàn thành ({{ countByStatus('COMPLETED') }})
          </button>
        </div>
        
        @if (isLoading) {
          <app-loading message="Đang tải khóa học..."></app-loading>
        } @else if (filteredCourses.length === 0) {
          <app-empty-state 
            title="Không có khóa học nào"
            [description]="activeFilter === 'all' ? 'Bạn chưa đăng ký khóa học nào' : 'Không có khóa học nào ở trạng thái này'"
          >
            <a routerLink="/courses/explore" class="btn btn-primary">Khám phá khóa học</a>
          </app-empty-state>
        } @else {
          <div class="courses-grid">
            @for (course of filteredCourses; track course.id) {
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
                    <span class="status-badge" [class]="course.status?.toLowerCase()">
                      {{ course.status_display || course.status }}
                    </span>
                  </div>
                  <div class="course-info">
                    <span class="course-subject">{{ course.subject?.name }}</span>
                    <h3 class="course-title">{{ course.title }}</h3>
                    <p class="course-description">{{ course.description | slice:0:80 }}...</p>
                    <div class="course-meta">
                      <span class="teacher">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                        {{ course.teacher?.full_name || 'Chưa có giảng viên' }}
                      </span>
                    </div>
                  </div>
                </a>
              </app-card>
            }
          </div>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .my-courses-page {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .page-header {
      margin-bottom: 24px;
    }
    
    .page-header h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .page-header p {
      color: #666;
    }
    
    .filter-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 32px;
      flex-wrap: wrap;
    }
    
    .tab {
      padding: 10px 20px;
      border: 2px solid #e0e0e0;
      background: #fff;
      border-radius: 25px;
      font-size: 0.9rem;
      font-weight: 500;
      color: #666;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    
    .tab:hover {
      border-color: #0f3460;
      color: #0f3460;
    }
    
    .tab.active {
      background: #0f3460;
      border-color: #0f3460;
      color: #fff;
    }
    
    .courses-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
    }
    
    .course-card {
      display: block;
      text-decoration: none;
      color: inherit;
    }
    
    .course-thumbnail {
      height: 180px;
      overflow: hidden;
      position: relative;
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
    
    .status-badge {
      position: absolute;
      top: 12px;
      right: 12px;
      font-size: 0.75rem;
      padding: 4px 12px;
      border-radius: 15px;
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
    
    .course-info {
      padding: 20px;
    }
    
    .course-subject {
      font-size: 0.75rem;
      color: #0f3460;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .course-title {
      font-size: 1.15rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 8px 0;
      line-height: 1.4;
    }
    
    .course-description {
      font-size: 0.9rem;
      color: #666;
      line-height: 1.5;
      margin-bottom: 16px;
    }
    
    .course-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      color: #888;
      font-size: 0.85rem;
    }
    
    .teacher {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    
    .teacher svg {
      width: 16px;
      height: 16px;
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
  `]
})
export class MyCoursesComponent implements OnInit {
  private courseService = inject(CourseService);
  
  allCourses: Course[] = [];
  filteredCourses: Course[] = [];
  isLoading = true;
  activeFilter: string = 'all';

  ngOnInit(): void {
    this.loadMyCourses();
  }

  private loadMyCourses(): void {
    this.courseService.getMyCourses().subscribe({
      next: (res) => {
        this.allCourses = res.results;
        this.filteredCourses = res.results;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  filterCourses(status: string): void {
    this.activeFilter = status;
    if (status === 'all') {
      this.filteredCourses = this.allCourses;
    } else {
      this.filteredCourses = this.allCourses.filter(c => c.status === status);
    }
  }

  countByStatus(status: string): number {
    return this.allCourses.filter(c => c.status === status).length;
  }
}

