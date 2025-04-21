import { onMounted } from 'vue'

export function useGoatCounter() {
  onMounted(() => {
    // Create and append the GoatCounter script
    const script = document.createElement('script')
    script.setAttribute('async', '')
    script.setAttribute('src', '//gc.zgo.at/count.js')
    script.setAttribute('data-goatcounter', 'https://arabicwithvideos.goatcounter.com/count')
    document.body.appendChild(script)
  })
} 