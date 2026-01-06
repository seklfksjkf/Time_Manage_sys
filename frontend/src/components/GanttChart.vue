<template>
  <div class="gantt-wrapper">
    <!-- 上半部分：任务列表 -->
    <div class="task-section">
      <div class="task-header">
        <div class="col-header col-task">TASK</div>
        <div class="col-header col-dates">DATES</div>
        <div class="col-header col-assignee">ASSIGNEE</div>
        <div class="col-header col-actions">ACTIONS</div>
        <div class="col-header col-milestone">MILESTONE</div>
      </div>

      <div class="task-list">
        <div
          v-for="task in tasks"
          :key="'task-' + task.id"
          class="task-row"
        >
          <div class="col-cell col-task">
            <el-tag :type="getStatusType(task.status)" size="small">
              {{ task.status }}
            </el-tag>
            <span class="task-name">{{ task.title }}</span>
          </div>
          <div class="col-cell col-dates">
            <span class="date-range">{{ formatDateRange(task.start_date, task.end_date) }}</span>
          </div>
          <div class="col-cell col-assignee">
            <span>{{ task.assigned_to_name || '-' }}</span>
          </div>
          <div class="col-cell col-actions">
            <el-button
              type="primary"
              size="small"
              circle
              @click="$emit('task-edit', task)"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button
              type="danger"
              size="small"
              circle
              @click="$emit('task-delete', task)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <div class="col-cell col-milestone">
            <div v-if="milestonesList.length > 0" class="milestone-list">
              <div
                v-for="milestone in milestonesList"
                :key="milestone.id"
                class="milestone-item"
                :style="{ backgroundColor: milestone.color || '#e74c3c' }"
              >
                <span class="milestone-name">{{ milestone.name }}</span>
                <span class="milestone-date">{{ formatMilestoneDate(milestone.date) }}</span>
              </div>
            </div>
            <span v-else class="no-milestone">-</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 下半部分：完整甘特图 -->
    <div class="gantt-section">
      <div class="gantt-timeline-header" ref="ganttTimelineRef">
        <div class="gantt-months">
          <div
            v-for="month in months"
            :key="'gantt-' + month.key"
            class="gantt-month"
            :style="{ width: month.width + 'px' }"
          >
            {{ month.label }}
          </div>
        </div>
        <div class="gantt-days">
          <div
            v-for="day in days"
            :key="'gantt-day-' + day.key"
            class="gantt-day"
            :class="{ weekend: day.isWeekend, today: day.isToday }"
            :style="{ width: day.width + 'px' }"
          >
            <span v-if="zoomLevel !== 'month'">{{ day.label }}</span>
          </div>
        </div>
      </div>

      <div class="gantt-chart" @scroll="handleGanttScroll">
        <!-- 背景网格 -->
        <div class="gantt-grid">
          <div
            v-for="day in days"
            :key="'grid-' + day.key"
            class="grid-col"
            :class="{ weekend: day.isWeekend, today: day.isToday }"
            :style="{ left: day.offset + 'px', width: day.width + 'px' }"
          ></div>
        </div>

        <!-- 任务条 -->
        <div class="gantt-bars">
          <div
            v-for="(task, index) in tasks"
            :key="'gantt-bar-' + task.id"
            class="gantt-bar-row"
            :style="{ top: (index * TASK_HEIGHT) + 'px' }"
          >
            <div
              v-if="task.start_date && task.end_date"
              class="gantt-task-bar"
              :class="[
                'status-' + task.status,
                'priority-' + task.priority,
                { selected: selectedTaskId === task.id }
              ]"
              :style="getBarStyle(task)"
              @click="handleTaskClick(task)"
              @mousedown="startDrag($event, task)"
            >
              <div class="bar-background">
                <div class="bar-progress" :style="{ width: task.progress + '%' }"></div>
              </div>
              <div class="bar-label">
                <span class="bar-title">{{ task.title }}</span>
                <span class="bar-percent">{{ task.progress }}%</span>
              </div>
              
              <!-- 调整手柄 -->
              <div 
                class="resize-handle left-handle" 
                @mousedown.stop="startResize($event, task, 'left')"
              ></div>
              <div 
                class="resize-handle right-handle" 
                @mousedown.stop="startResize($event, task, 'right')"
              ></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { ElTag } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  tasks: {
    type: Array,
    required: true
  },
  milestones: {
    type: Array,
    default: () => []
  },
  startDate: {
    type: Date,
    default: null
  },
  endDate: {
    type: Date,
    default: null
  },
  zoomLevel: {
    type: String,
    default: 'day'
  }
})

