<script setup>
import { ref, onMounted, watchEffect, watchPostEffect, nextTick, watch } from 'vue';
import { useToast } from 'vue-toastification';
import FormulaResult from './components/FormulaResult.vue';
import FeedbackPopup from './components/FeedbackPopup.vue';
import Shields from './components/Shields.vue';
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline';

const toast = useToast();

const API_ROOT = import.meta.env.VITE_API_ROOT;
// const API_ROOT = 'http://localhost:5676'; // Replace with actual API root

const formula = ref('');
const showFeedback = ref(false);
const uploadedImageUrl = ref('');
const uploadedImageFile = ref(null); // Store the uploaded image file
const renderedSvg = ref('');
const isTypstInitialized = ref(false);
const darkMode = ref(false); // Add darkMode ref
const isRecognizing = ref(false); // Add loading state
const isRendering = ref(false); // Add loading state

const initializeTypst = () => {
  return new Promise((resolve) => {
    const typstScript = document.getElementById('typst');
    if (typstScript) {
      typstScript.addEventListener('load', () => {
        $typst.setCompilerInitOptions({
          getModule: () =>
            'https://cdn.jsdelivr.net/npm/@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm',
        });
        $typst.setRendererInitOptions({
          getModule: () =>
            'https://cdn.jsdelivr.net/npm/@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm',
        });
        isTypstInitialized.value = true;
        resolve();
      });
    } else {
      // Handle case where the script is not found or already loaded
      isTypstInitialized.value = true;
      resolve();
    }
  });
};
const renderFormula = async () => {
  if (!isTypstInitialized.value || !formula.value) {
    return;
  }
  try {
    const value = await $typst.svg({
      mainContent: `#set page(width: auto, height: auto, margin: (x: 5pt, y: 5pt))
      //#show math.equation: set text(26pt)
      $ ${formula.value} $`
    });

    // Create a temporary div to parse the SVG string
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = value;
    const svgElement = tempDiv.querySelector('svg');

    if (svgElement) {
      svgElement.style.width = "100%";
      svgElement.style.height = "auto";
      renderedSvg.value = tempDiv.innerHTML;
      await nextTick();
    } else {
      throw new Error("SVG element not found");
    }
  } catch (error) {
    toast.error(`Error: ${error}`);
    renderedSvg.value = `Error occurred while rendering: ${error}`;
  } finally {
    isRendering.value = false; // Move loading state here
  }
};

// Function to update SVG colors based on the theme
const updateSvgTheme = (svgElement, mode) => {
  const themeColor = mode ? "#ffffff" : "#000000";
  svgElement.querySelectorAll("*").forEach((element) => {
    element.setAttribute("fill", themeColor);
    element.setAttribute("stroke", themeColor);
  });
};

// Watch for changes in darkMode and update the SVG theme
watchPostEffect(() => {
  const svgContainer = document.querySelector(".rendered-svg-container svg");
  console.log(1)
  if (svgContainer) {
    updateSvgTheme(svgContainer, darkMode.value);
  }
});


watch([isTypstInitialized, formula], renderFormula);

const handleFileUpload = async (file) => {
  try {
    uploadedImageFile.value = file; // Save the uploaded image file
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

    isRecognizing.value = true; // Move loading state here
    isRendering.value = true;

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
    isRecognizing.value = false;
  }
};

const submitFeedback = async (isHandwritten) => {
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
      toast.error('Failed to submit feedback.');
    }
  } catch (error) {
    toast.error(`An error occurred while submitting feedback: ${error}`);
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

const fileInputRef = ref(null);

const handleImageClick = () => {
  fileInputRef.value.click();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    handleFileUpload(file);
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
      <div class="flex items-center space-x-2">
        <SunIcon v-if="!darkMode" class="w-6 h-6 text-yellow-500" />
        <MoonIcon v-else class="w-6 h-6 text-gray-500" />
        <input type="checkbox" class="toggle toggle-lg" @change="toggleDarkMode" :checked="darkMode" />
      </div>
    </header>
    <div class="flex justify-center items-start flex-1 p-4">
      <div class="bg-base-100 p-6 rounded-lg shadow-offset mt-4 w-full max-w-6xl">
        <div class="flex justify-center">
          <Shields />
        </div>
        <FormulaResult :formula="formula" style="width: 100%; text-align: left;" />
        <div class="image-container flex justify-center items-center mt-4">
          <div class="uploaded-img-container tooltip tooltip-bottom" data-tip="Click or Paste to upload"
            @click="handleImageClick">
            <input type="file" ref="fileInputRef" class="hidden" @change="handleFileChange" accept="image/*" />
            <img v-if="uploadedImageUrl" :src="uploadedImageUrl" class="uploaded-img w-full" alt="Uploaded Image" />
            <div v-else class="placeholder w-full">
              <span class="text-center">Click or Paste to upload</span>
            </div>
          </div>

          <div class="rendered-svg-container tooltip tooltip-bottom" data-tip="Click to report recognize error"
            @click="showFeedback = true">
            <span v-if="isRendering" class="loading loading-spinner loading-lg"></span>
            <div v-else-if="renderedSvg" v-html="renderedSvg" class=" rendered-svg-containerml-4"></div>
            <div v-else class="svg-placeholder ml-4">SVG will be rendered here</div>
          </div>
        </div>
        <FeedbackPopup v-if="showFeedback" @close="showFeedback = false" @submit="submitFeedback" />
      </div>
    </div>
  </div>
</template>


<style scoped>
.rendered-svg-container {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: auto;
}

.rendered-svg-container svg {
  width: 100%;
  height: auto;
  pointer-events: none;
  /* Prevents SVG from intercepting clicks */
}


.rendered-svg-container,
.uploaded-img-container {
  flex: 1 1 0;
  max-width: 50%;
  height: auto;
  cursor: pointer;
}

.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  gap: 4px;
}

.placeholder,
.svg-placeholder {
  flex: 1 1 0;
  max-width: 100%;
  height: 200px;
  border: 2px dashed #ccc;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
}

.uploaded-img-container {
  position: relative;
  flex: 1 1 0;
  max-width: 50%;
  height: auto;
  cursor: pointer;
}

.loading-indicator {
  text-align: center;
  margin: 20px 0;
  font-size: 1.5rem;
  color: #666;
}
</style>
