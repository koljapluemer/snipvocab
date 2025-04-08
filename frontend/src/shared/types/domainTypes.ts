import type { Card } from "ts-fsrs";

export interface Word {
    original_word: string;
    meanings: string[];
}

export interface Flashcard extends Card, Word {
}

export interface Snippet {
    words: Word[];
    start: number;
    duration: number;
}

export interface Snippet {
  index: number
  start: number
  duration: number
  start_time: number
  end_time: number
}

export interface Video {
  youtube_id: string
  only_premium: boolean
  is_blacklisted: boolean
} 


export const FlashCardButtons = {
  again: 'Again',
  hard: 'Hard',
  good: 'Good',
  easy: 'Easy',
  seen: 'I Will Remember'
} as const

export type FlashCardButtonLabel = keyof typeof FlashCardButtons
