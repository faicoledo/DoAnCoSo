import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { NotificationService, Notification } from '../../../core/services/notification.service';

@Component({
  selector: 'app-notification-list',
  standalone: true,
  imports: [CommonModule, MainLayoutComponent, CardComponent, LoadingComponent, EmptyStateComponent],
  template: `
    <app-main-layout>
      <div class="notifications-page">
        <div class="page-header">
          <h1>Thông báo</h1>
          @if (notifications.length > 0) {
            <button class="btn btn-outline" (click)="markAllAsRead()">
              Đánh dấu tất cả đã đọc
            </button>
          }
        </div>
        
        @if (isLoading) {
          <app-loading message="Đang tải thông báo..."></app-loading>
        } @else if (notifications.length === 0) {
          <app-empty-state 
            title="Không có thông báo"
            description="Bạn chưa có thông báo nào"
          ></app-empty-state>
        } @else {
          <div class="notifications-list">
            @for (notification of notifications; track notification.id) {
              <app-card [hoverable]="true" [clickable]="true">
                <div 
                  class="notification-item"
                  [class.unread]="!notification.is_read"
                  (click)="markAsRead(notification)"
                >
                  <div class="notification-icon" [class]="getIconClass(notification.type)">
                    <span [innerHTML]="getIcon(notification.type)"></span>
                  </div>
                  <div class="notification-content">
                    <h3>{{ notification.title }}</h3>
                    <p>{{ notification.message }}</p>
                    <span class="time">{{ notification.created_at | date:'dd/MM/yyyy HH:mm' }}</span>
                  </div>
                  @if (!notification.is_read) {
                    <span class="unread-dot"></span>
                  }
                </div>
              </app-card>
            }
          </div>
        }
      </div>
    </app-main-layout>
  `,
  styles: [`
    .notifications-page {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    
    .page-header h1 {
      font-size: 1.75rem;
      color: #1a1a2e;
    }
    
    .btn {
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #e0e0e0;
      color: #666;
    }
    
    .btn-outline:hover {
      border-color: #0f3460;
      color: #0f3460;
    }
    
    .notifications-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .notification-item {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 4px;
      position: relative;
    }
    
    .notification-item.unread {
      background: #f8f9ff;
      margin: -24px;
      padding: 24px;
      border-radius: 16px;
    }
    
    .notification-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    
    .notification-icon.lesson {
      background: #e3f2fd;
      color: #1565c0;
    }
    
    .notification-icon.assignment {
      background: #e8f5e9;
      color: #2e7d32;
    }
    
    .notification-icon.deadline {
      background: #fff3e0;
      color: #ef6c00;
    }
    
    .notification-icon.graded {
      background: #f3e5f5;
      color: #7b1fa2;
    }
    
    .notification-icon.general {
      background: #f5f5f5;
      color: #666;
    }
    
    .notification-icon :deep(svg) {
      width: 24px;
      height: 24px;
    }
    
    .notification-content {
      flex: 1;
    }
    
    .notification-content h3 {
      font-size: 1rem;
      color: #1a1a2e;
      margin-bottom: 4px;
    }
    
    .notification-content p {
      font-size: 0.95rem;
      color: #666;
      line-height: 1.5;
      margin-bottom: 8px;
    }
    
    .time {
      font-size: 0.85rem;
      color: #999;
    }
    
    .unread-dot {
      width: 10px;
      height: 10px;
      background: #1565c0;
      border-radius: 50%;
      flex-shrink: 0;
    }
  `]
})
export class NotificationListComponent implements OnInit {
  private notificationService = inject(NotificationService);
  
  notifications: Notification[] = [];
  isLoading = true;

  ngOnInit(): void {
    this.loadNotifications();
  }

  private loadNotifications(): void {
    this.notificationService.getNotifications().subscribe({
      next: (notifications) => {
        this.notifications = notifications;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  markAsRead(notification: Notification): void {
    if (notification.is_read) return;
    
    this.notificationService.markAsRead(notification.id).subscribe({
      next: () => {
        notification.is_read = true;
      }
    });
  }

  markAllAsRead(): void {
    this.notificationService.markAllAsRead().subscribe({
      next: () => {
        this.notifications.forEach(n => n.is_read = true);
      }
    });
  }

  getIconClass(type: string): string {
    const map: Record<string, string> = {
      'LESSON_CREATED': 'lesson',
      'ASSIGNMENT_CREATED': 'assignment',
      'ASSIGNMENT_DEADLINE': 'deadline',
      'ASSIGNMENT_GRADED': 'graded',
      'GENERAL': 'general'
    };
    return map[type] || 'general';
  }

  getIcon(type: string): string {
    const icons: Record<string, string> = {
      'LESSON_CREATED': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>',
      'ASSIGNMENT_CREATED': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>',
      'ASSIGNMENT_DEADLINE': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      'ASSIGNMENT_GRADED': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      'GENERAL': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>'
    };
    return icons[type] || icons['GENERAL'];
  }
}


