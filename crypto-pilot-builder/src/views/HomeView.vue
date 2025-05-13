<template>
  <div class="dashboard">
    <h1 class="welcome">Welcome</h1>
    <div class="widgets">
      <div class="widget btc">
        <span class="label">BTC</span>
        <span class="value">+2.7%</span>
      </div>
      <div class="widget talk">
        <button class="talk-btn">Talk to Agent</button>
      </div>
      <div class="widget news">
        <span class="label">Actu by lulu</span>
        <div class="news-content">Dernières news crypto...</div>
      </div>
      <div class="widget empty"></div>
      <div class="widget empty"></div>
    </div>
  </div>
</template>

<script setup>
// Ici, tu pourras importer les vrais widgets ou données dynamiques plus tard
</script>

<style scoped>
.dashboard {
  padding: 2rem 3rem;
  flex: 1;
}
.welcome {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #fff;
}
.widgets {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 120px);
  gap: 1.5rem;
}
.widget {
  background: #232b4a;
  border-radius: 18px;
  box-shadow: 0 2px 12px #0002;
  padding: 1.5rem;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  font-size: 1.2rem;
}
.widget.btc {
  grid-column: 1;
  grid-row: 1;
  background: linear-gradient(90deg, #3a1c71 0%, #009ffd 100%);
  color: #fff;
  font-size: 1.5rem;
  font-weight: bold;
}
.widget.talk {
  grid-column: 2;
  grid-row: 1 / span 2;
  justify-content: center;
  align-items: center;
}
.talk-btn {
  background: #00e6a0;
  color: #232b4a;
  border: none;
  border-radius: 12px;
  padding: 1.2rem 2.5rem;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 8px #0002;
  transition: background 0.2s;
}
.talk-btn:hover {
  background: #00b37a;
}
.widget.news {
  grid-column: 3;
  grid-row: 1 / span 2;
  background: #232b4a;
  overflow: auto;
}
.news-content {
  margin-top: 0.7rem;
  font-size: 1rem;
  color: #b3b3b3;
}
.widget.empty {
  background: transparent;
  box-shadow: none;
}
</style> 