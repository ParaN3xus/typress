<script setup>
import { ref } from 'vue';

const fileInputRef = ref(null);
const emit = defineEmits();
const props = defineProps({
    imgUrl: String
});

const handleImageClick = () => {
    fileInputRef.value.click();
};

const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        emit('upload', file);
    }
};
</script>

<template>
    <div class="uploaded-img-container flex-1 tooltip tooltip-bottom" data-tip="Click or Paste to upload"
        @click="handleImageClick">
        <input type="file" ref="fileInputRef" class="hidden" @change="handleFileChange" accept="image/*" />
        <div v-if="imgUrl" class="flex items-center justify-center h-full">
            <img :src="imgUrl" class="w-full items-center flex" alt="Uploaded Image" />
        </div>
        <div v-else class="h-32 w-full flex items-center justify-center bg-base-100">
            <div class="border-2 border-dashed border-gray-400 h-full w-full flex items-center justify-center">
                <span class="text-gray-500">Click or Paste to upload image</span>
            </div>
        </div>
    </div>
</template>
