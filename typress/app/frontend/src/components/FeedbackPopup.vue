<script setup>
import { ref } from 'vue';
import { XMarkIcon } from '@heroicons/vue/24/solid';

const isHandwritten = ref(false);

const submitFeedback = () => {
  emit('submit', isHandwritten.value);
};
</script>
<template>
  <div id="feedback-popup" class="fixed inset-0 bg-gray-800 bg-opacity-75 flex justify-center items-center z-50"
    @click.self="$emit('close')">
    <div class="bg-base-100 p-6 rounded-lg shadow-xl relative max-w-lg w-full mx-4">
      <h2 class="text-xl font-bold mb-4 text-primary">Feedback</h2>
      <button id="close-popup" class="btn btn-square absolute top-4 right-4 bg-transparent hover:bg-red-500 group"
        @click="$emit('close')">
        <XMarkIcon class="h-6 w-6 text-red-500 group-hover:text-white" />
      </button>

      <label class="flex items-center mb-4 text-gray-700">
        <input type="checkbox" v-model="isHandwritten" class="checkbox mr-2" />
        <span>This image is handwritten</span>
      </label>
      <p class="text-base mb-2 text-gray-600">
        By pressing the "Submit" button, you agree to have your image uploaded
        to our server, used for training data, and publicly shared.
      </p>
      <p class="text-base mb-4 text-gray-600">Thank you for your support!</p>
      <div class="flex justify-end">
        <button class="btn btn-primary" @click="submitFeedback">Submit</button>
      </div>
    </div>
  </div>
</template>
