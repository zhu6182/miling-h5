<template>
  <div class="star-field">
    <div
      v-for="i in starCount"
      :key="'s'+i"
      class="star"
      :style="starStyles[i-1]"
    ></div>
    <div
      v-for="i in fallingCount"
      :key="'f'+i"
      class="star falling"
      :style="fallingStyles[i-1]"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  starCount: { type: Number, default: 60 },
  fallingCount: { type: Number, default: 3 }
})

const starStyles = computed(() => {
  const arr = []
  for (let i = 0; i < props.starCount; i++) {
    arr.push({
      left: Math.random() * 100 + '%',
      top: Math.random() * 100 + '%',
      width: Math.random() * 2 + 1 + 'px',
      height: Math.random() * 2 + 1 + 'px',
      opacity: Math.random() * 0.5 + 0.2,
      animationDelay: Math.random() * 3 + 's',
      animationDuration: Math.random() * 2 + 2 + 's'
    })
  }
  return arr
})

const fallingStyles = computed(() => {
  const arr = []
  for (let i = 0; i < props.fallingCount; i++) {
    arr.push({
      left: Math.random() * 100 + '%',
      animationDelay: Math.random() * 8 + 's',
      animationDuration: Math.random() * 4 + 6 + 's'
    })
  }
  return arr
})
</script>

<style scoped>
.star-field {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

.star.falling {
  width: 2px;
  height: 2px;
  animation: star-fall 8s linear infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

@keyframes star-fall {
  0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
}
</style>
