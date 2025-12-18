import { Routes } from '@angular/router';

export const LESSONS_ROUTES: Routes = [
  {
    path: ':id',
    loadComponent: () => import('./lesson-view/lesson-view.component').then(m => m.LessonViewComponent)
  }
];


