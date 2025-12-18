import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { LoadingComponent, EmptyStateComponent } from '../../../shared/components';
import { ApiService } from '../../../core/services/api.service';

interface Student {
  id: number;
  full_name: string;
  email: string;
  avatar: string | null;
  joined_at: string;
}

@Component({
  selector: 'app-course-students',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="page-container">
        <div class="page-header">
          <a routerLink="/teacher/students" class="back-link">← Quay lại</a>
          <h1>{{ courseTitle }}</h1>
          <p>Danh sách học viên đã đăng ký khóa học</p>
        </div>

        <app-loading *ngIf="isLoading"></app-loading>

        <app-empty-state
          *ngIf="!isLoading && students.length === 0"
          title="Chưa có học viên"
          message="Chưa có học viên nào đăng ký khóa học này."
        ></app-empty-state>

        <div class="students-grid" *ngIf="!isLoading && students.length > 0">
          @for (student of students; track student.id) {
            <a [routerLink]="['/teacher/students/course', courseId, 'student', student.id]" class="student-card">
              <div class="student-avatar">
                @if (student.avatar) {
                  <img [src]="student.avatar" [alt]="student.full_name">
                } @else {
                  <div class="avatar-placeholder">{{ student.full_name.charAt(0) }}</div>
                }
              </div>
              <div class="student-info">
                <h3>{{ student.full_name }}</h3>
                <p class="email">{{ student.email }}</p>
                <p class="joined">Đăng ký: {{ student.joined_at | date:'dd/MM/yyyy' }}</p>
              </div>
              <div class="arrow">→</div>
            </a>
          }
        </div>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .page-container { padding: 24px; max-width: 1200px; margin: 0 auto; }
    .page-header { margin-bottom: 24px; }
    .back-link { color: #0f3460; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 12px; }
    .back-link:hover { text-decoration: underline; }
    .page-header h1 { font-size: 1.8rem; color: #1a1a2e; margin-bottom: 8px; }
    .page-header p { color: #666; }
    
    .students-grid { display: flex; flex-direction: column; gap: 12px; }
    
    .student-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      text-decoration: none;
      color: inherit;
      transition: all 0.3s;
      border: 2px solid transparent;
    }
    .student-card:hover { border-color: #0f3460; transform: translateX(4px); }
    
    .student-avatar img, .avatar-placeholder {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      object-fit: cover;
    }
    .avatar-placeholder {
      background: linear-gradient(135deg, #0f3460, #1a1a2e);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      font-weight: 600;
    }
    
    .student-info { flex: 1; }
    .student-info h3 { font-size: 1rem; color: #1a1a2e; margin-bottom: 4px; }
    .student-info .email { font-size: 0.85rem; color: #666; margin-bottom: 2px; }
    .student-info .joined { font-size: 0.8rem; color: #888; }
    
    .arrow { font-size: 1.2rem; color: #ccc; transition: color 0.3s; }
    .student-card:hover .arrow { color: #0f3460; }
  `]
})
export class CourseStudentsComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private api = inject(ApiService);
  
  courseId: number = 0;
  courseTitle: string = 'Khóa học';
  students: Student[] = [];
  isLoading = true;

  ngOnInit(): void {
    this.courseId = Number(this.route.snapshot.paramMap.get('courseId'));
    this.loadStudents();
  }

  private loadStudents(): void {
    this.api.get<any>(`/teacher/courses/${this.courseId}/students/`).subscribe({
      next: (res) => {
        this.courseTitle = res.course_title || 'Khóa học';
        this.students = res.students || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}

