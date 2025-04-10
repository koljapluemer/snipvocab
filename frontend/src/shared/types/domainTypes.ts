import type { Card } from "ts-fsrs";

export interface Meaning {
  en: string
}

export interface Word {
    original_word: string;
    meanings: Meaning[];
}

export interface WordFlashCard extends Word {
  isDue: boolean;
  isNew: boolean;
  isFavorite: boolean;
  isBlacklisted: boolean;
}

export interface Snippet {
    start_time: number;
    end_time: number;
    video_id: string;
    index: number;
}

export interface SnippetDetails {
  start_time: number;
  end_time: number;
  video_id: string;
  index: number;
  words: Word[];
}


export const FlashCardButtons = {
  again: 'Again',
  hard: 'Hard',
  good: 'Good',
  easy: 'Easy',
  seen: 'I Will Remember'
} as const

export type FlashCardButtonLabel = keyof typeof FlashCardButtons
