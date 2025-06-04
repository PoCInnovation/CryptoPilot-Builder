<template>
  <div class="flex-container">
    <div>Bloc 1</div>
    <div class="ligne"></div>
    <div>Bloc 2</div>
  </div>
</template>

<style>
.flex-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ligne {
  height: 1px;
  background-color: gray;
  width: 100%;
}
</style>
