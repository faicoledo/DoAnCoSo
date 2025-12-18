import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainLayoutComponent } from '../../../layouts/main-layout/main-layout.component';
import { CardComponent } from '../../../shared/components/card/card.component';

@Component({
  selector: 'app-assignment-editor',
  standalone: true,
  imports: [CommonModule, MainLayoutComponent, CardComponent],
  template: `
    <app-main-layout>
      <div class="assignment-editor">
        <app-card>
          <div class="placeholder">
            <h2>Chỉnh sửa bài tập</h2>
            <p>Tính năng này đang được phát triển. Vui lòng sử dụng Django Admin để chỉnh sửa bài tập.</p>
            <a href="/admin/" target="_blank" class="btn btn-outline">Mở Django Admin</a>
          </div>
        </app-card>
      </div>
    </app-main-layout>
  `,
  styles: [`
    .assignment-editor {
      max-width: 800px;
      margin: 40px auto;
    }
    
    .placeholder {
      text-align: center;
      padding: 60px 20px;
    }
    
    .placeholder h2 {
      color: #1a1a2e;
      margin-bottom: 12px;
    }
    
    .placeholder p {
      color: #666;
      margin-bottom: 24px;
    }
    
    .btn {
      display: inline-block;
      padding: 12px 24px;
      border-radius: 10px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.3s ease;
    }
    
    .btn-outline {
      background: transparent;
      border: 2px solid #0f3460;
      color: #0f3460;
    }
    
    .btn-outline:hover {
      background: #0f3460;
      color: #fff;
    }
  `]
})
export class AssignmentEditorComponent {}


