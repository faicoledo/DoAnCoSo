import { Routes } from '@angular/router';

export const QUIZZES_ROUTES: Routes = [
  {
    path: ':id',
    loadComponent: () => import('./quiz-start/quiz-start.component').then(m => m.QuizStartComponent)
  },
  {
    path: ':id/take',
    loadComponent: () => import('./quiz-take/quiz-take.component').then(m => m.QuizTakeComponent)
  },
  {
    path: ':id/submit-file',
    loadComponent: () => import('./file-submit/file-submit.component').then(m => m.FileSubmitComponent)
  },
  {
    path: 'attempt/:attemptId/result',
    loadComponent: () => import('./quiz-result/quiz-result.component').then(m => m.QuizResultComponent)
  }
];


