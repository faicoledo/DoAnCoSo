import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card" [class.hoverable]="hoverable" [class.clickable]="clickable">
      @if (title || headerTemplate) {
        <div class="card-header">
          @if (headerTemplate) {
            <ng-content select="[card-header]"></ng-content>
          } @else {
            <h3 class="card-title">{{ title }}</h3>
            @if (subtitle) {
              <p class="card-subtitle">{{ subtitle }}</p>
            }
          }
        </div>
      }
      <div class="card-body" [class.no-padding]="noPadding">
        <ng-content></ng-content>
      </div>
      @if (footerTemplate) {
        <div class="card-footer">
          <ng-content select="[card-footer]"></ng-content>
        </div>
      }
    </div>
  `,
  styles: [`
    .card {
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      overflow: hidden;
      transition: all 0.3s ease;
    }
    
    .card.hoverable:hover {
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      transform: translateY(-4px);
    }
    
    .card.clickable {
      cursor: pointer;
    }
    
    .card-header {
      padding: 20px 24px;
      border-bottom: 1px solid #f0f0f0;
    }
    
    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
    }
    
    .card-subtitle {
      font-size: 0.9rem;
      color: #666;
      margin: 4px 0 0;
    }
    
    .card-body {
      padding: 24px;
    }
    
    .card-body.no-padding {
      padding: 0;
    }
    
    .card-footer {
      padding: 16px 24px;
      border-top: 1px solid #f0f0f0;
      background: #fafafa;
    }
  `]
})
export class CardComponent {
  @Input() title = '';
  @Input() subtitle = '';
  @Input() hoverable = false;
  @Input() clickable = false;
  @Input() noPadding = false;
  @Input() headerTemplate = false;
  @Input() footerTemplate = false;
}


