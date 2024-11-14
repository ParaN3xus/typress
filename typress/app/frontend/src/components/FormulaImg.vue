<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import { XMarkIcon } from '@heroicons/vue/24/solid';

const fileInputRef = ref(null);
const emit = defineEmits(['update:curBbox']);
const props = defineProps({
    imgUrl: String,
    bboxes: {
        type: Array,
        default: () => []
    },
    curBbox: {
        type: Object,
        default: null
    }
});

const bboxes = ref([...props.bboxes]);
const currentBbox = ref(props.curBbox);

watch(() => props.bboxes, (newBboxes) => {
    console.log(newBboxes)
    bboxes.value = [...newBboxes];
    if (newBboxes.length > 0) {
        currentBbox.value = newBboxes[0];
        emit('update:curBbox', newBboxes[0]);
    }
}, { deep: true });

const isDrawing = ref(false);
const isResizing = ref(false);
const drawStart = ref({ x: 0, y: 0 });
const imageRef = ref(null);
const imgScale = ref(1);
const resizeCorner = ref('');
const hoveredBbox = ref(null);

const calculateScale = () => {
    if (imageRef.value) {
        const imgWidth = imageRef.value.naturalWidth;
        const containerWidth = imageRef.value.clientWidth;
        imgScale.value = containerWidth / imgWidth;
    }
};

const scaleBbox = (bbox) => {
    return {
        x: bbox.x * imgScale.value,
        y: bbox.y * imgScale.value,
        width: bbox.width * imgScale.value,
        height: bbox.height * imgScale.value
    };
};

const drawBbox = (e) => {
    if (e.target === imageRef.value) {
        const rect = imageRef.value.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        isDrawing.value = true;
        drawStart.value = { x, y };
        const newBbox = {
            x: x / imgScale.value,
            y: y / imgScale.value,
            width: 0,
            height: 0
        };
        bboxes.value.push(newBbox);
        currentBbox.value = newBbox;
    }
};

const onMouseMove = (e) => {
    if (isDrawing.value) {
        const rect = imageRef.value.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const bbox = bboxes.value[bboxes.value.length - 1];
        const width = (x - drawStart.value.x) / imgScale.value;
        const height = (y - drawStart.value.y) / imgScale.value;

        if (width < 0) {
            bbox.x = x / imgScale.value;
            bbox.width = Math.abs(width);
        } else {
            bbox.x = drawStart.value.x / imgScale.value;
            bbox.width = width;
        }

        if (height < 0) {
            bbox.y = y / imgScale.value;
            bbox.height = Math.abs(height);
        } else {
            bbox.y = drawStart.value.y / imgScale.value;
            bbox.height = height;
        }

    } else if (isResizing.value && currentBbox.value) {
        const rect = imageRef.value.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const bbox = currentBbox.value;
        const scaled = scaleBbox(bbox);

        switch (resizeCorner.value) {
            case 'nw':
                const newWidth = scaled.x + scaled.width - x;
                const newHeight = scaled.y + scaled.height - y;
                bbox.x = x / imgScale.value;
                bbox.y = y / imgScale.value;
                bbox.width = newWidth / imgScale.value;
                bbox.height = newHeight / imgScale.value;
                break;
            case 'ne':
                bbox.width = (x - scaled.x) / imgScale.value;
                bbox.y = y / imgScale.value;
                bbox.height = (scaled.y + scaled.height - y) / imgScale.value;
                break;
            case 'sw':
                bbox.x = x / imgScale.value;
                bbox.width = (scaled.x + scaled.width - x) / imgScale.value;
                bbox.height = (y - scaled.y) / imgScale.value;
                break;
            case 'se':
                bbox.width = (x - scaled.x) / imgScale.value;
                bbox.height = (y - scaled.y) / imgScale.value;
                break;
        }

    }
};

const stopDrawing = () => {
    if (isDrawing.value || isResizing.value) {
        isDrawing.value = false;
        isResizing.value = false;
        emit('update:curBbox', currentBbox.value);
    }
};

const startResize = (corner, bbox, e) => {
    e.stopPropagation();
    isResizing.value = true;
    resizeCorner.value = corner;
    currentBbox.value = bbox;
};

const deleteBbox = (index, e) => {
    e.stopPropagation();
    bboxes.value.splice(index, 1);
    if (currentBbox.value === bboxes.value[index]) {
        currentBbox.value = bboxes.value[0] || null;
        emit('update:curBbox', currentBbox.value);
    }
};

const selectBbox = (bbox) => {
    currentBbox.value = bbox;
    emit('update:curBbox', bbox);
};

onMounted(() => {
    calculateScale();
    window.addEventListener('resize', calculateScale);
});
</script>

<template>
    <div class="relative flex-1 cursor-pointer" data-tip="Click or Paste to upload" @mousemove="onMouseMove"
        @mouseup="stopDrawing" @mouseleave="stopDrawing">

        <input type="file" ref="fileInputRef" class="hidden" accept="image/*" />

        <div v-if="props.imgUrl" class="relative w-full" @mousedown="drawBbox">
            <img ref="imageRef" :src="props.imgUrl" class="w-full h-auto draggable-none select-none"
                alt="Uploaded Image" @load="calculateScale" />

            <div v-for="(bbox, index) in bboxes" :key="index" :class="[
                'absolute border-2 transition-colors duration-200',
                bbox === currentBbox ? 'border-red-500' : 'border-green-500',
                bbox === hoveredBbox ? 'bg-green-500/20' : ''
            ]" :style="{
                left: `${scaleBbox(bbox).x}px`,
                top: `${scaleBbox(bbox).y}px`,
                width: `${scaleBbox(bbox).width}px`,
                height: `${scaleBbox(bbox).height}px`
            }" @mouseenter="hoveredBbox = bbox" @mouseleave="hoveredBbox = null" @click.stop="selectBbox(bbox)">

                <div class="absolute -top-2 -left-2 w-2 h-2 bg-white border border-black cursor-nw-resize"
                    @mousedown.stop="startResize('nw', bbox, $event)">
                </div>
                <div class="absolute -top-2 -right-2 w-2 h-2 bg-white border border-black cursor-ne-resize"
                    @mousedown.stop="startResize('ne', bbox, $event)">
                </div>
                <div class="absolute -bottom-2 -left-2 w-2 h-2 bg-white border border-black cursor-sw-resize"
                    @mousedown.stop="startResize('sw', bbox, $event)">
                </div>
                <div class="absolute -bottom-2 -right-2 w-2 h-2 bg-white border border-black cursor-se-resize"
                    @mousedown.stop="startResize('se', bbox, $event)">
                </div>

                <div v-if="bbox === hoveredBbox"
                    class="absolute -top-3 left-1/2 -translate-x-1/2 p-0.5 bg-red-500 rounded-full cursor-pointer hover:bg-red-600 transition-colors"
                    @click.stop="deleteBbox(index, $event)">
                    <XMarkIcon class="w-3 h-3 fill-white" />
                </div>
            </div>
        </div>
        <div v-else class="h-32 w-full flex items-center justify-center bg-base-100">
            <div class="border-2 border-dashed border-gray-400 h-full w-full flex items-center justify-center">
                <span class="text-gray-500">Click or Paste to upload image</span>
            </div>
        </div>
    </div>
</template>