<script setup>
import { ref } from 'vue';
import { useToast } from 'vue-toastification';

const props = defineProps({
  formula: String
});

const toast = useToast();

const copyToClipboard = () => {
  navigator.clipboard.writeText(props.formula).then(() => {
    toast.success('Copied!');
  });
};
</script>

<template>
  <div class="tooltip tooltip-bottom w-full h-full" data-tip="Click to copy" @click="copyToClipboard">
    <div v-if="formula == ''" class="skeleton w-full h-14"></div>
    <pre v-else id="result-text"
      class="whitespace-pre-wrap bg-base-100 p-4 rounded-lg shadow-inner-strong hover:bg-base-200 transition">{{ formula || 'Upload or paste an image to see the result here...' }}</pre>
  </div>
</template>