import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { CourseService } from '../../../core/services/course.service';
import { Course, Subject } from '../../../core/models';

@Component({
  selector: 'app-course-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="course-list-page">
        <div class="page-header">
          <h1>Khám phá khóa học</h1>
          <p>Tìm kiếm và đăng ký các khóa học phù hợp với bạn</p>
        </div>
        
        <div class="filters">
          <div class="search-box">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input 
              type="text" 
              [(ngModel)]="searchQuery"
              (ngModelChange)="onSearch()"
              placeholder="Tìm kiếm khóa học..."
            >
          </div>
          
          <select [(ngModel)]="selectedSubject" (ngModelChange)="onFilterChange()">
            <option [ngValue]="null">Tất cả môn học</option>
            @for (subject of subjects; track subject.id) {
              <option [ngValue]="subject.id">{{ subject.name }}</option>
            }
          </select>
        </div>
        
        @if (isLoading) {
          <app-loading message="Đang tải khóa học..."></app-loading>
        } @else if (courses.length === 0) {
          <app-empty-state 
            title="Không tìm thấy khóa học"
            description="Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm"
          ></app-empty-state>
        } @else {
          <div class="courses-grid">
            @for (course of courses; track course.id) {
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
                    <p class="course-description">{{ course.description | slice:0:100 }}...</p>
                    <div class="course-meta">
                      <span class="teacher">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                        {{ course.teacher?.full_name }}
                      </span>
                    </div>
                  </div>
                </a>
              </app-card>
            }
          </div>
          
          @if (hasMore) {
            <div class="load-more">
              <button class="btn btn-outline" (click)="loadMore()" [disabled]="isLoadingMore">
                @if (isLoadingMore) {
                  Đang tải...
                } @else {
                  Xem thêm
                }
              </button>
            </div>
          }
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .course-list-page {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .page-header {
      margin-bottom: 32px;
    }
    
    .page-header h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .page-header p {
      color: #666;
    }
    
    .filters {
      display: flex;
      gap: 16px;
      margin-bottom: 32px;
      flex-wrap: wrap;
    }
    
    .search-box {
      flex: 1;
      min-width: 250px;
      position: relative;
    }
    
    .search-box svg {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      width: 20px;
      height: 20px;
      color: #999;
    }
    
    .search-box input {
      width: 100%;
      padding: 14px 16px 14px 48px;
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      font-size: 1rem;
      transition: all 0.3s ease;
      box-sizing: border-box;
    }
    
    .search-box input:focus {
      outline: none;
      border-color: #0f3460;
    }
    
    .filters select {
      padding: 14px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      font-size: 1rem;
      background: #fff;
      min-width: 180px;
      cursor: pointer;
    }
    
    .filters select:focus {
      outline: none;
      border-color: #0f3460;
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
    
    .load-more {
      text-align: center;
      margin-top: 40px;
    }
    
    .btn {
      padding: 12px 32px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #0f3460;
      color: #0f3460;
    }
    
    .btn-outline:hover:not(:disabled) {
      background: #0f3460;
      color: #fff;
    }
    
    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  `]
})
export class CourseListComponent implements OnInit {
  private courseService = inject(CourseService);
  
  courses: Course[] = [];
  subjects: Subject[] = [];
  searchQuery = '';
  selectedSubject: number | null = null;
  isLoading = true;
  isLoadingMore = false;
  hasMore = false;
  currentPage = 1;

  ngOnInit(): void {
    this.loadSubjects();
    this.loadCourses();
  }

  private loadSubjects(): void {
    this.courseService.getSubjects().subscribe({
      next: (subjects) => this.subjects = subjects,
      error: () => {}
    });
  }

  loadCourses(): void {
    this.isLoading = true;
    this.currentPage = 1;
    
    this.courseService.getCourses({
      search: this.searchQuery || undefined,
      subject: this.selectedSubject || undefined,
      page: this.currentPage
    }).subscribe({
      next: (res) => {
        this.courses = res.results;
        this.hasMore = !!res.next;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  loadMore(): void {
    this.isLoadingMore = true;
    this.currentPage++;
    
    this.courseService.getCourses({
      search: this.searchQuery || undefined,
      subject: this.selectedSubject || undefined,
      page: this.currentPage
    }).subscribe({
      next: (res) => {
        this.courses = [...this.courses, ...res.results];
        this.hasMore = !!res.next;
        this.isLoadingMore = false;
      },
      error: () => {
        this.isLoadingMore = false;
      }
    });
  }

  onSearch(): void {
    this.loadCourses();
  }

  onFilterChange(): void {
    this.loadCourses();
  }
}