const emit = defineEmits(['task-click', 'task-edit', 'task-delete', 'task-update'])

const ganttTimelineRef = ref(null)
const selectedTaskId = ref(null)

const TASK_HEIGHT = 60

const dragState = ref({
  isDragging: false,
  isResizing: false,
  taskId: null,
  direction: null,
  startX: 0
})

// 每天宽度
const DAY_WIDTH = computed(() => {
  switch (props.zoomLevel) {
    case 'month': return 8
    case 'week': return 20
    case 'day':
    default: return 40
  }
})

// 项目开始日期
const projectStart = computed(() => {
  const dates = []
  
  if (props.startDate) {
    dates.push(new Date(props.startDate))
  }
  
  props.tasks.forEach(t => {
    const d = new Date(t.start_date)
    if (!isNaN(d.getTime())) dates.push(d)
  })
  
  if (dates.length === 0) return new Date()
  
  const minDate = new Date(Math.min(...dates))
  minDate.setHours(0, 0, 0, 0)
  return minDate
})

// 项目结束日期（扩展显示更多月份）
const projectEnd = computed(() => {
  const dates = []
  
  if (props.endDate) {
    dates.push(new Date(props.endDate))
  }
  
  props.tasks.forEach(t => {
    const d = new Date(t.end_date)
    if (!isNaN(d.getTime())) dates.push(d)
  })
  
  let actualEnd
  if (dates.length === 0) {
    actualEnd = new Date()
    actualEnd.setDate(actualEnd.getDate() + 30)
  } else {
    actualEnd = new Date(Math.max(...dates))
  }
  
  // 扩展到该月的最后一天，再加上3个完整月份
  const extendedEnd = new Date(actualEnd)
  // 先到当月月底
  extendedEnd.setMonth(extendedEnd.getMonth() + 1)
  extendedEnd.setDate(0)
  // 再加3个完整月份
  extendedEnd.setMonth(extendedEnd.getMonth() + 3)
  extendedEnd.setDate(new Date(extendedEnd.getFullYear(), extendedEnd.getMonth() + 1, 0).getDate())
  
  return extendedEnd
})

// 生成天数（先生成天数数组）
const days = computed(() => {
  const result = []
  const current = new Date(projectStart.value)
  current.setHours(0, 0, 0, 0)
  
  const end = new Date(projectEnd.value)
  end.setHours(0, 0, 0, 0)
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  // 确保使用一致的 DAY_WIDTH
  const dayWidth = DAY_WIDTH.value
  let offset = 0
  
  console.log(`🔄 Generating days with DAY_WIDTH: ${dayWidth}, zoomLevel: ${props.zoomLevel}`)
  
  // 循环直到当前日期超过结束日期
  while (current <= end) {
    const dayOfWeek = current.getDay()
    const currentDate = new Date(current)
    currentDate.setHours(0, 0, 0, 0)
    
    result.push({
      key: current.toISOString(),
      label: current.getDate(),
      date: new Date(current),
      year: current.getFullYear(),
      month: current.getMonth(),
      isWeekend: dayOfWeek === 0 || dayOfWeek === 6,
      isToday: currentDate.getTime() === today.getTime(),
      offset: offset,
      width: dayWidth  // 存储每天的宽度，确保一致性
    })
    
    offset += dayWidth
    current.setDate(current.getDate() + 1)
  }
  
  console.log(`✅ Total days: ${result.length}, DAY_WIDTH: ${dayWidth}px`)
  console.log(`📅 Date range: ${projectStart.value.toLocaleDateString()} to ${projectEnd.value.toLocaleDateString()}`)
  
  return result
})

