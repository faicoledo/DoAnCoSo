import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { CourseService } from '../../../core/services/course.service';
import { Lesson, Resource, Assignment } from '../../../core/models';

@Component({
  selector: 'app-lesson-view',
  standalone: true,
  imports: [CommonModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      @if (isLoading) {
        <app-loading [overlay]="true" message="Đang tải bài học..."></app-loading>
      } @else if (lesson) {
        <div class="lesson-view">
          <div class="lesson-header">
            <a routerLink="/courses" class="back-link">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
              Quay lại
            </a>
            <h1>{{ lesson.title }}</h1>
            @if (lesson.description) {
              <p class="description">{{ lesson.description }}</p>
            }
          </div>
          
          <div class="lesson-content">
            <div class="main-content">
              @if (selectedResource) {
                <app-card>
                  <div class="resource-viewer">
                    @if (selectedResource.type === 'VIDEO') {
                      <div class="video-container">
                        @if (selectedResource.video_url && isYoutubeUrl(selectedResource.video_url)) {
                          <iframe 
                            [src]="getYoutubeEmbedUrl(selectedResource.video_url)"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen
                          ></iframe>
                        } @else if (selectedResource.video_url) {
                          <video controls [src]="selectedResource.video_url">
                            Trình duyệt không hỗ trợ video.
                          </video>
                        }
                      </div>
                    } @else if (selectedResource.type === 'DOCUMENT') {
                      <div class="document-viewer">
                        @if (isPdf(selectedResource.document_url)) {
                          <iframe [src]="getSafeUrl(selectedResource.document_url)" class="pdf-viewer"></iframe>
                        } @else {
                          <div class="download-prompt">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                            </svg>
                            <h3>{{ selectedResource.title }}</h3>
                            <p>Tài liệu này không thể xem trực tiếp</p>
                            <a [href]="selectedResource.document_url" download class="btn btn-primary">
                              Tải xuống
                            </a>
                          </div>
                        }
                      </div>
                    }
                    
                    <div class="resource-info">
                      <h3>{{ selectedResource.title }}</h3>
                      @if (selectedResource.duration_display) {
                        <span class="duration">{{ selectedResource.duration_display }}</span>
                      }
                      @if (selectedResource.file_size_display) {
                        <span class="file-size">{{ selectedResource.file_size_display }}</span>
                      }
                    </div>
                  </div>
                </app-card>
              }
              
              @if (lesson.assignments && lesson.assignments.length > 0) {
                <app-card title="Bài tập" class="assignments-section">
                  <div class="assignments-list">
                    @for (assignment of lesson.assignments; track assignment.id) {
                      <a 
                        [routerLink]="getAssignmentLink(assignment)"
                        class="assignment-item"
                        [class.available]="assignment.is_available"
                      >
                        <div class="assignment-icon" [class.quiz]="assignment.type === 'QUIZ'">
                          @if (assignment.type === 'QUIZ') {
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                            </svg>
                          } @else {
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                            </svg>
                          }
                        </div>
                        <div class="assignment-info">
                          <span class="assignment-title">{{ assignment.title }}</span>
                          <div class="assignment-meta">
                            <span class="type">{{ assignment.type === 'QUIZ' ? 'Trắc nghiệm' : 'Nộp file' }}</span>
                            <span class="deadline">Hạn: {{ assignment.end_at | date:'dd/MM/yyyy HH:mm' }}</span>
                          </div>
                        </div>
                        @if (assignment.is_available) {
                          <span class="status-badge available">Đang mở</span>
                        } @else {
                          <span class="status-badge closed">Đã đóng</span>
                        }
                      </a>
                    }
                  </div>
                </app-card>
              }
            </div>
            
            <div class="sidebar-content">
              @if (lesson.resources && lesson.resources.length > 0) {
                <app-card title="Tài liệu bài học">
                  <div class="resources-list">
                    @for (resource of lesson.resources; track resource.id) {
                      <button 
                        class="resource-item"
                        [class.active]="selectedResource?.id === resource.id"
                        (click)="selectResource(resource)"
                      >
                        <div class="resource-icon">
                          @if (resource.type === 'VIDEO') {
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                          } @else {
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                            </svg>
                          }
                        </div>
                        <div class="resource-text">
                          <span class="resource-title">{{ resource.title }}</span>
                          @if (resource.duration_display) {
                            <span class="resource-meta">{{ resource.duration_display }}</span>
                          }
                        </div>
                      </button>
                    }
                  </div>
                </app-card>
              }
            </div>
          </div>
        </div>
      }
    </app-main-layout>
  `,
  styles: [`
    .lesson-view {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    .lesson-header {
      margin-bottom: 32px;
    }
    
    .back-link {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #666;
      text-decoration: none;
      font-size: 0.95rem;
      margin-bottom: 16px;
    }
    
    .back-link:hover {
      color: #0f3460;
    }
    
    .back-link svg {
      width: 18px;
      height: 18px;
    }
    
    .lesson-header h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .description {
      color: #666;
      font-size: 1rem;
      line-height: 1.6;
    }
    
    .lesson-content {
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 24px;
    }
    
    @media (max-width: 1024px) {
      .lesson-content {
        grid-template-columns: 1fr;
      }
      
      .sidebar-content {
        order: -1;
      }
    }
    
    .main-content {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    .video-container {
      position: relative;
      padding-bottom: 56.25%;
      height: 0;
      background: #000;
      border-radius: 12px;
      overflow: hidden;
    }
    
    .video-container iframe,
    .video-container video {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .document-viewer {
      min-height: 500px;
    }
    
    .pdf-viewer {
      width: 100%;
      height: 600px;
      border: none;
      border-radius: 8px;
    }
    
    .download-prompt {
      text-align: center;
      padding: 60px 20px;
      background: #f5f7fa;
      border-radius: 12px;
    }
    
    .download-prompt svg {
      width: 64px;
      height: 64px;
      color: #0f3460;
      margin-bottom: 16px;
    }
    
    .download-prompt h3 {
      color: #1a1a2e;
      margin-bottom: 8px;
    }
    
    .download-prompt p {
      color: #666;
      margin-bottom: 20px;
    }
    
    .resource-info {
      padding: 20px 0 0;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .resource-info h3 {
      flex: 1;
      font-size: 1.1rem;
      color: #1a1a2e;
      margin: 0;
    }
    
    .duration, .file-size {
      font-size: 0.9rem;
      color: #888;
    }
    
    .resources-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .resource-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border: none;
      background: transparent;
      border-radius: 10px;
      cursor: pointer;
      text-align: left;
      width: 100%;
      transition: background 0.2s ease;
    }
    
    .resource-item:hover {
      background: #f5f7fa;
    }
    
    .resource-item.active {
      background: #e3f2fd;
    }
    
    .resource-icon {
      width: 40px;
      height: 40px;
      background: #f0f0f0;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #666;
    }
    
    .resource-item.active .resource-icon {
      background: #1565c0;
      color: #fff;
    }
    
    .resource-icon svg {
      width: 20px;
      height: 20px;
    }
    
    .resource-text {
      flex: 1;
      min-width: 0;
    }
    
    .resource-title {
      display: block;
      font-weight: 500;
      color: #1a1a2e;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .resource-meta {
      font-size: 0.85rem;
      color: #888;
    }
    
    .assignments-section {
      margin-top: 8px;
    }
    
    .assignments-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .assignment-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 12px;
      text-decoration: none;
      color: inherit;
      transition: all 0.2s ease;
    }
    
    .assignment-item.available:hover {
      background: #e3f2fd;
      transform: translateX(4px);
    }
    
    .assignment-icon {
      width: 48px;
      height: 48px;
      background: #e0e0e0;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #666;
    }
    
    .assignment-icon.quiz {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    .assignment-icon svg {
      width: 24px;
      height: 24px;
    }
    
    .assignment-info {
      flex: 1;
    }
    
    .assignment-title {
      display: block;
      font-weight: 600;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    
    .assignment-meta {
      display: flex;
      gap: 16px;
      font-size: 0.85rem;
      color: #888;
    }
    
    .status-badge {
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    
    .status-badge.available {
      background: #d4edda;
      color: #155724;
    }
    
    .status-badge.closed {
      background: #f8d7da;
      color: #721c24;
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
  `]
})
export class LessonViewComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private courseService = inject(CourseService);
  private sanitizer = inject(DomSanitizer);
  
  lesson: Lesson | null = null;
  selectedResource: Resource | null = null;
  isLoading = true;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadLesson(id);
  }

  private loadLesson(id: number): void {
    this.courseService.getLessonDetail(id).subscribe({
      next: (lesson) => {
        this.lesson = lesson;
        if (lesson.resources && lesson.resources.length > 0) {
          this.selectedResource = lesson.resources[0];
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  selectResource(resource: Resource): void {
    this.selectedResource = resource;
  }

  getYoutubeEmbedUrl(url: string): SafeResourceUrl {
    const videoId = this.extractYoutubeId(url);
    return this.sanitizer.bypassSecurityTrustResourceUrl(
      `https://www.youtube.com/embed/${videoId}`
    );
  }

  private extractYoutubeId(url: string): string {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : '';
  }

  isYoutubeUrl(url: string): boolean {
    return url.includes('youtube.com') || url.includes('youtu.be');
  }

  getSafeUrl(url?: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url || '');
  }

  isPdf(url?: string): boolean {
    return url?.toLowerCase().endsWith('.pdf') || false;
  }

  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  getAssignmentLink(assignment: Assignment): string[] | null {
    if (assignment.type === 'QUIZ') {
      return ['/quizzes', String(assignment.id)];
    } else {
      return ['/quizzes', String(assignment.id), 'submit-file'];
    }
  }
}


