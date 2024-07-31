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
  <div class="tooltip tooltip-top" data-tip="Click to copy" @click="copyToClipboard">
    <pre id="result-text" class="whitespace-pre-wrap bg-gray-100 p-4 rounded-lg shadow-inner hover:bg-gray-200 transition">{{ formula || 'Upload or paste an image to see the result here...' }}</pre>
  </div>
</template>