// 生成月份（基于实际渲染的天数）
const months = computed(() => {
  const monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
  const monthNamesFull = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  
  // 强制追踪所有依赖
  const zoomLevel = props.zoomLevel  // 明确追踪 zoomLevel
  const dayWidth = DAY_WIDTH.value   // 追踪 DAY_WIDTH
  const allDays = days.value         // 追踪 days
  
  console.log(`🔄 Recalculating months with zoomLevel: ${zoomLevel}, DAY_WIDTH: ${dayWidth}px, Total days: ${allDays.length}`)
  
  // 按月份分组统计（改用 reduce 方法确保正确）
  const monthGroups = []
  const monthCountMap = {}
  
  // 统计每个月的天数
  allDays.forEach(day => {
    const monthKey = `${day.year}-${day.month}`
    if (!monthCountMap[monthKey]) {
      monthCountMap[monthKey] = {
        year: day.year,
        month: day.month,
        count: 0
      }
    }
    monthCountMap[monthKey].count++
  })
  
  // 转换为数组并保持顺序
  Object.keys(monthCountMap).forEach(key => {
    const { year, month, count } = monthCountMap[key]
    monthGroups.push({ year, month, count })
    console.log(`  └─ ${monthNamesFull[month]} ${year}: ${count} days`)
  })
  
  // 验证总天数
  const totalDaysInMonths = monthGroups.reduce((sum, m) => sum + m.count, 0)
  console.log(`  ✅ Total days in months: ${totalDaysInMonths} (should be ${allDays.length})`)
  
  // 生成月份数组并验证
  const result = monthGroups.map(({ year, month, count }) => {
    const width = count * dayWidth
    console.log(`📅 Month: ${monthNamesFull[month]} ${year}, Days: ${count}, Width: ${width}px (${count} × ${dayWidth}px)`)
    return {
      key: `${year}-${month}`,
      shortLabel: `${monthNames[month]} ${year}`,
      label: `${monthNamesFull[month]} ${year}`,
      width: width
    }
  })
  
  // 验证总宽度
  const totalMonthWidth = result.reduce((sum, m) => sum + m.width, 0)
  const totalDayWidth = allDays.reduce((sum, d) => sum + d.width, 0)
  const expectedWidth = allDays.length * dayWidth
  
  console.log(`\n📊 Width Verification:`)
  console.log(`  Total months: ${result.length}`)
  console.log(`  Total days: ${allDays.length}`)
  console.log(`  Month width sum: ${totalMonthWidth}px`)
  console.log(`  Day width sum: ${totalDayWidth}px`)
  console.log(`  Expected (${allDays.length} × ${dayWidth}): ${expectedWidth}px`)
  console.log(`  Month ↔ Expected: ${totalMonthWidth === expectedWidth ? '✅ MATCH' : '❌ MISMATCH'}`)
  console.log(`  Day ↔ Expected: ${totalDayWidth === expectedWidth ? '✅ MATCH' : '❌ MISMATCH'}`)
  console.log(`  Month ↔ Day: ${totalMonthWidth === totalDayWidth ? '✅ MATCH' : '❌ MISMATCH'}\n`)
  
  return result
})

// 获取任务条样式
const getBarStyle = (task) => {
  const start = new Date(task.start_date)
  const end = new Date(task.end_date)
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return { display: 'none' }
  }
  
  const dayWidth = DAY_WIDTH.value
  const startOffset = Math.floor((start - projectStart.value) / (1000 * 60 * 60 * 24))
  const duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  
  return {
    left: (startOffset * dayWidth) + 'px',
    width: Math.max(duration * dayWidth - 4, Math.min(40, dayWidth * 2)) + 'px'
  }
}

// 里程碑列表（用于显示在任务列表中）
const milestonesList = computed(() => {
  return props.milestones || []
})

