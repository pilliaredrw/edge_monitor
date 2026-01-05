
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const nodes = ref([])
const loading = ref(true)
let timer = null

// 注意：这里使用相对路径 '/api/dashboard'
// 在本地开发时，我们需要在 vite.config.js 中配置代理
// 在生产环境下，Nginx 会处理这个路径
const fetchStats = async () => {
  try {
    const response = await fetch('/api/dashboard')
    const data = await response.json()
    nodes.value = data
    loading.value = false
  } catch (error) {
    console.error("数据获取失败:", error)
  }
}

onMounted(() => {
  fetchStats()
  timer = setInterval(fetchStats, 3000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
    <div class="max-w-7xl mx-auto">
      <header class="flex justify-between items-end mb-12 border-b border-slate-700 pb-6">
        <div>
          <h1 class="text-4xl font-black tracking-tighter text-blue-400">EDGE MONITOR</h1>
          <p class="text-slate-400 mt-2 text-sm uppercase tracking-widest">探针说是</p>
        </div>
        <div class="text-right">
          <span class="text-xs bg-slate-800 px-3 py-1 rounded text-slate-500 font-mono">
            REFRESH: 3000MS
          </span>
        </div>
      </header>

      <main v-if="!loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="node in nodes" :key="node.node_id" 
             class="bg-slate-800 border border-slate-700 rounded-xl p-6 transition-all hover:border-blue-500/50 shadow-lg">
          
          <div class="flex justify-between items-start mb-6">
            <h2 class="text-xl font-bold truncate pr-4">{{ node.node_name }}</h2>
            <div :class="node.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'" 
                 class="w-3 h-3 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)]"></div>
          </div>

          <div v-if="node.status === 'online'" class="space-y-6">
            <div>
              <div class="flex justify-between text-xs mb-2 text-slate-400 uppercase font-bold">
                <span>CPU Load</span>
                <span class="text-slate-200">{{ node.cpu.cpu_usage_percent }}%</span>
              </div>
              <div class="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 transition-all duration-500" 
                     :style="{ width: node.cpu.cpu_usage_percent + '%' }"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs mb-2 text-slate-400 uppercase font-bold">
                <span>Memory Usage</span>
                <span class="text-slate-200">{{ node.memory.usage_percent }}%</span>
              </div>
              <div class="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                <div class="h-full bg-purple-500 transition-all duration-500" 
                     :style="{ width: node.memory.usage_percent + '%' }"></div>
              </div>
              <div class="mt-2 text-[10px] text-slate-500 font-mono text-right">
                {{ node.memory.available_gb }}GB / {{ node.memory.total_gb }}GB FREE
              </div>
            </div>
          </div>

          <div v-else class="h-32 flex items-center justify-center border border-dashed border-slate-700 rounded-lg">
             <span class="text-slate-600 font-mono text-sm uppercase italic">Node Connection Lost</span>
          </div>
        </div>
      </main>

      <div v-else class="text-center py-20 animate-pulse text-slate-500 font-mono uppercase tracking-tighter">
        Initializing secure connection...
      </div>
    </div>
  </div>
</template>