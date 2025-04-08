import type { Flashcard, FlashCardButtonLabel } from "@/shared/types/domainTypes"
import { shuffleArray } from "@/shared/utils/listUtils"
import { ref, watch } from "vue"

export function useFlashCardStackHandler(initialFlashcards: Flashcard[]) {
  const flashCardStack = ref<Flashcard[]>(initialFlashcards)

  // first shuffle the flashcards
  console.info('Initial flashcards:', initialFlashcards.map(card => card.original_word))
  flashCardStack.value = shuffleArray(flashCardStack.value)
  console.info('After shuffling:', flashCardStack.value.map(card => card.original_word))

  // Watch for changes in the flashcard stack
  watch(flashCardStack, (newStack) => {
    console.info('Flashcard stack changed:', {
      stackSize: newStack.length,
      nextCard: newStack[0]?.original_word,
      remainingCards: newStack.map(card => card.original_word)
    })
  }, { deep: true })

  function rateFlashcardAndGetNext(flashcard: Flashcard, rating: FlashCardButtonLabel): Flashcard|undefined {
    handleFlashcardEvaluated(flashcard, rating)
    return getNextFlashcard()
  }

  function getNextFlashcard():Flashcard|undefined {
    // get first flashcard from stack, also remove it from stack
    const flashcard = flashCardStack.value.shift()
    console.info('Getting next flashcard:', flashcard?.original_word, 'Remaining:', flashCardStack.value.map(card => card.original_word))
    return flashcard
  }

  function handleFlashcardEvaluated(flashcard: Flashcard, rating: FlashCardButtonLabel) {
    // if 'again' or 'seen', put the flashcard at a random!!!! position in the stack
    // if 'hard', put the flashcard at the end of the stack
    // otherwise, don't do anything
    if (rating === 'again' || rating === 'seen') {
      // If there's only one position (index 0), don't add the card back
      // this prevents showing the same card immediately after it was shown
      if (flashCardStack.value.length <= 1) {
        console.info(`Not adding card "${flashcard.original_word}" back as there's no valid position`)
        return
      }

      // Generate random index excluding 0
      const randomIndex = Math.floor(Math.random() * (flashCardStack.value.length - 1)) + 1
      console.info(`Adding card "${flashcard.original_word}" back at random position ${randomIndex} due to rating "${rating}"`)
      flashCardStack.value.splice(randomIndex, 0, flashcard)
      console.info('Stack after adding:', flashCardStack.value.map(card => card.original_word))
    } else if (rating === 'hard') {
      console.info(`Adding card "${flashcard.original_word}" to end of stack due to rating "${rating}"`)
      flashCardStack.value.push(flashcard)
      console.info('Stack after adding:', flashCardStack.value.map(card => card.original_word))
    }
  }

  return {
    flashCardStack,
    getNextFlashcard,
    handleFlashcardEvaluated,
    rateFlashcardAndGetNext
  }
}

