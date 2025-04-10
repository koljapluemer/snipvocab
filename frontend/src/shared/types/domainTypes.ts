import type { Card } from "ts-fsrs";

export interface Meaning {
  en: string
}

export interface Word {
    originalWord: string;
    meanings: Meaning[];
}

export interface WordFlashCard extends Word {
  isDue: boolean;
  isNew: boolean;
  isFavorite: boolean;
  isBlacklisted: boolean;
}

export interface Snippet {
    videoId: string;
    index: number;
    startTime: number;
    endTime: number;
}

export interface SnippetDetails {
  startTime: number;
  endTime: number;
  videoId: string;
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
