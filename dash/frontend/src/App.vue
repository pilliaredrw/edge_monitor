<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const nodes = ref([])
const initialLoading = ref(true)
let timer = null

const initDashboard = async () => {
  try {
    const res = await fetch('/api/nodes')
    const list = await res.json()
    
    nodes.value = list.map(node => ({
      ...node,
      status: 'loading',
      data: null,
      error: null
    }))
    
    initialLoading.value = false
    fetchAllStatuses()
  } catch (e) {
    console.error("无法获取节点清单:", e)
  }
}

const fetchAllStatuses = () => {
  nodes.value.forEach((node, index) => {
    fetchSingleNodeStatus(index)
  })
}

const fetchSingleNodeStatus = async (index) => {
  const node = nodes.value[index]
  try {
    const res = await fetch(`/api/node/${node.id}/status`)
    const result = await res.json()
    
    nodes.value[index] = {
      ...node,
      status: result.status,
      data: result,
      error: result.error || null
    }
  } catch (e) {
    nodes.value[index].status = 'offline'
    nodes.value[index].error = 'Network Error'
  }
}

onMounted(() => {
  initDashboard()
  timer = setInterval(fetchAllStatuses, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans">
    <div class="max-w-7xl mx-auto">
      
      <!-- Header -->
      <header class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-xl font-bold text-slate-100 font-mono">
            mini-monitor
          </h1>
          <p class="text-xs text-slate-500 font-mono mt-1">
            {{ nodes.length }} nodes · polling every 5s
          </p>
        </div>
        <div class="flex items-center gap-3 text-xs font-mono text-slate-400">
          <span>mode: pull</span>
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            connected
          </span>
        </div>
      </header>

      <!-- Loading -->
      <div v-if="initialLoading" class="flex flex-col items-center justify-center py-20">
        <div class="w-12 h-12 border-4 border-slate-700 border-t-slate-500 rounded-full animate-spin mb-4"></div>
        <p class="text-slate-500 font-mono text-sm animate-pulse">
          connecting to aggregator...
        </p>
      </div>

      <!-- Nodes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="(node, index) in nodes" :key="node.id"
             class="bg-slate-900 border border-slate-800 rounded-2xl p-6 transition-all duration-200 hover:border-slate-600">
          
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="text-lg font-semibold text-slate-100 font-mono">
                {{ node.name }}
              </h2>
              <code class="text-[10px] text-slate-500 font-mono">uid: {{ node.id }}</code>
            </div>
            
            <!-- Status -->
            <div v-if="node.status === 'loading'" class="w-4 h-4 border-2 border-slate-700 border-t-slate-500 rounded-full animate-spin"></div>
            <div v-else :class="node.status === 'online' ? 'text-emerald-400' : 'text-slate-500'"
                 class="text-xs font-mono font-semibold">
              {{ node.status }}
            </div>
          </div>

          <!-- Online Node Stats -->
          <div v-if="node.status === 'online' && node.data" class="space-y-4">
            <div>
              <div class="flex justify-between text-[11px] mb-1 font-mono">
                <span>CPU Load</span>
                <span class="text-blue-400 font-bold">{{ node.data.cpu.cpu_usage_percent }}%</span>
              </div>
              <div class="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-slate-500 transition-all duration-1000"
                     :style="{ width: node.data.cpu.cpu_usage_percent + '%' }"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-[11px] mb-1 font-mono">
                <span>Memory Usage</span>
                <span class="text-purple-400 font-bold">{{ node.data.memory.usage_percent }}%</span>
              </div>
              <div class="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-slate-500 transition-all duration-1000"
                     :style="{ width: node.data.memory.usage_percent + '%' }"></div>
              </div>
              <div class="mt-2 flex justify-between items-center text-[9px] font-mono text-slate-500">
                <span>cores: {{ node.data.cpu.cpu_cores }}</span>
                <span>{{ node.data.memory.available_gb }}GB / {{ node.data.memory.total_gb }}GB free</span>
              </div>
            </div>
          </div>

          <!-- Offline Node -->
          <div v-else-if="node.status === 'offline'"
               class="h-28 flex flex-col justify-center text-xs font-mono text-slate-500 border border-dashed border-slate-800 rounded-xl">
            <div>status: offline</div>
            <div class="text-slate-600">{{ node.error || 'timeout' }}</div>
          </div>

          <!-- Placeholder -->
          <div v-else class="h-28 flex items-center justify-center">
            <div class="space-y-2 w-full">
              <div class="h-2 bg-slate-800 rounded animate-pulse w-3/4"></div>
              <div class="h-2 bg-slate-800 rounded animate-pulse w-1/2"></div>
            </div>
          </div>

        </div>
      </div>

      <!-- Footer -->
      <footer class="mt-10 text-center text-xs text-slate-500 font-mono">
        telemetry via FastAPI aggregator
      </footer>

    </div>
  </div>
</template>

<style>
body {
  cursor: default;
  user-select: none;
}
</style>
