<script setup lang="ts">
import axios from 'axios'
import { useRouter } from 'vue-router'
import { inject, ref, onMounted } from 'vue'
import { AgGridVue } from "ag-grid-vue3";
import type { GridOptions, Theme } from 'ag-grid-community'

interface Project {
    project_id: string
}

// reactive state
const router = useRouter()
const mdTheme = inject<Theme<unknown>>('mdTheme');

const md = ref<Project[]>([])
const error = ref<string | null>(null)
const loading = ref(true)

const columnDefs: GridOptions['columnDefs'] = [
    { headerName: 'Project', field: 'project_id' },
]

onMounted(async () => {
    try {
        const res = await axios.get('/api/projects')
        if (res.data.status === "success") {
            md.value = res.data.table
        } else {
            error.value = 'Failed to load projects'
        }
    } catch (e) {
        error.value = 'Network or server error'
        console.error(e)
    } finally {
        loading.value = false
    }
})

// event handlers
function onRowClicked(event: any) {
    const projectId = event.data?.project_id
    if (projectId) {
        router.push(`/project/${projectId}`)
    }
}

// grid options
const gridOptions: GridOptions = {
    columnDefs,
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        wrapText: false,
        autoHeight: false,
    },
    pagination: true,
    paginationAutoPageSize: false,
    animateRows: false,
}
</script>

<template>
    <div>
        <div v-if="loading">Loading...</div>
        <div v-if="error" class="error">{{ error }}</div>
        <ag-grid-vue v-else class="ag-theme-balham ag-grid-wrapper" :rowData="md" :gridOptions="gridOptions"
            :theme="mdTheme" @rowClicked="onRowClicked" />
    </div>
</template>


<style scoped>
.ag-grid-wrapper {
    height: 100vh;
    width: 80vw;
}
</style>
