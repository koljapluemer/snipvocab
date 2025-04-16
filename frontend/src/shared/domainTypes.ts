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

export type FlashCardStack = WordFlashCard[]

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

export interface EnrichedSnippetDetails extends SnippetDetails {
  perceivedDifficulty?: number;
  lastUpdated?: Date;
}

export enum LearningEventType {
  AGAIN = "AGAIN", 
  HARD = "HARD",   // Rating.Hard
  GOOD = "GOOD",   // Rating.Good
  EASY = "EASY"    // Rating.Easy
}

export interface LearningEvent {
  eventType: LearningEventType;
  timestamp: number;
  originalWord: string;
}
