import { shuffleArray } from "@/shared/utils/listUtils";
import type { FlashCardStack, WordFlashCard } from "src/shared/types/domainTypes";

export const shuffleFlashcardIntoStack = (stack: FlashCardStack, flashcard: WordFlashCard): FlashCardStack => {
    if (stack.length === 0) {
        return stack;
    }

    const stackWithFlashcard = addFlashcardToEndOfStack(stack, flashcard);
    const shuffledStack = shuffleArray(stackWithFlashcard);
    return shuffledStack;
};

export const addFlashcardToEndOfStack = (stack: FlashCardStack, flashcard: WordFlashCard): FlashCardStack => {
    return [...stack, flashcard];
};
