import { Routes } from '@angular/router';

export const COURSES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./my-courses/my-courses.component').then(m => m.MyCoursesComponent)
  },
  {
    path: 'explore',
    loadComponent: () => import('./course-list/course-list.component').then(m => m.CourseListComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('./course-detail/course-detail.component').then(m => m.CourseDetailComponent)
  }
];


