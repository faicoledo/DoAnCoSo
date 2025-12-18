import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./admin-dashboard/admin-dashboard.component').then(m => m.AdminDashboardComponent)
  },
  {
    path: 'users',
    loadComponent: () => import('./user-management/user-management.component').then(m => m.UserManagementComponent)
  },
  {
    path: 'subjects',
    loadComponent: () => import('./subject-management/subject-management.component').then(m => m.SubjectManagementComponent)
  },
  {
    path: 'courses',
    loadComponent: () => import('./course-management/course-management.component').then(m => m.CourseManagementComponent)
  },
  {
    path: 'enrollments',
    loadComponent: () => import('./enrollment-management/enrollment-management.component').then(m => m.EnrollmentManagementComponent)
  }
];


