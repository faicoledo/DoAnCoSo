import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Notification {
  id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
  related_object_type?: string;
  related_object_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  constructor(private api: ApiService) {}

  getNotifications(params?: { is_read?: boolean }): Observable<Notification[]> {
    return this.api.get<Notification[]>('/notifications/', params);
  }

  markAsRead(id: number): Observable<any> {
    return this.api.post(`/notifications/${id}/read/`, {});
  }

  markAllAsRead(): Observable<any> {
    return this.api.post('/notifications/mark-all-read/', {});
  }

  getUnreadCount(): Observable<{ count: number }> {
    return this.api.get<{ count: number }>('/notifications/unread-count/');
  }
}


