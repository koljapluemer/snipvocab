<template>
  <section class="py-16">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-bold text-primary mb-4">Premium Account</h2>
      <p class="text-xl text-base-content/80">
        Unlock unlimited learning potential and accelerate your language journey
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Free Tier -->
      <div class="card bg-base-200 shadow-xl hover:shadow-2xl transition-shadow duration-300">
        <div class="card-body">
          <h3 class="card-title text-2xl mb-6">Free Account</h3>
          
          <ul class="space-y-4 text-lg">
            <li class="flex items-start gap-4">
              <div class="badge badge-primary badge-outline badge-lg min-w-[100px] text-center">Limited</div>
              <span class="text-base-content/90">2 videos per day</span>
            </li>
            <li class="flex items-start gap-4">
              <div class="badge badge-primary badge-outline badge-lg min-w-[100px] text-center">Basic</div>
              <span class="text-base-content/90">Standard learning features</span>
            </li>
            <li class="flex items-start gap-4">
              <div class="badge badge-primary badge-outline badge-lg min-w-[100px] text-center">Free</div>
              <span class="text-base-content/90">No cost</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Premium Tier -->
      <div class="card bg-gradient-to-br from-primary to-primary-focus text-primary-content shadow-xl hover:shadow-2xl transition-shadow duration-300">
        <div class="card-body">
          <h3 class="card-title text-2xl mb-6">Premium Account</h3>
          
          <ul class="space-y-4 text-lg">
            <li class="flex items-start gap-4">
              <div class="badge badge-outline badge-lg min-w-[100px] text-center">Unlimited</div>
              <span>Unlimited video practice</span>
            </li>
            <li class="flex items-start gap-4">
              <div class="badge badge-outline badge-lg min-w-[100px] text-center">Enhanced</div>
              <span>Advanced learning features</span>
            </li>
            <li class="flex items-start gap-4">
              <div class="badge badge-outline badge-lg min-w-[100px] text-center">Premium</div>
              <span>Full access to all content</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="mt-12 text-center">
      <div class="stats shadow">
        <div class="stat">
          <div class="stat-title text-lg">Daily Practice Limit</div>
          <div class="stat-value text-primary text-3xl">Unlimited</div>
          <div class="stat-desc text-lg">With Premium</div>
        </div>
        <div class="stat">
          <div class="stat-title text-lg">Free Account</div>
          <div class="stat-value text-error text-3xl">2</div>
          <div class="stat-desc text-lg">Videos per day</div>
        </div>
      </div>
    </div>
  </section>
</template>

