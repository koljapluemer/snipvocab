import type { Directive } from 'vue'

const intersect: Directive = {
  mounted(el, binding) {
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          binding.value()
        }
      })
    }, options)

    observer.observe(el)
    el._intersectObserver = observer
  },
  unmounted(el) {
    if (el._intersectObserver) {
      el._intersectObserver.disconnect()
    }
  }
}

export default intersect 