// 辅助函数
const formatDateRange = (start, end) => {
  if (!start || !end) return '-'
  const s = new Date(start)
  const e = new Date(end)
  if (isNaN(s.getTime()) || isNaN(e.getTime())) return '-'
  return `${s.getMonth() + 1}/${s.getDate()} - ${e.getMonth() + 1}/${e.getDate()}`
}

const formatMilestoneDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    in_progress: '',
    completed: 'success',
    blocked: 'danger',
    cancelled: 'info'
  }
  return types[status] || ''
}

// 同步滚动
const handleGanttScroll = (e) => {
  if (ganttTimelineRef.value) {
    ganttTimelineRef.value.scrollLeft = e.target.scrollLeft
  }
}

// 任务点击
const handleTaskClick = (task) => {
  selectedTaskId.value = task.id
  emit('task-click', task)
}

// 拖拽功能
const startDrag = (e, task) => {
  if (dragState.value.isResizing) return
  
  dragState.value = {
    isDragging: true,
    isResizing: false,
    taskId: task.id,
    startX: e.clientX,
    initialStart: new Date(task.start_date),
    initialEnd: new Date(task.end_date)
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  e.preventDefault()
}

const onDrag = (e) => {
  if (!dragState.value.isDragging) return
  
  const deltaX = e.clientX - dragState.value.startX
  const daysDelta = Math.round(deltaX / DAY_WIDTH.value)
  
  if (daysDelta !== 0) {
    const task = props.tasks.find(t => t.id === dragState.value.taskId)
    if (task) {
      const newStart = new Date(dragState.value.initialStart)
      const newEnd = new Date(dragState.value.initialEnd)
      
      newStart.setDate(newStart.getDate() + daysDelta)
      newEnd.setDate(newEnd.getDate() + daysDelta)
      
      emit('task-update', {
        id: task.id,
        start_date: newStart.toISOString(),
        end_date: newEnd.toISOString()
      })
      
      dragState.value.initialStart = newStart
      dragState.value.initialEnd = newEnd
      dragState.value.startX = e.clientX
    }
  }
}

const stopDrag = () => {
  dragState.value.isDragging = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 调整大小
const startResize = (e, task, direction) => {
  dragState.value = {
    isDragging: false,
    isResizing: true,
    taskId: task.id,
    direction: direction,
    startX: e.clientX,
    initialStart: new Date(task.start_date),
    initialEnd: new Date(task.end_date)
  }
  
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

const onResize = (e) => {
  if (!dragState.value.isResizing) return
  
  const deltaX = e.clientX - dragState.value.startX
  const daysDelta = Math.round(deltaX / DAY_WIDTH.value)
  
  if (daysDelta !== 0) {
    const task = props.tasks.find(t => t.id === dragState.value.taskId)
    if (!task) return
    
    let newStart = new Date(dragState.value.initialStart)
    let newEnd = new Date(dragState.value.initialEnd)
    
    if (dragState.value.direction === 'left') {
      newStart.setDate(newStart.getDate() + daysDelta)
      if (newStart >= newEnd) return
    } else {
      newEnd.setDate(newEnd.getDate() + daysDelta)
      if (newEnd <= newStart) return
    }
    
    emit('task-update', {
      id: task.id,
      start_date: newStart.toISOString(),
      end_date: newEnd.toISOString()
    })
    
    if (dragState.value.direction === 'left') {
      dragState.value.initialStart = newStart
    } else {
      dragState.value.initialEnd = newEnd
    }
    dragState.value.startX = e.clientX
  }
}

const stopResize = () => {
  dragState.value.isResizing = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

// DOM宽度测量和调试
onMounted(() => {
  nextTick(() => {
    measureWidths()
  })
})

// 监听zoomLevel变化，重新测量
watch(() => props.zoomLevel, () => {
  nextTick(() => {
    measureWidths()
  })
})

const measureWidths = () => {
  console.log('\n🔍 ===== DOM Width Measurement =====')
  
  // 测量月份元素
  const monthElements = document.querySelectorAll('.gantt-month')
  console.log(`\n📦 Month Elements (${monthElements.length} total):`)
  let totalMonthWidth = 0
  monthElements.forEach((el, index) => {
    const width = el.offsetWidth
    const computedStyle = window.getComputedStyle(el)
    const setWidth = computedStyle.width
    totalMonthWidth += width
    console.log(`  ${index + 1}. ${el.textContent.trim()}:`)
    console.log(`      Actual (offsetWidth): ${width}px`)
    console.log(`      CSS (width): ${setWidth}`)
  })
  console.log(`  ➡️  Total Month Width: ${totalMonthWidth}px`)
  
  // 测量日期元素
  const dayElements = document.querySelectorAll('.gantt-day')
  console.log(`\n📅 Day Elements (${dayElements.length} total):`)
  let totalDayWidth = 0
  const dayWidths = new Set()
  dayElements.forEach((el, index) => {
    const width = el.offsetWidth
    totalDayWidth += width
    dayWidths.add(width)
    if (index < 5 || index >= dayElements.length - 5) {
      console.log(`  ${index + 1}. Day ${el.textContent.trim()}: ${width}px`)
    } else if (index === 5) {
      console.log(`  ... (${dayElements.length - 10} more days) ...`)
    }
  })
  console.log(`  ➡️  Total Day Width: ${totalDayWidth}px`)
  console.log(`  ➡️  Unique Day Widths: [${Array.from(dayWidths).join(', ')}]px`)
  
  // 测量网格列元素
  const gridElements = document.querySelectorAll('.grid-col')
  console.log(`\n🔲 Grid Elements (${gridElements.length} total):`)
  const gridWidths = new Set()
  gridElements.forEach(el => {
    gridWidths.add(el.offsetWidth)
  })
  console.log(`  ➡️  Unique Grid Widths: [${Array.from(gridWidths).join(', ')}]px`)
  
  // 对比结果
  console.log(`\n📊 Comparison:`)
  console.log(`  Month Total: ${totalMonthWidth}px`)
  console.log(`  Day Total: ${totalDayWidth}px`)
  console.log(`  Difference: ${Math.abs(totalMonthWidth - totalDayWidth)}px`)
  console.log(`  Match: ${totalMonthWidth === totalDayWidth ? '✅ YES' : '❌ NO'}`)
  console.log(`\n💡 DAY_WIDTH setting: ${DAY_WIDTH.value}px (zoomLevel: ${props.zoomLevel})`)
  console.log(`\n🔍 ===== End Measurement =====\n`)
}
</script>

<style scoped>
.gantt-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
}

/* ========== 上半部分：任务列表 ========== */
.task-section {
  flex: 0 0 auto;
  max-height: 40%;
  display: flex;
  flex-direction: column;
  border: 2px solid #e74c3c;
  border-bottom: none;
  overflow: hidden;
}

.task-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 2px solid #409eff;
  flex-shrink: 0;
}

.col-header {
  padding: 14px 16px;
  font-weight: 700;
  font-size: 13px;
  color: #303133;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  border-right: 1px solid #e4e7ed;
}

.col-task {
  width: 280px;
}

.col-dates {
  width: 180px;
}

.col-assignee {
  width: 140px;
}

.col-actions {
  width: 140px;
}

.col-milestone {
  flex: 1;
  min-width: 200px;
  border-right: none;
}

.task-list {
  flex: 1;
  overflow-y: auto;
}

.task-row {
  display: flex;
  min-height: 60px;
  border-bottom: 1px solid #e4e7ed;
  transition: background 0.2s;
}

.task-row:hover {
  background: #f5f7fa;
}

.col-cell {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
  border-right: 1px solid #e4e7ed;
}

.col-cell.col-task {
  gap: 10px;
}

.task-name {
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.date-range {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.col-cell.col-actions {
  gap: 10px;
  justify-content: center;
}

.col-cell.col-milestone {
  padding: 8px 16px;
}

.milestone-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.milestone-item {
  display: inline-flex;
  flex-direction: column;
  padding: 6px 12px;
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  gap: 2px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.milestone-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.milestone-name {
  font-weight: 600;
}

.milestone-date {
  font-size: 11px;
  opacity: 0.9;
}

.no-milestone {
  color: #909399;
  font-size: 13px;
}

/* ========== 下半部分：甘特图 ========== */
.gantt-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 2px solid #e74c3c;
  overflow: hidden;
}

.gantt-timeline-header {
  flex-shrink: 0;
  overflow-x: hidden;
  overflow-y: hidden;
  background: #f5f7fa;
  border-bottom: 2px solid #409eff;
}

.gantt-months {
  display: flex;
  border-bottom: 1px solid #dcdfe6;
  background: linear-gradient(to bottom, #f0f5ff, #e6f0ff);
}

.gantt-month {
  padding: 12px 4px;
  text-align: center;
  font-weight: 700;
  font-size: 14px;
  color: #409eff;
  background: linear-gradient(to bottom, #f0f5ff, #e6f0ff);
  border-right: 1px solid #dcdfe6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  min-width: 0;
}


.gantt-days {
  display: flex;
}

.gantt-day {
  padding: 8px 2px;
  text-align: center;
  font-size: 11px;
  color: #909399;
  border-right: 1px solid #e4e7ed;
  flex-shrink: 0;
  font-weight: 500;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
  min-width: 0;
}


.gantt-day.weekend {
  background: #fff5f5;
  color: #f56c6c;
}

.gantt-day.today {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 700;
  box-shadow: inset 0 0 0 2px #1890ff;
}

.gantt-chart {
  flex: 1;
  position: relative;
  overflow: auto;
}

.gantt-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  background: #fafafa;
}

.grid-col {
  position: absolute;
  top: 0;
  bottom: 0;
  border-right: 1px solid #e4e7ed;
  box-sizing: border-box;
}

.grid-col.weekend {
  background: #fef5f5;
}

.grid-col.today {
  background: #e6f7ff;
  border-right: 2px solid #1890ff;
}

.gantt-bars {
  position: relative;
  z-index: 2;
  min-height: 100%;
}

.gantt-bar-row {
  position: absolute;
  left: 0;
  right: 0;
  height: 60px;
}

.gantt-task-bar {
  position: absolute;
  height: 44px;
  top: 8px;
  border-radius: 6px;
  cursor: move;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  transition: box-shadow 0.2s, transform 0.2s;
}

.gantt-task-bar:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  transform: translateY(-1px);
  z-index: 10;
}

.gantt-task-bar.selected {
  box-shadow: 0 0 0 3px #409eff;
  z-index: 11;
}

.bar-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.bar-progress {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.25);
  transition: width 0.3s;
}

.bar-label {
  position: relative;
  z-index: 2;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  font-size: 13px;
  font-weight: 600;
  height: 100%;
}

.bar-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-percent {
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
}

/* 状态颜色 */
.gantt-task-bar.status-pending {
  background: linear-gradient(135deg, #909399 0%, #b3b6ba 100%);
}

.gantt-task-bar.status-in_progress {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.gantt-task-bar.status-completed {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.gantt-task-bar.status-blocked {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.gantt-task-bar.status-cancelled {
  background: linear-gradient(135deg, #dcdfe6 0%, #e4e7ed 100%);
}

/* 调整手柄 */
.resize-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: ew-resize;
  z-index: 3;
  opacity: 0;
  transition: opacity 0.2s;
}

.gantt-task-bar:hover .resize-handle {
  opacity: 1;
}

.left-handle {
  left: 0;
  background: linear-gradient(to right, rgba(255,255,255,0.6), transparent);
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}

.right-handle {
  right: 0;
  background: linear-gradient(to left, rgba(255,255,255,0.6), transparent);
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}

/* 滚动条 */
.task-list::-webkit-scrollbar,
.gantt-chart::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.task-list::-webkit-scrollbar-track,
.gantt-chart::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.task-list::-webkit-scrollbar-thumb,
.gantt-chart::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 5px;
}

.task-list::-webkit-scrollbar-thumb:hover,
.gantt-chart::-webkit-scrollbar-thumb:hover {
  background: #555;
}

</style>
