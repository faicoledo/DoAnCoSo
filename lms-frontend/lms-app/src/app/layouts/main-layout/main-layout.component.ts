import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { SidebarComponent } from '../../shared/components/sidebar/sidebar.component';
import { NotificationService } from '../../core/services/notification.service';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, HeaderComponent, SidebarComponent],
  template: `
    <app-header 
      [unreadCount]="unreadCount" 
      (toggleSidebar)="sidebarCollapsed = !sidebarCollapsed"
    ></app-header>
    <app-sidebar [collapsed]="sidebarCollapsed"></app-sidebar>
    <main class="main-content" [class.sidebar-collapsed]="sidebarCollapsed">
      <ng-content></ng-content>
    </main>
  `,
  styles: [`
    .main-content {
      margin-left: 260px;
      margin-top: 64px;
      min-height: calc(100vh - 64px);
      padding: 24px;
      background: #f5f7fa;
      transition: margin-left 0.3s ease;
    }
    
    .main-content.sidebar-collapsed {
      margin-left: 72px;
    }
    
    @media (max-width: 768px) {
      .main-content {
        margin-left: 0;
        padding: 16px;
      }
    }
  `]
})
export class MainLayoutComponent implements OnInit {
  private notificationService = inject(NotificationService);
  private api = inject(ApiService);
  private authService = inject(AuthService);
  
  sidebarCollapsed = false;
  unreadCount = 0;

  ngOnInit(): void {
    this.loadUnreadCount();
    this.loadUserProfile();
  }

  private loadUnreadCount(): void {
    this.notificationService.getUnreadCount().subscribe({
      next: (res) => this.unreadCount = res.count,
      error: () => {}
    });
  }

  private loadUserProfile(): void {
    this.api.get<any>('/auth/me/').subscribe({
      next: (user) => this.authService.updateCurrentUser(user),
      error: () => {}
    });
  }
}


