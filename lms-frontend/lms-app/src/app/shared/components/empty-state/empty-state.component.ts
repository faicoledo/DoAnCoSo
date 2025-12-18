import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="empty-state">
      <div class="icon" [innerHTML]="icon"></div>
      <h3>{{ title }}</h3>
      @if (description) {
        <p>{{ description }}</p>
      }
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }
    
    .icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 20px;
      color: #ccc;
    }
    
    .icon :deep(svg) {
      width: 100%;
      height: 100%;
    }
    
    h3 {
      font-size: 1.2rem;
      color: #333;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 0.95rem;
      max-width: 400px;
      margin: 0 auto 20px;
    }
  `]
})
export class EmptyStateComponent {
  @Input() title = 'Không có dữ liệu';
  @Input() description = '';
  @Input() icon = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>';
}


