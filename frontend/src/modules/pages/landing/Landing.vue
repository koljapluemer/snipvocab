<script setup lang="ts">
import PremiumAdvantages from '@/modules/elements/premium-advantages/PremiumAdvantages.vue';

</script>

<template>
  <div class="container mx-auto px-4">
    <img 
      src="/hero.png"
      alt="Demo image of how the Arabic With Videos App works: First, pick a video, then practice the vocabulary for a given section, then watch and evaluate the section"
      class="w-full mt-5"
    />

    <section class="py-8 flex flex-col gap-2 items-center">
      <h1>Welcome to the <em>Arabic With Videos</em> App!</h1>
      <h3>Learn a language with videos, the fun way.</h3>
      <router-link to="/dashboard" class="btn btn-primary btn-lg">Start Learning</router-link>
    </section>

    <section class="py-8">
      <h2>The Method:</h2>
      <ol class="list-decimal pl-8 space-y-4">
        <li>Pick a video that looks interesting.</li>
        <li>Practice the vocabulary needed to understand a few seconds of the video.</li>
        <li>Watch the video snippet and evaluate how well you understood it.</li>
        <li>Repeat until you got the whole video.</li>
      </ol>
    </section>

    <section class="py-8">
      <h2>Learn More:</h2>
      <p class="my-4">
        Hi, I'm 
        <a href="https://koljapluemer.com/" class="link link-primary" target="_blank" rel="noopener noreferrer">
          Kolja Sam
        </a>. 
        I enjoy studying languages, and I decided to build this app because...
      </p>
      <ul class="list-disc list-inside space-y-4">
        <li>
          ...I'm a big fan of the idea of 
          <a href="https://en.wikipedia.org/wiki/Input_hypothesis" 
             class="link link-primary" 
             target="_blank" 
             rel="noopener noreferrer">
            Comprehensible Input
          </a>, 
          but such content is not always easy to find, especially for beginner level in more obscure languages. 
          The Arabic With Videos App makes (almost) everything comprehensible by teaching you the relevant words just before.
        </li>
        <li>
          ...I want to watch content in my target language that's actually interesting, not just language learning 
          videos and kid's TV.
        </li>
        <li>
          ...I acknowledge the importance of vocabulary study, but learning arbitrary words that may or may not be 
          useful in the future bores me easily. Having the payoff of understanding a video snippet two minutes 
          later is much more fun.
        </li>
      </ul>
    </section>

    <PremiumAdvantages />

    
  </div>
</template>

