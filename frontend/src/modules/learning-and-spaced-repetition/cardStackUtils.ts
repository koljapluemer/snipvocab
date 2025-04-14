import type { FlashCardStack, WordFlashCard } from "src/shared/types/domainTypes";

export const shuffleFlashcardIntoStack = (stack: FlashCardStack, flashcard: WordFlashCard): FlashCardStack => {
    console.log('shuffleFlashcardIntoStack(): stack at beginning', stack, '\nflashcard:', flashcard)
    if (stack.length === 0) {
        return stack;
    }
   
    // Generate a random index between 1 and stack.length (inclusive)
    const insertIndex = Math.floor(Math.random() * (stack.length)) + 1;
    
    // Insert the flashcard at the chosen index
    const newStack = [...stack.slice(0, insertIndex), flashcard, ...stack.slice(insertIndex)];
    console.log('shuffleFlashcardIntoStack(): newStack', newStack)
    return newStack;
};

export const addFlashcardToEndOfStack = (stack: FlashCardStack, flashcard: WordFlashCard): FlashCardStack => {
    return [...stack, flashcard];
};
