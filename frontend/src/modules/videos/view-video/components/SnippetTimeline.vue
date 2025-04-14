<template>
  <div class="mt-8">
    <h3 class="text-lg font-semibold mb-4">Snippets Timeline</h3>
    <div class="relative w-full h-12 bg-base-200 rounded-lg overflow-hidden">
      <div v-for="(snippet, index) in snippets" :key="index"
        class="absolute h-full cursor-pointer transition-all duration-200" :class="[
          currentSnippetIndex === index ? 'ring-2 ring-primary' : '',
          'hover:brightness-110 hover:scale-[1.02]'
        ]" :style="{
          left: `${(snippet.startTime / totalDuration) * 100}%`,
          width: `${((snippet.endTime - snippet.startTime) / totalDuration) * 100}%`,
          backgroundColor: getDifficultyColor(enrichedSnippets[index]?.perceivedDifficulty ?? null, index)
        }" :title="`Snippet ${index + 1}: ${formatTime(snippet.startTime)} - ${formatTime(snippet.endTime)}
Understanding: ${enrichedSnippets[index]?.perceivedDifficulty ?? 'Not rated'} %`" @click="$emit('jump-to-snippet', index)" />
    </div>
    <div class="flex justify-between mt-2 text-sm text-gray-500">
      <span>0:00</span>
      <span>{{ formatTime(totalDuration) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Snippet, EnrichedSnippetDetails } from '@/shared/types/domainTypes';

interface Props {
  snippets: Snippet[];
  enrichedSnippets: EnrichedSnippetDetails[];
  currentSnippetIndex: number | null;
}

const props = defineProps<Props>();
defineEmits<{
  (e: 'jump-to-snippet', index: number): void;
}>();

// Compute total duration from the last snippet's end time
const totalDuration = computed(() => {
  if (props.snippets.length === 0) return 0;
  return props.snippets[props.snippets.length - 1].endTime;
});

// Compute color based on difficulty (0-100)
const getDifficultyColor = (difficulty: number | null, index: number) => {
  if (difficulty === null) {
    // Alternate between light and dark gray for unrated snippets
    return index % 2 === 0 ? 'bg-base-100' : 'bg-base-300';
  }

  // Map difficulty to HSL color space
  // 0 -> 120 (green), 50 -> yellow, 100 -> 0 (red)
  const hue = difficulty * 1.2; // 0 is green, 120 is red
  const saturation = 100;
  const lightness = 45; // Keep it dark enough for good contrast

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
};

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};
</script>
