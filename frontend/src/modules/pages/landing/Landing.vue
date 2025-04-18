<script setup lang="ts">
import PremiumAdvantages from '@/modules/elements/premium-advantages/PremiumAdvantages.vue';

</script>

<template>
  <img src="/hero.png"
    alt="Demo image of how the Arabic With Videos App works: First, pick a video, then practice the vocabulary for a given section, then watch and evaluate the section"
    class="w-full mt-5 rounded-xl shadow-xl" />

  <section class="text-center">
    <h1 class="text-4xl font-bold text-primary mb-4">Welcome to <em>Arabic With Videos</em></h1>
    <h3 class="text-xl text-base-content/80 mb-8">Learn a language with videos, the fun way.</h3>
    <router-link :to="{ name: 'register' }" class="btn btn-primary btn-lg">Sign Up & Start Learning</router-link>
  </section>

  <section class="py-8">
    <h2 class="text-3xl font-bold text-primary mb-8 text-center">The Method</h2>
    <div class="max-w-3xl mx-auto">
      <ol class="space-y-6 text-lg">
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-lg min-w-[40px] text-center">1</div>
          <span class="text-base-content/90">Pick a video that looks interesting.</span>
        </li>
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-lg min-w-[40px] text-center">2</div>
          <span class="text-base-content/90">Practice the vocabulary needed to understand a few seconds of the
            video.</span>
        </li>
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-lg min-w-[40px] text-center">3</div>
          <span class="text-base-content/90">Watch the video snippet and evaluate how well you understood it.</span>
        </li>
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-lg min-w-[40px] text-center">4</div>
          <span class="text-base-content/90">Repeat until you got the whole video.</span>
        </li>
      </ol>
    </div>
  </section>

  <section class="py-8">
    <h2 class="text-3xl font-bold text-primary mb-8 text-center">Why Use <em>Arabic With Videos</em>?</h2>
    <div class="max-w-3xl mx-auto">
      <ul class="space-y-6 text-lg">
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">1</div>
          <span class="text-base-content/90">
            Based on the proven
            <a href="https://en.wikipedia.org/wiki/Input_hypothesis" class="link link-primary" target="_blank"
              rel="noopener noreferrer">
              Comprehensible Input
            </a>
            method, our app makes any video content accessible by teaching you the relevant vocabulary just before you
            need it.
          </span>
        </li>
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">2</div>
          <span class="text-base-content/90">
            Learn from authentic content that interests you, not just language learning materials or children's shows.
          </span>
        </li>
        <li class="flex items-start gap-4">
          <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">3</div>
          <span class="text-base-content/90">
            Immediate application of new vocabulary makes learning more engaging and effective. See your progress in
            real-time as you understand more of each video.
          </span>
        </li>
      </ul>

    </div>
  </section>

  <PremiumAdvantages />

  <router-link :to="{ name: 'register' }" class="btn btn-primary btn-lg mx-auto">Sign Up Now</router-link>


</template>
