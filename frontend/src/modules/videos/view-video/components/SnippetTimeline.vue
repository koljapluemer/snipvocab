<template>
  <div class="mt-8">
    <h3 class="text-lg font-semibold mb-4">Snippets Timeline</h3>
    <div class="relative w-full h-12 bg-base-200 rounded-lg overflow-hidden">
      <div v-for="(snippet, index) in enrichedSnippets" :key="index"
        class="absolute h-full cursor-pointer transition-all duration-200" :class="[
          currentSnippetIndex === index ? 'ring-2 ring-primary' : '',
          'hover:brightness-110 hover:scale-[1.02]'
        ]" :style="{
          left: `${getLeftPosition(index)}%`,
          width: `${getWidth(index)}%`,
          backgroundColor: getDifficultyColor(snippet.perceivedDifficulty ?? null, index)
        }" :title="`Snippet ${index + 1}: ${formatTime(snippet.startTime)} - ${formatTime(snippet.endTime)}
Understanding: ${snippet.perceivedDifficulty ?? 'Not rated'}`" @click="$emit('jump-to-snippet', index)" />
    </div>
    <div class="flex justify-between mt-2 text-sm text-gray-500">
      <span>0:00</span>
      <span>{{ formatTime(totalDuration) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { EnrichedSnippetDetails } from '@/shared/domainTypes';

interface Props {
  enrichedSnippets: EnrichedSnippetDetails[];
  currentSnippetIndex: number | null;
}

const props = defineProps<Props>();
defineEmits<{
  (e: 'jump-to-snippet', index: number): void;
}>();

// Compute total duration from the last snippet's end time
const totalDuration = computed(() => {
  if (props.enrichedSnippets.length === 0) return 0;
  return props.enrichedSnippets[props.enrichedSnippets.length - 1].endTime;
});

// Get the left position for a snippet
const getLeftPosition = (index: number): number => {
  if (index === 0) return 0;
  const previousSnippet = props.enrichedSnippets[index - 1];
  return (previousSnippet.endTime / totalDuration.value) * 100;
};

// Get the width for a snippet
const getWidth = (index: number): number => {
  const snippet = props.enrichedSnippets[index];
  const startTime = index === 0 ? 0 : props.enrichedSnippets[index - 1].endTime;
  return ((snippet.endTime - startTime) / totalDuration.value) * 100;
};

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
