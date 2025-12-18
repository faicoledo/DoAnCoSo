import { Routes } from '@angular/router';

export const TEACHER_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./teacher-dashboard/teacher-dashboard.component').then(m => m.TeacherDashboardComponent)
  },
  {
    path: 'courses',
    loadComponent: () => import('./course-management/course-management.component').then(m => m.CourseManagementComponent)
  },
  {
    path: 'courses/:id',
    loadComponent: () => import('./course-editor/course-editor.component').then(m => m.CourseEditorComponent)
  },
  {
    path: 'submissions',
    loadComponent: () => import('./submission-list/submission-list.component').then(m => m.SubmissionListComponent)
  },
  {
    path: 'students',
    loadComponent: () => import('./student-list/student-list.component').then(m => m.StudentListComponent)
  },
  {
    path: 'students/course/:courseId',
    loadComponent: () => import('./course-students/course-students.component').then(m => m.CourseStudentsComponent)
  },
  {
    path: 'students/course/:courseId/student/:studentId',
    loadComponent: () => import('./student-grades/student-grades.component').then(m => m.StudentGradesComponent)
  },
  {
    path: 'assignments/:id',
    loadComponent: () => import('./assignment-editor/assignment-editor.component').then(m => m.AssignmentEditorComponent)
  },
  {
    path: 'assignments/:id/submissions',
    loadComponent: () => import('./submission-list/submission-list.component').then(m => m.SubmissionListComponent)
  },
  {
    path: 'assignments/:id/questions',
    loadComponent: () => import('./question-editor/question-editor.component').then(m => m.QuestionEditorComponent)
  }
];


