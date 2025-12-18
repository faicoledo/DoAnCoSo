import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { CourseService } from '../../../core/services/course.service';
import { ApiService } from '../../../core/services/api.service';
import { Course, Module, Lesson } from '../../../core/models';

@Component({
  selector: 'app-course-editor',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MainLayoutComponent, CardComponent, LoadingComponent],
  template: `
    <app-main-layout>
      @if (isLoading) {
        <app-loading [overlay]="true" message="Đang tải..."></app-loading>
      } @else if (course) {
        <div class="course-editor">
          <div class="page-header">
            <a routerLink="/teacher/courses" class="back-link">← Quay lại danh sách</a>
            <div class="header-row">
              <div>
                <h1>{{ course.title }}</h1>
                <p class="subject">{{ course.subject?.name }}</p>
              </div>
              <button class="btn btn-primary" (click)="openAddModule()">+ Thêm chương</button>
            </div>
          </div>
          
          <div class="content-tree">
            @for (module of course.modules; track module.id; let mi = $index) {
              <app-card>
                <div class="module-header">
                  <div class="module-info">
                    <div class="order-control">
                      <span class="module-number">Chương {{ mi + 1 }}</span>
                      <div class="order-buttons">
                        @if (mi > 0) {
                          <button class="btn-order" title="Di chuyển lên" (click)="moveModule(module, 'up', mi)">▲</button>
                        }
                        @if (mi < course!.modules!.length - 1) {
                          <button class="btn-order" title="Di chuyển xuống" (click)="moveModule(module, 'down', mi)">▼</button>
                        }
                      </div>
                    </div>
                    <h2>{{ module.title }}</h2>
                    @if (module.description) {
                      <p class="module-desc">{{ module.description }}</p>
                    }
                  </div>
                  <div class="module-actions">
                    <button class="btn-icon" title="Thêm bài học" (click)="openAddLesson(module)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    </button>
                    <button class="btn-icon" title="Sửa chương" (click)="openEditModule(module)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                    </button>
                    <button class="btn-icon danger" title="Xóa chương" (click)="deleteModule(module)">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </div>
                
                @if (module.lessons && module.lessons.length > 0) {
                  <div class="lessons-list">
                    @for (lesson of module.lessons; track lesson.id; let li = $index) {
                      <div class="lesson-item">
                        <div class="lesson-info">
                          <div class="order-control">
                            <span class="lesson-number">Bài {{ li + 1 }}</span>
                            <div class="order-buttons">
                              @if (li > 0) {
                                <button class="btn-order" title="Di chuyển lên" (click)="moveLesson(lesson, 'up', li, module)">▲</button>
                              }
                              @if (li < module.lessons!.length - 1) {
                                <button class="btn-order" title="Di chuyển xuống" (click)="moveLesson(lesson, 'down', li, module)">▼</button>
                              }
                            </div>
                          </div>
                          <h3>{{ lesson.title }}</h3>
                          
                          <!-- Resources -->
                          @if (lesson.resources && lesson.resources.length > 0) {
                            <div class="resources">
                              @for (resource of lesson.resources; track resource.id) {
                                <div class="resource-item">
                                  <span class="resource-tag" [class]="resource.type.toLowerCase()">
                                    {{ getResourceTypeLabel(resource.type) }}: {{ resource.title }}
                                  </span>
                                  <div class="resource-actions">
                                    <button class="btn-xs" title="Sửa" (click)="openEditResource(resource, lesson)">✏️</button>
                                    <button class="btn-xs danger" title="Xóa" (click)="deleteResource(resource)">🗑️</button>
                                  </div>
                                </div>
                              }
                            </div>
                          }
                          
                          <!-- Assignments -->
                          @if (lesson.assignments && lesson.assignments.length > 0) {
                            <div class="assignments">
                              @for (assignment of lesson.assignments; track assignment.id) {
                                <div class="assignment-item">
                                  <a [routerLink]="['/teacher/assignments', assignment.id, 'submissions']" class="assignment-link">
                                    <span class="assignment-type" [class.quiz]="assignment.type === 'QUIZ'">
                                      {{ assignment.type === 'QUIZ' ? 'Quiz' : 'Bài tập' }}
                                    </span>
                                    {{ assignment.title }}
                                  </a>
                                  <div class="assignment-actions">
                                    @if (assignment.type === 'QUIZ') {
                                      <a [routerLink]="['/teacher/assignments', assignment.id, 'questions']" class="btn-xs" title="Quản lý câu hỏi">📝</a>
                                    }
                                    <button class="btn-xs" title="Sửa" (click)="openEditAssignment(assignment, lesson)">✏️</button>
                                    <button class="btn-xs danger" title="Xóa" (click)="deleteAssignment(assignment)">🗑️</button>
                                  </div>
                                </div>
                              }
                            </div>
                          }
                        </div>
                        <div class="lesson-actions">
                          <button class="btn-sm" (click)="openAddResource(lesson)">+ Tài liệu</button>
                          <button class="btn-sm" (click)="openAddAssignment(lesson)">+ Bài tập</button>
                          <button class="btn-icon" title="Sửa" (click)="openEditLesson(lesson, module)">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                          </button>
                          <button class="btn-icon danger" title="Xóa" (click)="deleteLesson(lesson, module)">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                          </button>
                        </div>
                      </div>
                    }
                  </div>
                } @else {
                  <p class="no-content">Chưa có bài học - <a href="javascript:void(0)" (click)="openAddLesson(module)">Thêm bài học</a></p>
                }
              </app-card>
            }
            
            @if (!course.modules || course.modules.length === 0) {
              <app-card>
                <div class="empty-state">
                  <p>Khóa học chưa có nội dung.</p>
                  <button class="btn btn-primary" (click)="openAddModule()">Thêm chương đầu tiên</button>
                </div>
              </app-card>
            }
          </div>
        </div>
      }
      
      <!-- Modal -->
      @if (showModal) {
        <div class="modal-overlay" (click)="closeModal()">
          <div class="modal" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h3>{{ modalTitle }}</h3>
              <button class="close-btn" (click)="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
              @switch (modalType) {
                @case ('module') {
                  <div class="form-group">
                    <label>Tên chương *</label>
                    <input type="text" [(ngModel)]="moduleForm.title" placeholder="Nhập tên chương">
                  </div>
                  <div class="form-group">
                    <label>Mô tả</label>
                    <textarea [(ngModel)]="moduleForm.description" rows="3" placeholder="Mô tả ngắn về chương"></textarea>
                  </div>
                }
                @case ('lesson') {
                  <div class="form-group">
                    <label>Tên bài học *</label>
                    <input type="text" [(ngModel)]="lessonForm.title" placeholder="Nhập tên bài học">
                  </div>
                  <div class="form-group">
                    <label>Mô tả</label>
                    <textarea [(ngModel)]="lessonForm.description" rows="3" placeholder="Mô tả ngắn về bài học"></textarea>
                  </div>
                }
                @case ('resource') {
                  <div class="form-group">
                    <label>Loại tài liệu *</label>
                    <select [(ngModel)]="resourceForm.type">
                      <option value="DOCUMENT">Tài liệu (PDF, Word...)</option>
                      <option value="VIDEO">Video</option>
                      <option value="LINK">Liên kết</option>
                      <option value="TEXT">Văn bản</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Tiêu đề *</label>
                    <input type="text" [(ngModel)]="resourceForm.title" placeholder="Tiêu đề tài liệu">
                  </div>
                  @if (resourceForm.type === 'DOCUMENT') {
                    <div class="form-group">
                      <label>File tài liệu</label>
                      <input type="file" (change)="onFileSelect($event, 'document')">
                    </div>
                  }
                  @if (resourceForm.type === 'VIDEO') {
                    <div class="form-group">
                      <label>Nguồn video</label>
                      <select [(ngModel)]="resourceForm.video_source">
                        <option value="FILE">Upload file</option>
                        <option value="URL">URL (YouTube...)</option>
                      </select>
                    </div>
                    @if (resourceForm.video_source === 'FILE') {
                      <div class="form-group">
                        <label>File video</label>
                        <input type="file" accept="video/*" (change)="onFileSelect($event, 'video')">
                      </div>
                    } @else {
                      <div class="form-group">
                        <label>URL video</label>
                        <input type="text" [(ngModel)]="resourceForm.video_url" placeholder="https://youtube.com/...">
                      </div>
                    }
                  }
                  @if (resourceForm.type === 'LINK') {
                    <div class="form-group">
                      <label>URL liên kết *</label>
                      <input type="text" [(ngModel)]="resourceForm.link_url" placeholder="https://...">
                    </div>
                  }
                  @if (resourceForm.type === 'TEXT') {
                    <div class="form-group">
                      <label>Nội dung văn bản</label>
                      <textarea [(ngModel)]="resourceForm.text_content" rows="6" placeholder="Nhập nội dung..."></textarea>
                    </div>
                  }
                }
                @case ('assignment') {
                  <div class="form-group">
                    <label>Loại bài tập *</label>
                    <select [(ngModel)]="assignmentForm.type">
                      <option value="QUIZ">Trắc nghiệm (Quiz)</option>
                      <option value="SUBMISSION">Nộp file</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Tiêu đề *</label>
                    <input type="text" [(ngModel)]="assignmentForm.title" placeholder="Tiêu đề bài tập">
                  </div>
                  <div class="form-group">
                    <label>Mô tả</label>
                    <textarea [(ngModel)]="assignmentForm.description" rows="3" placeholder="Hướng dẫn làm bài"></textarea>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Thời gian (phút)</label>
                      <input type="number" [(ngModel)]="assignmentForm.time_limit" placeholder="Không giới hạn">
                    </div>
                    <div class="form-group">
                      <label>Số lần làm</label>
                      <input type="number" [(ngModel)]="assignmentForm.attempts_allowed" placeholder="Không giới hạn">
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Hạn nộp</label>
                      <input type="datetime-local" [(ngModel)]="assignmentForm.due_date">
                    </div>
                    <div class="form-group">
                      <label>Điểm tối đa</label>
                      <input type="number" [(ngModel)]="assignmentForm.max_score" value="100">
                    </div>
                  </div>
                }
              }
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline" (click)="closeModal()">Hủy</button>
              <button class="btn btn-primary" (click)="saveModal()" [disabled]="isSaving">
                {{ isSaving ? 'Đang lưu...' : 'Lưu' }}
              </button>
            </div>
          </div>
        </div>
      }
    </app-main-layout>
  `,
  styles: [`
    .course-editor { max-width: 1000px; margin: 0 auto; }
    .page-header { margin-bottom: 32px; }
    .back-link { color: #666; text-decoration: none; font-size: 0.9rem; display: inline-block; margin-bottom: 8px; }
    .header-row { display: flex; justify-content: space-between; align-items: flex-start; }
    .page-header h1 { font-size: 1.75rem; color: #1a1a2e; margin-bottom: 4px; }
    .subject { color: #0f3460; font-weight: 500; }
    .content-tree { display: flex; flex-direction: column; gap: 20px; }
    
    .module-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
    .module-number { font-size: 0.8rem; color: #0f3460; font-weight: 600; text-transform: uppercase; }
    .module-header h2 { font-size: 1.15rem; color: #1a1a2e; margin-top: 4px; }
    .module-desc { font-size: 0.9rem; color: #666; margin-top: 4px; }
    .module-actions { display: flex; gap: 8px; }
    
    .btn-icon { width: 36px; height: 36px; border: none; background: #f5f7fa; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
    .btn-icon svg { width: 18px; height: 18px; color: #666; }
    .btn-icon:hover { background: #e3f2fd; }
    .btn-icon:hover svg { color: #0f3460; }
    .btn-icon.danger:hover { background: #fdeaea; }
    .btn-icon.danger:hover svg { color: #e74c3c; }
    
    .lessons-list { border-top: 1px solid #f0f0f0; }
    .lesson-item { padding: 16px 0; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: flex-start; }
    .lesson-item:last-child { border-bottom: none; }
    .lesson-number { font-size: 0.75rem; color: #888; text-transform: uppercase; }
    .lesson-info h3 { font-size: 1rem; color: #1a1a2e; margin: 4px 0 12px; }
    .lesson-actions { display: flex; gap: 8px; align-items: center; }
    
    .btn-sm { padding: 6px 12px; font-size: 0.8rem; background: #f5f7fa; border: none; border-radius: 6px; cursor: pointer; color: #0f3460; font-weight: 500; }
    .btn-sm:hover { background: #e3f2fd; }
    
    .resources { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .resource-tag { padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; }
    .resource-tag.document { background: #e3f2fd; color: #1565c0; }
    .resource-tag.video { background: #fce4ec; color: #c2185b; }
    .resource-tag.link { background: #e8f5e9; color: #2e7d32; }
    .resource-tag.text { background: #fff3e0; color: #ef6c00; }
    
    .assignments { display: flex; flex-wrap: wrap; gap: 8px; }
    .assignment-link { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; background: #f5f7fa; border-radius: 8px; text-decoration: none; color: #333; font-size: 0.9rem; transition: all 0.2s ease; }
    .assignment-link:hover { background: #e3f2fd; }
    .assignment-type { padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: #e0e0e0; color: #666; }
    .assignment-type.quiz { background: #e8f5e9; color: #2e7d32; }
    
    .resource-item, .assignment-item { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .resource-actions, .assignment-actions { display: flex; gap: 4px; }
    .btn-xs { padding: 2px 6px; font-size: 0.7rem; background: transparent; border: none; cursor: pointer; border-radius: 4px; }
    .btn-xs:hover { background: #f0f0f0; }
    .btn-xs.danger:hover { background: #fdeaea; }
    
    .order-control { display: flex; align-items: center; gap: 8px; }
    .order-buttons { display: flex; flex-direction: column; gap: 2px; }
    .btn-order { width: 20px; height: 16px; font-size: 0.6rem; background: #f5f7fa; border: 1px solid #e0e0e0; border-radius: 3px; cursor: pointer; line-height: 1; }
    .btn-order:hover { background: #e3f2fd; border-color: #0f3460; }
    
    .no-content { color: #888; font-style: italic; padding: 16px 0; }
    .no-content a { color: #0f3460; }
    .empty-state { text-align: center; padding: 40px 20px; }
    .empty-state p { color: #666; margin-bottom: 20px; }
    
    .btn { display: inline-block; padding: 12px 24px; border-radius: 10px; font-weight: 600; text-decoration: none; transition: all 0.3s ease; border: none; cursor: pointer; }
    .btn-primary { background: linear-gradient(135deg, #0f3460, #1a1a2e); color: #fff; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(15, 52, 96, 0.3); }
    .btn-outline { background: transparent; border: 2px solid #e0e0e0; color: #666; }
    .btn-outline:hover { border-color: #0f3460; color: #0f3460; }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }
    
    /* Modal */
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
    .modal { background: #fff; border-radius: 16px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
    .modal-header h3 { font-size: 1.2rem; color: #1a1a2e; }
    .close-btn { width: 32px; height: 32px; border: none; background: #f5f7fa; border-radius: 8px; font-size: 1.5rem; cursor: pointer; line-height: 1; }
    .modal-body { padding: 24px; }
    .modal-footer { padding: 16px 24px; border-top: 1px solid #f0f0f0; display: flex; justify-content: flex-end; gap: 12px; }
    
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 500; color: #333; font-size: 0.9rem; }
    .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; box-sizing: border-box; }
    .form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #0f3460; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  `]
})
export class CourseEditorComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private courseService = inject(CourseService);
  private api = inject(ApiService);
  
  course: Course | null = null;
  isLoading = true;
  
  // Modal state
  showModal = false;
  modalType: 'module' | 'lesson' | 'resource' | 'assignment' = 'module';
  modalTitle = '';
  isSaving = false;
  editingId: number | null = null;
  currentModule: Module | null = null;
  currentLesson: any = null;
  
  // Forms
  moduleForm = { title: '', description: '' };
  lessonForm = { title: '', description: '' };
  resourceForm = { type: 'DOCUMENT', title: '', video_source: 'FILE', video_url: '', link_url: '', text_content: '' };
  assignmentForm = { type: 'QUIZ', title: '', description: '', time_limit: null as number | null, attempts_allowed: null as number | null, due_date: '', max_score: 100 };
  
  selectedFile: File | null = null;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadCourse(id);
  }

  private loadCourse(id: number): void {
    this.courseService.getCourseDetail(id).subscribe({
      next: (course) => {
        this.course = course;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  getResourceTypeLabel(type: string): string {
    const map: Record<string, string> = { 'DOCUMENT': 'Tài liệu', 'VIDEO': 'Video', 'LINK': 'Liên kết', 'TEXT': 'Văn bản' };
    return map[type] || type;
  }

  // Module actions
  openAddModule(): void {
    this.modalType = 'module';
    this.modalTitle = 'Thêm chương mới';
    this.editingId = null;
    this.moduleForm = { title: '', description: '' };
    this.showModal = true;
  }

  openEditModule(module: Module): void {
    this.modalType = 'module';
    this.modalTitle = 'Sửa chương';
    this.editingId = module.id;
    this.moduleForm = { title: module.title, description: module.description || '' };
    this.showModal = true;
  }

  deleteModule(module: Module): void {
    if (confirm(`Xóa chương "${module.title}"? Tất cả bài học trong chương cũng sẽ bị xóa.`)) {
      this.api.delete(`/teacher/modules/${module.id}/`).subscribe({
        next: () => this.loadCourse(this.course!.id),
        error: () => alert('Không thể xóa chương')
      });
    }
  }

  // Lesson actions
  openAddLesson(module: Module): void {
    this.modalType = 'lesson';
    this.modalTitle = 'Thêm bài học';
    this.currentModule = module;
    this.editingId = null;
    this.lessonForm = { title: '', description: '' };
    this.showModal = true;
  }

  openEditLesson(lesson: Lesson, module: Module): void {
    this.modalType = 'lesson';
    this.modalTitle = 'Sửa bài học';
    this.currentModule = module;
    this.editingId = lesson.id;
    this.lessonForm = { title: lesson.title, description: lesson.description || '' };
    this.showModal = true;
  }

  deleteLesson(lesson: Lesson, module: Module): void {
    if (confirm(`Xóa bài học "${lesson.title}"?`)) {
      this.api.delete(`/teacher/lessons/${lesson.id}/`).subscribe({
        next: () => this.loadCourse(this.course!.id),
        error: () => alert('Không thể xóa bài học')
      });
    }
  }

  // Resource actions
  openAddResource(lesson: any): void {
    this.modalType = 'resource';
    this.modalTitle = 'Thêm tài liệu';
    this.currentLesson = lesson;
    this.editingId = null;
    this.resourceForm = { type: 'DOCUMENT', title: '', video_source: 'FILE', video_url: '', link_url: '', text_content: '' };
    this.selectedFile = null;
    this.showModal = true;
  }

  // Assignment actions
  openAddAssignment(lesson: any): void {
    this.modalType = 'assignment';
    this.modalTitle = 'Thêm bài tập';
    this.currentLesson = lesson;
    this.editingId = null;
    this.assignmentForm = { type: 'QUIZ', title: '', description: '', time_limit: null, attempts_allowed: null, due_date: '', max_score: 100 };
    this.showModal = true;
  }

  onFileSelect(event: Event, type: string): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
    }
  }

  closeModal(): void {
    this.showModal = false;
    this.selectedFile = null;
  }

  saveModal(): void {
    this.isSaving = true;
    
    switch (this.modalType) {
      case 'module':
        this.saveModule();
        break;
      case 'lesson':
        this.saveLesson();
        break;
      case 'resource':
        this.saveResource();
        break;
      case 'assignment':
        this.saveAssignment();
        break;
    }
  }

  private saveModule(): void {
    const data = { ...this.moduleForm, course: this.course!.id };
    const request = this.editingId
      ? this.api.patch(`/teacher/modules/${this.editingId}/`, data)
      : this.api.post('/teacher/modules/', data);
    
    request.subscribe({
      next: () => { this.closeModal(); this.loadCourse(this.course!.id); this.isSaving = false; },
      error: () => { alert('Lỗi khi lưu'); this.isSaving = false; }
    });
  }

  private saveLesson(): void {
    const data = { ...this.lessonForm, module: this.currentModule!.id };
    const request = this.editingId
      ? this.api.patch(`/teacher/lessons/${this.editingId}/`, data)
      : this.api.post('/teacher/lessons/', data);
    
    request.subscribe({
      next: () => { this.closeModal(); this.loadCourse(this.course!.id); this.isSaving = false; },
      error: () => { alert('Lỗi khi lưu'); this.isSaving = false; }
    });
  }

  private saveResource(): void {
    const formData = new FormData();
    formData.append('lesson', this.currentLesson.id.toString());
    formData.append('type', this.resourceForm.type);
    formData.append('title', this.resourceForm.title);
    
    if (this.resourceForm.type === 'DOCUMENT' && this.selectedFile) {
      formData.append('document_file', this.selectedFile);
    } else if (this.resourceForm.type === 'VIDEO') {
      formData.append('video_source', this.resourceForm.video_source);
      if (this.resourceForm.video_source === 'FILE' && this.selectedFile) {
        formData.append('video_file', this.selectedFile);
      } else {
        formData.append('video_url', this.resourceForm.video_url);
      }
    } else if (this.resourceForm.type === 'LINK') {
      formData.append('link_url', this.resourceForm.link_url);
    } else if (this.resourceForm.type === 'TEXT') {
      formData.append('text_content', this.resourceForm.text_content);
    }
    
    const url = this.editingId ? `/teacher/resources/${this.editingId}/` : '/teacher/resources/';
    const request = this.editingId
      ? this.api.patch(url, formData)
      : this.api.post(url, formData);
    
    request.subscribe({
      next: () => { this.closeModal(); this.loadCourse(this.course!.id); this.isSaving = false; },
      error: () => { alert('Lỗi khi lưu'); this.isSaving = false; }
    });
  }

  private saveAssignment(): void {
    const data: any = {
      lesson: this.currentLesson.id,
      type: this.assignmentForm.type,
      title: this.assignmentForm.title,
      description: this.assignmentForm.description,
      max_score: this.assignmentForm.max_score
    };
    if (this.assignmentForm.time_limit) data.time_limit = this.assignmentForm.time_limit;
    if (this.assignmentForm.attempts_allowed) data.attempts_allowed = this.assignmentForm.attempts_allowed;
    if (this.assignmentForm.due_date) data.due_date = this.assignmentForm.due_date;
    
    const request = this.editingId
      ? this.api.patch(`/teacher/assignments/${this.editingId}/`, data)
      : this.api.post('/teacher/assignments/', data);
    
    request.subscribe({
      next: () => { this.closeModal(); this.loadCourse(this.course!.id); this.isSaving = false; },
      error: () => { alert('Lỗi khi lưu'); this.isSaving = false; }
    });
  }

  // Resource edit/delete
  openEditResource(resource: any, lesson: any): void {
    this.modalType = 'resource';
    this.modalTitle = 'Sửa tài liệu';
    this.currentLesson = lesson;
    this.editingId = resource.id;
    this.resourceForm = {
      type: resource.type,
      title: resource.title,
      video_source: resource.video_source || 'FILE',
      video_url: resource.video_url || '',
      link_url: resource.link_url || '',
      text_content: resource.text_content || ''
    };
    this.showModal = true;
  }

  deleteResource(resource: any): void {
    if (confirm(`Xóa tài liệu "${resource.title}"?`)) {
      this.api.delete(`/teacher/resources/${resource.id}/`).subscribe({
        next: () => this.loadCourse(this.course!.id),
        error: () => alert('Không thể xóa tài liệu')
      });
    }
  }

  // Assignment edit/delete
  openEditAssignment(assignment: any, lesson: any): void {
    this.modalType = 'assignment';
    this.modalTitle = 'Sửa bài tập';
    this.currentLesson = lesson;
    this.editingId = assignment.id;
    this.assignmentForm = {
      type: assignment.type,
      title: assignment.title,
      description: assignment.instructions || '',
      time_limit: assignment.time_limit,
      attempts_allowed: assignment.attempts_allowed,
      due_date: '',
      max_score: assignment.max_score || 100
    };
    this.showModal = true;
  }

  deleteAssignment(assignment: any): void {
    if (confirm(`Xóa bài tập "${assignment.title}"?`)) {
      this.api.delete(`/teacher/assignments/${assignment.id}/`).subscribe({
        next: () => this.loadCourse(this.course!.id),
        error: () => alert('Không thể xóa bài tập')
      });
    }
  }

  // Order management
  moveModule(module: Module, direction: 'up' | 'down', index: number): void {
    const modules = this.course!.modules!;
    const swapIndex = direction === 'up' ? index - 1 : index + 1;
    const items = [
      { id: modules[index].id, order: modules[swapIndex].order },
      { id: modules[swapIndex].id, order: modules[index].order }
    ];
    this.updateOrder('module', items);
  }

  moveLesson(lesson: Lesson, direction: 'up' | 'down', index: number, module: Module): void {
    const lessons = module.lessons!;
    const swapIndex = direction === 'up' ? index - 1 : index + 1;
    const items = [
      { id: lessons[index].id, order: lessons[swapIndex].order },
      { id: lessons[swapIndex].id, order: lessons[index].order }
    ];
    this.updateOrder('lesson', items);
  }

  private updateOrder(type: string, items: { id: number; order: number }[]): void {
    this.api.patch('/teacher/update-order/', { type, items }).subscribe({
      next: () => this.loadCourse(this.course!.id),
      error: () => alert('Không thể cập nhật thứ tự')
    });
  }
}
