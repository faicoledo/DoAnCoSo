import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { TeacherService } from '../../../core/services/teacher.service';

interface Course {
  id: number;
  title: string;
  description: string;
  total_students: number;
  status: string;
  status_display: string;
}

@Component({
  selector: 'app-student-list',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <h1>Quản lý học viên</h1>
          <p>Chọn khóa học để xem danh sách học viên</p>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && courses.length === 0"
          title="Chưa có khóa học"
          message="Bạn chưa có khóa học nào."
        ></app-empty-state>

        <div class="courses-grid" *ngIf="!isLoading && courses.length > 0">
          @for (course of courses; track course.id) {
            <a [routerLink]="['/teacher/students/course', course.id]" class="course-card">
              <div class="course-info">
                <h3>{{ course.title }}</h3>
                <p class="description">{{ course.description || 'Không có mô tả' }}</p>
              </div>
              <div class="course-meta">
                <div class="student-count">
                  <span class="count">{{ course.total_students }}</span>
                  <span class="label">học viên</span>
                </div>
                <span class="status" [class]="course.status.toLowerCase()">{{ course.status_display }}</span>
              </div>
            </a>
          }
        </div>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .page-container { padding: 24px; max-width: 1200px; margin: 0 auto; }
    .page-header { margin-bottom: 24px; }
    .page-header h1 { font-size: 1.8rem; color: #1a1a2e; margin-bottom: 8px; }
    .page-header p { color: #666; }
    
    .courses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
    
    .course-card {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 20px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      text-decoration: none;
      color: inherit;
      transition: all 0.3s;
      border: 2px solid transparent;
    }
    .course-card:hover { border-color: #0f3460; transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
    
    .course-info h3 { font-size: 1.1rem; color: #1a1a2e; margin-bottom: 8px; }
    .description { font-size: 0.9rem; color: #666; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    
    .course-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid #f0f0f0; }
    
    .student-count { display: flex; flex-direction: column; align-items: center; }
    .student-count .count { font-size: 1.5rem; font-weight: 700; color: #0f3460; }
    .student-count .label { font-size: 0.8rem; color: #888; }
    
    .status { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    .status.ongoing { background: #e8f5e9; color: #2e7d32; }
    .status.upcoming { background: #fff3e0; color: #ef6c00; }
    .status.completed { background: #e3f2fd; color: #1565c0; }
  `]
})
export class StudentListComponent implements OnInit {
  teacherService = inject(TeacherService);
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
}

