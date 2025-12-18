import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { CourseService } from '../../../core/services/course.service';
import { Course, Module } from '../../../core/models';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      @if (isLoading) {
        <app-loading [overlay]="true" message="Đang tải khóa học..."></app-loading>
      } @else if (course) {
        <div class="course-detail">
          <div class="course-header">
            <div class="header-content">
              <span class="subject-badge">{{ course.subject?.name }}</span>
              <h1>{{ course.title }}</h1>
              <p class="description">{{ course.description }}</p>
              <div class="meta">
                <span class="teacher">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  {{ course.teacher?.full_name }}
                </span>
                <span class="modules-count">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                  </svg>
                  {{ course.modules?.length || 0 }} chương
                </span>
              </div>
              
            </div>
            
            @if (course.thumbnail) {
              <div class="header-thumbnail">
                <img [src]="course.thumbnail" [alt]="course.title">
              </div>
            }
          </div>
          
          <div class="course-content">
            <h2>Nội dung khóa học</h2>
            
            @if (!canAccessLessons && course.status) {
              <div class="course-status-notice" [class]="course.status.toLowerCase()">
                @if (course.status === 'UPCOMING') {
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span>Khóa học chưa bắt đầu. Bạn có thể xem nội dung nhưng chưa thể truy cập bài học.</span>
                } @else if (course.status === 'COMPLETED') {
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span>Khóa học đã kết thúc.</span>
                }
              </div>
            }
            
            @if (course.modules && course.modules.length > 0) {
              <div class="modules-list">
                @for (module of course.modules; track module.id; let i = $index) {
                  <app-card>
                    <div class="module-item" (click)="toggleModule(module.id)">
                      <div class="module-header">
                        <span class="module-number">Chương {{ i + 1 }}</span>
                        <h3>{{ module.title }}</h3>
                        <svg 
                          class="expand-icon" 
                          [class.expanded]="expandedModules.has(module.id)"
                          xmlns="http://www.w3.org/2000/svg" 
                          fill="none" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                        >
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                      </div>
                      
                      @if (module.description) {
                        <p class="module-description">{{ module.description }}</p>
                      }
                    </div>
                    
                    @if (expandedModules.has(module.id) && module.lessons) {
                      <div class="lessons-list">
                        @for (lesson of module.lessons; track lesson.id) {
                          <a 
                            [routerLink]="canAccessLessons ? ['/lessons', lesson.id] : null"
                            class="lesson-item"
                            [class.locked]="!canAccessLessons"
                          >
                            <div class="lesson-icon">
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                              </svg>
                            </div>
                            <div class="lesson-info">
                              <span class="lesson-title">{{ lesson.title }}</span>
                              @if (lesson.resources && lesson.resources.length > 0) {
                                <span class="lesson-meta">{{ lesson.resources.length }} tài liệu</span>
                              }
                            </div>
                            @if (!canAccessLessons) {
                              <svg class="lock-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                              </svg>
                            }
                          </a>
                        }
                      </div>
                    }
                  </app-card>
                }
              </div>
            } @else {
              <p class="no-content">Khóa học chưa có nội dung.</p>
            }
          </div>
        </div>
      }
    </app-main-layout>
  `,
  styles: [`
    .course-detail {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .course-header {
      display: grid;
      grid-template-columns: 1fr 400px;
      gap: 40px;
      margin-bottom: 40px;
      padding: 40px;
      background: linear-gradient(135deg, #1a1a2e, #0f3460);
      border-radius: 20px;
      color: #fff;
    }
    
    @media (max-width: 900px) {
      .course-header {
        grid-template-columns: 1fr;
      }
      
      .header-thumbnail {
        order: -1;
      }
    }
    
    .subject-badge {
      display: inline-block;
      padding: 6px 14px;
      background: rgba(255,255,255,0.2);
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 16px;
    }
    
    .course-header h1 {
      font-size: 2rem;
      margin-bottom: 16px;
      line-height: 1.3;
    }
    
    .description {
      font-size: 1rem;
      opacity: 0.9;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    
    .meta {
      display: flex;
      gap: 24px;
      margin-bottom: 32px;
      opacity: 0.9;
    }
    
    .meta span {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .meta svg {
      width: 20px;
      height: 20px;
    }
    
    .header-thumbnail {
      border-radius: 16px;
      overflow: hidden;
    }
    
    .header-thumbnail img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .btn {
      padding: 14px 32px;
      border: none;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    
    .btn-primary {
      background: #fff;
      color: #1a1a2e;
    }
    
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
    
    .enrolled-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      background: rgba(46, 204, 113, 0.2);
      color: #2ecc71;
      border-radius: 12px;
      font-weight: 600;
    }
    
    .enrolled-badge svg {
      width: 20px;
      height: 20px;
    }
    
    .course-content h2 {
      font-size: 1.5rem;
      color: #1a1a2e;
      margin-bottom: 24px;
    }
    
    .modules-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .module-item {
      cursor: pointer;
    }
    
    .module-header {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .module-number {
      font-size: 0.85rem;
      color: #0f3460;
      font-weight: 600;
      text-transform: uppercase;
    }
    
    .module-header h3 {
      flex: 1;
      font-size: 1.1rem;
      color: #1a1a2e;
      margin: 0;
    }
    
    .expand-icon {
      width: 20px;
      height: 20px;
      color: #666;
      transition: transform 0.3s ease;
    }
    
    .expand-icon.expanded {
      transform: rotate(180deg);
    }
    
    .module-description {
      margin-top: 8px;
      color: #666;
      font-size: 0.95rem;
    }
    
    .lessons-list {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
    }
    
    .lesson-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px;
      border-radius: 10px;
      text-decoration: none;
      color: inherit;
      transition: background 0.2s ease;
    }
    
    .lesson-item:hover:not(.locked) {
      background: #f5f7fa;
    }
    
    .lesson-item.locked {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .lesson-icon {
      width: 40px;
      height: 40px;
      background: #e3f2fd;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #1565c0;
    }
    
    .lesson-icon svg {
      width: 20px;
      height: 20px;
    }
    
    .lesson-info {
      flex: 1;
    }
    
    .lesson-title {
      display: block;
      font-weight: 500;
      color: #1a1a2e;
    }
    
    .lesson-meta {
      font-size: 0.85rem;
      color: #888;
    }
    
    .lock-icon {
      width: 20px;
      height: 20px;
      color: #999;
    }
    
    .lesson-item.locked {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .course-status-notice {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      border-radius: 12px;
      margin-bottom: 24px;
    }
    
    .course-status-notice svg {
      width: 24px;
      height: 24px;
      flex-shrink: 0;
    }
    
    .course-status-notice.upcoming {
      background: #fff3cd;
      color: #856404;
    }
    
    .course-status-notice.completed {
      background: #e2e3e5;
      color: #383d41;
    }
    
    .no-content {
      text-align: center;
      color: #666;
      padding: 40px;
    }
  `]
})
export class CourseDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private courseService = inject(CourseService);
  
  course: Course | null = null;
  isLoading = true;
  expandedModules = new Set<number>();

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadCourse(id);
  }

  private loadCourse(id: number): void {
    this.courseService.getCourseDetail(id).subscribe({
      next: (course) => {
        this.course = course;
        this.isLoading = false;
        // Mở rộng tất cả các module mặc định
        if (course.modules) {
          course.modules.forEach(m => this.expandedModules.add(m.id));
        }
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  toggleModule(moduleId: number): void {
    if (this.expandedModules.has(moduleId)) {
      this.expandedModules.delete(moduleId);
    } else {
      this.expandedModules.add(moduleId);
    }
  }

  get canAccessLessons(): boolean {
    return this.course?.status === 'ONGOING';
  }
}


