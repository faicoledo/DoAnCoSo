export interface Subject {
  id: number;
  name: string;
  description?: string;
}

export interface Course {
  id: number;
  title: string;
  description?: string;
  thumbnail?: string;
  subject?: Subject | null;
  teacher?: {
    id: number;
    full_name: string;
  } | null;
  is_published: boolean;
  created_at: string;
  modules?: Module[];
  status?: 'UPCOMING' | 'ONGOING' | 'COMPLETED';
  status_display?: string;
  role_in_course?: string;
  start_date?: string;
  end_date?: string;
  modules_count?: number;
  students_count?: number;
  total_modules?: number;
  total_students?: number;
}

export interface Module {
  id: number;
  title: string;
  description?: string;
  order: number;
  lessons?: Lesson[];
}

export interface Lesson {
  id: number;
  title: string;
  description?: string;
  order: number;
  resources?: Resource[];
  assignments?: Assignment[];
}

export interface Resource {
  id: number;
  title: string;
  type: 'DOCUMENT' | 'VIDEO' | 'LINK' | 'TEXT';
  type_display?: string;
  document_url?: string;
  video_url?: string;
  link_url?: string;
  text_content?: string;
  duration?: number;
  duration_display?: string;
  file_size?: number;
  file_size_display?: string;
  is_uploaded?: boolean;
  order: number;
}

export interface Assignment {
  id: number;
  title: string;
  instructions?: string;
  type: 'QUIZ' | 'FILE_UPLOAD';
  start_at: string;
  end_at: string;
  time_limit?: number;
  attempts_allowed: number;
  max_score: number;
  is_available: boolean;
}


