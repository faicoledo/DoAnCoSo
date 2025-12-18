import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loading',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (overlay) {
      <div class="loading-overlay">
        <div class="spinner-container">
          <div class="spinner" [style.width.px]="size" [style.height.px]="size"></div>
          @if (message) {
            <p class="message">{{ message }}</p>
          }
        </div>
      </div>
    } @else {
      <div class="loading-inline">
        <div class="spinner" [style.width.px]="size" [style.height.px]="size"></div>
        @if (message) {
          <span class="message">{{ message }}</span>
        }
      </div>
    }
  `,
  styles: [`
    .loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255,255,255,0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }
    
    .spinner-container {
      text-align: center;
    }
    
    .loading-inline {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 20px;
    }
    
    .spinner {
      border: 3px solid #f0f0f0;
      border-top-color: #0f3460;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .message {
      color: #666;
      margin-top: 12px;
    }
    
    .loading-inline .message {
      margin: 0;
    }
  `]
})
export class LoadingComponent {
  @Input() size = 40;
  @Input() message = '';
  @Input() overlay = false;
}


