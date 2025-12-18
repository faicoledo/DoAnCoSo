# LMS Frontend - Angular

Giao diện người dùng cho hệ thống quản lý học tập (LMS).

## Cấu trúc dự án

```
src/app/
├── core/                    # Core module
│   ├── guards/             # Auth guards
│   ├── interceptors/       # HTTP interceptors
│   ├── models/             # TypeScript interfaces
│   └── services/           # API services
├── shared/                  # Shared module
│   ├── components/         # Reusable components
│   ├── pipes/              # Custom pipes
│   └── directives/         # Custom directives
├── features/               # Feature modules
│   ├── auth/               # Login, Register
│   ├── courses/            # Course listing, detail
│   ├── lessons/            # Lesson viewer
│   ├── quizzes/            # Quiz system
│   ├── notifications/      # Notifications
│   ├── profile/            # User profile
│   ├── teacher/            # Teacher dashboard
│   └── admin/              # Admin dashboard
└── layouts/                # Layout components
```

## Cài đặt

```bash
cd lms-frontend/lms-app
npm install
```

## Chạy development server

```bash
ng serve
```

Mở trình duyệt tại `http://localhost:4200/`

## Build production

```bash
ng build --configuration production
```

## Kết nối với Backend

Cấu hình API URL trong `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

## Tính năng đã hoàn thành

### Giao diện Học viên
- [x] Đăng nhập / Đăng ký
- [x] Dashboard
- [x] Danh sách khóa học
- [x] Chi tiết khóa học
- [x] Xem bài học
- [x] Xem tài liệu (video, document)
- [x] Làm bài quiz
- [x] Xem kết quả quiz
- [x] Thông báo
- [x] Hồ sơ cá nhân

### Giao diện Giảng viên
- [x] Dashboard giảng viên
- [x] Quản lý khóa học
- [x] Xem danh sách bài nộp
- [x] Chấm điểm bài nộp

### Giao diện Admin
- [x] Dashboard Admin (placeholder)
- [ ] Quản lý người dùng (sử dụng Django Admin)
- [ ] Quản lý khóa học (sử dụng Django Admin)
- [ ] Báo cáo & Thống kê

## Công nghệ sử dụng

- Angular 19
- TypeScript
- SCSS
- RxJS
- Angular Router
- Angular Forms
