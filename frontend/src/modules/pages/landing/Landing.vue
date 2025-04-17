<script setup lang="ts">
import PremiumAdvantages from '@/modules/elements/premium-advantages/PremiumAdvantages.vue';

</script>

<template>
  <div class="container mx-auto px-4">
    <img 
      src="/hero.png"
      alt="Demo image of how the Arabic With Videos App works: First, pick a video, then practice the vocabulary for a given section, then watch and evaluate the section"
      class="w-full mt-5 rounded-xl shadow-xl"
    />

    <section class="py-16 text-center">
      <h1 class="text-4xl font-bold text-primary mb-4">Welcome to <em>Arabic With Videos</em></h1>
      <h3 class="text-xl text-base-content/80 mb-8">Learn a language with videos, the fun way.</h3>
      <router-link to="/dashboard" class="btn btn-primary btn-lg">Start Learning</router-link>
    </section>

    <section class="py-16">
      <h2 class="text-3xl font-bold text-primary mb-8 text-center">The Method</h2>
      <div class="max-w-3xl mx-auto">
        <ol class="space-y-6 text-lg">
          <li class="flex items-start gap-4">
            <div class="badge badge-primary badge-lg min-w-[40px] text-center">1</div>
            <span class="text-base-content/90">Pick a video that looks interesting.</span>
          </li>
          <li class="flex items-start gap-4">
            <div class="badge badge-primary badge-lg min-w-[40px] text-center">2</div>
            <span class="text-base-content/90">Practice the vocabulary needed to understand a few seconds of the video.</span>
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

    <section class="py-16">
      <h2 class="text-3xl font-bold text-primary mb-8 text-center">Learn More</h2>
      <div class="max-w-3xl mx-auto">
        <p class="text-lg text-base-content/90 mb-8">
          Hi, I'm 
          <a href="https://koljapluemer.com/" class="link link-primary" target="_blank" rel="noopener noreferrer">
            Kolja Sam
          </a>. 
          I enjoy studying languages, and I decided to build this app because...
        </p>
        <ul class="space-y-6 text-lg">
          <li class="flex items-start gap-4">
            <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">1</div>
            <span class="text-base-content/90">
              ...I'm a big fan of the idea of 
              <a href="https://en.wikipedia.org/wiki/Input_hypothesis" 
                 class="link link-primary" 
                 target="_blank" 
                 rel="noopener noreferrer">
                Comprehensible Input
              </a>, 
              but such content is not always easy to find, especially for beginner level in more obscure languages. 
              The Arabic With Videos App makes (almost) everything comprehensible by teaching you the relevant words just before.
            </span>
          </li>
          <li class="flex items-start gap-4">
            <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">2</div>
            <span class="text-base-content/90">
              ...I want to watch content in my target language that's actually interesting, not just language learning 
              videos and kid's TV.
            </span>
          </li>
          <li class="flex items-start gap-4">
            <div class="badge badge-primary badge-outline badge-lg min-w-[40px] text-center">3</div>
            <span class="text-base-content/90">
              ...I acknowledge the importance of vocabulary study, but learning arbitrary words that may or may not be 
              useful in the future bores me easily. Having the payoff of understanding a video snippet two minutes 
              later is much more fun.
            </span>
          </li>
        </ul>
      </div>
    </section>

    <PremiumAdvantages />
  </div>
</template>

