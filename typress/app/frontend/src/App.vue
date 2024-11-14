<script setup>
import { ref, onMounted, watchEffect, watchPostEffect, nextTick, watch } from 'vue';
import { useToast } from 'vue-toastification';
import FormulaResult from './components/FormulaResult.vue';
import FeedbackPopup from './components/FeedbackPopup.vue';
import Shields from './components/Shields.vue';
import FormulaImg from './components/FormulaImg.vue';
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline';

const toast = useToast();

var API_ROOT = window.API_ROOT || window.location.origin;

if (process.env.NODE_ENV === 'development') {
  var API_ROOT = "http://localhost:5676";
  console.log('You are in development mode!');
}

const formula = ref(undefined);
const showFeedback = ref(false);
const uploadedImageUrl = ref('');
const uploadedImageFile = ref(null); // Store the uploaded image file
const renderedSvg = ref('');
const isTypstInitialized = ref(false);
const isRendering = ref(false);
const showFeedbackTooltip = ref(false);
const isSubmittingFeedback = ref(false);

const currentHour = new Date().getHours();
const darkMode = ref(currentHour >= 19 || currentHour < 7);

const initializeTypst = () => {
  return new Promise((resolve) => {
    const typstScript = document.getElementById('typst');
    typstScript.addEventListener('load', () => {
      $typst.setCompilerInitOptions({
        getModule: () =>
          '/wasm/typst_ts_web_compiler_bg.wasm',
      });
      $typst.setRendererInitOptions({
        getModule: () =>
          '/wasm/typst_ts_renderer_bg.wasm',
      });
      $typst.svg({ mainContent: "" })
      isTypstInitialized.value = true;
      resolve();
    });
  });
};

const renderFormula = async (formula_text) => {
  if (!isTypstInitialized.value || !formula_text) {
    return;
  }
  try {
    const value = await $typst.svg({
      mainContent: `#set page(width: auto, height: auto, margin: (x: 5pt, y: 5pt))
      $ ${formula_text} $`
    });

    // Create a temporary div to parse the SVG string
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = value;
    const svgElement = tempDiv.querySelector('svg');

    if (svgElement) {
      svgElement.style.width = "100%";
      svgElement.style.height = "auto";
      renderedSvg.value = tempDiv.innerHTML;
    } else {
      throw new Error("SVG element not found");
    }
  } catch (error) {
    toast.error(`Error: ${error}`);
    renderedSvg.value = `Error occurred while rendering: ${error}`;
  } finally {
    isRendering.value = false;
  }
};

watchPostEffect(() => {
  const svgContent = renderedSvg.value;

  if (!svgContent) {
    return;
  }

  const svgContainer = document.querySelector(".rendered-svg-container svg");
  if (!svgContainer) {
    return;
  }
  const themeColor = darkMode.value ? "#ffffff" : "#000000";
  svgContainer.querySelectorAll("*").forEach((element) => {
    element.setAttribute("fill", themeColor);
    element.setAttribute("stroke", themeColor);
  });
});

watch([isTypstInitialized, formula], async () => {
  if (!formula.value) {
    return;
  }
  await renderFormula(formula.value);

  setTimeout(() => {
    showFeedbackTooltip.value = true;

    setTimeout(() => {
      showFeedbackTooltip.value = false;
    }, 3000);
  }, 1500);
});

const handleFileUpload = async (file) => {
  try {
    formula.value = '';
    isRendering.value = true;

    uploadedImageFile.value = file;
    const reader = new FileReader();
    reader.onload = (event) => {
      uploadedImageUrl.value = event.target.result;
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch(`${API_ROOT}/api/formula`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (data.formula) {
      toast.success("Image recognized!");
      formula.value = data.formula;
    } else {
      toast.error(data.error || 'Invalid response from server.');
    }
  } catch (error) {
    toast.error(`Error: ${error}`);
  } finally {
  }
};

const submitFeedback = async (isHandwritten) => {
  isSubmittingFeedback.value = true;

  const formData = new FormData();
  formData.append('file', uploadedImageFile.value);
  formData.append('is_handwritten', isHandwritten);
  formData.append('recognized', formula.value);

  try {
    const response = await fetch('https://typress-feedback.xn--xkrsa0ti6rf4cf98d.com/send_formula_feedback', {
      method: 'POST',
      body: formData
    });
    if (response.status === 200) {
      showFeedback.value = false;
      toast.success('Feedback submitted successfully');
    } else {
      toast.error(`Failed to submit feedback: ${response}`);
    }
  } catch (error) {
    toast.error(`An error occurred while submitting feedback: ${error}`);
  } finally {
    isSubmittingFeedback.value = false;
  }
};

const handlePaste = (event) => {
  const items = (event.clipboardData || event.originalEvent.clipboardData).items;
  for (let item of items) {
    if (item.kind === 'file') {
      const file = item.getAsFile();
      handleFileUpload(file);
      break;
    }
  }
};



const toggleDarkMode = () => {
  darkMode.value = !darkMode.value;
};

onMounted(async () => {
  window.addEventListener('paste', handlePaste);
  await initializeTypst();
});
</script>

<template>
  <div :data-theme="darkMode ? 'dark' : 'light'" class="w-full flex flex-col min-h-screen">
    <header class="flex justify-between items-center w-full bg-base-200 p-4 px-8">
      <h1 class="text-2xl font-bold">Typress</h1>
      <label class="swap swap-rotate">
        <input type="checkbox" class="theme-controller" @change="toggleDarkMode" :checked="darkMode" />
        <SunIcon class="swap-off w-10 h-10 text-yellow-500" />
        <MoonIcon class="swap-on w-10 h-10 text-gray-500" />
      </label>
    </header>
    <div class="flex justify-center items-start flex-1 p-4">
      <div class="bg-base-100 p-6 rounded-lg shadow-offset mt-4 w-full max-w-6xl">
        <div class="flex justify-center">
          <Shields />
        </div>
        <FormulaResult :formula="formula" class="w-full text-left" />
        <div class="image-container flex justify-center items-stretch w-full gap-4 mt-4">
          <FormulaImg :img-url="uploadedImageUrl" @upload="handleFileUpload"></FormulaImg>

          <div class="rendered-svg-container flex-1 tooltip tooltip-bottom"
            :class="{ 'tooltip-open': showFeedbackTooltip }" data-tip="Click to report recognize error"
            @click="showFeedback = true">
            <div v-if="isRendering" class="skeleton w-full h-full"></div>
            <div v-else-if="renderedSvg" class="flex items-center justify-center h-full">
              <div v-html="renderedSvg" class="flex items-center justify-center w-full h-full max-w-full max-h-full" />
            </div>
          </div>
        </div>
        <FeedbackPopup v-if="showFeedback" :is-loading="isSubmittingFeedback" @close="showFeedback = false"
          @submit="submitFeedback" />
      </div>
    </div>
  </div>
</template>


<style scoped>
.uploaded-img-container,
.rendered-svg-container {
  max-width: 50%;
}
</style>