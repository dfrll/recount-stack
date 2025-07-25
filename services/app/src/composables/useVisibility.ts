import { ref } from 'vue'

export function useVisibility(initial = true) {
    const isVisible = ref(initial)

    function toggle() {
        isVisible.value = !isVisible.value
    }

    return {
        isVisible,
        toggle,
    }
}
