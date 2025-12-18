import { Routes } from '@angular/router';
import { authGuard, guestGuard, teacherGuard, adminGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'auth/login',
    pathMatch: 'full'
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES)
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./features/courses/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'courses',
    canActivate: [authGuard],
    loadChildren: () => import('./features/courses/courses.routes').then(m => m.COURSES_ROUTES)
  },
  {
    path: 'lessons',
    canActivate: [authGuard],
    loadChildren: () => import('./features/lessons/lessons.routes').then(m => m.LESSONS_ROUTES)
  },
  {
    path: 'quizzes',
    canActivate: [authGuard],
    loadChildren: () => import('./features/quizzes/quizzes.routes').then(m => m.QUIZZES_ROUTES)
  },
  {
    path: 'my-assignments',
    canActivate: [authGuard],
    loadComponent: () => import('./features/my-assignments/my-assignments.component').then(m => m.MyAssignmentsComponent)
  },
  {
    path: 'notifications',
    canActivate: [authGuard],
    loadChildren: () => import('./features/notifications/notifications.routes').then(m => m.NOTIFICATIONS_ROUTES)
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    loadChildren: () => import('./features/profile/profile.routes').then(m => m.PROFILE_ROUTES)
  },
  {
    path: 'teacher',
    canActivate: [teacherGuard],
    loadChildren: () => import('./features/teacher/teacher.routes').then(m => m.TEACHER_ROUTES)
  },
  {
    path: 'admin',
    canActivate: [adminGuard],
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES)
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
