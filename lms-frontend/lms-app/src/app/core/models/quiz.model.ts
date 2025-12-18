export interface Question {
  id: number;
  order: number;
  text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  points: number;
}

export interface QuizStart {
  attempt_id: number;
  assignment_title: string;
  time_limit?: number;
  started_at: string;
  questions: Question[];
}

export interface Answer {
  question_id: number;
  chosen_answer: 'A' | 'B' | 'C' | 'D';
}

export interface QuizSubmit {
  answers: Answer[];
}

export interface AttemptResult {
  attempt_id: number;
  assignment_title: string;
  total_questions: number;
  correct_count: number;
  score: number;
  max_score: number;
  started_at: string;
  submitted_at: string;
  details: AttemptDetail[];
}

export interface AttemptDetail {
  question_id: number;
  question_text: string;
  selected_answer?: string;
  correct_answer: string;
  is_correct: boolean;
  points: number;
  explanation?: string;
}


