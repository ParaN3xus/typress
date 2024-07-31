<script setup>
import { ref } from 'vue';
import UploadFile from './components/UploadFile.vue';
import FormulaResult from './components/FormulaResult.vue';
import FeedbackPopup from './components/FeedbackPopup.vue';

const API_ROOT = 'your_api_root_here'; // Replace with actual API root

const formula = ref('');
const showFeedback = ref(false);
const errorMessage = ref('');

const handleFileUpload = async (file) => {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch(`${API_ROOT}/api/formula`, {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (data.formula) {
      formula.value = data.formula;
    } else {
      errorMessage.value = data.error || 'Invalid response from server.';
    }
  } catch (error) {
    errorMessage.value = `An error occurred: ${error}`;
  }
};

const submitFeedback = async (isHandwritten) => {
  // Handle feedback submission logic here
};
</script>

<template>
  <div class="flex justify-center items-start min-h-screen">
    <div class=" bg-white p-6 rounded-lg shadow-md mt-4">
      <h1 class="text-2xl font-bold text-center mb-4">Typress: Typst Math Expressions OCR</h1>
      <UploadFile @file-uploaded="handleFileUpload" @feedback="showFeedback = true" />
      <FormulaResult :formula="formula" />
      <div class="flex justify-center items-center mt-4">
        <img id="uploaded-image" class="max-w-xs" alt="Uploaded Image" style="display:none;">
        <div id="formula-render" class="ml-4"></div>
      </div>
      <FeedbackPopup v-if="showFeedback" @close="showFeedback = false" @submit="submitFeedback" />
    </div>
  </div>
</template>