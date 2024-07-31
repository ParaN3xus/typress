<script setup>
const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    displayImage(file);
    emit('file-uploaded', file);
  }
};

const displayImage = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = document.getElementById('uploaded-image');
    img.src = e.target.result;
    img.style.display = 'block';
  };
  reader.readAsDataURL(file);
};
</script>

<template>
  <div class="flex justify-between items-center mb-4">
    <div>
      <label for="file-input" class="btn btn-neutral">Choose File</label>
      <input type="file" id="file-input" class="hidden" @change="onFileChange" accept="image/*" />
    </div>
    <div>
      <button class="btn btn-neutral" @click="$emit('feedback')">Report Recognition Error</button>
    </div>
  </div>
</template>